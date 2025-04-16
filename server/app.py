from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import dotenv
import openai
import googlemaps
import requests
from datetime import datetime

# Load environment variables
dotenv.load_dotenv(override=True)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get API keys from environment variables
openai_api_key = os.environ.get("OPENAI_API_KEY")
google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

# Initialize clients
client = None
gmaps = None
maps_api_available = False

# Sample restaurant data for fallback
SAMPLE_RESTAURANTS = [
    {
        "name": "Healthy Bites",
        "formatted_address": "123 Main St, Anytown, CA 90210",
        "rating": 4.5,
        "price_level": 2,
        "types": ["restaurant", "food", "health"],
        "opening_hours": {"open_now": True}
    },
    {
        "name": "Green Garden Cafe",
        "formatted_address": "456 Oak Ave, Anytown, CA 90210",
        "rating": 4.2,
        "price_level": 1,
        "types": ["restaurant", "food", "vegetarian"],
        "opening_hours": {"open_now": True}
    },
    {
        "name": "Protein Powerhouse",
        "formatted_address": "789 Pine St, Anytown, CA 90210",
        "rating": 4.7,
        "price_level": 3,
        "types": ["restaurant", "food", "gym"],
        "opening_hours": {"open_now": True}
    },
    {
        "name": "Mediterranean Delight",
        "formatted_address": "321 Elm St, Anytown, CA 90210",
        "rating": 4.3,
        "price_level": 2,
        "types": ["restaurant", "food", "mediterranean"],
        "opening_hours": {"open_now": True}
    },
    {
        "name": "Asian Fusion",
        "formatted_address": "654 Maple Dr, Anytown, CA 90210",
        "rating": 4.6,
        "price_level": 2,
        "types": ["restaurant", "food", "asian"],
        "opening_hours": {"open_now": True}
    }
]

# Initialize OpenAI client
if openai_api_key and openai_api_key != "your_openai_api_key_here":
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        client.models.list()
        print("OpenAI API initialized successfully!")
    except Exception as e:
        print(f"Error initializing OpenAI client: {str(e)}")

# Initialize Google Maps client
try:
    if google_maps_api_key:
        # Test the API key with a simple Places API request
        test_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-33.8670522,151.1957362&radius=500&type=restaurant&key={google_maps_api_key}"
        test_response = requests.get(test_url)
        test_data = test_response.json()
        
        if test_data.get('status') == 'OK':
            gmaps = googlemaps.Client(key=google_maps_api_key)
            maps_api_available = True
            print("Google Maps API initialized successfully!")
        else:
            print(f"Google Maps API test failed. Status: {test_data.get('status')}, Error: {test_data.get('error_message', 'No error message')}")
    else:
        print("Google Maps API key not found in environment variables")
except Exception as e:
    print(f"Error initializing Google Maps client: {str(e)}")

def get_restaurants_by_zipcode(zipcode, radius=5000):
    """Get restaurants using Google Places API by zipcode"""
    if not maps_api_available:
        print("Google Maps API is not available. Using sample restaurant data instead.")
        return SAMPLE_RESTAURANTS
    
    try:
        # First, geocode the zipcode to get coordinates
        geocode_result = gmaps.geocode(zipcode)
        if not geocode_result:
            print(f"Could not find location for zipcode: {zipcode}")
            # Use a fallback location for testing
            print("Using a fallback location (San Francisco) for testing purposes.")
            location = {"lat": 37.7749, "lng": -122.4194}
        else:
            location = geocode_result[0]['geometry']['location']
        
        # Get nearby restaurants
        places_result = gmaps.places_nearby(
            location=location,
            radius=radius,
            type='restaurant',
            open_now=True
        )
        
        if not places_result.get('results'):
            print(f"No restaurants found near {zipcode}. Using a fallback location.")
            # Use a fallback location with known restaurants
            fallback_location = {"lat": 37.7749, "lng": -122.4194}
            places_result = gmaps.places_nearby(
                location=fallback_location,
                radius=radius,
                type='restaurant',
                open_now=True
            )
        
        # Get detailed information for each restaurant
        restaurants = []
        for place in places_result.get('results', []):
            place_id = place['place_id']
            # Use valid fields for the Places API
            details = gmaps.place(place_id, fields=['name', 'formatted_address', 'rating', 'price_level', 'opening_hours', 'business_status', 'user_ratings_total'])
            if details.get('result'):
                restaurants.append(details['result'])
        
        if not restaurants:
            print("No restaurants found. Using sample data instead.")
            return SAMPLE_RESTAURANTS
            
        return restaurants
    except Exception as e:
        error_message = str(e)
        print(f"Error fetching restaurants: {error_message}")
        
        # Fallback to sample data
        print("Using sample restaurant data instead.")
        return SAMPLE_RESTAURANTS

def create_rag_prompt(restaurants, preferences):
    """Create a RAG prompt with restaurant data and user preferences"""
    # Limit the number of restaurants to avoid exceeding token limit
    limited_restaurants = restaurants[:8]  # Increased from 5 to 8
    
    # Create a more concise restaurant context
    restaurant_context = []
    for restaurant in limited_restaurants:
        restaurant_info = {
            "name": restaurant.get("name", "Unknown"),
            "formatted_address": restaurant.get("formatted_address", "Address not available"),
            "rating": restaurant.get("rating", 0),
            "price_level": restaurant.get("price_level", 0),
            "types": restaurant.get("types", []),
            "opening_hours": restaurant.get("opening_hours", {"open_now": False})
        }
        restaurant_context.append(restaurant_info)
    
    restaurant_json = json.dumps(restaurant_context, separators=(',', ':'))
    
    # Get user's price range
    min_price = preferences.get('price_range', [10, 25])[0]
    max_price = preferences.get('price_range', [10, 25])[1]
    
    prompt = f"""Based on the following restaurant data and user preferences, provide MULTIPLE diverse meal recommendations that match their dietary goals. Aim to provide at least 3-5 different recommendations from different restaurants.

Restaurant Data:
{restaurant_json}

User Preferences:
{json.dumps(preferences, separators=(',', ':'))}

CRITICAL REQUIREMENTS:
1. Provide AT LEAST 3 different recommendations that match these targets:
   - Total calories: {preferences.get('calorie_count')} calories (±30%)
   - Protein: {preferences.get('macronutrients', {}).get('protein_grams')} grams (±40%)
   - Carbs: {preferences.get('macronutrients', {}).get('carbs_grams')} grams (±40%)
   - Fats: {preferences.get('macronutrients', {}).get('fats_grams')} grams (±40%)
   - Price range: ${min_price} - ${max_price}

2. For EACH restaurant, suggest multiple ways to meet the targets:
   - Provide different combinations of items
   - Example: "Grilled Chicken + Rice + Vegetables" or "Burger + Side Salad + Sweet Potato"
   - Include specific portion sizes and modifications
   - Suggest different options for different preferences

3. Focus on practical combinations that will help reach ALL macro targets:
   - If carbs are low, suggest adding bread, rice, or potato sides
   - If protein is low, suggest adding grilled chicken or protein shake
   - If fats are low, suggest adding dressings or avocado

4. Make recommendations DIVERSE:
   - Include different cuisines
   - Mix of lighter and heartier options
   - Various protein sources (meat, fish, vegetarian)
   - Different meal types (bowls, sandwiches, platters)

Please provide recommendations in this exact JSON format:
{{
    "recommendations": [
        {{
            "restaurant_name": "Restaurant Name",
            "address": "Full Address",
            "dish_name": "Main Dish + Side Items",
            "calories": 1000,
            "macronutrients": {{
                "protein": 75,
                "carbs": 100,
                "fats": 33
            }},
            "reason": "Explanation of how this meets the targets",
            "price_range": 15
        }},
        {{
            "restaurant_name": "Different Restaurant",
            "address": "Different Address",
            "dish_name": "Different Combination",
            "calories": 950,
            "macronutrients": {{
                "protein": 70,
                "carbs": 95,
                "fats": 35
            }},
            "reason": "Different explanation",
            "price_range": 18
        }}
    ]
}}

Note: 
- The price_range should be a single numeric value representing the estimated total cost in dollars
- Provide at least 3 different recommendations
- Each recommendation should be from a different restaurant if possible
- Make sure combinations are practical and available at the restaurant
- Include specific portion sizes and modifications needed"""
    
    return prompt

def validate_recommendations(recommendations_data, preferences):
    """Validate recommendations and add information about missing targets"""
    recommendations = recommendations_data.get('recommendations', [])
    if not recommendations:
        return []
        
    target_calories = preferences.get('calorie_count')
    target_macros = preferences.get('macronutrients', {})
    target_protein = target_macros.get('protein_grams')
    target_carbs = target_macros.get('carbs_grams')
    target_fats = target_macros.get('fats_grams')
    price_range = preferences.get('price_range', [10, 25])
    min_price, max_price = price_range[0], price_range[1]
    
    def is_within_range(value, target, target_type=None):
        if not target or not value:
            return True
        try:
            value = float(value)
            target = float(target)
            
            if target_type == 'macro':
                lower_bound = target * 0.55
                upper_bound = target * 1.45
            elif target_type == 'price':
                # Price must be within the specified range
                return min_price <= value <= max_price
            else:  # calories
                lower_bound = target * 0.85  # Stricter bounds for calories
                upper_bound = target * 1.15
            
            return lower_bound <= value <= upper_bound
        except (TypeError, ValueError):
            return False
    
    def get_missing_targets(calories, protein, carbs, fats, price):
        missing = []
        
        # Check calories - required target
        if not is_within_range(calories, target_calories):
            if calories < float(target_calories) * 0.85:
                missing.append(f"Low calories: {calories} (target: {target_calories})")
            else:
                missing.append(f"High calories: {calories} (target: {target_calories})")
        
        # Check price - required target
        if not is_within_range(price, None, 'price'):
            if price < min_price:
                missing.append(f"Price too low: ${price} (min: ${min_price})")
            else:
                missing.append(f"Price too high: ${price} (max: ${max_price})")
        
        # Check macros - optional targets
        if not is_within_range(protein, target_protein, 'macro'):
            if protein < float(target_protein) * 0.55:
                missing.append(f"Low protein: {protein}g (target: {target_protein}g)")
            else:
                missing.append(f"High protein: {protein}g (target: {target_protein}g)")
                
        if not is_within_range(carbs, target_carbs, 'macro'):
            if carbs < float(target_carbs) * 0.55:
                missing.append(f"Low carbs: {carbs}g (target: {target_carbs}g)")
            else:
                missing.append(f"High carbs: {carbs}g (target: {target_carbs}g)")
                
        if not is_within_range(fats, target_fats, 'macro'):
            if fats < float(target_fats) * 0.55:
                missing.append(f"Low fats: {fats}g (target: {target_fats}g)")
            else:
                missing.append(f"High fats: {fats}g (target: {target_fats}g)")
        
        return missing
    
    enhanced_recommendations = []
    seen_restaurants = set()
    
    for rec in recommendations:
        try:
            calories = rec.get('calories', 0)
            price = rec.get('price_range', 0)
            macros = rec.get('macronutrients', {})
            protein = macros.get('protein', 0)
            carbs = macros.get('carbs', 0)
            fats = macros.get('fats', 0)
            restaurant_name = rec.get('restaurant_name', '')
            
            # Get list of missing targets
            missing_targets = get_missing_targets(calories, protein, carbs, fats, price)
            
            # Skip recommendations that don't meet calorie or price targets
            if any(("calories" in target.lower() or "price" in target.lower()) for target in missing_targets):
                print(f"Skipping {restaurant_name} due to missing required targets: calories or price")
                continue
            
            # Add missing targets to the recommendation
            enhanced_rec = {
                **rec,
                "missing_targets": missing_targets,
                "matches_all_targets": len(missing_targets) == 0
            }
            
            # Add suggestions for missing targets
            if missing_targets:
                suggestions = []
                if any("Low carbs" in m for m in missing_targets):
                    suggestions.append("Add a side of rice, bread, or potatoes to increase carbs")
                if any("Low protein" in m for m in missing_targets):
                    suggestions.append("Add grilled chicken or a protein shake to increase protein")
                if any("Low fats" in m for m in missing_targets):
                    suggestions.append("Add avocado, dressing, or nuts to increase fats")
                enhanced_rec["suggestions"] = suggestions
            
            # Only add if we haven't seen this restaurant or if it's a particularly good match
            if restaurant_name not in seen_restaurants or len(missing_targets) <= 1:
                enhanced_recommendations.append(enhanced_rec)
                seen_restaurants.add(restaurant_name)
                
            print(f"Processed {restaurant_name}: {len(missing_targets)} missing targets")
            
        except Exception as e:
            print(f"Error processing recommendation: {str(e)}")
            continue
    
    # Sort recommendations: perfect matches first, then by number of missing targets
    enhanced_recommendations.sort(key=lambda x: (not x["matches_all_targets"], len(x["missing_targets"])))
    
    return enhanced_recommendations

# API Routes
@app.route('/api/status', methods=['GET'])
def api_status():
    """Check the status of the API and its dependencies"""
    return jsonify({
        'status': 'ok',
        'openai_api': 'available' if client else 'unavailable',
        'google_maps_api': 'available' if maps_api_available else 'unavailable'
    })

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    """Get restaurants by ZIP code"""
    zipcode = request.args.get('zipcode', '46556')
    radius = int(request.args.get('radius', 5000))
    
    restaurants = get_restaurants_by_zipcode(zipcode, radius)
    return jsonify(restaurants)

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get restaurant recommendations based on user preferences"""
    try:
        print("\n=== New Recommendation Request ===")
        print("Request received at:", datetime.now())
        
        if not request.is_json:
            print("Error: Request is not JSON")
            return jsonify({'error': 'Request must be JSON'}), 400
            
        if not client:
            print("Error: OpenAI API is not available")
            return jsonify({'error': 'OpenAI API is not available'}), 503
        
        data = request.json
        print("Received data:", json.dumps(data, indent=2))
        
        if not data or 'preferences' not in data:
            print("Error: Missing preferences in request")
            return jsonify({'error': 'Missing preferences'}), 400
            
        preferences = data.get('preferences', {})
        zipcode = preferences.get('zipcode', '')
        
        if not zipcode:
            print("Error: Missing or empty zipcode")
            return jsonify({'error': 'ZIP code is required'}), 400
            
        print(f"Processing preferences for zipcode: {zipcode}")
        
        # Get restaurants
        restaurants = get_restaurants_by_zipcode(zipcode)
        print(f"Found {len(restaurants)} restaurants")
        
        # Create RAG prompt with restaurant data
        rag_prompt = create_rag_prompt(restaurants, preferences)
        print("Generated RAG prompt")
        
        try:
            print("Calling OpenAI API...")
            # Make OpenAI API call
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI dining assistant that provides restaurant recommendations in JSON format. Always respond with valid JSON."},
                    {"role": "user", "content": rag_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Get the response text
            response_text = completion.choices[0].message.content
            print("OpenAI API response received")
            print("Response:", response_text)
            
            try:
                # Parse the response as JSON and validate
                recommendations_data = json.loads(response_text)
                print("Successfully parsed OpenAI response as JSON")
                
                valid_recommendations = validate_recommendations(recommendations_data, preferences)
                print(f"Found {len(valid_recommendations)} valid recommendations")
                
                if not valid_recommendations:
                    print("No valid recommendations found after validation")
                    return jsonify({
                        "error": "No recommendations found that match your dietary goals",
                        "recommendations": []
                    }), 200
                
                print("Returning recommendations to client")
                return jsonify({"recommendations": valid_recommendations})
                
            except json.JSONDecodeError as e:
                print(f"Error parsing OpenAI response as JSON: {e}")
                print("Response text:", response_text)
                return jsonify({
                    "error": "Failed to parse recommendations",
                    "recommendations": []
                }), 200
                
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return jsonify({
                'error': f'Error generating recommendations: {str(e)}',
                'recommendations': []
            }), 200
            
    except Exception as e:
        print(f"Error in recommendations endpoint: {e}")
        return jsonify({
            'error': f'Server error: {str(e)}',
            'recommendations': []
        }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 