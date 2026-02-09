# TravelAI: AI-Powered Travel Itinerary Generator

TravelAI is a Flask-based web application that leverages the Gemini AI and Google Maps APIs to generate personalized travel itineraries. Users can sign up, log in, and request travel plans between a source and destination city. The AI provides detailed itineraries including travel information, accommodation suggestions, daily activities, budget breakdowns, and practical tips.

## Features

- **User Authentication**: Secure sign-up and sign-in functionality.
- **AI-Powered Itinerary Generation**: Utilizes Gemini AI to create comprehensive travel plans.
- **Google Maps Integration**: Uses Google Geocoding, Places, and Distance Matrix APIs for location data and travel information.
- **Chat History**: Stores and displays past travel requests and AI responses.
- **Markdown Rendering**: AI responses are rendered in Markdown for better readability.
- **Responsive Design**: Basic styling for a user-friendly experience.

## Technologies Used

- **Backend**: Python, Flask, Flask-SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **APIs**: Google Gemini API, Google Maps Platform (Geocoding API, Places API, Distance Matrix API)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository_url>
cd TravelAI
```

### 2. Set up a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

TravelAI requires API keys for Google Gemini and Google Maps Platform. Obtain these keys from the respective developer consoles:

- **Google Gemini API**: [Google AI Studio](https://aistudio.google.com/)
- **Google Maps Platform**: [Google Cloud Console](https://console.cloud.google.com/)

Once you have your API keys, set them as environment variables. It is **highly recommended** to use environment variables for security reasons.

```bash
export FLASK_SECRET_KEY="your_flask_secret_key"
export GOOGLE_API_KEY="your_google_api_key"
export GEMINI_API_KEY="your_gemini_api_key"
```

Replace `your_flask_secret_key`, `your_google_api_key`, and `your_gemini_api_key` with your actual keys. For development, you can also set these directly in `app.py` (though not recommended for production).

### 5. Run the Application

```bash
python app.py
```

The application will run on `http://127.0.0.1:5000/` (or `http://localhost:5000/`).

## Usage

1. **Sign Up**: Create a new account.
2. **Sign In**: Log in with your credentials.
3. **Chat**: Enter your travel request in the chat interface (e.g., "Plan a trip from London to Paris for 5 days").
4. **View Itinerary**: The AI will generate a detailed travel itinerary.
5. **Chat History**: View your past conversations and itineraries.

## Project Structure

```
TravelAI/
├── app.py              # Main Flask application file
├── instance/           # Contains SQLite database files
│   └── travel_planner.db
├── static/             # Static files (CSS, JavaScript)
│   ├── script.js
│   └── style.css
└── templates/          # HTML templates
    ├── history.html
    ├── index.html
    ├── signin.html
    ├── signup.html
    └── welcome.html
```

## Contributing

Feel free to fork the repository, open issues, or submit pull requests to improve TravelAI.

## License

This project is open source and available under the MIT License.
