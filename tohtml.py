import os
from tqdm import tqdm

def parse_mcqs_from_txt(filepath):
    """
    Parses a structured text file to extract MCQs. This function remains the same.
    """
    if not os.path.exists(filepath):
        print(f"Error: The file '{filepath}' was not found.")
        print("Please make sure the .txt file is in the same directory as the script.")
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    mcqs = []
    current_mcq = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("Question:"):
            if current_mcq: mcqs.append(current_mcq)
            current_mcq = {"question": line[10:].strip(), "options": []}
        elif line.startswith("-"):
            if "question" in current_mcq:
                current_mcq["options"].append(line[1:].strip())
        elif line.startswith("---"):
            if current_mcq: mcqs.append(current_mcq)
            current_mcq = {}
            
    if current_mcq and "question" in current_mcq:
        mcqs.append(current_mcq)
        
    return mcqs

def create_fast_html_document(mcqs, output_filename):
    """
    Creates a beautifully formatted HTML file from a list of MCQs.
    This is extremely fast.
    """
    # Start of the HTML document with CSS for styling
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>PakMCQs Question Bank</title>
        <style>
            body {{ font-family: Cambria, Cochin, Georgia, Times, 'Times New Roman', serif; line-height: 1.6; margin: 40px; }}
            h1 {{ text-align: center; }}
            .mcq-block {{ margin-bottom: 25px; }}
            .question {{ font-weight: bold; font-size: 1.1em; }}
            ul {{ list-style-type: none; padding-left: 20px; }}
            li {{ margin-bottom: 5px; }}
            .correct {{ color: #008000; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>PakMCQs Complete Question Bank</h1>
        <p><i>A formatted collection of {len(mcqs)} questions.</i></p>
        <hr>
    """

    # Loop through all MCQs and append them as HTML strings
    for i, mcq in enumerate(tqdm(mcqs, desc="Generating HTML")):
        html_content += f'<div class="mcq-block">\n'
        html_content += f'  <p class="question">{i + 1}. {mcq["question"]}</p>\n'
        html_content += '  <ul>\n'
        
        for option_text in mcq['options']:
            is_correct = "[Correct]" in option_text
            clean_option = option_text.replace("[Correct]", "").strip()
            
            if is_correct:
                html_content += f'    <li class="correct">{clean_option}</li>\n'
            else:
                html_content += f'    <li>{clean_option}</li>\n'
        
        html_content += '  </ul>\n'
        html_content += '</div>\n'

    # Close the HTML tags
    html_content += """
    </body>
    </html>
    """

    # Write the entire string to a file at once
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

# --- Main Execution ---
INPUT_FILENAME = "pakmcqs_all_questions_fast.txt"
OUTPUT_FILENAME = "PakMCQs_Formatted.html"

print(f"Reading MCQs from '{INPUT_FILENAME}'...")
mcq_data = parse_mcqs_from_txt(INPUT_FILENAME)

if mcq_data:
    print(f"Successfully parsed {len(mcq_data)} MCQs.")
    create_fast_html_document(mcq_data, OUTPUT_FILENAME)
    print("\nProcess finished successfully!")
    print(f"Your beautifully formatted file is saved as: {OUTPUT_FILENAME}")
    print("\nNext Steps: Open the .html file with Microsoft Word and use 'Save As' to create a .docx file.")