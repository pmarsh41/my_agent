"""
Evaluation Framework for Protein Tracker App
Implements human feedback collection and LLM-as-judge evaluations
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
# import pandas as pd
# from arize.pandas.logger import Client
# from arize.utils.types import ModelTypes, Environments

# New imports for categorical evaluation
from evaluation_categories import (
    validate_category,
    category_to_score,
    VALID_CATEGORIES
)
from categorical_prompt_templates import (
    FOOD_DETECTION_PROMPT,
    PROTEIN_ESTIMATION_PROMPT,
    CONVERSATIONAL_RESPONSE_PROMPT,
    DEFAULT_RESPONSES
)


# Evaluation Types
class EvaluationType(str, Enum):
    HUMAN_FEEDBACK = "human_feedback"
    LLM_JUDGE = "llm_judge"
    GROUND_TRUTH = "ground_truth"


# Feedback Models
class FoodDetectionFeedback(BaseModel):
    """Human feedback on food detection accuracy"""
    span_id: str
    detected_foods: List[str]
    actual_foods: List[str]
    missing_foods: List[str] = Field(default_factory=list)
    incorrect_foods: List[str] = Field(default_factory=list)
    accuracy_score: float = Field(ge=0, le=1)  # 0-1 scale
    notes: Optional[str] = None


class ProteinEstimateFeedback(BaseModel):
    """Human feedback on protein estimation"""
    span_id: str
    estimated_protein: float
    actual_protein: Optional[float] = None
    accuracy_rating: int = Field(ge=1, le=5)  # 1-5 scale
    is_overestimate: Optional[bool] = None
    is_underestimate: Optional[bool] = None
    notes: Optional[str] = None


class ConversationalQualityFeedback(BaseModel):
    """Human feedback on response quality"""
    span_id: str
    helpfulness: int = Field(ge=1, le=5)
    accuracy: int = Field(ge=1, le=5)
    clarity: int = Field(ge=1, le=5)
    tone: int = Field(ge=1, le=5)
    overall_quality: int = Field(ge=1, le=5)
    suggestions: Optional[str] = None


class PortionSizeFeedback(BaseModel):
    """Human feedback on portion size suggestions"""
    span_id: str
    portion_suggestions: Dict[str, str]
    accuracy_ratings: Dict[str, int]  # food_name -> 1-5 rating
    were_portions_realistic: bool
    notes: Optional[str] = None


# LLM Judge Evaluator
class LLMJudgeEvaluator:
    """Uses an LLM to evaluate the quality of meal analysis"""
    
    def __init__(self, model_name: str = "gpt-4o"):
        self.llm = ChatOpenAI(model=model_name, temperature=0.1)
        
    async def evaluate_food_detection(self, 
                                    image_description: str,
                                    detected_foods: List[str]) -> Dict[str, Any]:
        """Evaluate food detection using categorical classification.
        
        Returns categorical assessment instead of numerical score.
        Categories: CONFIDENT_DETECTION, LIKELY_DETECTION, UNCERTAIN_DETECTION, POOR_DETECTION, FAILED_DETECTION
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", FOOD_DETECTION_PROMPT),
            ("human", "Image description: {image_description}\nDetected foods: {detected_foods}")
        ])
        
        response = await self.llm.ainvoke(
            prompt.format_messages(
                image_description=image_description,
                detected_foods=json.dumps(detected_foods)
            )
        )
        
        try:
            # Get the actual content string from the response
            content = str(response.content)
            
            # Clean the response content to handle potential formatting issues
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            if content.endswith('```'):
                content = content[:-3]  # Remove ```
            content = content.strip()
            
            result = json.loads(content)
            # Validate the categorical response
            result['detection_reliability'] = validate_category(
                result.get('detection_reliability', ''),
                'food_detection'
            )
            return result
        except Exception as e:
            print(f"Food detection evaluation parsing error: {e}")
            return DEFAULT_RESPONSES["food_detection"]
    
    async def evaluate_protein_estimate(self,
                                      foods: List[str],
                                      portions: List[str],
                                      estimated_protein: float) -> Dict[str, Any]:
        """Evaluate protein estimation using categorical classification.
        
        Returns categorical assessment instead of numerical score.
        Categories: HIGHLY_RELIABLE, MODERATELY_RELIABLE, SOMEWHAT_RELIABLE, UNRELIABLE, INVALID
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROTEIN_ESTIMATION_PROMPT),
            ("human", "Foods: {foods}\nPortions: {portions}\nEstimated protein: {protein}g")
        ])
        
        response = await self.llm.ainvoke(
            prompt.format_messages(
                foods=json.dumps(foods),
                portions=json.dumps(portions),
                protein=estimated_protein
            )
        )
        
        try:
            result = json.loads(response.content)
            # Validate the categorical response
            result['reliability'] = validate_category(
                result.get('reliability', ''),
                'protein_reliability'
            )
            # Set default range if not provided
            if 'suggested_range' not in result or not result['suggested_range']:
                result['suggested_range'] = [estimated_protein * 0.8, estimated_protein * 1.2]
            return result
        except:
            fallback = DEFAULT_RESPONSES["protein_estimation"].copy()
            fallback['suggested_range'] = [estimated_protein * 0.8, estimated_protein * 1.2]
            return fallback
    
    async def evaluate_conversational_response(self,
                                             user_context: str,
                                             response_text: str,
                                             foods_detected: List[str]) -> Dict[str, Any]:
        """Evaluate conversational response quality using categorical classification.
        
        Returns categorical assessment for each quality dimension.
        Categories: Four dimensions each with 4 categorical levels
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", CONVERSATIONAL_RESPONSE_PROMPT),
            ("human", """User context: {context}
            Foods detected: {foods}
            AI Response: {response}""")
        ])
        
        response = await self.llm.ainvoke(
            prompt.format_messages(
                context=user_context,
                foods=json.dumps(foods_detected),
                response=response_text
            )
        )
        
        try:
            result = json.loads(response.content)
            # Validate all categorical responses
            result['helpfulness'] = validate_category(
                result.get('helpfulness', ''),
                'helpfulness'
            )
            result['accuracy'] = validate_category(
                result.get('accuracy', ''),
                'accuracy'
            )
            result['tone'] = validate_category(
                result.get('tone', ''),
                'tone'
            )
            result['completeness'] = validate_category(
                result.get('completeness', ''),
                'completeness'
            )
            return result
        except:
            return DEFAULT_RESPONSES["conversational_response"]


# Evaluation Data Curator
class EvaluationDataCurator:
    """Curates spans from Arize for evaluation"""
    
    def __init__(self, space_id: str, api_key: str):
        # self.arize_client = Client(space_id=space_id, api_key=api_key)
        self.space_id = space_id
        self.api_key = api_key
        
    def get_evaluation_dataset_schema(self) -> Dict[str, Any]:
        """Define the schema for evaluation datasets"""
        return {
            # Input columns
            "span_id": "string",
            "trace_id": "string", 
            "user_id": "integer",
            "timestamp": "datetime",
            "image_data": "string",  # base64 encoded
            
            # Output columns
            "foods_detected": "list[string]",
            "protein_estimate": "float",
            "analysis_text": "string",
            "portion_suggestions": "dict",
            
            # Metadata columns
            "latency_ms": "float",
            "model_version": "string",
            "endpoint": "string",
            
            # Evaluation columns (to be filled)
            "human_food_accuracy": "float",  # 0-1
            "human_protein_accuracy": "integer",  # 1-5
            "human_response_quality": "integer",  # 1-5
            "llm_food_plausibility": "float",  # 0-1
            "llm_protein_reasonableness": "float",  # 0-1
            "llm_response_quality": "float",  # 1-5 normalized to 0-1
            
            # Ground truth (when available)
            "gt_foods": "list[string]",
            "gt_protein": "float",
            "gt_portions": "dict"
        }
    
    def create_evaluation_batch(self, 
                              num_samples: int = 100,
                              strategy: str = "random") -> Dict[str, Any]:
        """Create a batch of spans for evaluation"""
        
        # In production, this would query Arize API
        # For now, return a sample structure
        schema = self.get_evaluation_dataset_schema()
        
        # Create sample data structure
        dataset = {
            "columns": list(schema.keys()),
            "num_samples": num_samples,
            "strategy": strategy,
            "data": []  # Would contain actual span data
        }
        
        # Selection strategies
        if strategy == "random":
            # Random sampling
            pass
        elif strategy == "edge_cases":
            # Focus on edge cases:
            # - Very high/low protein estimates
            # - Unusual number of foods detected
            # - High latency spans
            # - Low confidence scores
            pass
        elif strategy == "recent":
            # Most recent spans
            pass
        elif strategy == "problematic":
            # Spans with previous low ratings
            pass
            
        return dataset


# Evaluation Pipeline
class EvaluationPipeline:
    """Orchestrates the evaluation process"""
    
    def __init__(self, 
                 arize_space_id: str,
                 arize_api_key: str,
                 llm_model: str = "gpt-4o"):
        self.curator = EvaluationDataCurator(arize_space_id, arize_api_key)
        self.llm_judge = LLMJudgeEvaluator(llm_model)
        self.pending_evaluations = {}
        
    async def run_llm_evaluation(self, span_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run LLM evaluation on a single span"""
        
        # Extract relevant data
        foods = span_data.get("foods_detected", [])
        protein = span_data.get("protein_estimate", 0)
        response_text = span_data.get("analysis_text", "")
        
        # Run evaluations in parallel
        tasks = [
            self.llm_judge.evaluate_food_detection(
                "User uploaded meal image",  # In production, use actual image analysis
                foods
            ),
            self.llm_judge.evaluate_protein_estimate(
                foods,
                span_data.get("portion_suggestions", []),
                protein
            ),
            self.llm_judge.evaluate_conversational_response(
                "User tracking daily protein intake",
                response_text,
                foods
            )
        ]
        
        results = await asyncio.gather(*tasks)
        
        return {
            "span_id": span_data["span_id"],
            "food_detection_eval": results[0],
            "protein_estimate_eval": results[1],
            "response_quality_eval": results[2],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def store_evaluation_results(self, 
                               evaluations: List[Dict[str, Any]],
                               eval_type: EvaluationType):
        """Store evaluation results back to Arize"""
        
        # In production, this would send evaluations to Arize
        # For now, just store locally or log
        print(f"Storing {len(evaluations)} evaluations of type {eval_type}")
        
        # Would integrate with Arize API here
        return {"success": True, "count": len(evaluations)}
        
    def get_evaluation_metrics(self) -> Dict[str, Any]:
        """Calculate aggregate evaluation metrics"""
        
        return {
            "food_detection": {
                "human_accuracy_avg": 0.0,
                "llm_plausibility_avg": 0.0,
                "agreement_rate": 0.0
            },
            "protein_estimation": {
                "human_accuracy_avg": 0.0,
                "llm_reasonableness_avg": 0.0,
                "avg_deviation_from_truth": 0.0
            },
            "response_quality": {
                "human_quality_avg": 0.0,
                "llm_quality_avg": 0.0,
                "dimension_scores": {
                    "helpfulness": 0.0,
                    "accuracy": 0.0,
                    "clarity": 0.0,
                    "tone": 0.0
                }
            }
        }


# Example usage
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = EvaluationPipeline(
        arize_space_id="your_space_id",
        arize_api_key="your_api_key"
    )
    
    # Create evaluation batch
    curator = pipeline.curator
    eval_batch = curator.create_evaluation_batch(
        num_samples=50,
        strategy="edge_cases"
    )
    
    print("Evaluation Dataset Schema:")
    print(json.dumps(curator.get_evaluation_dataset_schema(), indent=2))