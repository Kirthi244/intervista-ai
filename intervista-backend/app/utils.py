# app/utils.py
from dotenv import load_dotenv
import os

load_dotenv()
import os
import google.generativeai as genai

# Load API key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Choose a working model
MODEL_NAME = "gemini-2.5-flash"  # or use any model from the list you printed
model = genai.GenerativeModel(MODEL_NAME)

async def call_gemini_chat(prompt: str) -> str:
    """
    Call Google Gemini to generate a response for the given prompt.
    """
    try:
        # Generate content
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # Handle errors gracefully
        print(f"Gemini API call failed: {str(e)}")
        return f"Error: {str(e)}"
