"""
Smart Meal Analysis Agent - Realistic AI-Assisted Food Logging
Uses LangGraph workflows for intelligent food identification and portion estimation
"""
from typing import Dict, List, Optional, Any, Tuple
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from openinference.instrumentation import using_prompt_template
import json
import os
from nutrition_database import nutrition_db

# Initialize LLM for food analysis
analysis_llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini",
    temperature=0.1,  # Low temperature for consistent analysis
    max_tokens=1500,
    timeout=30
)

@tool
def identify_foods_in_image(params: Dict[str, Any]) -> Dict[str, Any]:
    """Identify foods in image with confidence scores and visual reasoning.
    
    Uses OpenAI Vision API to analyze meal images and identify foods with
    confidence levels, visual cues, and preparation methods.
    
    Args:
        params: Dictionary containing:
            - image_data: Base64 encoded image data
            - image_mime_type: MIME type of the image (default: "image/jpeg")
            
    Returns:
        Dict containing:
            - success: Boolean indicating if analysis was successful
            - identified_foods: List of identified foods with confidence scores
            - total_foods_found: Number of foods identified
            - raw_response: Original AI response for debugging
            - error: Error message if analysis failed
    """
    image_data = params.get("image_data", "")
    image_mime_type = params.get("image_mime_type", "image/jpeg")
    
    system_prompt = """You are a food identification expert. Analyze images to identify foods with confidence levels.

IMPORTANT: Focus on IDENTIFICATION, not precise nutrition calculations. Be honest about what you can and cannot see clearly.

For each food you identify, provide:
1. Food name (be specific: "grilled chicken breast" not just "chicken")
2. Confidence level (1-10, where 10 = absolutely certain)
3. Visual reasoning (what visual cues led to identification)
4. Estimated relative size (small/medium/large compared to typical portions)
5. Preparation method if visible (grilled, fried, steamed, etc.)

If you're unsure about something, say so! It's better to be honest than guess."""
    
    prompt_template = """Analyze this meal image and identify the foods present.

For each food item, provide a JSON structure with:
- "name": specific food name
- "confidence": 1-10 confidence score  
- "visual_cues": what you see that led to this identification
- "estimated_size": "small", "medium", or "large" relative to typical portions
- "preparation": cooking method if visible
- "notes": any uncertainty or additional observations

Format your response as a JSON array of food items. Be thorough but honest about limitations.

Example format:
[
  {
    "name": "grilled chicken breast",
    "confidence": 8,
    "visual_cues": "white meat, grill marks visible, lean appearance",
    "estimated_size": "medium",
    "preparation": "grilled",
    "notes": "appears to be about 5-6oz based on plate proportion"
  }
]"""
    
    prompt_template_variables = {
        "image_analysis": "meal identification"
    }
    
    try:
        with using_prompt_template(
            template=prompt_template,
            variables=prompt_template_variables,
            version="smart-food-id-v1.0",
        ):
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=[
                    {"type": "text", "text": prompt_template},
                    {"type": "image_url", "image_url": {"url": f"data:{image_mime_type};base64,{image_data}"}}
                ])
            ]
            
            response = analysis_llm.invoke(messages)
            
            # Parse response
            
            try:
                # Clean up the response - remove markdown code blocks if present
                # OpenAI sometimes wraps JSON responses in markdown code blocks
                response_content = response.content.strip()
                if response_content.startswith('```json'):
                    response_content = response_content[7:]  # Remove ```json
                if response_content.endswith('```'):
                    response_content = response_content[:-3]  # Remove ```
                response_content = response_content.strip()
                
                # Parse the cleaned JSON response
                identified_foods = json.loads(response_content)
                if not isinstance(identified_foods, list):
                    identified_foods = [identified_foods]
                print(f"✅ Successfully parsed JSON response with {len(identified_foods)} foods")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {str(e)}")
                print(f"🔍 Attempting to extract food info from text response...")
                
                # FALLBACK PARSING: When AI doesn't return valid JSON
                # This happens when the AI responds in natural language instead of structured JSON
                # We use simple keyword matching to extract basic food information
                response_text = response.content.strip().lower()
                
                # Simple parsing for common patterns - this is a fallback mechanism
                # In production, you might want more sophisticated NLP parsing
                identified_foods = []
                if "egg" in response_text:
                    # Common egg identification pattern
                    identified_foods.append({
                        "name": "hard-boiled egg",
                        "confidence": 8,
                        "visual_cues": "oval white object with egg appearance",
                        "estimated_size": "medium",
                        "preparation": "boiled",
                        "notes": f"Extracted from AI response"
                    })
                elif any(word in response_text for word in ["chicken", "breast", "meat"]):
                    # Common chicken/meat identification pattern
                    identified_foods.append({
                        "name": "chicken",
                        "confidence": 7,
                        "visual_cues": "meat-like appearance",
                        "estimated_size": "medium", 
                        "preparation": "cooked",
                        "notes": "Extracted from AI response"
                    })
                elif "no" in response_text and ("food" in response_text or "clear" in response_text):
                    # Handle cases where AI can't identify clear foods
                    identified_foods.append({
                        "name": "unclear image",
                        "confidence": 2,
                        "visual_cues": "image quality issues",
                        "estimated_size": "unknown",
                        "preparation": "unknown",
                        "notes": "AI couldn't identify clear foods"
                    })
                else:
                    # Generic fallback for any other response
                    # This preserves the AI's response for debugging while providing a structure
                    identified_foods.append({
                        "name": "unidentified food",
                        "confidence": 4,
                        "visual_cues": "AI provided response but unclear format",
                        "estimated_size": "medium",
                        "preparation": "unknown",
                        "notes": f"Response: {response.content[:200]}..."
                    })
                
                print(f"🔍 Extracted {len(identified_foods)} foods from text response")
            
            return {
                "success": True,
                "identified_foods": identified_foods,
                "total_foods_found": len(identified_foods),
                "raw_response": response.content
            }
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error in food identification: {error_msg}")
        
        
        return {
            "success": False,
            "identified_foods": [],
            "total_foods_found": 0,
            "error": error_msg,
            "raw_response": ""
        }

@tool
def match_foods_to_database(identified_foods: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Match AI-identified foods to nutrition database entries.
    
    Searches the nutrition database for matches to AI-identified foods
    and combines confidence scores from both sources.
    
    Args:
        identified_foods: List of foods identified by vision AI with confidence scores
        
    Returns:
        Dict containing:
            - matched_foods: List of foods successfully matched to database
            - unmatched_foods: List of foods not found in database
            - total_matched: Number of successfully matched foods
            - total_unmatched: Number of unmatched foods
    """
    from nutrition_database import NutritionDatabase
    nutrition_db = NutritionDatabase()
    matched_foods = []
    unmatched_foods = []
    
    for food_item in identified_foods:
        food_name = food_item.get("name", "")
        confidence = food_item.get("confidence", 0)
        
        # Search nutrition database
        db_matches = nutrition_db.search_food(food_name)
        
        if db_matches and db_matches[0][1] > 0.5:  # Good database match
            best_match_id, match_confidence = db_matches[0]
            food_info = nutrition_db.get_food_info(best_match_id)
            
            # Combine AI confidence with database match confidence
            combined_confidence = (confidence / 10) * match_confidence
            
            matched_foods.append({
                "ai_identification": food_item,
                "database_match": {
                    "food_id": best_match_id,
                    "food_info": food_info,
                    "match_confidence": match_confidence,
                    "combined_confidence": combined_confidence
                },
                "suggested_portions": food_info["common_portions"],
                "visual_cues": food_info["visual_cues"]
            })
        else:
            # No good database match
            unmatched_foods.append({
                "ai_identification": food_item,
                "reason": "No database match found" if not db_matches else "Low match confidence",
                "suggestions": "Manual entry required"
            })
    
    return {
        "matched_foods": matched_foods,
        "unmatched_foods": unmatched_foods,
        "match_success_rate": len(matched_foods) / len(identified_foods) if identified_foods else 0
    }

@tool
def suggest_portions_with_reasoning(params: Dict) -> Dict[str, Any]:
    """Suggest portion sizes with visual reasoning and user-friendly explanations.
    
    Args:
        params: Dict containing 'matched_foods' and optional 'image_context'
    """
    matched_foods = params.get("matched_foods", [])
    image_context = params.get("image_context", "")
    
    from nutrition_database import NutritionDatabase
    nutrition_db = NutritionDatabase()
    
    portion_suggestions = []
    total_protein = 0.0
    
    for food_match in matched_foods:
        ai_food = food_match["ai_identification"]
        db_food = food_match["database_match"]["food_info"]
        estimated_size = ai_food.get("estimated_size", "medium")
        
        # Get portion details
        portions = db_food["common_portions"]
        available_portions = list(portions.keys())
        
        # Smart mapping based on food type and available portions
        if "egg" in food_match["database_match"]["food_id"]:
            # For eggs, map size estimates to egg counts
            size_to_egg_mapping = {
                "small": "one_egg",
                "medium": "one_egg", 
                "large": "two_eggs",
                "extra_large": "three_eggs"
            }
            suggested_portion = size_to_egg_mapping.get(estimated_size, "one_egg")
        else:
            # For regular foods, use standard size mapping
            size_mapping = {
                "small": "small",
                "medium": "medium", 
                "large": "large",
                "extra_large": "large"
            }
            suggested_portion = size_mapping.get(estimated_size, "medium")
        
        # Fallback to first available portion if suggested doesn't exist
        if suggested_portion not in portions:
            suggested_portion = available_portions[0]
        
        portion_info = portions[suggested_portion]
        
        # Calculate protein for suggested portion
        protein_calc = nutrition_db.calculate_protein(
            food_match["database_match"]["food_id"],
            suggested_portion,
            ai_food.get("preparation", "default")
        )
        
        # Create user-friendly explanation
        explanation = f"Based on the visual size, this looks like {portion_info['description']} "
        explanation += f"({portion_info['grams']}g). "
        
        if ai_food.get("visual_cues"):
            explanation += f"I can see: {ai_food['visual_cues']}. "
        
        confidence_text = "very confident" if ai_food.get("confidence", 0) >= 8 else \
                         "fairly confident" if ai_food.get("confidence", 0) >= 6 else \
                         "somewhat uncertain"
        
        explanation += f"I'm {confidence_text} about this identification."
        
        portion_suggestions.append({
            "food_name": db_food["name"],
            "food_id": food_match["database_match"]["food_id"],
            "suggested_portion": suggested_portion,
            "portion_details": portion_info,
            "protein_estimate": protein_calc,
            "alternative_portions": {k: v for k, v in portions.items() if k != suggested_portion},
            "confidence": ai_food.get("confidence", 5),
            "explanation": explanation,
            "visual_reasoning": ai_food.get("visual_cues", ""),
            "preparation": ai_food.get("preparation", "default")
        })
    
    return {
        "portion_suggestions": portion_suggestions,
        "total_estimated_protein": sum(
            p["protein_estimate"]["protein_grams"] 
            for p in portion_suggestions 
            if p["protein_estimate"]
        ),
        "confidence_summary": _generate_confidence_summary(portion_suggestions)
    }

def _generate_confidence_summary(suggestions: List[Dict]) -> str:
    """Generate a user-friendly confidence summary"""
    if not suggestions:
        return "No foods identified"
    
    avg_confidence = sum(s["confidence"] for s in suggestions) / len(suggestions)
    
    if avg_confidence >= 8:
        return "I'm very confident about these identifications"
    elif avg_confidence >= 6:
        return "I'm fairly confident about most of these foods"
    elif avg_confidence >= 4:
        return "I can identify some foods but am uncertain about others"
    else:
        return "This image is challenging - I'd recommend manual entry"

@tool
def generate_conversational_response(portion_suggestions: List[Dict], unmatched_foods: List[Dict]) -> str:
    """Generate a friendly, conversational response for the user.
    
    Args:
        portion_suggestions: Successfully matched and portioned foods
        unmatched_foods: Foods that couldn't be matched to database
    """
    if not portion_suggestions and not unmatched_foods:
        return "I'm having trouble identifying foods in this image. Could you help me out by telling me what you're eating?"
    
    response = "Here's what I can see in your meal:\n\n"
    
    # Process matched foods
    for i, suggestion in enumerate(portion_suggestions, 1):
        name = suggestion["food_name"]
        portion = suggestion["portion_details"]["description"]
        protein = suggestion["protein_estimate"]["protein_grams"] if suggestion["protein_estimate"] else 0
        confidence = suggestion["confidence"]
        
        response += f"{i}. **{name}** - {portion}\n"
        response += f"   🥩 Estimated protein: {protein}g\n"
        
        if confidence >= 8:
            response += f"   ✅ Very confident about this one\n"
        elif confidence >= 6:
            response += f"   👍 Pretty sure about this\n"
        else:
            response += f"   🤔 Less certain - please double-check\n"
        
        response += f"   💭 {suggestion['explanation']}\n\n"
    
    # Process unmatched foods
    if unmatched_foods:
        response += "I also see some foods I'm not sure about:\n"
        for food in unmatched_foods:
            name = food["ai_identification"]["name"]
            response += f"• {name} - Could you help me identify this?\n"
        response += "\n"
    
    # Summary
    total_protein = sum(
        s["protein_estimate"]["protein_grams"] 
        for s in portion_suggestions 
        if s["protein_estimate"]
    )
    
    response += f"**Total estimated protein: {total_protein:.1f}g**\n\n"
    response += "Does this look accurate? You can adjust any portions that seem off!"
    
    return response

# Workflow state for smart meal analysis
class SmartMealAnalysisState:
    def __init__(self):
        self.image_data = ""
        self.user_id = 0
        self.identified_foods = []
        self.matched_foods = []
        self.unmatched_foods = []
        self.portion_suggestions = []
        self.conversational_response = ""
        self.total_protein_estimate = 0.0
        self.confidence_level = "unknown"
        self.requires_user_input = False
        self.error_messages = []