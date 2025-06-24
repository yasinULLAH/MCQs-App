import json
import os
from tqdm import tqdm

# --- CONFIGURATION ---
ENGLISH_JSON_FILE = "mcqs_data.json"
URDU_JSON_FILE = "mcqs_urdu.json"
BILINGUAL_OUTPUT_FILE = "mcqs_bilingual_sequential2.json"

def merge_files_with_unique_ids():
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

    # --- Create a dictionary for fast lookups using the original MCQ ID ---
    english_mcqs_dict = {mcq['id']: mcq for mcq in english_mcqs}

    bilingual_sequential_mcqs = []
    
    # --- THE FIX: Initialize a new, global counter for unique IDs ---
    unique_id_counter = 1

    print("\nCreating sequential English/Urdu list with new unique IDs...")
    # Iterate through the primary list
    for urdu_mcq in tqdm(urdu_mcqs, desc="Merging with new IDs"):
        original_mcq_id = urdu_mcq['id']
        
        # Find the corresponding English MCQ from the dictionary
        english_mcq = english_mcqs_dict.get(original_mcq_id)

        if english_mcq:
            # --- Process English Version ---
            # Make a copy to avoid modifying the original data
            new_english_mcq = english_mcq.copy()
            # Assign the new, unique ID from our counter
            new_english_mcq['id'] = unique_id_counter
            bilingual_sequential_mcqs.append(new_english_mcq)
            # IMPORTANT: Increment the counter
            unique_id_counter += 1
            
            # --- Process Urdu Version ---
            new_urdu_mcq = urdu_mcq.copy()
            # Assign the next new, unique ID
            new_urdu_mcq['id'] = unique_id_counter
            bilingual_sequential_mcqs.append(new_urdu_mcq)
            # IMPORTANT: Increment the counter again
            unique_id_counter += 1
        else:
            # Fallback: If no matching English question, still add the Urdu one with a unique ID
            new_urdu_mcq = urdu_mcq.copy()
            new_urdu_mcq['id'] = unique_id_counter
            bilingual_sequential_mcqs.append(new_urdu_mcq)
            unique_id_counter += 1

    # --- Save the final merged file ---
    print(f"\nSaving sequential data to '{BILINGUAL_OUTPUT_FILE}'...")
    with open(BILINGUAL_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(bilingual_sequential_mcqs, f, indent=2, ensure_ascii=False)

    print("\nProcess complete!")
    print(f"Sequential bilingual file '{BILINGUAL_OUTPUT_FILE}' has been created successfully.")
    print(f"Total entries in new file: {len(bilingual_sequential_mcqs)}")

if __name__ == "__main__":
    merge_files_with_unique_ids()