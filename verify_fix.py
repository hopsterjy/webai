
import google.generativeai as genai
import toml
import os

try:
    secrets = toml.load(".streamlit/secrets.toml")
    GEMINI_API_KEY = secrets["GEMINI_API_KEY"]
except Exception as e:
    print(f"Error loading secrets: {e}")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model_name = 'gemini-flash-latest'

print(f"Testing model: {model_name}")
model = genai.GenerativeModel(model_name)

try:
    response = model.generate_content("Hello")
    print("\n--- Gemini Response ---\n")
    print(response.text)
    print("\nSUCCESS: Model is accessible.")
except Exception as e:
    print(f"\nFAILED: {e}")
