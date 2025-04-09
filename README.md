# NutriGo - AI Dining Assistant 🍽️🤖

NutriGo is an AI-powered dining assistant that helps nutrition-conscious users discover nearby restaurants aligned with their dietary goals and preferences. The application uses OpenAI's GPT-4 model to provide personalized restaurant recommendations and engage in helpful conversations about nutrition and dining choices.

## Features

1. **Personalized Restaurant Discovery**:

   - Input your dietary restrictions, allergies, and cuisine preferences
   - Get restaurant recommendations based on your preferences
   - Filter by price range and distance

2. **Interactive Chat Interface**:

   - Chat with the AI assistant about restaurants and dietary advice
   - Ask follow-up questions about specific restaurants
   - Get nutritional information and recommendations

3. **Dietary Preference Management**:
   - Set multiple dietary restrictions (Vegetarian, Vegan, Gluten-Free, etc.)
   - Specify food allergies
   - Choose preferred cuisines
   - Set price range preferences

## Setup Instructions

1. Clone this repository:

   ```bash
   git clone <repository-url>
   cd NutriGo
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with your API keys:

   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   ```

4. Run the application:

   ```bash
   streamlit run nutrigo_app.py
   ```

5. Open your browser and navigate to http://localhost:8501

## Required API Keys

- **OpenAI API Key**: Required for the AI chat functionality
- **Google Maps API Key**: Required for restaurant location services

## Technologies Used

- **Streamlit**: For the web interface
- **OpenAI GPT-4**: For AI-powered conversations and recommendations
- **Google Maps API**: For restaurant location and search functionality
- **Python**: Core programming language

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
