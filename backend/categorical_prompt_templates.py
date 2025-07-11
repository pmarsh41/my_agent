"""
Template prompts for LLM-as-Judge categorical evaluations.
These templates should replace the numerical scoring prompts in evaluation_framework.py
"""

# FOOD DETECTION EVALUATION PROMPT
FOOD_DETECTION_PROMPT = """You are an expert nutritionist evaluating food detection accuracy.
Given an image description and a list of detected foods, evaluate the reliability of the detections.

EVALUATION CATEGORIES:
- CONFIDENT_DETECTION: All foods clearly visible and identifiable with high confidence
- LIKELY_DETECTION: Most foods identifiable with minor uncertainty in 1-2 items
- UNCERTAIN_DETECTION: Some foods difficult to distinguish, moderate uncertainty  
- POOR_DETECTION: Many foods unclear or potentially misidentified
- FAILED_DETECTION: Unable to reliably identify meal contents due to image quality or complexity

Consider these factors:
1. Are the detected foods plausible given the description?
2. Are there likely foods missing from the detection?
3. Are there any foods that seem incorrect or implausible?
4. How clear and identifiable would these foods be in a typical meal photo?

Respond with JSON containing:
- detection_reliability: [CATEGORY from above]
- likely_missing: list of foods that might be missing
- potentially_incorrect: list of foods that seem questionable
- reasoning: brief explanation for the category choice

Example response:
{
    "detection_reliability": "LIKELY_DETECTION",
    "likely_missing": ["sauce", "seasoning"],
    "potentially_incorrect": [],
    "reasoning": "Most foods are clearly identifiable, but small accompaniments like sauces might be missed"
}"""

# PROTEIN ESTIMATION EVALUATION PROMPT  
PROTEIN_ESTIMATION_PROMPT = """You are a nutrition expert evaluating protein estimates.
Given foods, portions, and a protein estimate, evaluate the reliability of the calculation.

EVALUATION CATEGORIES:
- HIGHLY_RELIABLE: Protein estimate based on clear portions and well-known foods with high accuracy
- MODERATELY_RELIABLE: Estimate reasonable but some portion or food identification uncertainty
- SOMEWHAT_RELIABLE: Estimate approximate due to unclear portions or unfamiliar foods
- UNRELIABLE: Significant uncertainty in foods or portions makes estimate questionable
- INVALID: Cannot provide meaningful protein estimate due to detection failures

Reference protein values:
- Chicken breast (4oz): ~35g protein
- Eggs (1 large): ~6g protein  
- Greek yogurt (1 cup): ~20g protein
- Black beans (1 cup): ~15g protein
- Salmon (4oz): ~30g protein
- Tofu (4oz): ~20g protein
- Quinoa (1 cup cooked): ~8g protein

Consider these factors:
1. Are the food identifications accurate and specific enough?
2. Are the portion estimates reasonable and well-defined?
3. Does the total protein estimate align with known values?
4. Are there any unusual or hard-to-estimate foods?

Respond with JSON containing:
- reliability: [CATEGORY from above]
- suggested_range: [min, max] estimated range in grams
- confidence_factors: list of factors that increase/decrease confidence
- main_protein_sources: list of primary protein contributors
- reasoning: brief explanation for the category choice

Example response:
{
    "reliability": "MODERATELY_RELIABLE",
    "suggested_range": [38, 45],
    "confidence_factors": ["clear chicken identification", "uncertain rice portion"],
    "main_protein_sources": ["chicken breast", "quinoa"],
    "reasoning": "Main protein source is clearly identified but side portions are estimated"
}"""

# CONVERSATIONAL RESPONSE EVALUATION PROMPT
CONVERSATIONAL_RESPONSE_PROMPT = """You are evaluating the quality of AI nutritional guidance responses.
Evaluate the response across four dimensions using categorical classifications.

HELPFULNESS CATEGORIES:
- HIGHLY_HELPFUL: Provides specific, actionable nutritional guidance tailored to the meal
- MODERATELY_HELPFUL: Gives useful information with minor gaps in actionability  
- SOMEWHAT_HELPFUL: Basic information provided but lacks depth or specific guidance
- NOT_HELPFUL: Vague, irrelevant, or provides no actionable information

ACCURACY CATEGORIES:
- HIGHLY_ACCURATE: All nutritional information is scientifically correct and well-supported
- MOSTLY_ACCURATE: Generally correct with minor inaccuracies or oversimplifications
- SOMEWHAT_ACCURATE: Some questionable information but core facts are correct
- INACCURATE: Contains misleading or scientifically incorrect nutritional information

TONE CATEGORIES:
- EXCELLENT_TONE: Very encouraging, supportive, and motivating without being condescending
- GOOD_TONE: Positive and motivating with appropriate enthusiasm
- ACCEPTABLE_TONE: Neutral tone that doesn't discourage but lacks motivation
- POOR_TONE: Negative, discouraging, or inappropriate tone for health guidance

COMPLETENESS CATEGORIES:
- COMPREHENSIVE: Addresses all relevant aspects of the meal and user's nutritional needs
- ADEQUATE: Covers the main points but may miss some relevant details
- INCOMPLETE: Missing important information that would be helpful to the user
- MISSING_KEY_INFO: Fails to address core aspects of the meal or user's needs

Consider these factors:
1. Does the response provide actionable nutritional advice?
2. Is the nutritional information scientifically accurate?
3. Is the tone encouraging and appropriate for health guidance?
4. Does it address the user's meal comprehensively?

Respond with JSON containing:
- helpfulness: [HELPFULNESS CATEGORY]
- accuracy: [ACCURACY CATEGORY]  
- tone: [TONE CATEGORY]
- completeness: [COMPLETENESS CATEGORY]
- strengths: list of strong points in the response
- improvements: list of areas that could be better
- reasoning: brief explanation for each category choice

Example response:
{
    "helpfulness": "HIGHLY_HELPFUL",
    "accuracy": "MOSTLY_ACCURATE", 
    "tone": "EXCELLENT_TONE",
    "completeness": "ADEQUATE",
    "strengths": ["specific protein breakdown", "encouraging language", "actionable advice"],
    "improvements": ["could mention meal timing", "missing micronutrient info"],
    "reasoning": "Response provides specific nutritional guidance with encouraging tone, minor gaps in comprehensiveness"
}"""

# ERROR HANDLING FALLBACKS
DEFAULT_RESPONSES = {
    "food_detection": {
        "detection_reliability": "UNCERTAIN_DETECTION",
        "likely_missing": [],
        "potentially_incorrect": [],
        "reasoning": "Failed to parse LLM response for food detection evaluation"
    },
    "protein_estimation": {
        "reliability": "SOMEWHAT_RELIABLE", 
        "suggested_range": [0, 0],  # Will be filled with estimate ±20%
        "confidence_factors": [],
        "main_protein_sources": [],
        "reasoning": "Failed to parse LLM response for protein evaluation"
    },
    "conversational_response": {
        "helpfulness": "SOMEWHAT_HELPFUL",
        "accuracy": "SOMEWHAT_ACCURATE",
        "tone": "ACCEPTABLE_TONE", 
        "completeness": "ADEQUATE",
        "strengths": [],
        "improvements": ["LLM evaluation failed"],
        "reasoning": "Failed to parse LLM response for conversational evaluation"
    }
}