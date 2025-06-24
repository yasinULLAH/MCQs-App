import json
import csv
import os
from tqdm import tqdm

# --- CONFIGURATION ---
SOURCE_JSON = "mcqs_data.json"
CSV_FOR_TRANSLATION = "for_translation.csv"
TRANSLATED_CSV_FROM_SHEETS = "translated_from_sheets.csv"
FINAL_URDU_JSON = "mcqs_urdu.json"

def convert_json_to_csv():
    """
    Reads the structured JSON file and flattens it into a CSV
    perfectly formatted for translation in Google Sheets.
    (This function is unchanged)
    """
    if not os.path.exists(SOURCE_JSON):
        print(f"Error: Source file '{SOURCE_JSON}' not found.")
        return

    print(f"Loading data from '{SOURCE_JSON}'...")
    with open(SOURCE_JSON, 'r', encoding='utf-8') as f:
        mcqs = json.load(f)

    with open(CSV_FOR_TRANSLATION, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['unique_id', 'source_text', 'is_correct', 'translated_text'])

        print("Converting JSON to CSV format...")
        for mcq in tqdm(mcqs, desc="Processing MCQs"):
            question_id = f"{mcq['id']}_question"
            writer.writerow([question_id, mcq['question'], '', ''])
            for i, option in enumerate(mcq['options']):
                option_id = f"{mcq['id']}_option_{i}"
                writer.writerow([option_id, option['text'], option['correct'], ''])

    print(f"\nSuccessfully created '{CSV_FOR_TRANSLATION}'.")
    print("\n--- NEXT STEPS ---")
    print("1. Open Google Sheets.")
    print(f"2. Go to 'File' -> 'Import' and upload '{CSV_FOR_TRANSLATION}'.")
    print("3. In cell D2, enter this formula: =GOOGLETRANSLATE(B2, \"en\", \"ur\")")
    print("4. Drag the blue square at the corner of cell D2 all the way down to apply the formula to all rows.")
    print("5. Once translation is complete, go to 'File' -> 'Download' -> 'Comma Separated Values (.csv)'.")
    print(f"6. Save that file as '{TRANSLATED_CSV_FROM_SHEETS}' in this same folder.")
    print("7. Run this script again and choose Mode 2.")

def convert_csv_to_json():
    """
    Reads the translated CSV file from Google Sheets and reconstructs
    it back into the original structured JSON format.
    (This function has been fixed)
    """
    if not os.path.exists(TRANSLATED_CSV_FROM_SHEETS):
        print(f"Error: Translated file '{TRANSLATED_CSV_FROM_SHEETS}' not found.")
        print("Please make sure you have downloaded the translated file from Google Sheets and named it correctly.")
        return

    reconstructed_data = {}
    print(f"Loading translated data from '{TRANSLATED_CSV_FROM_SHEETS}'...")
    with open(TRANSLATED_CSV_FROM_SHEETS, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) 

        for row in tqdm(reader, desc="Reconstructing JSON"):
            # --- THE FIX IS HERE ---
            # If the row is empty or the first cell is empty, skip it.
            if not row or not row[0]:
                continue
            # --- END OF FIX ---

            unique_id, source_text, is_correct, translated_text = row
            
            final_text = translated_text if translated_text else source_text

            parts = unique_id.split('_')
            mcq_id = int(parts[0])

            if mcq_id not in reconstructed_data:
                reconstructed_data[mcq_id] = {'id': mcq_id, 'question': '', 'options': []}

            if parts[1] == 'question':
                reconstructed_data[mcq_id]['question'] = final_text
            elif parts[1] == 'option':
                reconstructed_data[mcq_id]['options'].append({
                    'text': final_text,
                    'correct': is_correct.upper() == 'TRUE'
                })

    final_json_list = sorted(list(reconstructed_data.values()), key=lambda x: x['id'])

    print(f"\nSaving reconstructed data to '{FINAL_URDU_JSON}'...")
    with open(FINAL_URDU_JSON, 'w', encoding='utf-8') as f:
        json.dump(final_json_list, f, indent=2, ensure_ascii=False)
    
    print("\nSuccessfully created the final Urdu JSON file!")
    print("You can now use this with the HTML app generator.")

# --- Main Menu ---
if __name__ == "__main__":
    while True:
        print("\n--- MCQs Data Converter ---")
        print("Choose your operation:")
        print("1. Convert JSON to CSV (For Google Sheets translation)")
        print("2. Convert translated CSV back to JSON")
        print("3. Exit")
        
        choice = input("Enter your choice (1, 2, or 3): ")
        
        if choice == '1':
            convert_json_to_csv()
            break
        elif choice == '2':
            convert_csv_to_json()
            break
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")