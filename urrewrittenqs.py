import os
import json
import math
from tqdm import tqdm
import google.generativeai as genai

# --- CONFIGURATION ---
INPUT_FILENAME = "mcqs_data.json"
OUTPUT_FILENAME = "mcqs_urdu_gemini.json"
BATCH_SIZE = 75

# --- LOAD API KEY (Hard-coded for this example) ---
# IMPORTANT: Use the NEW key you generated, not the one you posted.
api_key = "AIzaSyBfu2LWQfdkqN4jhHeFBpI0Em_xijxhLo8" 
if api_key == "YOUR_NEW_SECRET_API_KEY_HERE":
    print("Error: Please replace 'YOUR_NEW_SECRET_API_KEY_HERE' with your actual Gemini API key.")
    exit()
genai.configure(api_key=api_key)


def translate_batch_with_gemini(batch_of_mcqs, model):
    json_input_string = json.dumps(batch_of_mcqs, indent=2)
    prompt = f"""
    You are an expert English-to-Urdu translator specializing in structured data.
    You will be given a JSON array of objects. Each object represents a multiple-choice question.
    Your task is to:
    1. Translate the value of the "question" key into fluent Urdu.
    2. For each object in the "options" array, translate the value of its "text" key into fluent Urdu.
    3. Maintain the exact original JSON structure, including all keys like "id" and "correct".
    Return ONLY the translated JSON array as a raw string, without any surrounding text, explanations, or markdown code blocks like ```json.
    Here is the JSON array to translate:
    {json_input_string}
    """
    try:
        response = model.generate_content(prompt)
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response_text)
    except Exception as e:
        print(f"\nAn error occurred during API call or JSON parsing: {e}")
        print("Skipping this batch. The original English batch will be used.")
        return batch_of_mcqs

# --- MAIN EXECUTION ---
if not os.path.exists(INPUT_FILENAME):
    print(f"Error: Input file '{INPUT_FILENAME}' not found.")
    exit()

print(f"Loading English questions from '{INPUT_FILENAME}'...")
with open(INPUT_FILENAME, 'r', encoding='utf-8') as f:
    original_mcqs = json.load(f)

# --- THE FIX: Using a model name that is confirmed to be in your list ---
model_name_from_your_list = 'gemini-1.5-flash-latest'
print(f"Initializing model: {model_name_from_your_list}")
gemini_model = genai.GenerativeModel(model_name_from_your_list)

all_translated_mcqs = []
num_batches = math.ceil(len(original_mcqs) / BATCH_SIZE)

print(f"Starting Gemini Pro translation in {num_batches} batches...")

for i in tqdm(range(0, len(original_mcqs), BATCH_SIZE), desc="Translating Batches with Gemini"):
    batch = original_mcqs[i:i + BATCH_SIZE]
    translated_batch = translate_batch_with_gemini(batch, gemini_model)
    all_translated_mcqs.extend(translated_batch)

print("\nReconstruction complete. All batches processed.")

print(f"Saving translated Urdu data to '{OUTPUT_FILENAME}'...")
with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
    json.dump(all_translated_mcqs, f, indent=2, ensure_ascii=False)

print("\nProcess complete!")
print(f"File saved as: {OUTPUT_FILENAME}")