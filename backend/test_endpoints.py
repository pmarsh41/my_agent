#!/usr/bin/env python3
"""
Quick test script to verify all observability endpoints work correctly
"""

import os
import json
import base64
import requests
import tempfile

# Create a minimal JPEG test image (tiny valid JPEG)
def create_test_image():
    """Create a minimal valid JPEG file"""
    # Minimal JPEG header + data (1x1 pixel black image)
    minimal_jpeg = base64.b64decode(
        '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB'
        'AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEB'
        'AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIA'
        'AhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEB'
        'AQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k='
    )
    return minimal_jpeg

def test_endpoint(endpoint_url, test_name, **kwargs):
    """Test a single endpoint"""
    print(f"🧪 Testing {test_name}")
    
    try:
        # Create test image
        image_data = create_test_image()
        
        # Prepare request
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_file.write(image_data)
            temp_file.flush()
            
            with open(temp_file.name, 'rb') as f:
                files = {'file': ('test_meal.jpg', f, 'image/jpeg')}
                
                # Different data format based on endpoint
                data = kwargs.get('data', {})
                
                response = requests.post(
                    endpoint_url,
                    files=files,
                    data=data,
                    timeout=10
                )
        
        # Cleanup
        os.unlink(temp_file.name)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {response.status_code}")
            print(f"   📊 Response keys: {list(result.keys())}")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    """Test all observability endpoints"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing All Observability Endpoints")
    print("=" * 50)
    
    # Check if server is running
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server not healthy. Start with: python main.py")
            return
        print("✅ Server is running and healthy\n")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Start server with: python main.py")
        return
    
    results = []
    
    # Test 1: /analyze-meal-smart/ (main frontend endpoint)
    success = test_endpoint(
        f"{base_url}/analyze-meal-smart/?user_id=1",
        "Smart Meal Analysis Endpoint"
    )
    results.append(("analyze-meal-smart", success))
    
    print()
    
    # Test 2: /analyze-meal-ai/ (LangGraph workflow)
    success = test_endpoint(
        f"{base_url}/analyze-meal-ai/",
        "AI Meal Analysis Endpoint", 
        data={"user_id": 2}
    )
    results.append(("analyze-meal-ai", success))
    
    print()
    
    # Test 3: /analyze-meal/ (simple legacy)
    success = test_endpoint(
        f"{base_url}/analyze-meal/",
        "Simple Meal Analysis Endpoint"
    )
    results.append(("analyze-meal", success))
    
    print()
    print("📈 Test Summary:")
    print("-" * 30)
    
    all_passed = True
    for endpoint, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {endpoint}: {status}")
        if not success:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All endpoints passed! Observability is working correctly.")
        print("📊 Upload a photo through your frontend to see traces in Arize!")
    else:
        print("⚠️ Some endpoints failed. Check server logs for details.")

if __name__ == "__main__":
    main()