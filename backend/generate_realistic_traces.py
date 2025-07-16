#!/usr/bin/env python3
"""
Generate realistic observability traces using actual meal photos
Creates diverse user scenarios and meal contexts for comprehensive Arize data
"""

import os
import json
import requests
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from pathlib import Path

# User personas with realistic protein goals and contexts
USER_PERSONAS = [
    {
        "user_id": 101,
        "name": "Athletic Mike",
        "weight": 185,
        "activity_level": "very_active", 
        "daily_protein_goal": 150,
        "age": 28,
        "profile": "Bodybuilder tracking high protein intake"
    },
    {
        "user_id": 102, 
        "name": "Weight Loss Sarah",
        "weight": 145,
        "activity_level": "moderate",
        "daily_protein_goal": 100,
        "age": 35,
        "profile": "Losing weight while maintaining muscle"
    },
    {
        "user_id": 103,
        "name": "Maintenance Joe",
        "weight": 175,
        "activity_level": "sedentary",
        "daily_protein_goal": 80,
        "age": 42,
        "profile": "Office worker maintaining current weight"
    },
    {
        "user_id": 104,
        "name": "Senior Betty",
        "weight": 125,
        "activity_level": "moderate",
        "daily_protein_goal": 120,
        "age": 68,
        "profile": "Senior focusing on protein for muscle preservation"
    },
    {
        "user_id": 105,
        "name": "Student Alex",
        "weight": 160,
        "activity_level": "active",
        "daily_protein_goal": 90,
        "age": 21,
        "profile": "College student building healthy habits"
    }
]

# Meal timing scenarios
MEAL_SCENARIOS = [
    {"time": "07:30", "meal_name": "Breakfast", "meal_number": 1, "typical_protein_so_far": 0},
    {"time": "12:00", "meal_name": "Lunch", "meal_number": 2, "typical_protein_so_far": 25},
    {"time": "15:30", "meal_name": "Afternoon Snack", "meal_number": 3, "typical_protein_so_far": 45},
    {"time": "18:45", "meal_name": "Dinner", "meal_number": 4, "typical_protein_so_far": 55},
    {"time": "21:00", "meal_name": "Evening Snack", "meal_number": 5, "typical_protein_so_far": 85}
]

def get_test_photos(photo_dir: str) -> List[str]:
    """Get list of test photo paths"""
    photo_dir = Path(photo_dir)
    if not photo_dir.exists():
        raise FileNotFoundError(f"Photo directory not found: {photo_dir}")
    
    # Get all JPG files
    photos = list(photo_dir.glob("*.JPG")) + list(photo_dir.glob("*.jpg"))
    
    if not photos:
        raise FileNotFoundError(f"No JPG files found in {photo_dir}")
    
    print(f"📸 Found {len(photos)} test photos")
    return [str(p) for p in photos]

def create_realistic_context(persona: Dict, scenario: Dict) -> Dict:
    """Create realistic user context for a meal scenario"""
    # Add some randomness to make it realistic
    protein_variance = random.randint(-5, 15)  # Some days you're ahead/behind
    current_protein = max(0, scenario["typical_protein_so_far"] + protein_variance)
    
    # Adjust based on persona
    if persona["name"] == "Athletic Mike":
        current_protein = int(current_protein * 1.2)  # Athletes eat more
    elif persona["name"] == "Weight Loss Sarah":
        current_protein = int(current_protein * 0.9)  # Slightly less during cut
    
    return {
        "daily_protein_goal": persona["daily_protein_goal"],
        "current_protein_today": current_protein,
        "meal_number_today": scenario["meal_number"],
        "weight": persona["weight"],
        "activity_level": persona["activity_level"],
        "dietary_preferences": get_dietary_preferences(persona),
        "meal_time": scenario["time"],
        "meal_name": scenario["meal_name"]
    }

def get_dietary_preferences(persona: Dict) -> List[str]:
    """Get realistic dietary preferences for persona"""
    preferences = []
    
    if persona["name"] == "Athletic Mike":
        preferences = ["high_protein", "lean_meats", "complex_carbs"]
    elif persona["name"] == "Weight Loss Sarah":  
        preferences = ["low_calorie", "high_fiber", "lean_protein"]
    elif persona["name"] == "Senior Betty":
        preferences = ["easy_digest", "nutrient_dense", "soft_foods"]
    elif persona["name"] == "Student Alex":
        preferences = ["budget_friendly", "quick_prep", "filling"]
    else:
        preferences = ["balanced", "moderate_portions"]
    
    return preferences

def analyze_photo_via_api(photo_path: str, persona: Dict, scenario: Dict, api_url: str = "http://localhost:8000") -> Dict:
    """Send photo analysis request with realistic context"""
    
    context = create_realistic_context(persona, scenario)
    
    try:
        # Read the actual photo
        with open(photo_path, "rb") as photo_file:
            files = {"file": (os.path.basename(photo_path), photo_file, "image/jpeg")}
            
            # Use the main frontend endpoint with query parameter
            response = requests.post(
                f"{api_url}/analyze-meal-smart/?user_id={persona['user_id']}",
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result,
                    "persona": persona,
                    "scenario": scenario,
                    "context": context,
                    "photo_path": photo_path
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned {response.status_code}: {response.text}",
                    "persona": persona,
                    "scenario": scenario,
                    "context": context,
                    "photo_path": photo_path
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "persona": persona,
            "scenario": scenario,
            "context": context,
            "photo_path": photo_path
        }

def generate_realistic_traces(photo_dir: str, traces_per_photo: int = 3, delay_seconds: int = 2) -> List[Dict]:
    """Generate realistic traces using actual meal photos"""
    
    photos = get_test_photos(photo_dir)
    results = []
    
    print(f"🚀 Starting realistic trace generation")
    print(f"📊 {len(photos)} photos × {traces_per_photo} scenarios = {len(photos) * traces_per_photo} total traces")
    print(f"⏱️ {delay_seconds}s delay between requests")
    print(f"👥 {len(USER_PERSONAS)} user personas")
    print(f"🍽️ {len(MEAL_SCENARIOS)} meal scenarios")
    print()
    
    for i, photo_path in enumerate(photos):
        photo_name = os.path.basename(photo_path)
        print(f"📸 Photo {i+1}/{len(photos)}: {photo_name}")
        
        # Generate multiple traces per photo with different personas/scenarios
        for trace_num in range(traces_per_photo):
            persona = random.choice(USER_PERSONAS)
            scenario = random.choice(MEAL_SCENARIOS)
            
            print(f"  🔄 Trace {trace_num+1}/{traces_per_photo}: {persona['name']} - {scenario['meal_name']}")
            
            # Make API request
            result = analyze_photo_via_api(photo_path, persona, scenario)
            results.append(result)
            
            if result["success"]:
                foods = result["response"].get("identified_foods", [])
                protein = result["response"].get("total_protein_estimate", 0)
                print(f"     ✅ Success: {len(foods)} foods, {protein}g protein")
            else:
                print(f"     ❌ Failed: {result['error']}")
            
            # Add delay between requests (except for last request)
            if not (i == len(photos) - 1 and trace_num == traces_per_photo - 1):
                time.sleep(delay_seconds)
        
        print()
    
    return results

def save_results(results: List[Dict], filename: str = None):
    """Save trace generation results"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"realistic_traces_results_{timestamp}.json"
    
    # Convert results to JSON-serializable format
    json_results = []
    for result in results:
        json_result = result.copy()
        # Convert any non-serializable objects
        for key, value in json_result.items():
            if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                json_result[key] = str(value)
        json_results.append(json_result)
    
    with open(filename, "w") as f:
        json.dump(json_results, f, indent=2, default=str)
    
    print(f"📁 Results saved to: {filename}")
    return filename

def print_summary(results: List[Dict]):
    """Print summary of trace generation results"""
    total_traces = len(results)
    successful_traces = len([r for r in results if r["success"]])
    failed_traces = total_traces - successful_traces
    
    # Analyze by persona
    persona_stats = {}
    for result in results:
        if result["success"]:
            persona_name = result["persona"]["name"]
            if persona_name not in persona_stats:
                persona_stats[persona_name] = 0
            persona_stats[persona_name] += 1
    
    # Analyze by meal type
    meal_stats = {}
    for result in results:
        if result["success"]:
            meal_name = result["scenario"]["meal_name"]
            if meal_name not in meal_stats:
                meal_stats[meal_name] = 0
            meal_stats[meal_name] += 1
    
    print(f"📈 Realistic Trace Generation Summary:")
    print(f"   Total Traces: {total_traces}")
    print(f"   Successful: {successful_traces}")
    print(f"   Failed: {failed_traces}")
    print(f"   Success Rate: {(successful_traces/total_traces)*100:.1f}%")
    print()
    
    if successful_traces > 0:
        print(f"👥 Traces by User Persona:")
        for persona, count in persona_stats.items():
            print(f"   {persona}: {count} traces")
        
        print(f"\n🍽️ Traces by Meal Type:")
        for meal, count in meal_stats.items():
            print(f"   {meal}: {count} traces")
        
        print()
        print(f"🎯 Check your Arize dashboard for realistic meal analysis data!")
        print(f"   Model ID: protein-tracker-app")
        print(f"   Environment: PRODUCTION")
        print(f"   Expected spans: {successful_traces}")
        print(f"   📊 Rich data with actual food detection and user contexts")

def main():
    """Main function to generate realistic traces"""
    print("🥗 Protein Tracker - Realistic Trace Generator")
    print("=" * 55)
    print()
    
    photo_directory = "/Users/philmarshall/Desktop/test-photos"
    
    # Check if photo directory exists
    if not os.path.exists(photo_directory):
        print(f"❌ Photo directory not found: {photo_directory}")
        print("   Please check the path and try again.")
        return
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ API health check failed. Make sure your server is running on port 8000")
            return
        print("✅ API is running and healthy")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure your FastAPI server is running: python main.py")
        return
    
    print(f"✅ Photo directory found: {photo_directory}")
    print()
    
    # Generate realistic traces
    results = generate_realistic_traces(
        photo_dir=photo_directory,
        traces_per_photo=3,  # 3 different user scenarios per photo
        delay_seconds=2      # 2 second delay between requests
    )
    
    # Save and summarize results
    filename = save_results(results)
    print_summary(results)
    
    print()
    print("🎉 Realistic trace generation completed!")
    print("   Your Arize dashboard should now show comprehensive meal analysis data")
    print("   with actual food detection results across diverse user scenarios!")

if __name__ == "__main__":
    main()