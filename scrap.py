import requests
from bs4 import BeautifulSoup
import time
import concurrent.futures
from tqdm import tqdm

def scrape_pakmcqs_page(page_url):
    """
    Scrapes questions and answers from a single PakMcqs page URL.
    Returns a list of formatted strings for writing to a file.
    """
    try:
        # Using a timeout is crucial for concurrent requests
        response = requests.get(page_url, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        # Errors are expected in large-scale scraping, we can ignore this page
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    page_content_blocks = []
    articles = soup.find_all('article', class_='l-post')

    for article in articles:
        question_tag = article.find('h2', class_='post-title')
        question = question_tag.text.strip() if question_tag else "No question found"

        excerpt_tag = article.find('div', class_='excerpt')
        if excerpt_tag:
            options_text = excerpt_tag.get_text(separator='|||').strip()
            lines = [line.strip() for line in options_text.split('|||') if line.strip()]
            
            correct_answer_tag = excerpt_tag.find('strong')
            correct_answer = correct_answer_tag.text.strip() if correct_answer_tag else ""

            options = [line for line in lines if "Submitted by:" not in line and "Updated by:" not in line]

            # Build the string block for this question
            content_block = f"Question: {question}\n"
            for opt in options:
                # Check if the correct answer is part of the option
                if correct_answer and correct_answer in opt:
                    content_block += f"- {opt} [Correct]\n"
                else:
                    content_block += f"- {opt}\n"
            
            content_block += "-" * 30 + "\n\n"
            page_content_blocks.append(content_block)
            
    return page_content_blocks

# --- Main Execution ---
base_url = "https://pakmcqs.com/page/"
total_pages = 2110
output_filename = "pakmcqs_all_questions_fast.txt"

# Create a list of all URLs to scrape
urls = [f"{base_url}{page_number}" for page_number in range(1, total_pages + 1)]

# Number of parallel workers (threads). 10 is a safe and fast number.
MAX_WORKERS = 10

print(f"Starting concurrent scrape with {MAX_WORKERS} workers...")

# Open the output file
with open(output_filename, 'w', encoding='utf-8') as f:
    # Use ThreadPoolExecutor to manage concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # The 'executor.map' function applies 'scrape_pakmcqs_page' to each URL.
        # 'tqdm' wraps the process to show a progress bar.
        results = list(tqdm(executor.map(scrape_pakmcqs_page, urls), total=len(urls)))
        
        print("\nScraping complete. Writing all data to file...")
        
        # Iterate through the results (which is a list of lists) and write to file
        for page_blocks in results:
            for block in page_blocks:
                f.write(block)

print(f"\nProcess finished. All data saved to {output_filename}")