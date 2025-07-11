#!/usr/bin/env python3
"""
Generate synthetic meal data for the Protein Tracker app.
This script creates realistic meal analysis requests to test the system and Arize tracing.
"""

import requests
import json
import time
import random
import base64
from datetime import datetime, timedelta
from typing import List, Dict
import os
import io

# Configuration
API_BASE_URL = "http://localhost:8000"
USER_ID = 1
DELAY_BETWEEN_REQUESTS = 5  # seconds between requests to avoid rate limits

# Sample meal descriptions for generating synthetic data
MEAL_TEMPLATES = [
    {
        "foods": ["grilled chicken breast", "brown rice", "steamed broccoli"],
        "protein_range": (35, 45),
        "meal_type": "lunch"
    },
    {
        "foods": ["scrambled eggs", "whole wheat toast", "avocado"],
        "protein_range": (18, 25),
        "meal_type": "breakfast"
    },
    {
        "foods": ["greek yogurt", "granola", "mixed berries"],
        "protein_range": (15, 20),
        "meal_type": "snack"
    },
    {
        "foods": ["salmon fillet", "quinoa", "asparagus"],
        "protein_range": (40, 50),
        "meal_type": "dinner"
    },
    {
        "foods": ["black bean burger", "sweet potato fries", "side salad"],
        "protein_range": (20, 28),
        "meal_type": "lunch"
    },
    {
        "foods": ["protein shake", "banana", "peanut butter"],
        "protein_range": (25, 35),
        "meal_type": "post-workout"
    },
    {
        "foods": ["turkey sandwich", "apple", "string cheese"],
        "protein_range": (22, 30),
        "meal_type": "lunch"
    },
    {
        "foods": ["tofu stir fry", "white rice", "mixed vegetables"],
        "protein_range": (18, 25),
        "meal_type": "dinner"
    },
    {
        "foods": ["cottage cheese", "peach slices", "almonds"],
        "protein_range": (20, 25),
        "meal_type": "snack"
    },
    {
        "foods": ["beef tacos", "refried beans", "guacamole"],
        "protein_range": (30, 40),
        "meal_type": "dinner"
    }
]

def create_dummy_image() -> bytes:
    """Create a simple dummy image and return as bytes."""
    # Create a minimal valid JPEG as bytes
    # This is a 1x1 pixel red JPEG image
    minimal_jpeg = (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c'
        b'\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c'
        b'\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xdb\x00C\x01\t\t\t'
        b'\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222'
        b'22222222222222222222222222222222\xff\xc0\x00\x11\x08\x00\x01\x00\x01'
        b'\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05'
        b'\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03'
        b'\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03'
        b'\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05'
        b'\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0'
        b'$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefg'
        b'hijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97'
        b'\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6'
        b'\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5'
        b'\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2'
        b'\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01'
        b'\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04'
        b'\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04'
        b'\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1'
        b'\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br'
        b'\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcd'
        b'efghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95'
        b'\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4'
        b'\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3'
        b'\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2'
        b'\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11'
        b'\x03\x11\x00?\x00\xf9\xfe\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a'
        b'(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0'
        b'\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02'
        b'\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a'
        b'(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0'
        b'\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x02'
        b'\x8a(\xa0\x02\x8a(\xa0\x02\x8a(\xa0\x0f\xff\xd9'
    )
    return minimal_jpeg

def generate_meal_request(meal_template: Dict) -> Dict:
    """Generate a meal analysis request from a template."""
    # Add some variation to the foods
    foods = meal_template["foods"].copy()
    
    # Randomly add portion sizes
    foods_with_portions = []
    for food in foods:
        portion_variations = ["small", "medium", "large", "1 cup", "6 oz", "1 serving"]
        if random.random() > 0.5:
            portion = random.choice(portion_variations)
            foods_with_portions.append(f"{portion} {food}")
        else:
            foods_with_portions.append(food)
    
    # Create the request
    return {
        "user_id": USER_ID,
        "image_data": create_dummy_image(),
        "meal_description": f"{meal_template['meal_type'].title()} with {', '.join(foods_with_portions)}"
    }

def test_smart_meal_analysis(num_requests: int = 5):
    """Generate and send synthetic meal analysis requests."""
    print(f"🚀 Starting synthetic data generation - {num_requests} requests")
    print(f"⏱️  Delay between requests: {DELAY_BETWEEN_REQUESTS} seconds")
    
    successful = 0
    failed = 0
    
    for i in range(num_requests):
        # Select a random meal template
        template = random.choice(MEAL_TEMPLATES)
        
        print(f"\n📸 Request {i+1}/{num_requests}: {template['meal_type']} meal")
        print(f"   Foods: {', '.join(template['foods'])}")
        
        try:
            # Create a file-like object from the dummy image
            image_bytes = create_dummy_image()
            files = {
                'file': (f'meal_{i+1}.jpg', io.BytesIO(image_bytes), 'image/jpeg')
            }
            
            # Send request to API with file upload
            response = requests.post(
                f"{API_BASE_URL}/analyze-meal-smart/",
                params={"user_id": USER_ID},
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success!")
                print(f"   🥩 Protein: {result.get('protein_estimate', 'N/A')}g")
                print(f"   🍽️  Foods detected: {len(result.get('foods_detected', []))}")
                print(f"   💬 Response: {result.get('analysis_text', '')[:100]}...")
                successful += 1
            else:
                print(f"   ❌ Failed with status: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
            failed += 1
        
        # Wait before next request to avoid rate limits
        if i < num_requests - 1:
            print(f"   ⏳ Waiting {DELAY_BETWEEN_REQUESTS} seconds...")
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   🎯 Success rate: {(successful/num_requests)*100:.1f}%")

def test_meal_confirmation(num_requests: int = 3):
    """Test the meal confirmation endpoint with synthetic data."""
    print(f"\n🍽️  Testing meal confirmation - {num_requests} requests")
    
    for i in range(num_requests):
        template = random.choice(MEAL_TEMPLATES)
        
        # Create confirmation request
        portions = []
        for food in template["foods"]:
            portions.append({
                "food_name": food,
                "quantity": round(random.uniform(0.5, 2.0), 1),
                "unit": random.choice(["cups", "oz", "grams", "serving"]),
                "protein": round(random.uniform(5, 20), 1)
            })
        
        request_data = {
            "user_id": USER_ID,
            "meal_portions": portions
        }
        
        print(f"\n✅ Confirmation {i+1}/{num_requests}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/confirm-meal-portions/",
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Meal logged successfully!")
                print(f"   🥩 Total protein: {result.get('total_protein', 'N/A')}g")
            else:
                print(f"   ❌ Failed with status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
        
        if i < num_requests - 1:
            time.sleep(DELAY_BETWEEN_REQUESTS)

def main():
    """Main function to run synthetic data generation."""
    print("🧬 Protein Tracker - Synthetic Data Generator")
    print("=" * 50)
    
    # Check if API is running by checking the docs endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/docs")
        if response.status_code != 200:
            print(f"❌ API returned status {response.status_code}. Make sure the backend is running!")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure the backend is running on port 8000!")
        return
    
    print("✅ API is running\n")
    
    # Generate meal analysis requests
    test_smart_meal_analysis(num_requests=10)
    
    # Test meal confirmations
    test_meal_confirmation(num_requests=5)
    
    print("\n✨ Synthetic data generation complete!")
    print("Check Arize to see the traces from these requests.")

if __name__ == "__main__":
    main()