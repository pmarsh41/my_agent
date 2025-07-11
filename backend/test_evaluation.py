#!/usr/bin/env python3
"""
Test script for the evaluation system
"""

import asyncio
import requests
import json
from datetime import datetime


API_BASE = "http://localhost:8000"

def test_evaluation_endpoints():
    """Test the evaluation API endpoints"""
    
    print("🧪 Testing Evaluation System")
    print("=" * 50)
    
    # Test 1: Get evaluation schema
    print("\n1. Testing evaluation schema endpoint...")
    try:
        response = requests.get(f"{API_BASE}/evaluate/dataset/schema")
        if response.status_code == 200:
            schema = response.json()
            print(f"✅ Schema retrieved with {schema['total_columns']} columns")
            print(f"   Categories: {list(schema['categories'].keys())}")
        else:
            print(f"❌ Schema endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
    
    # Test 2: Submit food detection feedback
    print("\n2. Testing food detection feedback...")
    try:
        feedback_data = {
            "span_id": "test_span_001",
            "detected_foods": ["chicken breast", "rice", "broccoli"],
            "actual_foods": ["chicken breast", "brown rice", "broccoli", "olive oil"],
            "missing_foods": ["olive oil"],
            "incorrect_foods": [],
            "accuracy_score": 0.85,
            "notes": "Missed the olive oil drizzle on top"
        }
        
        response = requests.post(
            f"{API_BASE}/evaluate/feedback/food-detection",
            json=feedback_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Food feedback submitted: {result['feedback_id']}")
        else:
            print(f"❌ Food feedback failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Food feedback test failed: {e}")
    
    # Test 3: Submit protein estimation feedback
    print("\n3. Testing protein estimation feedback...")
    try:
        protein_feedback = {
            "span_id": "test_span_001",
            "estimated_protein": 42.5,
            "actual_protein": 45.0,
            "accuracy_rating": 4,
            "is_underestimate": True,
            "notes": "Pretty close, but underestimated chicken portion slightly"
        }
        
        response = requests.post(
            f"{API_BASE}/evaluate/feedback/protein-estimate",
            json=protein_feedback
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Protein feedback submitted: {result['feedback_id']}")
        else:
            print(f"❌ Protein feedback failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Protein feedback test failed: {e}")
    
    # Test 4: Submit response quality feedback
    print("\n4. Testing response quality feedback...")
    try:
        quality_feedback = {
            "span_id": "test_span_001",
            "helpfulness": 5,
            "accuracy": 4,
            "clarity": 5,
            "tone": 5,
            "overall_quality": 4,
            "suggestions": "Could mention the importance of post-workout timing"
        }
        
        response = requests.post(
            f"{API_BASE}/evaluate/feedback/response-quality",
            json=quality_feedback
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Quality feedback submitted: {result['feedback_id']}")
            print(f"   Average score: {result['average_score']:.1f}/5")
        else:
            print(f"❌ Quality feedback failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Quality feedback test failed: {e}")
    
    # Test 5: Run LLM evaluation on a span
    print("\n5. Testing LLM evaluation...")
    try:
        span_data = {
            "span_id": "test_span_002",
            "foods_detected": ["greek yogurt", "granola", "blueberries"],
            "protein_estimate": 18.5,
            "analysis_text": "Nice breakfast choice! This Greek yogurt parfait provides about 18.5g of protein, mainly from the yogurt. The granola adds some texture and the blueberries provide antioxidants. This is a great way to start your day with quality protein!",
            "portion_suggestions": {
                "greek_yogurt": "1 cup",
                "granola": "2 tbsp", 
                "blueberries": "1/2 cup"
            }
        }
        
        response = requests.post(
            f"{API_BASE}/evaluate/llm-judge/evaluate-span",
            params={"span_id": "test_span_002"},
            json=span_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ LLM evaluation completed for span: {result['span_id']}")
            evaluation = result['evaluation']
            
            if 'food_detection_eval' in evaluation:
                food_eval = evaluation['food_detection_eval']
                print(f"   Food detection: {food_eval.get('detection_reliability', 'N/A')}")
                # Validate categorical response
                detection_category = food_eval.get('detection_reliability')
                valid_categories = ['CONFIDENT_DETECTION', 'LIKELY_DETECTION', 'UNCERTAIN_DETECTION', 'POOR_DETECTION', 'FAILED_DETECTION']
                if detection_category in valid_categories:
                    print(f"   ✅ Valid food detection category: {detection_category}")
                else:
                    print(f"   ❌ Invalid food detection category: {detection_category}")
            
            if 'protein_estimate_eval' in evaluation:
                protein_eval = evaluation['protein_estimate_eval']
                print(f"   Protein reliability: {protein_eval.get('reliability', 'N/A')}")
                # Validate categorical response
                reliability_category = protein_eval.get('reliability')
                valid_categories = ['HIGHLY_RELIABLE', 'MODERATELY_RELIABLE', 'SOMEWHAT_RELIABLE', 'UNRELIABLE', 'INVALID']
                if reliability_category in valid_categories:
                    print(f"   ✅ Valid protein reliability category: {reliability_category}")
                else:
                    print(f"   ❌ Invalid protein reliability category: {reliability_category}")
            
            if 'response_quality_eval' in evaluation:
                quality_eval = evaluation['response_quality_eval']
                print(f"   Response helpfulness: {quality_eval.get('helpfulness', 'N/A')}")
                print(f"   Response accuracy: {quality_eval.get('accuracy', 'N/A')}")
                print(f"   Response tone: {quality_eval.get('tone', 'N/A')}")
                print(f"   Response completeness: {quality_eval.get('completeness', 'N/A')}")
                # Validate categorical responses
                helpfulness = quality_eval.get('helpfulness')
                accuracy = quality_eval.get('accuracy')
                tone = quality_eval.get('tone')
                completeness = quality_eval.get('completeness')
                
                valid_helpfulness = ['HIGHLY_HELPFUL', 'MODERATELY_HELPFUL', 'SOMEWHAT_HELPFUL', 'NOT_HELPFUL']
                valid_accuracy = ['HIGHLY_ACCURATE', 'MOSTLY_ACCURATE', 'SOMEWHAT_ACCURATE', 'INACCURATE']
                valid_tone = ['EXCELLENT_TONE', 'GOOD_TONE', 'ACCEPTABLE_TONE', 'POOR_TONE']
                valid_completeness = ['COMPREHENSIVE', 'ADEQUATE', 'INCOMPLETE', 'MISSING_KEY_INFO']
                
                if helpfulness in valid_helpfulness:
                    print(f"   ✅ Valid helpfulness category: {helpfulness}")
                else:
                    print(f"   ❌ Invalid helpfulness category: {helpfulness}")
                    
                if accuracy in valid_accuracy:
                    print(f"   ✅ Valid accuracy category: {accuracy}")
                else:
                    print(f"   ❌ Invalid accuracy category: {accuracy}")
                    
                if tone in valid_tone:
                    print(f"   ✅ Valid tone category: {tone}")
                else:
                    print(f"   ❌ Invalid tone category: {tone}")
                    
                if completeness in valid_completeness:
                    print(f"   ✅ Valid completeness category: {completeness}")
                else:
                    print(f"   ❌ Invalid completeness category: {completeness}")
                
        else:
            print(f"❌ LLM evaluation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ LLM evaluation test failed: {e}")
    
    # Test 6: Get evaluation summary
    print("\n6. Testing evaluation analytics...")
    try:
        response = requests.get(f"{API_BASE}/evaluate/analytics/summary")
        if response.status_code == 200:
            summary = response.json()
            print(f"✅ Analytics summary retrieved")
            metrics = summary['metrics']
            print(f"   Food detection avg: {metrics['food_detection']['human_accuracy_avg']}")
            print(f"   Protein estimation avg: {metrics['protein_estimation']['human_accuracy_avg']}")
        else:
            print(f"❌ Analytics failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Analytics test failed: {e}")
    
    # Test 7: Create evaluation dataset
    print("\n7. Testing dataset creation...")
    try:
        response = requests.post(
            f"{API_BASE}/evaluate/dataset/create",
            params={"num_samples": 10, "strategy": "random"}
        )
        
        if response.status_code == 200:
            dataset = response.json()
            print(f"✅ Dataset created: {dataset['dataset_id']}")
            print(f"   Samples: {dataset['num_samples']}")
            print(f"   Strategy: {dataset['strategy']}")
        else:
            print(f"❌ Dataset creation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dataset creation test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Evaluation system testing complete!")


def test_evaluation_interface():
    """Test the evaluation HTML interface"""
    try:
        response = requests.get(f"{API_BASE}/templates/evaluation_interface.html")
        if response.status_code == 200:
            print("✅ Evaluation interface accessible")
            print(f"   URL: {API_BASE}/templates/evaluation_interface.html")
        else:
            print("❌ Evaluation interface not accessible")
    except Exception as e:
        print(f"❌ Interface test failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting evaluation system tests...")
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE}/docs")
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print("❌ API not responding")
            exit(1)
    except:
        print("❌ Cannot connect to API")
        print("Make sure your backend is running: python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        exit(1)
    
    # Run tests
    test_evaluation_endpoints()
    test_evaluation_interface()
    
    print("\n💡 Next steps:")
    print("1. Visit the evaluation interface at:")
    print(f"   {API_BASE}/templates/evaluation_interface.html")
    print("2. Start collecting human feedback on meal analysis results")
    print("3. Run LLM evaluations on historical spans")
    print("4. Monitor evaluation metrics in Arize")