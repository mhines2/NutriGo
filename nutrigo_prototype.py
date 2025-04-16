"""
NutriGo - AI-powered dining assistant that helps users discover restaurants
aligned with their dietary goals and preferences.
"""

import os
import json
import dotenv
import openai
import streamlit as st
import googlemaps
from datetime import datetime
import requests
import time

# Set Streamlit page config first (must be the first Streamlit command)
st.set_page_config(page_title="NutriGo - AI Dining Assistant", layout="wide")

# Initialize session state for tracking API initialization messages
if 'api_messages_shown' not in st.session_state:
    st.session_state.api_messages_shown = False

# Load environment variables from .env file
dotenv.load_dotenv(override=True)

# Check if API keys are loaded
openai_api_key = os.environ.get("OPENAI_API_KEY")
google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

# Initialize clients as None
client = None
gmaps = None
maps_api_available = False

# Check if API keys are valid
if not openai_api_key or openai_api_key == "your_openai_api_key_here":
    st.error("OpenAI API key not found. Please add your API key to the .env file.")
    st.stop()
else:
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        client.models.list()
        # Show success message only once at the beginning
        if not st.session_state.api_messages_shown:
            st.success("OpenAI API initialized successfully!")
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {str(e)}")
        st.stop()

# Initialize Google Maps client
try:
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not google_maps_api_key:
        st.error("Google Maps API key not found in environment variables")
        st.stop()
    
    # Test the API key with a simple Places API request
    test_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-33.8670522,151.1957362&radius=500&type=restaurant&key={google_maps_api_key}"
    test_response = requests.get(test_url)
    test_data = test_response.json()
    
    if test_data.get('status') != 'OK':
        st.error(f"Google Maps API test failed. Status: {test_data.get('status')}, Error: {test_data.get('error_message', 'No error message')}")
        st.stop()
    
    gmaps = googlemaps.Client(key=google_maps_api_key)
    maps_api_available = True  # Set the flag to True when API is successfully initialized
    
    # Show success message only once at the beginning
    if not st.session_state.api_messages_shown:
        st.success("Google Maps API initialized successfully!")
        # Mark that we've shown the messages
        st.session_state.api_messages_shown = True
    
except Exception as e:
    st.error(f"Error initializing Google Maps client: {str(e)}")
    st.error("Using sample restaurant data instead. For a full experience, please configure the Google Maps API properly.")
    # Fallback to sample data
    sample_restaurants = [
        {
            "name": "The Local Bistro",
            "rating": 4.5,
            "price_level": 2,
            "address": "123 Main St",
            "cuisine": "American",
            "location": {"lat": 37.7749, "lng": -122.4194}
        },
        {
            "name": "Sushi Master",
            "rating": 4.8,
            "price_level": 3,
            "address": "456 Market St",
            "cuisine": "Japanese",
            "location": {"lat": 37.7749, "lng": -122.4194}
        }
    ]
    restaurants = sample_restaurants

# Sample restaurant data for fallback mode
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

def get_restaurants_by_zipcode(zipcode, radius=5000):
    """Get restaurants using Google Places API by zipcode"""
    if not maps_api_available:
        st.warning("""
        Google Maps API is not available. Using sample restaurant data instead.
        For a full experience, please configure the Google Maps API properly.
        """)
        return SAMPLE_RESTAURANTS
    
    try:
        # First, geocode the zipcode to get coordinates
        geocode_result = gmaps.geocode(zipcode)
        if not geocode_result:
            st.error(f"Could not find location for zipcode: {zipcode}")
            # Use a fallback location for testing
            st.info("Using a fallback location (San Francisco) for testing purposes.")
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
            st.warning(f"No restaurants found near {zipcode}. Using a fallback location.")
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
            st.warning("No restaurants found. Using sample data instead.")
            return SAMPLE_RESTAURANTS
            
        return restaurants
    except Exception as e:
        error_message = str(e)
        if "REQUEST_DENIED" in error_message:
            # Try to get more detailed error information
            try:
                test_url = f"https://maps.googleapis.com/maps/api/geocode/json?address=90210&key={google_maps_api_key}"
                response = requests.get(test_url)
                error_data = response.json()
                
                if 'error_message' in error_data:
                    detailed_error = error_data['error_message']
                    
                    # Check if the error is related to IP restrictions
                    if "IP" in detailed_error and "authorized" in detailed_error:
                        # Extract the IP address from the error message
                        import re
                        ip_match = re.search(r'IP address ([0-9a-fA-F:\.]+)', detailed_error)
                        ip_address = ip_match.group(1) if ip_match else "unknown"
                        
                        st.error(f"""
                        Google Maps API request was denied due to IP restrictions.
                        
                        Error: {detailed_error}
                        
                        Your current IP address ({ip_address}) is not authorized to use this API key.
                        
                        To fix this:
                        1. Go to Google Cloud Console > APIs & Services > Credentials
                        2. Find your API key and click on it to edit
                        3. Under "Application restrictions", make sure "IP addresses" is selected
                        4. Add both your IPv4 and IPv6 addresses:
                           - IPv4: {requests.get('https://api.ipify.org').text}
                           - IPv6: {ip_address}
                        5. Click "Save"
                        
                        Alternatively, for development purposes, you could:
                        1. Remove IP restrictions entirely (not recommended for production)
                        2. Use a broader CIDR range that includes both your IPv4 and IPv6 addresses
                        
                        For help, visit: https://developers.google.com/maps/documentation/places/web-service/overview
                        """)
                    else:
                        st.error(f"""
                        Google Maps API request was denied with detailed error:
                        
                        {detailed_error}
                        
                        Please check your Google Cloud Console settings and ensure:
                        1. Places API is enabled
                        2. Geocoding API is enabled
                        3. Your API key has access to these APIs
                        4. Billing is enabled for your project
                        
                        For help, visit: https://developers.google.com/maps/documentation/places/web-service/overview
                        """)
                else:
                    st.error(f"""
                    Google Maps API request was denied. Error details: {error_data}
                    
                    Please check your Google Cloud Console settings and ensure:
                    1. Places API is enabled
                    2. Geocoding API is enabled
                    3. Your API key has access to these APIs
                    4. Billing is enabled for your project
                    
                    For help, visit: https://developers.google.com/maps/documentation/places/web-service/overview
                    """)
            except Exception as inner_e:
                st.error(f"""
                Google Maps API request was denied. This usually means:
                1. The API key is not properly configured
                2. The necessary APIs are not enabled
                3. The API key doesn't have the required permissions
                
                Please check your Google Cloud Console settings and ensure:
                1. Places API is enabled
                2. Geocoding API is enabled
                3. Your API key has access to these APIs
                4. Billing is enabled for your project
                
                For help, visit: https://developers.google.com/maps/documentation/places/web-service/overview
                
                Original error: {error_message}
                Additional error when trying to get details: {str(inner_e)}
                """)
        else:
            st.error(f"Error fetching restaurants: {error_message}")
        
        # Fallback to sample data
        st.warning("Using sample restaurant data instead.")
        return SAMPLE_RESTAURANTS

def create_rag_prompt(restaurants, preferences):
    """Create a RAG prompt with restaurant data and user preferences"""
    # Limit the number of restaurants to avoid exceeding token limit
    # Keep only the first 5 restaurants or fewer if there are less
    limited_restaurants = restaurants[:5]
    
    # Create a more concise restaurant context
    restaurant_context = []
    for restaurant in limited_restaurants:
        # Extract only the essential information
        restaurant_info = {
            "name": restaurant.get("name", "Unknown"),
            "formatted_address": restaurant.get("formatted_address", "Address not available"),
            "rating": restaurant.get("rating", 0),
            "price_level": restaurant.get("price_level", 0),
            "types": restaurant.get("types", []),
            "opening_hours": restaurant.get("opening_hours", {"open_now": False})
        }
        restaurant_context.append(restaurant_info)
    
    # Convert to JSON with minimal whitespace
    restaurant_json = json.dumps(restaurant_context, separators=(',', ':'))
    
    # Create a more concise prompt
    return f"""Based on the following restaurant data and user preferences, recommend specific meals that match their dietary goals.
    
Restaurant Data:
{restaurant_json}

User Preferences:
{json.dumps(preferences, separators=(',', ':'))}

Please provide recommendations in the following JSON format:
{{
    "recommendations": [
        {{
            "restaurant_name": "string",
            "address": "string",
            "dish_name": "string",
            "calories": number,
            "macronutrients": {{
                "protein": number,
                "carbs": number,
                "fats": number
            }},
            "reason": "string",
            "price_range": "string"
        }}
    ]
}}

Only include restaurants from the provided data that match the user's preferences."""

def main():
    st.title("NutriGo 🍽️🤖")
    st.subheader("Your AI-powered dining companion")
    
    if not client:
        st.error("OpenAI client is not properly initialized. Please check your API key and try again.")
        st.stop()
    
    # Sidebar for user preferences
    st.sidebar.header("Your Dietary Preferences")
    
    # Nutritional preferences section
    st.sidebar.subheader("Nutritional Preferences")
    calorie_count = st.sidebar.number_input(
        "Target Calories per Meal",
        min_value=0,
        max_value=2000,
        value=0,
        step=50
    )
    
    def calculate_default_macros(calories):
        if calories == 0:
            return 30, 50, 20
        
        protein_calories = calories * 0.30
        carbs_calories = calories * 0.45
        fats_calories = calories * 0.25
        
        protein_grams = round(protein_calories / 4)
        carbs_grams = round(carbs_calories / 4)
        fats_grams = round(fats_calories / 9)
        
        return protein_grams, carbs_grams, fats_grams
    
    default_protein, default_carbs, default_fats = calculate_default_macros(calorie_count)
    
    st.sidebar.write("Macronutrient Targets")
    protein_grams = st.sidebar.number_input(
        "Protein (g)", 
        min_value=0, 
        max_value=200, 
        value=default_protein, 
        step=5
    )
    carbs_grams = st.sidebar.number_input(
        "Carbs (g)", 
        min_value=0, 
        max_value=300, 
        value=default_carbs, 
        step=5
    )
    fats_grams = st.sidebar.number_input(
        "Fats (g)", 
        min_value=0, 
        max_value=100, 
        value=default_fats, 
        step=5
    )
    
    allergies = st.sidebar.text_input("Any Food Allergies? (comma-separated)", "None")
    
    st.sidebar.subheader("Location & Cuisine")
    zipcode = st.sidebar.text_input("Your ZIP code", "46556")  # Default ZIP code
    
    cuisine_preferences = st.sidebar.multiselect(
        "Preferred cuisines",
        ["Italian", "Mexican", "Chinese", "Japanese", "Indian", "Thai", "Mediterranean", "American", "Other"],
        default=[]
    )
    
    price_range = st.sidebar.slider(
        "Price range ($ per person)",
        min_value=1,
        max_value=50,
        value=(1, 50),
        step=1
    )
    
    # Auto-generate recommendations when the app starts or when the user clicks the button
    if 'recommendations_generated' not in st.session_state:
        st.session_state.recommendations_generated = False
    
    if st.sidebar.button("Find Meals"):
        if not zipcode:
            st.error("Please enter a ZIP code")
            return
            
        preferences = {
            "allergies": [allergy.strip() for allergy in allergies.split(",") if allergy.strip()],
            "calorie_count": calorie_count,
            "macronutrients": {
                "protein_grams": protein_grams,
                "carbs_grams": carbs_grams,
                "fats_grams": fats_grams
            },
            "zipcode": zipcode,
            "cuisine_preferences": cuisine_preferences,
            "price_range": price_range
        }
        
        st.session_state.preferences = preferences
        
        with st.spinner("Finding restaurants in your area..."):
            restaurants = get_restaurants_by_zipcode(zipcode)
            if not restaurants:
                st.error("No restaurants found in your area. Please try a different ZIP code.")
                return
                
            # Store the full list of restaurants
            st.session_state.restaurants = restaurants
            
            # Create RAG prompt with restaurant data
            rag_prompt = create_rag_prompt(restaurants, preferences)
            
            try:
                # Estimate token count (rough approximation)
                estimated_tokens = len(rag_prompt) // 4
                if estimated_tokens > 7000:  # Leave some buffer for the model's response
                    st.warning(f"Warning: The prompt is very large (approximately {estimated_tokens} tokens). This might exceed the model's context length. Using a smaller subset of restaurants.")
                    # Try again with fewer restaurants
                    rag_prompt = create_rag_prompt(restaurants[:3], preferences)
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI dining assistant that provides restaurant recommendations in JSON format. Always respond with valid JSON."},
                        {"role": "user", "content": rag_prompt}
                    ]
                )
                
                # Try to parse the response as JSON
                try:
                    recommendations = json.loads(response.choices[0].message.content)
                except json.JSONDecodeError:
                    # If parsing fails, try to extract JSON from the text
                    import re
                    json_match = re.search(r'\{[\s\S]*\}', response.choices[0].message.content)
                    if json_match:
                        try:
                            recommendations = json.loads(json_match.group(0))
                        except:
                            st.error("Could not parse recommendations as JSON. Displaying raw response.")
                            st.write(response.choices[0].message.content)
                            return
                    else:
                        st.error("Could not find JSON in the response. Displaying raw response.")
                        st.write(response.choices[0].message.content)
                        return
                
                st.session_state.recommendations = recommendations
                st.session_state.recommendations_generated = True
                
                # Display recommendations in a structured format
                st.subheader("Recommended Restaurants")
                for rec in recommendations.get("recommendations", []):
                    # Handle missing keys with default values
                    restaurant_name = rec.get('restaurant_name', 'Unknown Restaurant')
                    dish_name = rec.get('dish_name', 'No specific dish recommended')
                    
                    with st.expander(f"{restaurant_name} - {dish_name}"):
                        st.write(f"**Address:** {rec.get('address', 'Address not available')}")
                        st.write(f"**Dish:** {dish_name}")
                        st.write(f"**Calories:** {rec.get('calories', 'Not specified')}")
                        
                        # Handle nested macronutrients
                        macronutrients = rec.get('macronutrients', {})
                        st.write("**Macronutrients:**")
                        st.write(f"- Protein: {macronutrients.get('protein', 'Not specified')}g")
                        st.write(f"- Carbs: {macronutrients.get('carbs', 'Not specified')}g")
                        st.write(f"- Fats: {macronutrients.get('fats', 'Not specified')}g")
                        
                        st.write(f"**Price Range:** {rec.get('price_range', 'Not specified')}")
                        st.write(f"**Why this matches your preferences:** {rec.get('reason', 'No reason provided')}")
                
            except Exception as e:
                error_message = str(e)
                if "context_length_exceeded" in error_message:
                    st.error(f"""
                    Error: The prompt is too long for the OpenAI model to process.
                    
                    This happens when there are too many restaurants or too much data in the prompt.
                    The application is already trying to limit the data, but it seems we still have too much.
                    
                    Please try:
                    1. Using a more specific ZIP code to get fewer restaurants
                    2. Refreshing the page to try again
                    3. If the problem persists, contact support
                    """)
                else:
                    st.error(f"Error generating recommendations: {error_message}")
                st.stop()
    elif 'recommendations' in st.session_state:
        # Display previously generated recommendations
        st.subheader("Recommended Restaurants")
        for rec in st.session_state.recommendations.get("recommendations", []):
            # Handle missing keys with default values
            restaurant_name = rec.get('restaurant_name', 'Unknown Restaurant')
            dish_name = rec.get('dish_name', 'No specific dish recommended')
            
            with st.expander(f"{restaurant_name} - {dish_name}"):
                st.write(f"**Address:** {rec.get('address', 'Address not available')}")
                st.write(f"**Dish:** {dish_name}")
                st.write(f"**Calories:** {rec.get('calories', 'Not specified')}")
                
                # Handle nested macronutrients
                macronutrients = rec.get('macronutrients', {})
                st.write("**Macronutrients:**")
                st.write(f"- Protein: {macronutrients.get('protein', 'Not specified')}g")
                st.write(f"- Carbs: {macronutrients.get('carbs', 'Not specified')}g")
                st.write(f"- Fats: {macronutrients.get('fats', 'Not specified')}g")
                
                st.write(f"**Price Range:** {rec.get('price_range', 'Not specified')}")
                st.write(f"**Why this matches your preferences:** {rec.get('reason', 'No reason provided')}")

if __name__ == "__main__":
    main() 