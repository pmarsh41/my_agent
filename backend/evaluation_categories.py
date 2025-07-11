"""
Category definitions and validation for LLM-as-Judge evaluations.
This file provides the categorical labels and validation functions for the evaluation system.
"""

from enum import Enum
from typing import Dict, List, Any

# Category Definitions for LLM Judge
class FoodDetectionCategory(str, Enum):
    CONFIDENT_DETECTION = "CONFIDENT_DETECTION"
    LIKELY_DETECTION = "LIKELY_DETECTION" 
    UNCERTAIN_DETECTION = "UNCERTAIN_DETECTION"
    POOR_DETECTION = "POOR_DETECTION"
    FAILED_DETECTION = "FAILED_DETECTION"

class ProteinReliabilityCategory(str, Enum):
    HIGHLY_RELIABLE = "HIGHLY_RELIABLE"
    MODERATELY_RELIABLE = "MODERATELY_RELIABLE"
    SOMEWHAT_RELIABLE = "SOMEWHAT_RELIABLE"
    UNRELIABLE = "UNRELIABLE"
    INVALID = "INVALID"

class HelpfulnessCategory(str, Enum):
    HIGHLY_HELPFUL = "HIGHLY_HELPFUL"
    MODERATELY_HELPFUL = "MODERATELY_HELPFUL"
    SOMEWHAT_HELPFUL = "SOMEWHAT_HELPFUL"
    NOT_HELPFUL = "NOT_HELPFUL"

class AccuracyCategory(str, Enum):
    HIGHLY_ACCURATE = "HIGHLY_ACCURATE"
    MOSTLY_ACCURATE = "MOSTLY_ACCURATE"
    SOMEWHAT_ACCURATE = "SOMEWHAT_ACCURATE"
    INACCURATE = "INACCURATE"

class ToneCategory(str, Enum):
    EXCELLENT_TONE = "EXCELLENT_TONE"
    GOOD_TONE = "GOOD_TONE"
    ACCEPTABLE_TONE = "ACCEPTABLE_TONE"
    POOR_TONE = "POOR_TONE"

class CompletenessCategory(str, Enum):
    COMPREHENSIVE = "COMPREHENSIVE"
    ADEQUATE = "ADEQUATE"
    INCOMPLETE = "INCOMPLETE"
    MISSING_KEY_INFO = "MISSING_KEY_INFO"

# Validation mappings
VALID_CATEGORIES = {
    "food_detection": [e.value for e in FoodDetectionCategory],
    "protein_reliability": [e.value for e in ProteinReliabilityCategory],
    "helpfulness": [e.value for e in HelpfulnessCategory],
    "accuracy": [e.value for e in AccuracyCategory],
    "tone": [e.value for e in ToneCategory],
    "completeness": [e.value for e in CompletenessCategory]
}

# Category descriptions for prompts
FOOD_DETECTION_DESCRIPTIONS = {
    "CONFIDENT_DETECTION": "All foods clearly visible and identifiable with high confidence",
    "LIKELY_DETECTION": "Most foods identifiable with minor uncertainty in 1-2 items", 
    "UNCERTAIN_DETECTION": "Some foods difficult to distinguish, moderate uncertainty",
    "POOR_DETECTION": "Many foods unclear or potentially misidentified",
    "FAILED_DETECTION": "Unable to reliably identify meal contents due to image quality or complexity"
}

PROTEIN_RELIABILITY_DESCRIPTIONS = {
    "HIGHLY_RELIABLE": "Protein estimate based on clear portions and well-known foods with high accuracy",
    "MODERATELY_RELIABLE": "Estimate reasonable but some portion or food identification uncertainty",
    "SOMEWHAT_RELIABLE": "Estimate approximate due to unclear portions or unfamiliar foods",
    "UNRELIABLE": "Significant uncertainty in foods or portions makes estimate questionable",
    "INVALID": "Cannot provide meaningful protein estimate due to detection failures"
}

HELPFULNESS_DESCRIPTIONS = {
    "HIGHLY_HELPFUL": "Provides specific, actionable nutritional guidance tailored to the meal",
    "MODERATELY_HELPFUL": "Gives useful information with minor gaps in actionability",
    "SOMEWHAT_HELPFUL": "Basic information provided but lacks depth or specific guidance",
    "NOT_HELPFUL": "Vague, irrelevant, or provides no actionable information"
}

ACCURACY_DESCRIPTIONS = {
    "HIGHLY_ACCURATE": "All nutritional information is scientifically correct and well-supported",
    "MOSTLY_ACCURATE": "Generally correct with minor inaccuracies or oversimplifications",
    "SOMEWHAT_ACCURATE": "Some questionable information but core facts are correct",
    "INACCURATE": "Contains misleading or scientifically incorrect nutritional information"
}

TONE_DESCRIPTIONS = {
    "EXCELLENT_TONE": "Very encouraging, supportive, and motivating without being condescending",
    "GOOD_TONE": "Positive and motivating with appropriate enthusiasm",
    "ACCEPTABLE_TONE": "Neutral tone that doesn't discourage but lacks motivation",
    "POOR_TONE": "Negative, discouraging, or inappropriate tone for health guidance"
}

COMPLETENESS_DESCRIPTIONS = {
    "COMPREHENSIVE": "Addresses all relevant aspects of the meal and user's nutritional needs",
    "ADEQUATE": "Covers the main points but may miss some relevant details",
    "INCOMPLETE": "Missing important information that would be helpful to the user",
    "MISSING_KEY_INFO": "Fails to address core aspects of the meal or user's needs"
}

def validate_category(category: str, category_type: str) -> str:
    """Validate that a category is valid for the given type.
    
    Args:
        category: The category value to validate
        category_type: The type of category (e.g., 'food_detection', 'helpfulness')
        
    Returns:
        The validated category, or a default safe category if invalid
    """
    if category_type not in VALID_CATEGORIES:
        return "UNCERTAIN_DETECTION"  # Safe default
        
    if category not in VALID_CATEGORIES[category_type]:
        # Return middle-ground default for each type
        defaults = {
            "food_detection": "UNCERTAIN_DETECTION",
            "protein_reliability": "SOMEWHAT_RELIABLE", 
            "helpfulness": "SOMEWHAT_HELPFUL",
            "accuracy": "SOMEWHAT_ACCURATE",
            "tone": "ACCEPTABLE_TONE",
            "completeness": "ADEQUATE"
        }
        return defaults.get(category_type, "UNCERTAIN_DETECTION")
    
    return category

def category_to_score(category: str, category_type: str) -> float:
    """Convert categorical evaluation to numerical score for analytics.
    
    Args:
        category: The categorical evaluation
        category_type: The type of category
        
    Returns:
        Float score between 0.0 and 1.0
    """
    # Mapping for analytics purposes only
    score_maps = {
        "food_detection": {
            "CONFIDENT_DETECTION": 0.95,
            "LIKELY_DETECTION": 0.80,
            "UNCERTAIN_DETECTION": 0.60,
            "POOR_DETECTION": 0.40,
            "FAILED_DETECTION": 0.10
        },
        "protein_reliability": {
            "HIGHLY_RELIABLE": 0.95,
            "MODERATELY_RELIABLE": 0.80,
            "SOMEWHAT_RELIABLE": 0.60,
            "UNRELIABLE": 0.40,
            "INVALID": 0.10
        },
        "helpfulness": {
            "HIGHLY_HELPFUL": 0.95,
            "MODERATELY_HELPFUL": 0.75,
            "SOMEWHAT_HELPFUL": 0.55,
            "NOT_HELPFUL": 0.20
        },
        "accuracy": {
            "HIGHLY_ACCURATE": 0.95,
            "MOSTLY_ACCURATE": 0.80,
            "SOMEWHAT_ACCURATE": 0.60,
            "INACCURATE": 0.25
        },
        "tone": {
            "EXCELLENT_TONE": 0.95,
            "GOOD_TONE": 0.80,
            "ACCEPTABLE_TONE": 0.60,
            "POOR_TONE": 0.25
        },
        "completeness": {
            "COMPREHENSIVE": 0.95,
            "ADEQUATE": 0.75,
            "INCOMPLETE": 0.45,
            "MISSING_KEY_INFO": 0.20
        }
    }
    
    return score_maps.get(category_type, {}).get(category, 0.5)