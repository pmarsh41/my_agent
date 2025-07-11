from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any, AsyncGenerator
from pydantic import BaseModel
import os
from datetime import date, datetime
import shutil
import base64
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import uvicorn
import json
from evaluation_endpoints import setup_evaluation_endpoints

# Load environment variables
load_dotenv()

# Arize and tracing imports
from arize.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor
from openinference.instrumentation import using_prompt_template
from opentelemetry import trace

# LangGraph and LangChain imports
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# Database imports
from database import get_db, create_tables
from models import User, Meal, DailySummary, Notification, GoalStatus, NotificationType
from schemas import (
    UserCreate, UserUpdate, User as UserSchema, 
    MealCreate, Meal as MealSchema, 
    DailySummary as DailySummarySchema, 
    Notification as NotificationSchema
)

# Smart meal analysis imports
from smart_meal_agent import (
    identify_foods_in_image, 
    match_foods_to_database, 
    suggest_portions_with_reasoning,
    generate_conversational_response
)

# Global tracer provider
tracer_provider = None

# Initialize Arize tracing
def setup_tracing() -> Optional[Any]:
    """Initialize Arize tracing for observability.
    
    Returns:
        Optional[Any]: Tracer provider if successful, None otherwise
    """
    global tracer_provider
    try:
        space_id = os.getenv("ARIZE_SPACE_ID")
        api_key = os.getenv("ARIZE_API_KEY")
        
        if not space_id or not api_key or space_id == "your_arize_space_id_here" or api_key == "your_arize_api_key_here":
            print("ℹ️ Arize tracing disabled - credentials not configured")
            print("📝 To enable tracing, set ARIZE_SPACE_ID and ARIZE_API_KEY in backend/.env")
            return None
        
        # Set OTLP exporter environment variables for better timeout handling
        os.environ["OTEL_EXPORTER_OTLP_TIMEOUT"] = "30000"  # 30 seconds timeout
        os.environ["OTEL_BSP_MAX_EXPORT_BATCH_SIZE"] = "1"  # Send only 1 trace at a time
        os.environ["OTEL_BSP_SCHEDULE_DELAY"] = "30000"  # 30 seconds delay between exports
        os.environ["OTEL_BSP_MAX_QUEUE_SIZE"] = "2048"  # Larger queue to buffer traces
            
        tracer_provider = register(
            space_id=space_id,
            api_key=api_key,
            project_name="protein-tracker"
        )
        
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
        
        print("✅ Arize tracing initialized successfully")
        print(f"📊 Project: protein-tracker")
        print(f"🔗 Space ID: {space_id[:8]}...")
        print("⚡ Rate limiting configured: 32 traces per batch, 10s between exports")
        
        return tracer_provider
        
    except Exception as e:
        print(f"ℹ️ Arize tracing setup failed: {str(e)}")
        print("📝 Continuing without tracing - this is optional")
        return None

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for setup and teardown.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None: Application context
    """
    # Setup tracing before anything else
    setup_tracing()
    # Create database tables
    create_tables()
    yield

app = FastAPI(title="Protein Intake Agent API", lifespan=lifespan)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup evaluation endpoints and pipeline
space_id = os.getenv("ARIZE_SPACE_ID")
api_key = os.getenv("ARIZE_API_KEY")

if space_id and api_key:
    evaluation_pipeline = setup_evaluation_endpoints(app, space_id, api_key)
    print("✅ Evaluation system initialized")
else:
    print("⚠️ Evaluation system disabled - Arize credentials not found")

# Pydantic models for meal analysis
class MealAnalysisRequest(BaseModel):
    user_id: int
    
class MealAnalysisResponse(BaseModel):
    foods_detected: List[str]
    protein_estimate: float
    meal_id: Optional[int] = None

# New smart analysis models
class SmartMealAnalysisResponse(BaseModel):
    success: bool
    conversation_response: str
    identified_foods: List[Dict[str, Any]]
    portion_suggestions: List[Dict[str, Any]]
    unmatched_foods: List[Dict[str, Any]]
    total_protein_estimate: float
    confidence_level: str
    requires_user_input: bool
    
class PortionConfirmationRequest(BaseModel):
    user_id: int
    confirmed_portions: List[Dict[str, Any]]  # User's confirmed/adjusted portions

# Define the state for smart meal analysis graph
class SmartMealAnalysisState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: int
    image_data: str  # base64 encoded image
    image_mime_type: Optional[str]  # image MIME type
    identified_foods: Optional[List[Dict]]
    matched_foods: Optional[List[Dict]]
    unmatched_foods: Optional[List[Dict]]
    portion_suggestions: Optional[List[Dict]]
    conversation_response: Optional[str]
    total_protein_estimate: Optional[float]
    confidence_level: Optional[str]
    requires_user_input: Optional[bool]
    final_result: Optional[Dict[str, Any]]

# Initialize the LLM
llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=1000,
    timeout=30
)

# Define protein analysis tools
@tool
def analyze_meal_image(image_data: str) -> Dict[str, Any]:
    """Analyze a meal image to identify foods and estimate protein content.
    
    Args:
        image_data: Base64 encoded image data
    """
    system_prompt = """You are a nutrition expert specializing in food identification and protein estimation. 
    Analyze the image and provide accurate food identification and protein estimates.
    Be specific and conservative in your estimates."""
    
    prompt_template = """Analyze this meal image and provide:
1. List of foods you can identify
2. Estimated protein content for each food item
3. Total protein estimate for the meal

Format your response as:
Foods: [food1, food2, food3]
Protein per item: [food1: Xg, food2: Yg, food3: Zg]
Total protein: XXg

Be conservative and realistic in your estimates. If you're unsure about an item, provide a lower estimate."""
    
    prompt_template_variables = {
        "image_analysis": "meal image analysis"
    }
    
    try:
        with using_prompt_template(
            template=prompt_template,
            variables=prompt_template_variables,
            version="meal-analysis-v1.0",
        ):
            # Create message with image
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=[
                    {"type": "text", "text": prompt_template},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ])
            ]
            
            response = llm.invoke(messages)
            
            # Parse the response to extract foods and protein
            content = response.content
            foods = []
            protein_estimate = 0.0
            
            # Simple parsing - in production, you'd want more robust parsing
            lines = content.split('\n')
            for line in lines:
                if line.startswith('Foods:'):
                    foods_str = line.replace('Foods:', '').strip()
                    foods = [food.strip(' []') for food in foods_str.split(',')]
                elif line.startswith('Total protein:'):
                    protein_str = line.replace('Total protein:', '').strip().replace('g', '')
                    try:
                        protein_estimate = float(protein_str)
                    except:
                        protein_estimate = 0.0
            
            return {
                "foods_detected": foods,
                "protein_estimate": protein_estimate,
                "analysis_text": content
            }
            
    except Exception as e:
        print(f"Error in meal analysis: {str(e)}")
        return {
            "foods_detected": [],
            "protein_estimate": 0.0,
            "analysis_text": f"Analysis failed: {str(e)}"
        }

@tool
def log_meal_to_database(user_id: int, foods_detected: List[str], protein_estimate: float, image_filename: str = None) -> Dict[str, Any]:
    """Log the analyzed meal to the database.
    
    Args:
        user_id: User ID
        foods_detected: List of detected foods
        protein_estimate: Estimated protein content
        image_filename: Optional image filename
    """
    try:
        # This would normally use dependency injection, but for the tool we'll create a session
        from database import SessionLocal
        db = SessionLocal()
        
        # Create meal entry
        meal_data = {
            "user_id": user_id,
            "foods_detected": json.dumps(foods_detected),
            "protein_estimate": protein_estimate,
            "image_url": f"/uploads/{image_filename}" if image_filename else None,
            "timestamp": datetime.utcnow()
        }
        
        db_meal = Meal(**meal_data)
        db.add(db_meal)
        db.commit()
        db.refresh(db_meal)
        
        # Update daily summary
        meal_date = db_meal.timestamp.date()
        _update_daily_summary(db, user_id, meal_date)
        
        db.close()
        
        return {
            "success": True,
            "meal_id": db_meal.id,
            "message": "Meal logged successfully"
        }
        
    except Exception as e:
        print(f"Error logging meal: {str(e)}")
        return {
            "success": False,
            "meal_id": None,
            "message": f"Failed to log meal: {str(e)}"
        }

# Helper function to update daily summary (keeping existing logic)
def _update_daily_summary(db: Session, user_id: int, summary_date: date):
    """Helper function to update or create daily summary for a user and date"""
    # Calculate total protein for the day
    total_protein_result = db.query(func.sum(Meal.protein_estimate)).filter(
        Meal.user_id == user_id,
        func.date(Meal.timestamp) == summary_date
    ).scalar()
    total_protein = float(total_protein_result) if total_protein_result is not None else 0.0
    
    # Get user's protein goal
    user = db.query(User).filter(User.id == user_id).first()
    goal = float(user.protein_goal) if user and user.protein_goal else 0.0
    
    # Determine status
    if goal == 0:
        status = GoalStatus.ON_TRACK
    elif total_protein >= goal:
        status = GoalStatus.MET
    elif total_protein >= goal * 0.8:  # 80% of goal
        status = GoalStatus.ON_TRACK
    else:
        status = GoalStatus.MISSED
    
    # Check if daily summary exists and update, or create new one
    existing_summary = db.query(DailySummary).filter(
        DailySummary.user_id == user_id,
        DailySummary.date == summary_date
    ).first()
    
    if existing_summary:
        existing_summary.total_protein = total_protein
        existing_summary.goal = goal
        existing_summary.status = status
        existing_summary.updated_at = datetime.utcnow()
    else:
        # Create new daily summary
        db_summary = DailySummary(
            user_id=user_id,
            date=summary_date,
            total_protein=total_protein,
            goal=goal,
            status=status
        )
        db.add(db_summary)
    
    db.commit()

# =============================================================================
# LANGGRAPH WORKFLOW NODES - Smart Meal Analysis Pipeline
# =============================================================================
# This workflow uses 4 specialized agents to process meal images:
# 1. Food ID Agent: Analyzes images to identify foods with confidence scores
# 2. DB Matching Agent: Matches identified foods to nutrition database
# 3. Portion Agent: Suggests portion sizes based on visual cues
# 4. Conversation Agent: Generates natural language responses
# =============================================================================

def food_identification_node(state: SmartMealAnalysisState) -> SmartMealAnalysisState:
    """Step 1: Identify foods in the image with confidence scores
    
    This node uses OpenAI Vision API to analyze meal images and identify
    individual food items with confidence levels, visual reasoning, and
    preparation methods. It's designed to be honest about limitations
    and provide detailed reasoning for each identification.
    """
    try:
        print(f"🔍 Starting smart food identification for user {state['user_id']}")
        
        # Call function directly to avoid LangChain parameter issues
        # This bypasses the tool wrapper and calls the underlying function
        from smart_meal_agent import identify_foods_in_image
        identification_result = identify_foods_in_image.func({
            "image_data": state["image_data"],
            "image_mime_type": state.get("image_mime_type", "image/jpeg")
        })
        
        if identification_result["success"]:
            print(f"✅ Identified {identification_result['total_foods_found']} foods")
            
            return {
                "messages": [HumanMessage(content=f"Food identification completed: {identification_result['total_foods_found']} foods found")],
                "identified_foods": identification_result["identified_foods"]
            }
        else:
            print(f"❌ Food identification failed: {identification_result.get('error', 'Unknown error')}")
            return {
                "messages": [HumanMessage(content=f"Food identification failed")],
                "identified_foods": [],
                "requires_user_input": True
            }
        
    except Exception as e:
        print(f"❌ Food identification error: {str(e)}")
        return {
            "messages": [HumanMessage(content=f"Food identification failed: {str(e)}")],
            "identified_foods": [],
            "requires_user_input": True
        }

def database_matching_node(state: SmartMealAnalysisState) -> SmartMealAnalysisState:
    """Step 2: Match identified foods to nutrition database
    
    This node takes AI-identified foods and matches them against our
    comprehensive nutrition database using fuzzy matching algorithms.
    It combines AI confidence scores with database match confidence
    to provide accurate nutrition information.
    """
    try:
        print(f"🔍 Matching foods to database")
        
        identified_foods = state.get("identified_foods", [])
        if not identified_foods:
            return {
                "messages": [HumanMessage(content="No foods to match")],
                "matched_foods": [],
                "unmatched_foods": []
            }
        
        # Call function directly to avoid LangChain parameter issues
        # Uses fuzzy matching to find the best database matches
        from smart_meal_agent import match_foods_to_database
        matching_result = match_foods_to_database.func(identified_foods)
        
        print(f"✅ Database matching completed - {len(matching_result['matched_foods'])} matched, {len(matching_result['unmatched_foods'])} unmatched")
        
        return {
            "messages": [HumanMessage(content=f"Database matching completed")],
            "matched_foods": matching_result["matched_foods"],
            "unmatched_foods": matching_result["unmatched_foods"]
        }
        
    except Exception as e:
        print(f"❌ Database matching error: {str(e)}")
        return {
            "messages": [HumanMessage(content=f"Database matching failed: {str(e)}")],
            "matched_foods": [],
            "unmatched_foods": state.get("identified_foods", [])
        }

def portion_suggestion_node(state: SmartMealAnalysisState) -> SmartMealAnalysisState:
    """Step 3: Suggest portions with reasoning
    
    This node analyzes matched foods and suggests appropriate portion sizes
    based on visual cues, typical serving sizes, and preparation methods.
    It provides detailed reasoning for each portion suggestion and calculates
    total protein estimates with confidence levels.
    """
    try:
        print(f"🍽️ Generating portion suggestions")
        
        matched_foods = state.get("matched_foods", [])
        if not matched_foods:
            return {
                "messages": [HumanMessage(content="No matched foods for portion estimation")],
                "portion_suggestions": [],
                "total_protein_estimate": 0.0
            }
        
        # Call function directly to avoid LangChain parameter issues
        # Analyzes visual cues and suggests appropriate portion sizes
        from smart_meal_agent import suggest_portions_with_reasoning
        portion_result = suggest_portions_with_reasoning.func({
            "matched_foods": matched_foods,
            "image_context": "meal photo analysis"
        })
        
        print(f"✅ Portion suggestions generated - estimated {portion_result['total_estimated_protein']:.1f}g protein")
        
        return {
            "messages": [HumanMessage(content="Portion suggestions generated")],
            "portion_suggestions": portion_result["portion_suggestions"],
            "total_protein_estimate": portion_result["total_estimated_protein"],
            "confidence_level": portion_result["confidence_summary"]
        }
        
    except Exception as e:
        print(f"❌ Portion suggestion error: {str(e)}")
        return {
            "messages": [HumanMessage(content=f"Portion suggestion failed: {str(e)}")],
            "portion_suggestions": [],
            "total_protein_estimate": 0.0,
            "confidence_level": "error"
        }

def conversation_generation_node(state: SmartMealAnalysisState) -> SmartMealAnalysisState:
    """Step 4: Generate conversational response for user
    
    This node creates a natural language response that summarizes the analysis
    results, explains portion suggestions, and handles unmatched foods gracefully.
    It determines if user input is required and provides helpful guidance.
    """
    try:
        print(f"💬 Generating conversational response")
        
        portion_suggestions = state.get("portion_suggestions", [])
        unmatched_foods = state.get("unmatched_foods", [])
        
        # Generate natural language response based on analysis results
        conversation_response = generate_conversational_response.invoke({
            "portion_suggestions": portion_suggestions,
            "unmatched_foods": unmatched_foods
        })
        
        requires_input = len(unmatched_foods) > 0 or len(portion_suggestions) == 0
        
        print(f"✅ Conversational response generated")
        
        final_result = {
            "success": True,
            "conversation_response": conversation_response,
            "identified_foods": state.get("identified_foods", []),
            "portion_suggestions": portion_suggestions,
            "unmatched_foods": unmatched_foods,
            "total_protein_estimate": state.get("total_protein_estimate", 0.0),
            "confidence_level": state.get("confidence_level", "unknown"),
            "requires_user_input": requires_input
        }
        
        return {
            "messages": [HumanMessage(content="Analysis complete")],
            "conversation_response": conversation_response,
            "requires_user_input": requires_input,
            "final_result": final_result
        }
        
    except Exception as e:
        print(f"❌ Conversation generation error: {str(e)}")
        
        error_result = {
            "success": False,
            "conversation_response": "I'm having trouble analyzing this image. Could you help me by telling me what foods you're eating?",
            "identified_foods": [],
            "portion_suggestions": [],
            "unmatched_foods": [],
            "total_protein_estimate": 0.0,
            "confidence_level": "error",
            "requires_user_input": True,
            "error": str(e)
        }
        
        return {
            "messages": [HumanMessage(content=f"Analysis failed: {str(e)}")],
            "conversation_response": error_result["conversation_response"],
            "requires_user_input": True,
            "final_result": error_result
        }

# =============================================================================
# GRAPH CONSTRUCTION - Smart Meal Analysis Workflow
# =============================================================================
# This creates a 4-step pipeline that processes meal images:
# START → Food ID → DB Match → Portion → Conversation → END
# Each step adds data to the state and passes it to the next node
# =============================================================================

def create_smart_meal_analysis_graph():
    """Create and compile the smart meal analysis graph
    
    Builds a LangGraph workflow that processes meal images through
    4 specialized nodes, each adding information to the state
    and passing it to the next step in the pipeline.
    
    Returns:
        Compiled LangGraph workflow ready for execution
    """
    workflow = StateGraph(SmartMealAnalysisState)
    
    # Add nodes to the workflow
    workflow.add_node("food_identification", food_identification_node)
    workflow.add_node("database_matching", database_matching_node)
    workflow.add_node("portion_suggestion", portion_suggestion_node)
    workflow.add_node("conversation_generation", conversation_generation_node)
    
    # Define the linear workflow path
    workflow.add_edge(START, "food_identification")
    workflow.add_edge("food_identification", "database_matching")
    workflow.add_edge("database_matching", "portion_suggestion")
    workflow.add_edge("portion_suggestion", "conversation_generation")
    workflow.add_edge("conversation_generation", END)
    
    # Compile with memory
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

# Define the legacy state for backwards compatibility
class ProteinAnalysisState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: int
    image_data: str  # base64 encoded image
    foods_detected: Optional[List[str]]
    protein_estimate: Optional[float]
    meal_logged: Optional[bool]
    final_result: Optional[Dict[str, Any]]

# Legacy workflow for backwards compatibility
def image_analysis_node(state: ProteinAnalysisState) -> ProteinAnalysisState:
    """Analyze the meal image to identify foods and estimate protein"""
    try:
        print(f"🔍 Starting meal image analysis for user {state['user_id']}")
        
        analysis_result = analyze_meal_image.invoke({
            "image_data": state["image_data"]
        })
        
        print(f"✅ Image analysis completed - found {len(analysis_result['foods_detected'])} foods")
        
        return {
            "messages": [HumanMessage(content=f"Analysis completed: {analysis_result['analysis_text']}")],
            "foods_detected": analysis_result["foods_detected"],
            "protein_estimate": analysis_result["protein_estimate"]
        }
        
    except Exception as e:
        print(f"❌ Image analysis error: {str(e)}")
        return {
            "messages": [HumanMessage(content=f"Analysis failed: {str(e)}")],
            "foods_detected": [],
            "protein_estimate": 0.0
        }

def meal_logging_node(state: ProteinAnalysisState) -> ProteinAnalysisState:
    """Log the analyzed meal to the database"""
    try:
        print(f"💾 Logging meal for user {state['user_id']}")
        
        foods = state.get("foods_detected", [])
        protein = state.get("protein_estimate", 0.0)
        
        logging_result = log_meal_to_database.invoke({
            "user_id": state["user_id"],
            "foods_detected": foods,
            "protein_estimate": protein
        })
        
        print(f"✅ Meal logging completed - success: {logging_result['success']}")
        
        return {
            "messages": [HumanMessage(content=f"Logging completed: {logging_result['message']}")],
            "meal_logged": logging_result["success"],
            "final_result": {
                "foods_detected": foods,
                "protein_estimate": protein,
                "meal_id": logging_result.get("meal_id"),
                "success": logging_result["success"]
            }
        }
        
    except Exception as e:
        print(f"❌ Meal logging error: {str(e)}")
        return {
            "messages": [HumanMessage(content=f"Logging failed: {str(e)}")],
            "meal_logged": False,
            "final_result": {
                "foods_detected": state.get("foods_detected", []),
                "protein_estimate": state.get("protein_estimate", 0.0),
                "meal_id": None,
                "success": False,
                "error": str(e)
            }
        }

# Build the protein analysis graph
def create_protein_analysis_graph():
    """Create and compile the protein analysis graph"""
    workflow = StateGraph(ProteinAnalysisState)
    
    # Add nodes
    workflow.add_node("image_analysis", image_analysis_node)
    workflow.add_node("meal_logging", meal_logging_node)
    
    # Define workflow
    workflow.add_edge(START, "image_analysis")
    workflow.add_edge("image_analysis", "meal_logging")
    workflow.add_edge("meal_logging", END)
    
    # Compile with memory
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

# API Routes - keeping all existing routes and adding new LangGraph-powered analysis

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Protein Intake Agent API is running with LangGraph"}

# All existing user endpoints remain the same...
@app.post("/users/", response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[UserSchema])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserSchema)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    # Auto-calculate protein goal if weight and activity level are provided
    if user.weight and user.activity_level and not user.protein_goal:
        protein_multipliers = {
            "sedentary": 1.0,
            "moderate": 1.2,
            "active": 1.4,
            "very_active": 1.6
        }
        multiplier = protein_multipliers.get(user.activity_level.value, 1.2)
        user.protein_goal = user.weight * multiplier
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user

# New Smart LangGraph-powered meal analysis endpoint
@app.post("/analyze-meal-smart/", response_model=SmartMealAnalysisResponse)
async def analyze_meal_smart(user_id: int, file: UploadFile = File(...)):
    """Analyze meal using smart AI-assisted workflow with conversational interface"""
    try:
        # Read and encode image
        image_bytes = file.file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Detect actual image format from content, not just filename
        # Check the actual file header/magic bytes
        image_header = image_bytes[:12]
        
        if image_header.startswith(b'\x89PNG'):
            image_mime_type = 'image/png'
        elif image_header.startswith(b'\xff\xd8\xff'):
            image_mime_type = 'image/jpeg'
        elif b'ftyphei' in image_header or b'ftypmif1' in image_header:
            # HEIC format - OpenAI doesn't support this
            print("⚠️ HEIC format detected - not supported by OpenAI Vision")
            return SmartMealAnalysisResponse(
                success=False,
                conversation_response="I can't analyze HEIC/HEIF images (iPhone camera format). Please convert to JPEG or change your camera settings to 'Most Compatible' format and try again.",
                identified_foods=[],
                portion_suggestions=[],
                unmatched_foods=[],
                total_protein_estimate=0.0,
                confidence_level="unsupported_format",
                requires_user_input=True
            )
        elif image_header.startswith(b'GIF8'):
            image_mime_type = 'image/gif'
        elif image_header.startswith(b'RIFF') and b'WEBP' in image_header:
            image_mime_type = 'image/webp'
        else:
            # Fallback to filename detection
            filename = file.filename.lower()
            if filename.endswith('.png'):
                image_mime_type = 'image/png'
            elif filename.endswith(('.jpg', '.jpeg')):
                image_mime_type = 'image/jpeg'
            elif filename.endswith('.gif'):
                image_mime_type = 'image/gif'
            elif filename.endswith('.webp'):
                image_mime_type = 'image/webp'
            else:
                image_mime_type = 'image/jpeg'  # Default fallback
        
        # Save uploaded file
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_location = os.path.join(uploads_dir, f"meal_{user_id}_{timestamp}_{file.filename}")
        
        # Reset file pointer and save
        file.file.seek(0)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create and run the smart meal analysis graph
        graph = create_smart_meal_analysis_graph()
        
        initial_state = {
            "messages": [],
            "user_id": user_id,
            "image_data": image_base64,
            "image_mime_type": image_mime_type,
            "identified_foods": None,
            "matched_foods": None,
            "unmatched_foods": None,
            "portion_suggestions": None,
            "conversation_response": None,
            "total_protein_estimate": None,
            "confidence_level": "analyzing",
            "requires_user_input": None,
            "final_result": None
        }
        
        config = {"configurable": {"thread_id": f"smart_meal_analysis_{user_id}_{timestamp}"}}
        
        print(f"🚀 Starting smart meal analysis for user {user_id}")
        
        output = graph.invoke(initial_state, config)
        
        print(f"✅ Smart meal analysis completed")
        
        if output and output.get("final_result"):
            result = output["final_result"]
            return SmartMealAnalysisResponse(**result)
        else:
            # Fallback response
            return SmartMealAnalysisResponse(
                success=False,
                conversation_response="I'm having trouble analyzing this image. Could you help me by telling me what foods you're eating?",
                identified_foods=[],
                portion_suggestions=[],
                unmatched_foods=[],
                total_protein_estimate=0.0,
                confidence_level="error",
                requires_user_input=True
            )
            
    except Exception as e:
        print(f"❌ Smart meal analysis error: {str(e)}")
        return SmartMealAnalysisResponse(
            success=False,
            conversation_response=f"Analysis failed: {str(e)}. Please try again or enter your meal manually.",
            identified_foods=[],
            portion_suggestions=[],
            unmatched_foods=[],
            total_protein_estimate=0.0,
            confidence_level="error",
            requires_user_input=True
        )

# Legacy LangGraph-powered meal analysis endpoint (keeping for backwards compatibility)
@app.post("/analyze-meal-ai/", response_model=MealAnalysisResponse)
async def analyze_meal_ai(request: MealAnalysisRequest, file: UploadFile = File(...)):
    """Analyze meal using AI-powered LangGraph workflow"""
    try:
        # Read and encode image
        image_bytes = file.file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Save uploaded file
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        file_location = os.path.join(uploads_dir, file.filename)
        
        # Reset file pointer and save
        file.file.seek(0)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create and run the protein analysis graph
        graph = create_protein_analysis_graph()
        
        initial_state = {
            "messages": [],
            "user_id": request.user_id,
            "image_data": image_base64,
            "foods_detected": None,
            "protein_estimate": None,
            "meal_logged": None,
            "final_result": None
        }
        
        config = {"configurable": {"thread_id": f"meal_analysis_{request.user_id}_{datetime.now().isoformat()}"}}
        
        print(f"🚀 Starting AI meal analysis for user {request.user_id}")
        
        output = graph.invoke(initial_state, config)
        
        print(f"✅ AI meal analysis completed")
        
        if output and output.get("final_result"):
            result = output["final_result"]
            return MealAnalysisResponse(
                foods_detected=result.get("foods_detected", []),
                protein_estimate=result.get("protein_estimate", 0.0),
                meal_id=result.get("meal_id")
            )
        else:
            raise HTTPException(status_code=500, detail="Analysis completed but no results available")
            
    except Exception as e:
        print(f"❌ AI meal analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Keep the original simple analysis endpoint for backward compatibility
@app.post("/analyze-meal/")
def analyze_meal_simple(file: UploadFile = File(...)):
    """Simple meal analysis (legacy endpoint)"""
    try:
        # Read image bytes
        image_bytes = file.file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Use the LangGraph tool directly
        result = analyze_meal_image.invoke({"image_data": image_base64})
        
        return {
            "foods_detected": result["foods_detected"],
            "protein_estimate": result["protein_estimate"],
            "analysis_text": result["analysis_text"]
        }
        
    except Exception as e:
        return {"error": "Analysis failed", "details": str(e)}

# File upload endpoint
@app.post("/upload/")
def upload_image(file: UploadFile = File(...)):
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    file_location = os.path.join(uploads_dir, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    url = f"/uploads/{file.filename}"
    return {"url": url}

# All other existing endpoints for meals, daily summaries, notifications...
# (keeping all the existing functionality)

@app.post("/meals/", response_model=MealSchema)
def create_meal(meal: MealCreate, db: Session = Depends(get_db)):
    meal_dict = meal.dict()
    if 'foods_detected' in meal_dict and isinstance(meal_dict['foods_detected'], list):
        meal_dict['foods_detected'] = json.dumps(meal_dict['foods_detected'])
    db_meal = Meal(**meal_dict)
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    
    # Automatically update daily summary for this meal's date
    meal_date = db_meal.timestamp.date()
    _update_daily_summary(db, meal.user_id, meal_date)
    
    return db_meal

@app.get("/meals/", response_model=List[MealSchema])
def get_meals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    meals = db.query(Meal).offset(skip).limit(limit).all()
    return meals

@app.get("/users/{user_id}/meals", response_model=List[MealSchema])
def get_user_meals(user_id: int, db: Session = Depends(get_db)):
    meals = db.query(Meal).filter(Meal.user_id == user_id).all()
    return meals

# Endpoint for confirming portions and logging final meal
@app.post("/confirm-meal-portions/")
async def confirm_meal_portions(request: PortionConfirmationRequest, db: Session = Depends(get_db)):
    """Handle user confirmation of portions and log final meal to database"""
    try:
        total_protein = 0.0
        logged_foods = []
        
        for portion_data in request.confirmed_portions:
            food_name = portion_data.get("food_name", "Unknown food")
            protein_amount = portion_data.get("protein_grams", 0.0)
            portion_description = portion_data.get("portion_description", "")
            
            total_protein += protein_amount
            logged_foods.append(f"{food_name} ({portion_description})")
        
        # Create meal entry
        meal_data = {
            "user_id": request.user_id,
            "foods_detected": json.dumps(logged_foods),
            "protein_estimate": total_protein,
            "image_url": None,  # Could link to saved image if needed
            "timestamp": datetime.utcnow()
        }
        
        db_meal = Meal(**meal_data)
        db.add(db_meal)
        db.commit()
        db.refresh(db_meal)
        
        # Update daily summary
        meal_date = db_meal.timestamp.date()
        _update_daily_summary(db, request.user_id, meal_date)
        
        return {
            "success": True,
            "message": f"Meal logged successfully! Total protein: {total_protein:.1f}g",
            "meal_id": db_meal.id,
            "total_protein": total_protein,
            "foods_logged": logged_foods
        }
        
    except Exception as e:
        print(f"❌ Meal confirmation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to log meal: {str(e)}")

# Mount static files for uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)