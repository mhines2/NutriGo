"""
NutriGo - AI-powered dining assistant that helps users discover restaurants
aligned with their dietary goals and preferences.
"""

import os
import dotenv
import openai
import streamlit as st
import googlemaps
from datetime import datetime

# Load environment variables from .env file
dotenv.load_dotenv(override=True)

# Check if API keys are loaded
openai_api_key = os.environ.get("OPENAI_API_KEY")
google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

# Initialize clients as None
client = None
gmaps = None

# Check if API keys are valid
if not openai_api_key or openai_api_key == "your_openai_api_key_here":
    st.error("OpenAI API key not found. Please add your API key to the .env file.")
    st.stop()
else:
    try:
        # Initialize OpenAI client with minimal configuration
        client = openai.OpenAI(
            api_key=openai_api_key
        )
        # Test the API key with a simple request
        client.models.list()
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {str(e)}")
        st.stop()

if not google_maps_api_key or google_maps_api_key == "your_google_maps_api_key_here":
    st.warning("Google Maps API key not found. Restaurant location features will be limited.")
else:
    try:
        # Initialize Google Maps client
        gmaps = googlemaps.Client(key=google_maps_api_key)
    except Exception as e:
        st.warning(f"Error initializing Google Maps client: {str(e)}")

def get_nearby_restaurants(location, radius=5000):
    """Get nearby restaurants using Google Places API"""
    if not gmaps:
        st.warning("Google Maps API is not configured. Cannot fetch nearby restaurants.")
        return []
    
    try:
        places_result = gmaps.places_nearby(
            location=location,
            radius=radius,
            type='restaurant',
            open_now=True
        )
        return places_result.get('results', [])
    except Exception as e:
        st.error(f"Error fetching restaurants: {e}")
        return []

def main():
    st.set_page_config(page_title="NutriGo - AI Dining Assistant", layout="wide")
    st.title("NutriGo 🍽️🤖")
    st.subheader("Your AI-powered dining companion")
    
    # Check if OpenAI client is initialized
    if not client:
        st.error("OpenAI client is not properly initialized. Please check your API key and try again.")
        st.stop()
    
    # Sidebar for user preferences
    st.sidebar.header("Your Dietary Preferences")
    
    # Nutritional preferences section
    st.sidebar.subheader("Nutritional Preferences")
    calorie_count = st.sidebar.number_input(
        "Target calories per meal",
        min_value=0,
        max_value=2000,
        value=0,
        step=50
    )
    
    # Calculate default macronutrient values based on calorie input
    def calculate_default_macros(calories):
        if calories == 0:
            return 30, 50, 20  # Default values when no calories specified
        
        # Calculate macros based on standard ratios:
        # Protein: 30% of calories (4 calories per gram)
        # Carbs: 45% of calories (4 calories per gram)
        # Fats: 25% of calories (9 calories per gram)
        protein_calories = calories * 0.30
        carbs_calories = calories * 0.45
        fats_calories = calories * 0.25
        
        protein_grams = round(protein_calories / 4)
        carbs_grams = round(carbs_calories / 4)
        fats_grams = round(fats_calories / 9)
        
        return protein_grams, carbs_grams, fats_grams
    
    default_protein, default_carbs, default_fats = calculate_default_macros(calorie_count)
    
    st.sidebar.write("Macronutrient targets (grams)")
    protein_grams = st.sidebar.number_input(
        "Protein (g)", 
        min_value=0, 
        max_value=200, 
        value=default_protein, 
        step=5,
        help=f"Recommended: {default_protein}g ({round(calorie_count * 0.30)} calories) - 30% of total calories"
    )
    carbs_grams = st.sidebar.number_input(
        "Carbs (g)", 
        min_value=0, 
        max_value=300, 
        value=default_carbs, 
        step=5,
        help=f"Recommended: {default_carbs}g ({round(calorie_count * 0.45)} calories) - 45% of total calories"
    )
    fats_grams = st.sidebar.number_input(
        "Fats (g)", 
        min_value=0, 
        max_value=100, 
        value=default_fats, 
        step=5,
        help=f"Recommended: {default_fats}g ({round(calorie_count * 0.25)} calories) - 25% of total calories"
    )
    
    # Food allergies
    allergies = st.sidebar.text_input("Any food allergies? (comma-separated)", "")
    
    # Cuisine and location preferences
    st.sidebar.subheader("Cuisine & Location")
    
    # Location input
    location = st.sidebar.text_input("Your location (zip code)", "")
    
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
    max_distance = st.sidebar.slider("Maximum distance (miles)", 1, 10, 5)
    
    if st.sidebar.button("Submit Preferences"):
        initial_preferences = {
            "allergies": [allergy.strip() for allergy in allergies.split(",") if allergy.strip()],
            "calorie_count": calorie_count,
            "macronutrients": {
                "protein_grams": protein_grams,
                "carbs_grams": carbs_grams,
                "fats_grams": fats_grams
            },
            "location": location,
            "cuisine_preferences": cuisine_preferences,
            "price_range": price_range,
            "max_distance": max_distance
        }
        st.session_state.preferences = initial_preferences
        st.session_state.conversation = []

        st.success("Preferences submitted successfully! You can now chat with your AI Dining Assistant.")

        # Prepare initial conversation
        preferences = st.session_state.preferences
        initial_message = {
            "role": "system",
            "content": """You are NutriGo, an AI dining assistant focused on helping users discover specific meals 
            from restaurants that align with their dietary goals and preferences. You provide personalized meal 
            recommendations with approximate nutritional information and can engage in helpful conversations about 
            nutrition and dining choices. 

            When recommending meals, ALWAYS format your response in the following structure:
            
            Restaurant Name (Address)
            Dish: [Dish Name]
            Approximate Calories: [Calorie Count]
            Macronutrients: [Protein/Carbs/Fat breakdown]
            Reason: [Why this meal is a good match for the user's preferences]
            
            For each recommendation, use this exact format with the exact headings. If you're providing multiple 
            recommendations, separate them with a blank line. For general conversation or answering questions, 
            you don't need to use this format."""
        }
        user_message = {
            "role": "user",
            "content": f"""
            My location is {preferences['location'] if preferences['location'] else 'not specified'}.
            My allergies are: {', '.join(preferences['allergies']) if preferences['allergies'] else 'None'}.
            My target calorie count per meal is {preferences['calorie_count']} calories.
            My macronutrient targets are: {preferences['macronutrients']['protein_grams']}g protein, 
            {preferences['macronutrients']['carbs_grams']}g carbs, and {preferences['macronutrients']['fats_grams']}g fats.
            I prefer these cuisines: {', '.join(preferences['cuisine_preferences'])}.
            My preferred price range is ${preferences['price_range'][0]} to ${preferences['price_range'][1]} per person.
            I'm willing to travel up to {preferences['max_distance']} miles.
            Can you recommend specific meals from restaurants in my area that match my nutritional goals?
            """
        }

        st.session_state.conversation = [initial_message, user_message]
        
        with st.spinner("Finding restaurants that match your preferences..."):
            try:
                response = client.chat.completions.create(
                    messages=st.session_state.conversation,
                    model="gpt-4"
                )
                bot_reply = response.choices[0].message.content.strip()
                st.session_state.conversation.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                st.stop()

    # Chat Interface
    if "preferences" in st.session_state:
        st.subheader("Chat with NutriGo")
        message_container = st.container()

        with message_container:
            # Display previous conversation
            for message in st.session_state.conversation[2:]:
                if message["role"] == "user":
                    st.chat_message("user").write(message["content"])
                elif message["role"] == "assistant":
                    st.chat_message("assistant").write(message["content"])

        # Add user input at bottom
        def send_message():
            user_input = st.session_state.user_input
            if user_input:
                st.session_state.conversation.append({"role": "user", "content": user_input})
                with message_container:
                    st.chat_message("user").write(user_input)

                with st.spinner("Thinking..."):
                    try:
                        response = client.chat.completions.create(
                            messages=st.session_state.conversation,
                            model="gpt-4"
                        )
                        bot_reply = response.choices[0].message.content.strip()
                        st.session_state.conversation.append({"role": "assistant", "content": bot_reply})
                        with message_container:
                            # Display chat messages
                            for message in st.session_state.conversation:
                                if message["role"] == "user":
                                    st.chat_message("user").write(message["content"])
                                else:
                                    with st.chat_message("assistant"):
                                        # Split the message into sections
                                        content = message["content"]
                                        
                                        # Check if the message contains meal recommendations
                                        if "recommend" in content.lower() or "suggest" in content.lower():
                                            # Extract restaurant and meal information
                                            st.markdown("### 🍽️ Meal Recommendations")
                                            
                                            # Split content into paragraphs
                                            paragraphs = content.split('\n\n')
                                            
                                            for paragraph in paragraphs:
                                                # Check if paragraph contains a restaurant name (usually in quotes or followed by ':')
                                                if '"' in paragraph or ':' in paragraph:
                                                    # Format restaurant name
                                                    if '"' in paragraph:
                                                        restaurant = paragraph.split('"')[1]
                                                        st.markdown(f"#### 🏪 {restaurant}")
                                                    else:
                                                        restaurant = paragraph.split(':')[0].strip()
                                                        st.markdown(f"#### 🏪 {restaurant}")
                                                    
                                                    # Format meal details
                                                    meal_details = paragraph.split(':')[-1].strip()
                                                    st.markdown(f"**Dish:** {meal_details}")
                                                    
                                                    # Look for nutritional information
                                                    if "calories" in paragraph.lower():
                                                        st.markdown("**Nutritional Information:**")
                                                        st.markdown(f"- Calories: {paragraph.split('calories')[0].strip()}")
                                                        if "protein" in paragraph.lower():
                                                            st.markdown(f"- Protein: {paragraph.split('protein')[0].strip()}")
                                                        if "carbs" in paragraph.lower():
                                                            st.markdown(f"- Carbs: {paragraph.split('carbs')[0].strip()}")
                                                        if "fat" in paragraph.lower():
                                                            st.markdown(f"- Fat: {paragraph.split('fat')[0].strip()}")
                                                    
                                                    # Add reason for recommendation
                                                    if "reason" in paragraph.lower():
                                                        reason = paragraph.split('reason:')[-1].strip()
                                                        st.markdown(f"**Reason:** {reason}")
                                                    
                                                    st.markdown("---")
                                                else:
                                                    # Regular text paragraphs
                                                    st.markdown(paragraph)
                                        else:
                                            # Regular chat messages
                                            st.markdown(content)
                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")
                    finally:
                        st.session_state.user_input = ""

        # Add text input for messages
        st.text_input("Ask me about restaurants or dietary advice:", key="user_input", on_change=send_message)

if __name__ == "__main__":
    main() 