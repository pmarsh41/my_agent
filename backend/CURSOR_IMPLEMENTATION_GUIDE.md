# Cursor Implementation Guide: Categorical LLM Evaluation

## Overview
Convert the LLM-as-Judge evaluation system from numerical scoring to categorical classifications. All the category definitions and prompt templates have been prepared.

## Files to Modify

### 1. `evaluation_framework.py` - Core Changes

#### Import the new categories at the top:
```python
from evaluation_categories import (
    validate_category, 
    category_to_score,
    FOOD_DETECTION_DESCRIPTIONS,
    PROTEIN_RELIABILITY_DESCRIPTIONS,
    HELPFULNESS_DESCRIPTIONS,
    ACCURACY_DESCRIPTIONS,
    TONE_DESCRIPTIONS,
    COMPLETENESS_DESCRIPTIONS
)
from categorical_prompt_templates import (
    FOOD_DETECTION_PROMPT,
    PROTEIN_ESTIMATION_PROMPT, 
    CONVERSATIONAL_RESPONSE_PROMPT,
    DEFAULT_RESPONSES
)
```

#### Replace `evaluate_food_detection` method (lines ~85-115):
**OLD:** Returns `plausibility_score: 0-1`
**NEW:** Use `FOOD_DETECTION_PROMPT` and return categorical response

**Current function signature:**
```python
async def evaluate_food_detection(self, image_description: str, detected_foods: List[str]) -> Dict[str, Any]:
```

**New implementation should:**
1. Use `FOOD_DETECTION_PROMPT` instead of current prompt
2. Return categorical response with validation
3. Use `DEFAULT_RESPONSES["food_detection"]` for error handling

#### Replace `evaluate_protein_estimate` method (lines ~117-161):
**OLD:** Returns `reasonableness_score: 0-1`  
**NEW:** Use `PROTEIN_ESTIMATION_PROMPT` and return categorical response

**Current function signature:**
```python
async def evaluate_protein_estimate(self, foods: List[str], portions: List[str], estimated_protein: float) -> Dict[str, Any]:
```

**New implementation should:**
1. Use `PROTEIN_ESTIMATION_PROMPT` instead of current prompt
2. Return categorical response with validation
3. Use `DEFAULT_RESPONSES["protein_estimation"]` for error handling

#### Replace `evaluate_conversational_response` method (lines ~163-200):
**OLD:** Returns numerical scores `1-5` for each dimension
**NEW:** Use `CONVERSATIONAL_RESPONSE_PROMPT` and return categorical response

**Current function signature:**
```python
async def evaluate_conversational_response(self, user_context: str, response_text: str, foods_detected: List[str]) -> Dict[str, Any]:
```

**New implementation should:**
1. Use `CONVERSATIONAL_RESPONSE_PROMPT` instead of current prompt  
2. Return categorical response with validation
3. Use `DEFAULT_RESPONSES["conversational_response"]` for error handling

### 2. `evaluation_endpoints.py` - API Response Updates

#### Update the LLM evaluation test responses:

**In `run_llm_evaluation` function (~line 95):**
Update the sample response to use categorical values instead of numerical scores.

**In `get_evaluation_summary` function (~line 145):**
Update the mock metrics to show categorical distributions instead of numerical averages.

### 3. `test_evaluation.py` - Test Updates

#### Update test expectations (~line 105):
**OLD:** Expects numerical scores like `"plausibility_score": 0.85`
**NEW:** Expects categorical values like `"detection_reliability": "LIKELY_DETECTION"`

**In the LLM evaluation test, change expectations from:**
```python
print(f"   Food plausibility: {food_eval.get('plausibility_score', 'N/A')}")
print(f"   Protein reasonableness: {protein_eval.get('reasonableness_score', 'N/A')}")
```

**To:**
```python
print(f"   Food detection: {food_eval.get('detection_reliability', 'N/A')}")
print(f"   Protein reliability: {protein_eval.get('reliability', 'N/A')}")
```

## Implementation Steps

### Phase 1: Core LLM Updates (Priority 1)
1. ✅ Add imports to `evaluation_framework.py`
2. ✅ Replace `evaluate_food_detection` method with categorical version
3. ✅ Replace `evaluate_protein_estimate` method with categorical version  
4. ✅ Replace `evaluate_conversational_response` method with categorical version
5. ✅ Add error handling with `validate_category` function

### Phase 2: API Updates (Priority 2)  
6. ✅ Update `evaluation_endpoints.py` mock responses to use categorical data
7. ✅ Update analytics functions to handle categorical distributions

### Phase 3: Testing (Priority 3)
8. ✅ Update `test_evaluation.py` expectations for categorical responses
9. ✅ Test full pipeline end-to-end

## Key Implementation Notes

### Error Handling Pattern:
```python
try:
    result = json.loads(response.content)
    # Validate categories
    result['detection_reliability'] = validate_category(
        result.get('detection_reliability', ''), 
        'food_detection'
    )
    return result
except:
    return DEFAULT_RESPONSES["food_detection"]
```

### Prompt Usage Pattern:
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", FOOD_DETECTION_PROMPT),
    ("human", "Image description: {image_description}\nDetected foods: {detected_foods}")
])
```

### Analytics Conversion:
When analytics need numerical values, use:
```python
from evaluation_categories import category_to_score
score = category_to_score(category_value, category_type)
```

## Testing Validation

After implementation, verify:
- [ ] LLM responses contain categorical labels (not numbers)
- [ ] Invalid categories are caught and defaulted appropriately  
- [ ] API endpoints return categorical data in correct format
- [ ] Test script passes with new categorical expectations
- [ ] Error handling works when LLM returns unexpected responses

## Expected Output Format

### Food Detection:
```json
{
    "detection_reliability": "LIKELY_DETECTION",
    "likely_missing": ["sauce"],
    "potentially_incorrect": [],
    "reasoning": "Most foods clearly identified"
}
```

### Protein Estimation:
```json
{
    "reliability": "MODERATELY_RELIABLE", 
    "suggested_range": [38, 45],
    "confidence_factors": ["clear chicken identification"],
    "main_protein_sources": ["chicken breast"],
    "reasoning": "Main protein source clear"
}
```

### Response Quality:
```json
{
    "helpfulness": "HIGHLY_HELPFUL",
    "accuracy": "MOSTLY_ACCURATE",
    "tone": "EXCELLENT_TONE", 
    "completeness": "ADEQUATE",
    "strengths": ["specific advice"],
    "improvements": ["could mention timing"],
    "reasoning": "Provides actionable guidance"
}
```

This guide provides everything needed for a clean implementation of categorical evaluation!