import json
import os
from tqdm import tqdm

# --- CONFIGURATION ---
ENGLISH_JSON_FILE = "mcqs_data.json"
URDU_JSON_FILE = "mcqs_urdu.json"
BILINGUAL_OUTPUT_FILE = "mcqs_bilingual.json"

# --- MAIN EXECUTION ---
def merge_files():
    # --- Validation: Check if both source files exist ---
    if not os.path.exists(ENGLISH_JSON_FILE):
        print(f"Error: English source file '{ENGLISH_JSON_FILE}' not found.")
        return
    if not os.path.exists(URDU_JSON_FILE):
        print(f"Error: Urdu source file '{URDU_JSON_FILE}' not found.")
        return

    # --- Load both datasets into memory ---
    print("Loading English data...")
    with open(ENGLISH_JSON_FILE, 'r', encoding='utf-8') as f:
        english_mcqs = json.load(f)

    print("Loading Urdu data...")
    with open(URDU_JSON_FILE, 'r', encoding='utf-8') as f:
        urdu_mcqs = json.load(f)

    # --- Create dictionaries for fast lookups using the MCQ ID ---
    # This avoids slow, nested loops.
    english_mcqs_dict = {mcq['id']: mcq for mcq in english_mcqs}

    bilingual_mcqs = []

    print("\nCombining English and Urdu data...")
    # Iterate through the Urdu MCQs as the primary source
    for urdu_mcq in tqdm(urdu_mcqs, desc="Merging MCQs"):
        mcq_id = urdu_mcq['id']
        
        # Find the corresponding English MCQ using the dictionary
        english_mcq = english_mcqs_dict.get(mcq_id)

        if not english_mcq:
            # If for some reason there's no matching English question,
            # just use the Urdu one to avoid crashing.
            bilingual_mcqs.append(urdu_mcq)
            continue

        # --- Create the new bilingual MCQ object ---
        # 1. Combine the question text
        combined_question = f"{english_mcq['question']} / {urdu_mcq['question']}"

        # 2. Combine the options text
        combined_options = []
        for i, urdu_option in enumerate(urdu_mcq['options']):
            # Ensure we don't go out of bounds if the option counts differ
            if i < len(english_mcq['options']):
                english_option_text = english_mcq['options'][i]['text']
                combined_text = f"{english_option_text} / {urdu_option['text']}"
                
                combined_options.append({
                    "text": combined_text,
                    # The 'correct' flag is the same in both files, so we can take it from either
                    "correct": urdu_option['correct'] 
                })

        # 3. Build the final object, preserving the structure
        bilingual_mcq = {
            "id": mcq_id,
            "question": combined_question,
            "options": combined_options
        }
        bilingual_mcqs.append(bilingual_mcq)

    # --- Save the final merged file ---
    print(f"\nSaving combined data to '{BILINGUAL_OUTPUT_FILE}'...")
    with open(BILINGUAL_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(bilingual_mcqs, f, indent=2, ensure_ascii=False)

    print("\nProcess complete!")
    print(f"Bilingual file '{BILINGUAL_OUTPUT_FILE}' has been created successfully.")

if __name__ == "__main__":
    merge_files()