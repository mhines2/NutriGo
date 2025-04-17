# NutriGo - AI-Powered Dining Assistant 🍽️

NutriGo helps nutrition-conscious users discover nearby restaurants that align with their dietary goals and preferences. Using OpenAI's GPT models and Google Maps, it provides personalized restaurant recommendations with detailed nutritional information.

## Demo 🎥

Check out our [live demo video](NutriGo%20Live%20Demo.mp4) to see NutriGo in action!

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
- API Keys (required):
  - OpenAI API Key ([Get here](https://platform.openai.com/api-keys))
  - Google Maps API Key ([Get here](https://console.cloud.google.com/google/maps-apis/credentials))

### API Key Setup

1. **OpenAI API Key**:

   - Create an account at [OpenAI](https://platform.openai.com)
   - Navigate to API Keys section
   - Create a new secret key
   - ⚠️ Store this key securely, it cannot be viewed again

2. **Google Maps API Key**:
   - Create a project in [Google Cloud Console](https://console.cloud.google.com)
   - Enable Maps JavaScript API and Places API
   - Create credentials (API key)
   - ⚠️ Restrict the API key to your domains/IPs
   - ⚠️ Set usage quotas to prevent unexpected billing

### Environment Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/nutrigo.git
   cd nutrigo
   ```

2. Create a root `.env` file:

   ```env
   # API Keys
   OPENAI_API_KEY=your_key_here
   GOOGLE_MAPS_API_KEY=your_key_here

   # Server Configuration
   FLASK_ENV=development
   FLASK_APP=app.py
   ```

3. Follow the Backend and Frontend setup instructions below.

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

4. Create `.env` file in the server directory:

   ```env
   FLASK_ENV=development
   FLASK_APP=app.py

   # Add your API keys (keep these secret!)
   OPENAI_API_KEY=your_key_here
   GOOGLE_MAPS_API_KEY=your_key_here
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

3. Create `.env` file in the client directory:

   ```env
   # Add your Google Maps API key (keep this secret!)
   REACT_APP_GOOGLE_MAPS_API_KEY=your_key_here
   ```

4. Start development server:
   ```bash
   npm start
   ```
   Client will run on http://localhost:3000

## Security Best Practices 🔒

### API Keys

- Never commit `.env` files to version control
- Don't share API keys in code, screenshots, or logs
- Rotate keys if they've been accidentally exposed
- Use environment variables in production
- Set appropriate API key restrictions and quotas

### Environment Files

- Keep separate `.env` files for development and production
- Add `.env*` to `.gitignore`
- Use `.env.example` files to document required variables
- Regularly audit environment files for sensitive data

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
├── public/                # Static assets
├── server/                # Flask backend
│   ├── app.py            # Main server file
│   ├── requirements.txt  # Python dependencies
│   └── logs/            # Debug logs
├── .env                  # Root environment variables
├── nutrigo_prototype.py  # Initial prototype implementation
└── README.md
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
5. Create a Pull Request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

- OpenAI GPT API
- Google Maps Places API
- React & Flask communities
