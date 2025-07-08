"""
Comprehensive Nutrition Database for Smart Food Identification Agent
Based on USDA nutrition data with common portion sizes and preparation methods
"""
from typing import Dict, List, Optional, Tuple, Any

class NutritionDatabase:
    """Comprehensive nutrition database for food identification and protein calculation.
    
    Contains detailed nutrition information for 40+ common foods with
    protein content, portion sizes, preparation methods, and visual cues.
    """
    
    def __init__(self) -> None:
        """Initialize the nutrition database with comprehensive food data."""
        self.foods = self._initialize_database()
    
    def _initialize_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive food database with protein content per 100g.
        
        Returns:
            Dict containing food data with nutrition information, portion sizes,
            preparation methods, and visual identification cues.
        """
        return {
            # PROTEINS - MEAT
            "chicken_breast": {
                "name": "Chicken Breast",
                "category": "protein",
                "protein_per_100g": 31.0,
                "common_portions": {
                    "small": {"grams": 120, "description": "4oz serving"},
                    "medium": {"grams": 150, "description": "5oz serving"},
                    "large": {"grams": 180, "description": "6oz serving"},
                    "extra_large": {"grams": 240, "description": "8oz serving"}
                },
                "preparation_modifiers": {
                    "grilled": 1.0,
                    "baked": 1.0,
                    "fried": 0.9,  # Some protein lost to breading/oil
                    "boiled": 1.0,
                    "roasted": 1.0
                },
                "visual_cues": ["white meat", "lean", "palm-sized", "thick slice"],
                "confidence_keywords": ["chicken", "breast", "poultry", "white meat"]
            },
            "chicken_thigh": {
                "name": "Chicken Thigh",
                "category": "protein",
                "protein_per_100g": 26.0,
                "common_portions": {
                    "small": {"grams": 100, "description": "1 small thigh"},
                    "medium": {"grams": 130, "description": "1 medium thigh"},
                    "large": {"grams": 160, "description": "1 large thigh"}
                },
                "preparation_modifiers": {
                    "grilled": 1.0,
                    "baked": 1.0,
                    "fried": 0.9,
                    "roasted": 1.0
                },
                "visual_cues": ["darker meat", "bone-in or boneless", "triangular shape"],
                "confidence_keywords": ["chicken", "thigh", "dark meat"]
            },
            "beef_steak": {
                "name": "Beef Steak",
                "category": "protein",
                "protein_per_100g": 26.0,
                "common_portions": {
                    "small": {"grams": 150, "description": "5oz steak"},
                    "medium": {"grams": 200, "description": "7oz steak"},
                    "large": {"grams": 280, "description": "10oz steak"}
                },
                "preparation_modifiers": {
                    "grilled": 1.0,
                    "pan_seared": 1.0,
                    "broiled": 1.0,
                    "well_done": 0.95
                },
                "visual_cues": ["red meat", "thick cut", "grill marks", "marbled"],
                "confidence_keywords": ["beef", "steak", "sirloin", "ribeye", "filet"]
            },
            "ground_beef": {
                "name": "Ground Beef",
                "category": "protein",
                "protein_per_100g": 25.0,
                "common_portions": {
                    "small": {"grams": 100, "description": "1/4 lb patty"},
                    "medium": {"grams": 150, "description": "1/3 lb serving"},
                    "large": {"grams": 200, "description": "1/2 lb serving"}
                },
                "preparation_modifiers": {
                    "grilled": 1.0,
                    "pan_fried": 0.95,
                    "baked": 1.0
                },
                "visual_cues": ["crumbled", "patty shape", "browned"],
                "confidence_keywords": ["ground beef", "hamburger", "meatball", "patty"]
            },
            "salmon": {
                "name": "Salmon",
                "category": "protein",
                "protein_per_100g": 25.0,
                "common_portions": {
                    "small": {"grams": 120, "description": "4oz fillet"},
                    "medium": {"grams": 150, "description": "5oz fillet"},
                    "large": {"grams": 180, "description": "6oz fillet"}
                },
                "preparation_modifiers": {
                    "grilled": 1.0,
                    "baked": 1.0,
                    "pan_seared": 1.0,
                    "smoked": 1.1  # Concentrated
                },
                "visual_cues": ["pink/orange flesh", "flaky", "skin on/off", "fillet shape"],
                "confidence_keywords": ["salmon", "fish", "fillet", "pink fish"]
            },
            "tuna": {
                "name": "Tuna",
                "category": "protein",
                "protein_per_100g": 30.0,
                "common_portions": {
                    "small": {"grams": 120, "description": "4oz serving"},
                    "medium": {"grams": 150, "description": "5oz serving"},
                    "large": {"grams": 180, "description": "6oz serving"}
                },
                "preparation_modifiers": {
                    "grilled": 1.0,
                    "seared": 1.0,
                    "canned_water": 0.9,
                    "canned_oil": 0.85
                },
                "visual_cues": ["dark red/pink", "meaty texture", "steak-like"],
                "confidence_keywords": ["tuna", "ahi", "yellowfin", "fish steak"]
            },
            
            # PROTEINS - PLANT BASED
            "tofu": {
                "name": "Tofu",
                "category": "protein",
                "protein_per_100g": 8.0,
                "common_portions": {
                    "small": {"grams": 80, "description": "Small cube (3oz)"},
                    "medium": {"grams": 120, "description": "Medium serving (4oz)"},
                    "large": {"grams": 150, "description": "Large serving (5oz)"}
                },
                "preparation_modifiers": {
                    "raw": 1.0,
                    "grilled": 1.0,
                    "fried": 1.0,
                    "baked": 1.0
                },
                "visual_cues": ["white/beige", "cube shape", "soft texture"],
                "confidence_keywords": ["tofu", "bean curd", "soy"]
            },
            "tempeh": {
                "name": "Tempeh",
                "category": "protein",
                "protein_per_100g": 19.0,
                "common_portions": {
                    "small": {"grams": 80, "description": "Small slice (3oz)"},
                    "medium": {"grams": 100, "description": "Medium slice (3.5oz)"},
                    "large": {"grams": 120, "description": "Large slice (4oz)"}
                },
                "preparation_modifiers": {
                    "steamed": 1.0,
                    "grilled": 1.0,
                    "fried": 1.0
                },
                "visual_cues": ["nutty texture", "rectangular block", "visible beans"],
                "confidence_keywords": ["tempeh", "fermented soy"]
            },
            
            # PROTEINS - DAIRY & EGGS
            "eggs": {
                "name": "Eggs",
                "category": "protein",
                "protein_per_100g": 13.0,
                "common_portions": {
                    "one_egg": {"grams": 50, "description": "1 large egg"},
                    "two_eggs": {"grams": 100, "description": "2 large eggs"},
                    "three_eggs": {"grams": 150, "description": "3 large eggs"}
                },
                "preparation_modifiers": {
                    "scrambled": 1.0,
                    "fried": 1.0,
                    "boiled": 1.0,
                    "poached": 1.0,
                    "omelet": 1.0
                },
                "visual_cues": ["yellow yolk", "white protein", "oval shape"],
                "confidence_keywords": ["egg", "scrambled", "fried", "boiled", "omelet"]
            },
            "greek_yogurt": {
                "name": "Greek Yogurt",
                "category": "protein",
                "protein_per_100g": 10.0,
                "common_portions": {
                    "small": {"grams": 170, "description": "6oz container"},
                    "medium": {"grams": 227, "description": "8oz serving"},
                    "large": {"grams": 340, "description": "12oz serving"}
                },
                "preparation_modifiers": {
                    "plain": 1.0,
                    "flavored": 0.9  # Usually has less protein per weight
                },
                "visual_cues": ["thick creamy texture", "white", "bowl or container"],
                "confidence_keywords": ["yogurt", "greek yogurt", "dairy"]
            },
            
            # CARBOHYDRATES
            "white_rice": {
                "name": "White Rice",
                "category": "carbohydrate",
                "protein_per_100g": 2.7,
                "common_portions": {
                    "small": {"grams": 80, "description": "1/3 cup cooked"},
                    "medium": {"grams": 150, "description": "2/3 cup cooked"},
                    "large": {"grams": 200, "description": "1 cup cooked"}
                },
                "preparation_modifiers": {
                    "steamed": 1.0,
                    "boiled": 1.0,
                    "fried": 1.0
                },
                "visual_cues": ["small white grains", "fluffy texture", "individual grains"],
                "confidence_keywords": ["rice", "white rice", "grain", "steamed rice"]
            },
            "brown_rice": {
                "name": "Brown Rice",
                "category": "carbohydrate",
                "protein_per_100g": 3.0,
                "common_portions": {
                    "small": {"grams": 80, "description": "1/3 cup cooked"},
                    "medium": {"grams": 150, "description": "2/3 cup cooked"},
                    "large": {"grams": 200, "description": "1 cup cooked"}
                },
                "preparation_modifiers": {
                    "steamed": 1.0,
                    "boiled": 1.0,
                    "fried": 1.0
                },
                "visual_cues": ["brown grains", "nuttier appearance", "individual grains"],
                "confidence_keywords": ["brown rice", "whole grain rice", "grain"]
            },
            "quinoa": {
                "name": "Quinoa",
                "category": "carbohydrate",
                "protein_per_100g": 4.4,
                "common_portions": {
                    "small": {"grams": 80, "description": "1/3 cup cooked"},
                    "medium": {"grams": 150, "description": "2/3 cup cooked"},
                    "large": {"grams": 200, "description": "1 cup cooked"}
                },
                "preparation_modifiers": {
                    "steamed": 1.0,
                    "boiled": 1.0
                },
                "visual_cues": ["small round grains", "light colored", "fluffy"],
                "confidence_keywords": ["quinoa", "grain", "superfood"]
            },
            
            # VEGETABLES
            "broccoli": {
                "name": "Broccoli",
                "category": "vegetable",
                "protein_per_100g": 2.8,
                "common_portions": {
                    "small": {"grams": 80, "description": "1/2 cup"},
                    "medium": {"grams": 150, "description": "1 cup"},
                    "large": {"grams": 200, "description": "1.5 cups"}
                },
                "preparation_modifiers": {
                    "steamed": 1.0,
                    "raw": 1.0,
                    "roasted": 1.0,
                    "stir_fried": 1.0
                },
                "visual_cues": ["green florets", "tree-like structure", "stems"],
                "confidence_keywords": ["broccoli", "green vegetable", "florets"]
            },
            "spinach": {
                "name": "Spinach",
                "category": "vegetable",
                "protein_per_100g": 2.9,
                "common_portions": {
                    "small": {"grams": 30, "description": "1 cup raw"},
                    "medium": {"grams": 60, "description": "2 cups raw"},
                    "large": {"grams": 100, "description": "Large salad portion"}
                },
                "preparation_modifiers": {
                    "raw": 1.0,
                    "sauteed": 1.0,
                    "steamed": 1.0
                },
                "visual_cues": ["dark green leaves", "leafy", "wilted when cooked"],
                "confidence_keywords": ["spinach", "leafy greens", "salad"]
            },
            
            # LEGUMES
            "black_beans": {
                "name": "Black Beans",
                "category": "legume",
                "protein_per_100g": 9.0,
                "common_portions": {
                    "small": {"grams": 80, "description": "1/3 cup"},
                    "medium": {"grams": 120, "description": "1/2 cup"},
                    "large": {"grams": 180, "description": "3/4 cup"}
                },
                "preparation_modifiers": {
                    "cooked": 1.0,
                    "canned": 0.95
                },
                "visual_cues": ["small black oval beans", "individual beans visible"],
                "confidence_keywords": ["black beans", "beans", "legumes"]
            },
            "chickpeas": {
                "name": "Chickpeas",
                "category": "legume",
                "protein_per_100g": 8.0,
                "common_portions": {
                    "small": {"grams": 80, "description": "1/3 cup"},
                    "medium": {"grams": 120, "description": "1/2 cup"},
                    "large": {"grams": 180, "description": "3/4 cup"}
                },
                "preparation_modifiers": {
                    "cooked": 1.0,
                    "canned": 0.95,
                    "roasted": 1.1
                },
                "visual_cues": ["round beige beans", "bumpy texture"],
                "confidence_keywords": ["chickpeas", "garbanzo beans", "hummus base"]
            }
        }
    
    def search_food(self, query: str) -> List[Tuple[str, float]]:
        """Search for foods by name with confidence scoring.
        
        Performs fuzzy matching on food names and keywords to find
        the best matches for AI-identified foods.
        
        Args:
            query: Food name or description to search for
            
        Returns:
            List of tuples containing (food_id, confidence_score) sorted by confidence
        """
        query_lower = query.lower()
        matches = []
        
        # Special handling for common words that should prioritize specific foods
        if "egg" in query_lower and not any(meat in query_lower for meat in ["chicken breast", "beef", "pork"]):
            # If query contains "egg" and no conflicting meat terms, prioritize eggs
            for food_id, food_data in self.foods.items():
                if food_id == "eggs":
                    matches.append((food_id, 0.95))  # High priority for eggs
                    break
        
        for food_id, food_data in self.foods.items():
            confidence = 0.0
            
            # Exact name match
            if query_lower == food_data["name"].lower():
                confidence = 1.0
            # Partial name match
            elif query_lower in food_data["name"].lower():
                confidence = 0.8
            # Keyword match
            else:
                for keyword in food_data["confidence_keywords"]:
                    # Exact keyword match gets higher score
                    if keyword.lower() == query_lower:
                        confidence = max(confidence, 0.9)
                    # Word boundary matches
                    elif f" {keyword.lower()} " in f" {query_lower} " or query_lower.endswith(f" {keyword.lower()}") or query_lower.startswith(f"{keyword.lower()} "):
                        confidence = max(confidence, 0.8)
                    # Partial keyword match
                    elif keyword.lower() in query_lower:
                        confidence = max(confidence, 0.6)
                    elif query_lower in keyword.lower():
                        confidence = max(confidence, 0.7)
            
            if confidence > 0:
                matches.append((food_id, confidence))
        
        # Sort by confidence, highest first
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def get_food_info(self, food_id: str) -> Optional[Dict[str, Any]]:
        """Get complete food information.
        
        Args:
            food_id: Unique identifier for the food item
            
        Returns:
            Dictionary containing complete food data or None if not found
        """
        return self.foods.get(food_id)
    
    def calculate_protein(self, food_id: str, portion_size: str, preparation: str = "default") -> Optional[Dict[str, Any]]:
        """Calculate protein content for specific portion and preparation.
        
        Args:
            food_id: Unique identifier for the food item
            portion_size: Size category (small/medium/large)
            preparation: Cooking method (grilled/baked/fried/etc.)
            
        Returns:
            Dictionary containing protein calculation results or None if invalid
        """
        food_data = self.get_food_info(food_id)
        if not food_data:
            return None
        
        # Get portion weight
        if portion_size in food_data["common_portions"]:
            weight_grams = food_data["common_portions"][portion_size]["grams"]
            portion_description = food_data["common_portions"][portion_size]["description"]
        else:
            return None
        
        # Get preparation modifier
        prep_modifier = 1.0
        if preparation in food_data["preparation_modifiers"]:
            prep_modifier = food_data["preparation_modifiers"][preparation]
        
        # Calculate protein
        base_protein = food_data["protein_per_100g"]
        total_protein = (base_protein * weight_grams / 100) * prep_modifier
        
        return {
            "food_name": food_data["name"],
            "portion_description": portion_description,
            "weight_grams": weight_grams,
            "preparation": preparation,
            "protein_grams": round(total_protein, 1),
            "protein_per_100g": base_protein
        }
    
    def get_common_portions(self, food_id: str) -> Optional[Dict[str, Dict[str, Any]]]:
        """Get common portion sizes for a food.
        
        Args:
            food_id: Unique identifier for the food item
            
        Returns:
            Dictionary of portion sizes with weights and descriptions or None if not found
        """
        food_data = self.get_food_info(food_id)
        if food_data:
            return food_data["common_portions"]
        return None
    
    def get_visual_cues(self, food_id: str) -> Optional[List[str]]:
        """Get visual identification cues for a food.
        
        Args:
            food_id: Unique identifier for the food item
            
        Returns:
            List of visual cues for identification or None if not found
        """
        food_data = self.get_food_info(food_id)
        if food_data:
            return food_data["visual_cues"]
        return None
    
    def suggest_similar_foods(self, category: str) -> List[str]:
        """Get foods in the same category.
        
        Args:
            category: Food category (protein/carbohydrate/vegetable/legume)
            
        Returns:
            List of food IDs in the specified category
        """
        similar = []
        for food_id, food_data in self.foods.items():
            if food_data["category"] == category:
                similar.append(food_id)
        return similar

# Global nutrition database instance
nutrition_db = NutritionDatabase()