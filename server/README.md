# NutriGo Backend API

This is the backend API for the NutriGo application, which provides restaurant recommendations based on user dietary preferences.

## Setup

1. Create a virtual environment:

   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   FLASK_ENV=development
   FLASK_APP=app.py
   ```

## Running the API

Start the Flask server:

```
flask run
```

The API will be available at http://localhost:5000.

## API Endpoints

### GET /api/status

Check the status of the API and its dependencies.

### GET /api/restaurants?zipcode=46556&radius=5000

Get restaurants by ZIP code.

### POST /api/recommendations

Get restaurant recommendations based on user preferences.

Request body:

```json
{
  "preferences": {
    "allergies": ["peanuts", "shellfish"],
    "calorie_count": 800,
    "macronutrients": {
      "protein_grams": 30,
      "carbs_grams": 50,
      "fats_grams": 20
    },
    "zipcode": "46556",
    "cuisine_preferences": ["Italian", "Mexican"],
    "price_range": [1, 3]
  }
}
```
