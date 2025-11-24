import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # Load your .env file

# Configure API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env")

genai.configure(api_key=GOOGLE_API_KEY)

# List available models
models = genai.list_models()
print("Available models for this API key:")
for m in models:
    print(m.name)
