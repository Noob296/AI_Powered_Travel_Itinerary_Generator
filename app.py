# === app.py ===
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import re
import json
import os
from datetime import datetime
from markupsafe import Markup
from markdown import markdown as md_to_html

# === Flask App Setup ===
app = Flask(__name__)
# Use environment variable for secret key, with a fallback for development
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

# === Database Setup ===
# Use absolute path for database to avoid issues in different environments
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "instance", "travel_planner.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SESSION_PERMANENT'] = False

# === API Keys ===
# Load API keys from environment variables for security
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# === Init DB ===
db = SQLAlchemy(app)

# === Jinja Filter ===
@app.template_filter('markdown')
def markdown_filter(text):
    return Markup(md_to_html(text)) if text else ""

# === Models ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    chats = db.relationship('Chat', backref='user', lazy=True, cascade="all, delete-orphan")

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# === Utility Functions ===

def extract_json_from_text(text):
    try:
        match = re.search(r"\{[\s\S]*?\}", text)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print("❌ JSON parsing error:", e)
    return None

def extract_source_destination(user_input):
    system_prompt = """
    Extract only the source (starting city) and destination (target city) from the following unstructured travel query.
    If a source or destination cannot be confidently identified as a city, return an empty string for that field.

    Return your response in the following JSON format:
    {
      "source": "...",
      "destination": "..."
    }

    Here is the user's input:
    """
    payload = {
        "contents": [
            {"parts": [{"text": system_prompt + "\n" + user_input}]}
        ]
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        text_output = data["candidates"][0]["content"]["parts"][0]["text"]
        structured = extract_json_from_text(text_output)
        if structured and "source" in structured and "destination" in structured:
            return structured["source"].strip(), structured["destination"].strip()
    except Exception as e:
        print(f"❌ Gemini extraction failed: {e}")
    return "", ""

def get_coordinates(city):
    if not city or city == "YOUR_GOOGLE_API_KEY":
        return None
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={GOOGLE_API_KEY}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        json_data = res.json()
        if json_data['status'] == 'OK' and json_data['results']:
            loc = json_data['results'][0]['geometry']['location']
            return f"{loc['lat']},{loc['lng']}"
    except Exception as e:
        print(f"❌ Error getting coordinates for {city}: {e}")
    return None

def get_places(location, place_type):
    try:
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius=5000&type={place_type}&key={GOOGLE_API_KEY}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        results = res.json().get("results", [])
        return [f"- {p.get('name')} (Rating: {p.get('rating', 'N/A')}) - {p.get('vicinity')}" for p in results[:5]]
    except Exception as e:
        print(f"❌ Error getting places: {e}")
        return []

def get_city_places(city):
    loc = get_coordinates(city)
    if not loc:
        return f"No location found for {city}."
    
    out = [f"\n📍 Attractions in {city}:"]
    out.extend(get_places(loc, "tourist_attraction"))
    out.append(f"\n🏨 Hotels:")
    out.extend(get_places(loc, "lodging"))
    out.append(f"\n🍽️ Restaurants:")
    out.extend(get_places(loc, "restaurant"))
    return "\n".join(out)

def get_travel_info(src, dst):
    try:
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={src}&destinations={dst}&key={GOOGLE_API_KEY}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()['rows'][0]['elements'][0]
        if data['status'] == 'OK':
            return f"Distance: {data['distance']['text']}, Duration: {data['duration']['text']}"
    except Exception as e:
        print(f"❌ Error getting travel info: {e}")
    return "No travel data available."

def generate_itinerary(user_input, travel_data, places_info, source, destination):
    prompt = f"""
    User Request: \"\"\"{user_input}\"\"\"
    Travel Info: {travel_data}
    Destination Details: {places_info}

    You are a travel expert AI. Generate a detailed itinerary for a trip from {source} to {destination}.
    Include:
    1. Best mode of travel.
    2. Accommodation suggestions from the provided details.
    3. Daily itinerary with specific activities and meal recommendations.
    4. Approximate budget breakdown.
    5. Practical travel tips.

    Use Markdown for formatting.
    """
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {"Content-Type": "application/json"}
    try:
        res = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=120)
        res.raise_for_status()
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"❌ Gemini itinerary generation failed: {e}")
        return "❌ Failed to generate itinerary. Please check your API keys."

# === Routes ===

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("chat"))
    return render_template("welcome.html")

@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect(url_for("signin"))
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    if "user_id" not in session:
        return jsonify({"response": "Please log in."}), 401

    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"response": "No message provided."}), 400

    source, destination = extract_source_destination(user_input)
    
    if not source or not destination:
        response_message = "❌ I couldn't recognize your source or destination. Please specify them clearly (e.g., 'Plan a trip from New York to London')."
        db.session.add(Chat(user_id=session["user_id"], message=user_input, response=response_message))
        db.session.commit()
        return jsonify({"response": response_message})

    travel_data = get_travel_info(source, destination)
    places_info = get_city_places(destination)
    itinerary = generate_itinerary(user_input, travel_data, places_info, source, destination)
    
    db.session.add(Chat(user_id=session["user_id"], message=user_input, response=itinerary))
    db.session.commit()
    
    return jsonify({"response": itinerary})

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if User.query.filter_by(username=username).first():
            return render_template("signup.html", error="User already exists.")
        db.session.add(User(username=username, password=password))
        db.session.commit()
        return redirect(url_for("signin"))
    return render_template("signup.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("chat"))
        return render_template("signin.html", error="Invalid credentials.")
    return render_template("signin.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("signin"))
    user = db.session.get(User, session["user_id"])
    return render_template("history.html", chats=user.chats if user else [])

if __name__ == "__main__":
    with app.app_context():
        if not os.path.exists(os.path.join(basedir, "instance")):
            os.makedirs(os.path.join(basedir, "instance"))
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
