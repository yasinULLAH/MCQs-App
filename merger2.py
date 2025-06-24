import json
import os
from tqdm import tqdm

# --- CONFIGURATION ---
ENGLISH_JSON_FILE = "mcqs_data.json"
URDU_JSON_FILE = "mcqs_urdu.json"
BILINGUAL_OUTPUT_FILE = "mcqs_bilingual_sequential2.json"

def merge_files_sequentially():
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

    # --- Create a dictionary for fast lookups using the MCQ ID ---
    english_mcqs_dict = {mcq['id']: mcq for mcq in english_mcqs}

    bilingual_sequential_mcqs = []

    print("\nCreating sequential English/Urdu list...")
    # Iterate through the primary list (can be English or Urdu, let's use Urdu)
    for urdu_mcq in tqdm(urdu_mcqs, desc="Merging Sequentially"):
        mcq_id = urdu_mcq['id']
        
        # Find the corresponding English MCQ from the dictionary
        english_mcq = english_mcqs_dict.get(mcq_id)

        if english_mcq:
            # 1. First, append the complete English version
            bilingual_sequential_mcqs.append(english_mcq)
            
            # 2. Second, append the complete Urdu version
            bilingual_sequential_mcqs.append(urdu_mcq)
        else:
            # Fallback: If no matching English question is found, just add the Urdu one.
            bilingual_sequential_mcqs.append(urdu_mcq)

    # --- Save the final merged file ---
    print(f"\nSaving sequential data to '{BILINGUAL_OUTPUT_FILE}'...")
    with open(BILINGUAL_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(bilingual_sequential_mcqs, f, indent=2, ensure_ascii=False)

    print("\nProcess complete!")
    print(f"Sequential bilingual file '{BILINGUAL_OUTPUT_FILE}' has been created successfully.")
    print(f"Total entries in new file: {len(bilingual_sequential_mcqs)}")

if __name__ == "__main__":
    merge_files_sequentially()