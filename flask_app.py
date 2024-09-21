import os

import requests
from flask import Flask, jsonify, request
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from textblob import TextBlob
from transformers import pipeline

app = Flask(__name__)

# Database setup with SQLAlchemy
DATABASE_URL = "sqlite:///medical.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class MedicalInfo(Base):
    __tablename__ = "medical_info"
    id = Column(Integer, primary_key=True, index=True)
    condition = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)


# Create the table
Base.metadata.create_all(engine)


# Populate the database with some example data (only if empty)
def populate_database():
    session = SessionLocal()
    if session.query(MedicalInfo).count() == 0:
        conditions = [
            MedicalInfo(
                condition="headache",
                description="Common causes of headaches include stress, dehydration, and lack of sleep. Consult a healthcare professional for persistent headaches.",
            ),
            MedicalInfo(
                condition="fever",
                description="Fever can be a sign of infection. Drink plenty of fluids and rest. If fever persists, seek medical advice.",
            ),
            MedicalInfo(
                condition="cough",
                description="Coughs can be caused by infections, allergies, or irritants. If persistent or severe, consult a healthcare provider.",
            ),
        ]
        session.add_all(conditions)
        session.commit()
    session.close()


populate_database()

# Load the pre-trained text generation model
chatbot = pipeline("text-generation", model="hassiahk/DialoGPT-MedDialog-large")

# Simulate a user profile store
user_profiles = {}  # In production, use a persistent database


def get_user_profile(user_id):
    """Retrieve or create a user profile."""
    return user_profiles.get(user_id, {"history": []})


def update_user_profile(user_id, user_profile):
    """Update the user profile."""
    user_profiles[user_id] = user_profile


def query_medical_database(query):
    """Query the medical database for relevant information."""
    session = SessionLocal()

    condition = query.lower()
    condition = str(
        TextBlob(condition).correct()
    )  # Corrects the spelling of the disease

    info = (
        session.query(MedicalInfo)
        .filter(MedicalInfo.condition.like(f"%{condition}%"))
        .first()
    )
    session.close()
    if info:
        return info.description
    else:
        return None


def update_medical_database(condition, description):
    session = SessionLocal()

    info = (
        session.query(MedicalInfo)
        .filter(MedicalInfo.condition == condition)
        .update({"description": description})
    )

    session.commit()

    return info


def generate_response(user_input, user_profile):
    """Generate a response based on user input, medical database, and NLP model."""
    # 1. Attempt to retrieve information from the medical database
    db_response = query_medical_database(user_input)
    if db_response:
        return db_response

    # 2. If not found in the database, generate a response using the NLP model
    # Concatenate the conversation history for context
    chat = user_profile["history"][-5:]
    chat.append({"role": "user", "content": user_input})

    bot_response = chatbot(chat, max_length=1024, num_return_sequences=1)[0][
        "generated_text"
    ]
    return bot_response


@app.route("/chatbot", methods=["POST"])
def chatbot_route():
    """Handle user queries and generate responses."""
    data = request.json
    user_input = data.get("query")
    user_id = data.get("user_id", "default_user")  # Simplistic user identification

    if not user_input:
        return jsonify({"error": "No query provided."}), 400

    user_profile = get_user_profile(user_id)

    response = generate_response(user_input, user_profile)

    # Update user profile with the latest interaction
    user_profile["history"].extend(response)
    update_user_profile(user_id, user_profile)

    return jsonify({"response": response})


def call_external_api(query):
    """Call an external medical API to retrieve additional information."""
    # Example: Replace with a real API endpoint and handle authentication as needed
    # For demonstration, we will simulate an API response
    simulated_response = {"research": f"Latest research on {query}: ..."}
    return simulated_response


@app.route("/external_api", methods=["POST"])
def external_api_route():
    """Handle requests to external medical APIs."""
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "No query provided."}), 400

    response = call_external_api(query)
    return jsonify(response)


if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)
