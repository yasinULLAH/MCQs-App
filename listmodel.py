import google.generativeai as genai
import os

# Load your key the same way as your main script
api_key = "AIzaSyBfu2LWQfdkqN4jhHeFBpI0Em_xijxhLo8"
if not api_key:
    # Or paste your key here directly for a quick test
    api_key = "AIzaSyBfu2LWQfdkqN4jhHeFBpI0Em_xijxhLo8" 
    print("API Key not found as environment variable.")
    exit()

genai.configure(api_key=api_key)

print("--- Available Gemini Models ---")
for model in genai.list_models():
  # We only care about models that can generate content (the 'generateContent' method)
  if 'generateContent' in model.supported_generation_methods:
    print(f"- {model.name}")
print("\nUse one of the model names listed above in your main script.")