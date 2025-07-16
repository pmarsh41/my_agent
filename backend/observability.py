"""
Arize Observability Integration for Protein Tracker App
Instruments meal analysis workflow with comprehensive span logging
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from contextlib import contextmanager
import traceback

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from arize.pandas.logger import Client
from arize.utils.types import ModelTypes, Environments, Schema
import pandas as pd


class ProteinTrackerObservability:
    """Centralized observability for protein tracker app"""

    def __init__(self):
        self.space_id = os.getenv("ARIZE_SPACE_ID")
        self.api_key = os.getenv("ARIZE_API_KEY")
        self.model_id = "protein-tracker-app"
        self.model_version = "1.0.0"
        self.environment = Environments.PRODUCTION  # Use PRODUCTION for simpler setup

        if not self.space_id or not self.api_key:
            print("⚠️ Warning: Arize credentials not found. Observability disabled.")
            self.enabled = False
            return

        try:
            self.arize_client = Client(space_id=self.space_id, api_key=self.api_key)
            self.enabled = True
            print("✅ Arize observability initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Arize client: {e}")
            self.enabled = False

        # Current span context
        self.current_spans = {}

    def create_meal_analysis_span(self, 
                                user_id: int,
                                image_metadata: Dict[str, Any],
                                user_context: Dict[str, Any]) -> str:
        """Create root span for meal analysis request"""

        if not self.enabled:
            return str(uuid.uuid4())

        prediction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        # Prepare span data
        span_data = {
            "prediction_id": prediction_id,
            "prediction_timestamp": timestamp,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "environment": self.environment.value,

            # Request metadata
            "user_id": user_id,
            "meal_analysis_type": "ai_powered",
            "request_timestamp": timestamp.isoformat(),

            # Image metadata
            "image_size_bytes": image_metadata.get("size", 0),
            "image_format": image_metadata.get("format", "unknown"),
            "image_dimensions": json.dumps(image_metadata.get("dimensions", {})),

            # User context features
            "daily_protein_goal": user_context.get("daily_protein_goal", 0),
            "current_protein_today": user_context.get("current_protein_today", 0),
            "meal_number_today": user_context.get("meal_number_today", 0),
            "user_weight": user_context.get("weight"),
            "activity_level": user_context.get("activity_level"),
            "dietary_preferences": json.dumps(user_context.get("dietary_preferences", [])),

            # Workflow tracking
            "workflow_status": "started",
            "total_latency_ms": None,  # Will be updated on completion
        }

        # Store for completion
        self.current_spans[prediction_id] = {
            "start_time": timestamp,
            "data": span_data,
            "child_spans": []
        }

        return prediction_id

    def log_food_identification_node(self,
                                   prediction_id: str,
                                   vision_api_response: Dict[str, Any],
                                   detected_foods: List[str],
                                   confidence_scores: Dict[str, float],
                                   latency_ms: float) -> None:
        """Log food identification workflow node"""

        if not self.enabled or prediction_id not in self.current_spans:
            return

        node_data = {
            "node_name": "food_identification",
            "node_timestamp": datetime.utcnow().isoformat(),
            "node_latency_ms": latency_ms,
            "node_status": "completed",

            # Vision API details
            "vision_api_model": vision_api_response.get("model", "gpt-4-vision"),
            "vision_api_tokens": vision_api_response.get("usage", {}).get("total_tokens", 0),
            "vision_api_cost": vision_api_response.get("usage", {}).get("cost", 0),

            # Detection results
            "detected_foods_count": len(detected_foods),
            "detected_foods": json.dumps(detected_foods),
            "confidence_scores": json.dumps(confidence_scores),
            "avg_confidence": sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0,
            "min_confidence": min(confidence_scores.values()) if confidence_scores else 0,
            "max_confidence": max(confidence_scores.values()) if confidence_scores else 0,
        }

        self.current_spans[prediction_id]["child_spans"].append(node_data)

    def log_database_matching_node(self,
                                 prediction_id: str,
                                 nutrition_matches: Dict[str, Any],
                                 match_confidence: Dict[str, float],
                                 fallback_used: List[str],
                                 latency_ms: float) -> None:
        """Log database matching workflow node"""

        if not self.enabled or prediction_id not in self.current_spans:
            return

        node_data = {
            "node_name": "database_matching",
            "node_timestamp": datetime.utcnow().isoformat(),
            "node_latency_ms": latency_ms,
            "node_status": "completed",

            # Database matching results
            "nutrition_matches_count": len(nutrition_matches),
            "successful_matches": len([k for k, v in match_confidence.items() if v > 0.8]),
            "partial_matches": len([k for k, v in match_confidence.items() if 0.5 <= v <= 0.8]),
            "poor_matches": len([k for k, v in match_confidence.items() if v < 0.5]),
            "fallback_foods": json.dumps(fallback_used),
            "avg_match_confidence": sum(match_confidence.values()) / len(match_confidence) if match_confidence else 0,

            # Nutrition data quality
            "complete_nutrition_data": len([f for f, n in nutrition_matches.items() if n.get("protein_per_100g")]),
        }

        self.current_spans[prediction_id]["child_spans"].append(node_data)

    def log_portion_suggestion_node(self,
                                  prediction_id: str,
                                  portion_estimates: Dict[str, str],
                                  protein_calculations: Dict[str, float],
                                  total_protein: float,
                                  estimation_confidence: float,
                                  latency_ms: float) -> None:
        """Log portion suggestion workflow node"""

        if not self.enabled or prediction_id not in self.current_spans:
            return

        node_data = {
            "node_name": "portion_suggestion",
            "node_timestamp": datetime.utcnow().isoformat(),
            "node_latency_ms": latency_ms,
            "node_status": "completed",

            # Portion estimation results
            "portion_estimates": json.dumps(portion_estimates),
            "protein_per_food": json.dumps(protein_calculations),
            "total_protein_estimate": total_protein,
            "estimation_confidence": estimation_confidence,
            "high_protein_foods": len([f for f, p in protein_calculations.items() if p > 10]),

            # Estimation quality indicators
            "protein_range_reasonable": 5 <= total_protein <= 100,  # Reasonable meal range
            "portion_specificity": len([p for p in portion_estimates.values() if "cup" in p or "oz" in p]),
        }

        self.current_spans[prediction_id]["child_spans"].append(node_data)

    def log_conversation_generation_node(self,
                                       prediction_id: str,
                                       llm_response: Dict[str, Any],
                                       response_text: str,
                                       personalization_factors: List[str],
                                       latency_ms: float) -> None:
        """Log conversation generation workflow node"""

        if not self.enabled or prediction_id not in self.current_spans:
            return

        node_data = {
            "node_name": "conversation_generation",
            "node_timestamp": datetime.utcnow().isoformat(),
            "node_latency_ms": latency_ms,
            "node_status": "completed",

            # LLM response details
            "llm_model": llm_response.get("model", "gpt-4"),
            "llm_tokens": llm_response.get("usage", {}).get("total_tokens", 0),
            "llm_cost": llm_response.get("usage", {}).get("cost", 0),

            # Response characteristics
            "response_length": len(response_text),
            "response_word_count": len(response_text.split()),
            "personalization_factors": json.dumps(personalization_factors),
            "mentions_protein_goal": "goal" in response_text.lower(),
            "encouraging_tone": any(word in response_text.lower() for word in ["great", "excellent", "good", "keep"]),

            # Response completeness
            "includes_protein_breakdown": "protein" in response_text.lower(),
            "includes_suggestions": any(word in response_text.lower() for word in ["try", "consider", "suggest"]),
        }

        self.current_spans[prediction_id]["child_spans"].append(node_data)

    def complete_meal_analysis_span(self,
                                  prediction_id: str,
                                  final_results: Dict[str, Any],
                                  success: bool = True,
                                  error_message: str = None) -> None:
        """Complete and log the meal analysis span to Arize"""

        if not self.enabled or prediction_id not in self.current_spans:
            return

        span_info = self.current_spans[prediction_id]
        end_time = datetime.utcnow()
        total_latency = (end_time - span_info["start_time"]).total_seconds() * 1000

        # Update root span data
        span_data = span_info["data"].copy()
        span_data.update({
            "completion_timestamp": end_time.isoformat(),
            "total_latency_ms": total_latency,
            "workflow_status": "completed" if success else "failed",
            "success": success,
            "error_message": error_message or "",

            # Final results
            "final_detected_foods": json.dumps(final_results.get("detected_foods", [])),
            "final_protein_estimate": final_results.get("total_protein", 0),
            "final_response": final_results.get("response", ""),
            "final_confidence": final_results.get("confidence", 0),

            # Workflow performance
            "total_foods_detected": len(final_results.get("detected_foods", [])),
            "workflow_node_count": len(span_info["child_spans"]),
            "avg_node_latency": sum(node.get("node_latency_ms", 0) for node in span_info["child_spans"]) / max(len(span_info["child_spans"]), 1),
        })

        # Add child span summaries
        for i, node in enumerate(span_info["child_spans"]):
            for key, value in node.items():
                span_data[f"node_{i}_{key}"] = value

        # Create DataFrame for Arize
        df = pd.DataFrame([span_data])
        
        # Add prediction label for LLM models
        df["prediction_label"] = 1  # Default label for generative models

        # Define schema
        schema = Schema(
            prediction_id_column_name="prediction_id",
            timestamp_column_name="prediction_timestamp",
            prediction_label_column_name="prediction_label",
            feature_column_names=[
                "user_id", "daily_protein_goal", "current_protein_today",
                "meal_number_today", "user_weight", "activity_level",
                "image_size_bytes", "image_format"
            ],
            tag_column_names=[
                "model_version", "environment", "workflow_status",
                "total_foods_detected", "success"
            ]
        )

        try:
            # Log to Arize
            response = self.arize_client.log(
                dataframe=df,
                model_id=self.model_id,
                model_version=self.model_version,
                model_type=ModelTypes.GENERATIVE_LLM,
                environment=self.environment,
                schema=schema
            )

            if response.status_code == 200:
                print(f"✅ Logged meal analysis span {prediction_id} to Arize")
            else:
                print(f"⚠️ Failed to log span to Arize: {response.status_code}")

        except Exception as e:
            print(f"❌ Error logging to Arize: {e}")

        # Cleanup
        del self.current_spans[prediction_id]

    def log_error_span(self,
                      prediction_id: str,
                      error: Exception,
                      node_name: str = "unknown",
                      context: Dict[str, Any] = None) -> None:
        """Log error information for debugging"""

        if not self.enabled:
            return

        error_data = {
            "error_timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_traceback": traceback.format_exc(),
            "error_node": node_name,
            "error_context": json.dumps(context or {}),
        }

        if prediction_id in self.current_spans:
            self.current_spans[prediction_id]["data"].update(error_data)

        print(f"❌ Error in {node_name}: {error}")

    @contextmanager
    def trace_node(self, prediction_id: str, node_name: str):
        """Context manager for tracing workflow nodes"""
        start_time = datetime.utcnow()
        try:
            yield
        except Exception as e:
            print(f"❌ Error in {node_name}: {e}")
            raise
        finally:
            end_time = datetime.utcnow()
            latency = (end_time - start_time).total_seconds() * 1000
            print(f"⏱️ {node_name} completed in {latency:.2f}ms")


# Global instance
observability = ProteinTrackerObservability() 