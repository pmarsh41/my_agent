# Exact Code Changes Required

## Current State Analysis
Based on reading `evaluation_framework.py`, here are the exact changes needed:

## 1. Add Imports (at top of evaluation_framework.py)
**ADD AFTER line 16:**
```python
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
```

## 2. Replace evaluate_food_detection method (lines ~85-115)

**FIND this method signature:**
```python
async def evaluate_food_detection(self, 
                                image_description: str,
                                detected_foods: List[str]) -> Dict[str, Any]:
```

**REPLACE the entire method body with:**
```python
async def evaluate_food_detection(self, 
                                image_description: str,
                                detected_foods: List[str]) -> Dict[str, Any]:
    """Evaluate if detected foods are reasonable given an image"""
    
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
        result = json.loads(response.content)
        # Validate the category
        result['detection_reliability'] = validate_category(
            result.get('detection_reliability', ''), 
            'food_detection'
        )
        return result
    except:
        return DEFAULT_RESPONSES["food_detection"]
```

## 3. Replace evaluate_protein_estimate method (lines ~117-161)

**FIND this method (around line 117):**
```python
async def evaluate_protein_estimate(self,
                                  foods: List[str],
                                  portions: List[str],
                                  estimated_protein: float) -> Dict[str, Any]:
```

**REPLACE the entire method body with:**
```python
async def evaluate_protein_estimate(self,
                                  foods: List[str],
                                  portions: List[str],
                                  estimated_protein: float) -> Dict[str, Any]:
    """Evaluate if protein estimate is reasonable"""
    
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
        # Validate the category
        result['reliability'] = validate_category(
            result.get('reliability', ''), 
            'protein_reliability'
        )
        # Fill in suggested_range if missing
        if not result.get('suggested_range'):
            result['suggested_range'] = [estimated_protein * 0.8, estimated_protein * 1.2]
        return result
    except:
        fallback = DEFAULT_RESPONSES["protein_estimation"].copy()
        fallback['suggested_range'] = [estimated_protein * 0.8, estimated_protein * 1.2]
        return fallback
```

## 4. Replace evaluate_conversational_response method (lines ~163-200)

**FIND this method (around line 163):**
```python
async def evaluate_conversational_response(self,
                                         user_context: str,
                                         response_text: str,
                                         foods_detected: List[str]) -> Dict[str, Any]:
```

**REPLACE the entire method body with:**
```python
async def evaluate_conversational_response(self,
                                         user_context: str,
                                         response_text: str,
                                         foods_detected: List[str]) -> Dict[str, Any]:
    """Evaluate the quality of the conversational response"""
    
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
        # Validate all categories
        result['helpfulness'] = validate_category(
            result.get('helpfulness', ''), 'helpfulness'
        )
        result['accuracy'] = validate_category(
            result.get('accuracy', ''), 'accuracy'
        )
        result['tone'] = validate_category(
            result.get('tone', ''), 'tone'
        )
        result['completeness'] = validate_category(
            result.get('completeness', ''), 'completeness'
        )
        return result
    except:
        return DEFAULT_RESPONSES["conversational_response"]
```

## 5. Update run_llm_evaluation method (around line 320)

**FIND this section in the method:**
```python
        return {
            "span_id": span_data["span_id"],
            "food_detection_eval": results[0],
            "protein_estimate_eval": results[1],
            "response_quality_eval": results[2],
            "timestamp": datetime.utcnow().isoformat()
        }
```

**NO CHANGE NEEDED** - This section is already correct as it just passes through the results.

## 6. Update test_evaluation.py (around line 105)

**FIND these lines in the LLM evaluation test:**
```python
            if 'food_detection_eval' in evaluation:
                food_eval = evaluation['food_detection_eval']
                print(f"   Food plausibility: {food_eval.get('plausibility_score', 'N/A')}")
            
            if 'protein_estimate_eval' in evaluation:
                protein_eval = evaluation['protein_estimate_eval']
                print(f"   Protein reasonableness: {protein_eval.get('reasonableness_score', 'N/A')}")
```

**REPLACE with:**
```python
            if 'food_detection_eval' in evaluation:
                food_eval = evaluation['food_detection_eval']
                print(f"   Food detection: {food_eval.get('detection_reliability', 'N/A')}")
            
            if 'protein_estimate_eval' in evaluation:
                protein_eval = evaluation['protein_estimate_eval']
                print(f"   Protein reliability: {protein_eval.get('reliability', 'N/A')}")
                
            if 'response_quality_eval' in evaluation:
                quality_eval = evaluation['response_quality_eval']
                print(f"   Response helpfulness: {quality_eval.get('helpfulness', 'N/A')}")
                print(f"   Response accuracy: {quality_eval.get('accuracy', 'N/A')}")
```

## Summary of Changes
- ✅ Files created: `evaluation_categories.py`, `categorical_prompt_templates.py`
- 🔄 Need to modify: `evaluation_framework.py` (4 method replacements + imports)
- 🔄 Need to modify: `test_evaluation.py` (update expectations)
- 📋 Optional: Update `evaluation_endpoints.py` mock responses for better demos

**Total lines to change: ~150 lines across 2 files**
**Estimated time: 30-45 minutes for careful implementation**