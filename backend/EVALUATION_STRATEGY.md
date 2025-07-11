# Protein Tracker Evaluation Strategy

## Overview
This document outlines how to implement a comprehensive evaluation system for your protein tracking application using Arize Phoenix and human feedback.

### Categorical vs Numerical Evaluation Approach
This strategy uses **categorical labels** instead of numerical scores (1-5 or 0-1) for both human and LLM evaluations. This approach addresses:
- **LLM Token Issues:** Numerical tokens don't have semantic meaning to LLMs
- **Human Clarity:** Categories are more intuitive than arbitrary number scales  
- **Consistency:** Reduces variation in interpretation across evaluators
- **Actionability:** Categories directly suggest improvement areas

## Key Evaluation Areas

### 1. Food Detection Accuracy
**What to evaluate:**
- Correct identification of food items in images
- Missing foods that should have been detected
- False positives (foods detected that aren't there)
- Portion size accuracy

**Spans to prioritize:**
- Images with complex meals (multiple foods)
- Images with similar-looking foods (chicken vs turkey)
- Images with partially obscured foods
- Images with unusual or ethnic foods
- Images with liquids/sauces that are hard to identify

**Evaluation Categories:**
- ACCURATE: All foods correctly identified
- MOSTLY_ACCURATE: Minor identification issues
- SOMEWHAT_ACCURATE: Some foods missed or wrong
- INACCURATE: Many foods incorrectly identified

### 2. Protein Estimation Accuracy
**What to evaluate:**
- Accuracy of total protein calculation
- Individual food protein contributions
- Portion size impact on protein estimates
- Consistency across similar meals

**Spans to prioritize:**
- High-protein meals (>50g estimated)
- Low-protein meals (<10g estimated)
- Meals with protein powder/supplements
- Meals with mixed protein sources
- Vegetarian/vegan protein sources

**Evaluation Categories:**
- HIGHLY_ACCURATE: Within 2-3g of actual
- MOSTLY_ACCURATE: Within 5-8g of actual
- SOMEWHAT_ACCURATE: Within 10-15g of actual
- INACCURATE: Off by more than 15g

### 3. Conversational Response Quality
**What to evaluate:**
- Helpfulness and actionability
- Tone and encouragement
- Accuracy of nutritional advice
- Personalization to user context
- Completeness of information

**Spans to prioritize:**
- First-time user interactions
- Users with specific dietary goals
- Responses with nutritional recommendations
- Error or edge case handling
- Long conversation threads

**Evaluation Categories:**
- **Helpfulness:** HIGHLY_HELPFUL | MODERATELY_HELPFUL | SOMEWHAT_HELPFUL | NOT_HELPFUL
- **Accuracy:** HIGHLY_ACCURATE | MOSTLY_ACCURATE | SOMEWHAT_ACCURATE | INACCURATE
- **Tone:** EXCELLENT_TONE | GOOD_TONE | ACCEPTABLE_TONE | POOR_TONE
- **Completeness:** COMPREHENSIVE | ADEQUATE | INCOMPLETE | MISSING_KEY_INFO

## Dataset Curation Strategy

### Span Selection Criteria

#### 1. Random Sampling (Baseline)
```python
# 20% of evaluation dataset
strategy = "random"
criteria = {
    "sample_size": 100,
    "time_range": "last_7_days",
    "user_distribution": "proportional"
}
```

#### 2. Edge Cases (High Priority)
```python
# 40% of evaluation dataset
strategy = "edge_cases"
criteria = {
    # High/low protein estimates
    "protein_outliers": {
        "high_protein": ">60g",
        "low_protein": "<5g"
    },
    
    # Unusual food counts
    "food_count_outliers": {
        "many_foods": ">8 items",
        "few_foods": "1 item"
    },
    
    # Performance outliers
    "latency_outliers": ">10 seconds",
    "confidence_outliers": "<0.7",
    
    # Rare food types
    "uncommon_foods": [
        "ethnic_cuisines",
        "protein_supplements", 
        "exotic_proteins",
        "liquid_meals"
    ]
}
```

#### 3. User Journey Critical Points (Medium Priority)
```python
# 25% of evaluation dataset
strategy = "critical_moments"
criteria = {
    "first_meals": "user's first 3 meals",
    "goal_meals": "meals near protein goals",
    "streak_meals": "meals during streaks",
    "return_users": "users returning after 7+ days"
}
```

#### 4. Model Performance Monitoring (Medium Priority)  
```python
# 15% of evaluation dataset
strategy = "performance_monitoring"
criteria = {
    "model_versions": "compare across versions",
    "a_b_tests": "different prompt versions",
    "feature_flags": "new feature rollouts",
    "error_cases": "500 errors, timeouts, failures"
}
```

## Evaluation Dataset Schema

### Core Span Data
```python
SPAN_SCHEMA = {
    # Identifiers
    "span_id": "string",
    "trace_id": "string", 
    "user_id": "integer",
    "session_id": "string",
    
    # Timing
    "timestamp": "datetime",
    "latency_ms": "float",
    
    # Input data
    "image_base64": "string",
    "image_metadata": {
        "size_bytes": "integer",
        "dimensions": "tuple",
        "format": "string"
    },
    "user_context": {
        "daily_protein_goal": "float",
        "current_protein_today": "float",
        "meal_number_today": "integer",
        "dietary_preferences": "list[string]"
    },
    
    # Model outputs
    "foods_detected": "list[string]",
    "portion_suggestions": "dict[string, string]", 
    "protein_estimate": "float",
    "confidence_scores": "dict[string, float]",
    "analysis_text": "string",
    
    # Model metadata
    "model_version": "string",
    "prompt_version": "string",
    "llm_model": "string",
    "feature_flags": "list[string]",
    
    # Error handling
    "errors": "list[dict]",
    "warnings": "list[dict]",
    "fallback_used": "boolean"
}
```

### Evaluation Columns (to be filled by evaluators)
```python
EVALUATION_SCHEMA = {
    # Human evaluations - Categorical
    "human_food_accuracy": "string",  # ACCURATE | MOSTLY_ACCURATE | SOMEWHAT_ACCURATE | INACCURATE
    "human_food_missing": "list[string]",
    "human_food_incorrect": "list[string]",
    "human_protein_accuracy": "string",  # HIGHLY_ACCURATE | MOSTLY_ACCURATE | SOMEWHAT_ACCURATE | INACCURATE
    "human_protein_actual": "float",  # optional ground truth
    "human_response_helpfulness": "string",  # HIGHLY_HELPFUL | MODERATELY_HELPFUL | SOMEWHAT_HELPFUL | NOT_HELPFUL
    "human_response_accuracy": "string",  # HIGHLY_ACCURATE | MOSTLY_ACCURATE | SOMEWHAT_ACCURATE | INACCURATE
    "human_response_tone": "string",  # EXCELLENT_TONE | GOOD_TONE | ACCEPTABLE_TONE | POOR_TONE
    "human_response_completeness": "string",  # COMPREHENSIVE | ADEQUATE | INCOMPLETE | MISSING_KEY_INFO
    "human_notes": "string",
    
    # LLM Judge evaluations - Categorical
    "llm_food_detection": "string",  # CONFIDENT_DETECTION | LIKELY_DETECTION | UNCERTAIN_DETECTION | POOR_DETECTION | FAILED_DETECTION
    "llm_protein_reliability": "string",  # HIGHLY_RELIABLE | MODERATELY_RELIABLE | SOMEWHAT_RELIABLE | UNRELIABLE | INVALID
    "llm_response_helpfulness": "string",  # HIGHLY_HELPFUL | MODERATELY_HELPFUL | SOMEWHAT_HELPFUL | NOT_HELPFUL
    "llm_response_accuracy": "string",  # HIGHLY_ACCURATE | MOSTLY_ACCURATE | SOMEWHAT_ACCURATE | INACCURATE
    "llm_response_tone": "string",  # EXCELLENT_TONE | GOOD_TONE | ACCEPTABLE_TONE | POOR_TONE
    "llm_response_completeness": "string",  # COMPREHENSIVE | ADEQUATE | INCOMPLETE | MISSING_KEY_INFO
    "llm_reasoning": "string",
    
    # Ground truth (when available)
    "gt_foods": "list[string]",
    "gt_portions": "dict[string, float]",
    "gt_protein": "float",
    "gt_source": "string",  # "manual", "nutrition_label", "database"
    
    # Evaluation metadata
    "evaluator_id": "string",
    "evaluation_timestamp": "datetime",
    "evaluation_confidence": "float",
    "evaluation_time_spent_seconds": "integer"
}
```

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
1. **Setup evaluation endpoints** in your FastAPI app
2. **Implement basic human feedback collection**
3. **Create simple evaluation interface**
4. **Start collecting 10-20 evaluations per day**

```python
# Add to main.py
from evaluation_endpoints import setup_evaluation_endpoints

evaluation_pipeline = setup_evaluation_endpoints(
    app, 
    arize_space_id=os.getenv("ARIZE_SPACE_ID"),
    arize_api_key=os.getenv("ARIZE_API_KEY")
)
```

### Phase 2: LLM Judge (Week 3-4) 
1. **Implement LLM-as-judge evaluations**
2. **Run batch evaluations on historical data**
3. **Compare human vs LLM agreement**
4. **Optimize LLM judge prompts**

### Phase 3: Continuous Evaluation (Week 5+)
1. **Automated evaluation triggering**
2. **Dashboard for evaluation metrics**
3. **A/B testing with evaluation data**
4. **Model improvement based on feedback**

## Evaluation Triggers

### Automatic Evaluation
```python
EVALUATION_TRIGGERS = {
    # Sample percentage of production traffic
    "sample_rate": 0.05,  # 5% of spans
    
    # Always evaluate these cases
    "always_evaluate": [
        "protein_estimate > 80g",
        "protein_estimate < 2g", 
        "foods_detected.length > 10",
        "foods_detected.length == 0",
        "latency > 15000ms",
        "any(confidence < 0.5)",
        "error_occurred == true"
    ],
    
    # User-triggered evaluation
    "user_feedback": {
        "thumbs_down": "immediate_evaluation",
        "report_error": "immediate_evaluation", 
        "explicit_feedback": "store_with_span"
    }
}
```

### Human Evaluation Prioritization
```python
HUMAN_EVALUATION_PRIORITY = {
    "critical": [
        "user_reported_errors",
        "model_version_changes",
        "edge_cases_failing_llm_judge"
    ],
    
    "high": [
        "protein_outliers",
        "new_food_types",
        "low_confidence_predictions"
    ],
    
    "medium": [
        "random_sampling",
        "a_b_test_comparisons"
    ],
    
    "low": [
        "bulk_historical_analysis"
    ]
}
```

## Metrics to Track

### Model Performance Metrics
```python
MODEL_METRICS = {
    "food_detection": {
        "precision": "correctly_detected / total_detected",
        "recall": "correctly_detected / total_actual", 
        "f1_score": "harmonic_mean(precision, recall)",
        "accuracy_distribution": "ACCURATE: 65%, MOSTLY_ACCURATE: 25%, SOMEWHAT_ACCURATE: 8%, INACCURATE: 2%"
    },
    
    "protein_estimation": {
        "mae": "mean_absolute_error",
        "rmse": "root_mean_squared_error", 
        "mape": "mean_absolute_percentage_error",
        "accuracy_distribution": "HIGHLY_ACCURATE: 45%, MOSTLY_ACCURATE: 35%, SOMEWHAT_ACCURATE: 15%, INACCURATE: 5%"
    },
    
    "response_quality": {
        "helpfulness_distribution": "HIGHLY_HELPFUL: 40%, MODERATELY_HELPFUL: 35%, SOMEWHAT_HELPFUL: 20%, NOT_HELPFUL: 5%",
        "accuracy_distribution": "HIGHLY_ACCURATE: 50%, MOSTLY_ACCURATE: 30%, SOMEWHAT_ACCURATE: 15%, INACCURATE: 5%",
        "tone_distribution": "EXCELLENT_TONE: 60%, GOOD_TONE: 25%, ACCEPTABLE_TONE: 12%, POOR_TONE: 3%",
        "completeness_distribution": "COMPREHENSIVE: 35%, ADEQUATE: 45%, INCOMPLETE: 15%, MISSING_KEY_INFO: 5%"
    }
}
```

### Business Metrics
```python
BUSINESS_METRICS = {
    "user_engagement": {
        "retention_rate": "users returning after evaluation",
        "session_length": "time spent in app",
        "meals_logged": "meals per user per day"
    },
    
    "product_health": {
        "error_rate": "percentage of failed requests",
        "user_reports": "user-reported issues per day",
        "satisfaction_trend": "weekly satisfaction scores"
    }
}
```

## Getting Started Checklist

- [ ] Integrate evaluation endpoints into main.py
- [ ] Set up evaluation database tables
- [ ] Create evaluation interface (use provided HTML)
- [ ] Define your first evaluation batch (50 spans)
- [ ] Train 2-3 people on evaluation criteria
- [ ] Start with manual evaluations for 1 week
- [ ] Implement LLM judge for comparison
- [ ] Set up automated evaluation triggers
- [ ] Create evaluation dashboard in Arize
- [ ] Define success metrics and goals

## Next Steps

1. **Start small**: Begin with 10-20 manual evaluations
2. **Establish baseline**: Get human evaluation on diverse spans
3. **LLM calibration**: Compare LLM judge to human feedback
4. **Scale gradually**: Increase evaluation volume as you learn
5. **Iterate on criteria**: Refine evaluation rubrics based on insights