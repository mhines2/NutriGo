# NutriGo - AI-Powered Dining Assistant 🍽️

NutriGo helps nutrition-conscious users discover nearby restaurants that align with their dietary goals and preferences. Using OpenAI's GPT models and Google Maps, it provides personalized restaurant recommendations with detailed nutritional information.

## Features 🌟

### Core Features

- **Smart Restaurant Discovery**: Find restaurants based on location and dietary preferences
- **Nutritional Analysis**: Get detailed macro breakdowns for recommended meals
- **Personalized Recommendations**: Tailored suggestions based on:
  - Calorie goals
  - Macronutrient targets
  - Price range
  - Dietary restrictions
  - Cuisine preferences

### Technical Features

- **Real-time API Integration**: OpenAI GPT-3.5 & Google Maps
- **Detailed Logging System**: Session-based logging for debugging
- **Modern React Frontend**: Clean, responsive UI with TypeScript
- **RESTful Flask Backend**: Robust Python backend with error handling

## Setup 🚀

### Prerequisites

- Node.js (v16+)
- Python 3.8+
- API Keys:
  - OpenAI API Key
  - Google Maps API Key

### Backend Setup

1. Navigate to server directory:

   ```bash
   cd server
   ```

2. Create and activate virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   FLASK_ENV=development
   ```

5. Run the server:
   ```bash
   python app.py
   ```
   Server will run on http://localhost:5001

### Frontend Setup

1. Navigate to client directory:

   ```bash
   cd client
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm start
   ```
   Client will run on http://localhost:3000

## Development 🛠️

### Project Structure

```
nutrigo/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── context/      # React context
│   │   └── services/     # API services
│   └── package.json
└── server/                # Flask backend
    ├── app.py            # Main server file
    ├── requirements.txt  # Python dependencies
    └── logs/            # Debug logs
```

### Debugging

- Check `server/logs/session_[timestamp]/` for detailed request logs
- Each session includes:
  - `summary.txt`: Human-readable overview
  - `request.json`: Initial request
  - `restaurants.json`: Found restaurants
  - `final_recommendations.json`: Generated recommendations
  - `errors.txt`: Any errors encountered

### API Endpoints

- `GET /api/status`: Check API health
- `GET /api/restaurants`: Get restaurants by ZIP code
- `POST /api/recommendations`: Get personalized recommendations

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

- OpenAI GPT API
- Google Maps Places API
- React & Flask communities
