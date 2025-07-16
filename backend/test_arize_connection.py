"""
Test Arize connection before full integration
"""

import os
from observability import observability

def test_arize_connection():
    """Test basic Arize connectivity"""
    
    print("🔍 Testing Arize Connection...")
    print(f"Space ID configured: {'✅' if os.getenv('ARIZE_SPACE_ID') else '❌'}")
    print(f"API Key configured: {'✅' if os.getenv('ARIZE_API_KEY') else '❌'}")
    print(f"Observability enabled: {'✅' if observability.enabled else '❌'}")
    
    if observability.enabled:
        # Test span creation
        test_span_id = observability.create_meal_analysis_span(
            user_id=999,
            image_metadata={"size": 1000, "format": "image/jpeg"},
            user_context={"daily_protein_goal": 100, "current_protein_today": 30}
        )
        
        print(f"Test span created: {test_span_id}")
        
        # Complete the test span
        observability.complete_meal_analysis_span(
            prediction_id=test_span_id,
            final_results={"detected_foods": ["test_food"], "total_protein": 25},
            success=True
        )
        
        print("✅ Test span completed successfully")
        print("🌐 Check your Arize dashboard for the test span")
        print(f"   Model ID: protein-tracker-app")
        print(f"   Environment: VALIDATION")
        print(f"   Span ID: {test_span_id}")
    else:
        print("❌ Cannot test - observability not enabled")

if __name__ == "__main__":
    test_arize_connection()