import os
import json
from tqdm import tqdm

def parse_mcqs_from_txt(filepath):
    """
    Parses a structured text file and returns a clean list of MCQ dictionaries.
    """
    if not os.path.exists(filepath):
        print(f"Error: The file '{filepath}' was not found.")
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    mcqs = []
    current_mcq = {}
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith("Question:"):
            if current_mcq: mcqs.append(current_mcq)
            current_mcq = {"question": line[10:].strip(), "options": []}
        elif line.startswith("-"):
            if "question" in current_mcq:
                # Store options with a flag for correctness
                is_correct = "[Correct]" in line
                clean_option = line[1:].replace("[Correct]", "").strip()
                current_mcq["options"].append({"text": clean_option, "correct": is_correct})
        elif line.startswith("---"):
            if current_mcq: mcqs.append(current_mcq)
            current_mcq = {}
    if current_mcq and "question" in current_mcq: mcqs.append(current_mcq)
    return mcqs

def create_app_files(mcqs, json_filename, html_filename):
    """
    Creates the mcqs_data.json and the main HTML app shell.
    """
    print(f"Creating JSON data file: {json_filename}")
    # Assign a unique ID to each question for IndexedDB
    for i, mcq in enumerate(mcqs):
        mcq['id'] = i + 1
        
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(mcqs, f)

    # --- This is the HTML/CSS/JS for the application shell ---
    html_shell = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PakMCQs Interactive Study App</title>
    <style>
        :root {{
            --bg-color: #f4f7f9; --card-bg-color: #ffffff; --text-color: #2c3e50;
            --question-color: #212529; --correct-color: #198754; --border-color: #dee2e6;
            --shadow-color: rgba(0, 0, 0, 0.05); --header-bg: #ffffff; --accent-color: #007bff;
        }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background-color: var(--bg-color); color: var(--text-color); transition: background-color 0.3s, color 0.3s; }}
        body.dark-mode {{
            --bg-color: #121212; --card-bg-color: #1e1e1e; --text-color: #e0e0e0;
            --question-color: #ffffff; --correct-color: #28a745; --border-color: #444;
            --shadow-color: rgba(0, 0, 0, 0.2); --header-bg: #1e1e1e; --accent-color: #0d6efd;
        }}
        .header {{ position: sticky; top: 0; z-index: 1000; background-color: var(--header-bg); padding: 15px 30px; box-shadow: 0 2px 10px var(--shadow-color); border-bottom: 1px solid var(--border-color); }}
        .controls {{ display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; gap: 20px; }}
        #search-input {{ width: 100%; padding: 10px 15px; font-size: 16px; border-radius: 5px; border: 1px solid var(--border-color); background-color: var(--bg-color); color: var(--text-color); }}
        #theme-toggle-btn {{ padding: 10px 15px; border: none; background: none; cursor: pointer; font-size: 24px; }}
        main {{ padding: 20px; max-width: 1200px; margin: 0 auto; }}
        .mcq-block {{ background-color: var(--card-bg-color); border: 1px solid var(--border-color); border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px var(--shadow-color); }}
        .question {{ font-size: 1.1em; font-weight: 600; color: var(--question-color); margin-bottom: 15px; }}
        .options ul {{ list-style-type: none; padding-left: 5px; margin: 0; }}
        .options li {{ padding: 8px; border-radius: 5px; }}
        .correct-answer {{ color: var(--correct-color); font-weight: bold; }}
        .revealed .correct-answer {{ background-color: rgba(25, 135, 84, 0.1); }}
        .show-answer-btn {{ margin-top: 15px; padding: 8px 15px; border: 1px solid var(--border-color); border-radius: 5px; cursor: pointer; background-color: var(--bg-color); color: var(--text-color); font-weight: 500; }}
        #pagination {{ display: flex; justify-content: center; align-items: center; flex-wrap: wrap; padding: 20px; gap: 5px; }}
        #pagination button {{ padding: 10px 15px; cursor: pointer; border: 1px solid var(--border-color); background-color: var(--card-bg-color); color: var(--text-color); }}
        #pagination button.active {{ background-color: var(--accent-color); color: var(--card-bg-color); font-weight: bold; border-color: var(--accent-color); }}
        #status-bar {{ text-align: center; padding: 10px; color: #6c757d; }}
        .loading-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); color: white; display: flex; justify-content: center; align-items: center; font-size: 1.5em; z-index: 2000; }}
    </style>
</head>
<body>
    <div class="loading-overlay" id="loading-overlay">
        <p>Loading app...</p>
    </div>
    
    <header class="header">
        <div class="controls">
            <input type="search" id="search-input" placeholder="Type to search questions...">
            <button id="theme-toggle-btn" title="Toggle Dark/Light Mode">🌙</button>
        </div>
    </header>

    <main id="mcq-container"></main>
    <div id="status-bar"></div>
    <nav id="pagination"></nav>

    <script>
        document.addEventListener('DOMContentLoaded', async () => {{
            // --- CONFIGURATION ---
            const DB_NAME = 'PakMCQsDB';
            const STORE_NAME = 'mcqs';
            const DB_VERSION = 1; // Increment this if you change the data structure
            const DATA_URL = '{json_filename}';
            const MCQS_PER_PAGE = 50;

            const loadingOverlay = document.getElementById('loading-overlay');
            const loadingText = loadingOverlay.querySelector('p');
            const mcqContainer = document.getElementById('mcq-container');
            const paginationContainer = document.getElementById('pagination');
            const searchInput = document.getElementById('search-input');
            const statusBar = document.getElementById('status-bar');
            
            let db;
            let totalQuestions = {len(mcqs)};
            let currentPage = 1;

            // --- DATABASE LOGIC ---
            function openDB() {{
                return new Promise((resolve, reject) => {{
                    const request = indexedDB.open(DB_NAME, DB_VERSION);
                    request.onerror = () => reject("Error opening DB");
                    request.onsuccess = (event) => {{
                        db = event.target.result;
                        resolve(db);
                    }};
                    request.onupgradeneeded = (event) => {{
                        let db = event.target.result;
                        if (!db.objectStoreNames.contains(STORE_NAME)) {{
                            const store = db.createObjectStore(STORE_NAME, {{ keyPath: 'id' }});
                            store.createIndex('question_idx', 'question', {{ unique: false }});
                        }}
                    }};
                }});
            }}

            async function populateDB() {{
                loadingText.textContent = 'Setting up for first use... Fetching data...';
                const response = await fetch(DATA_URL);
                const mcqs = await response.json();
                
                loadingText.textContent = 'Populating local database... Please wait.';
                const transaction = db.transaction(STORE_NAME, 'readwrite');
                const store = transaction.objectStore(STORE_NAME);
                store.clear();

                for (const mcq of mcqs) {{
                    store.put(mcq);
                }}

                return new Promise((resolve) => {{
                    transaction.oncomplete = () => {{
                        localStorage.setItem('db_version', DB_VERSION);
                        localStorage.setItem('total_questions', mcqs.length);
                        totalQuestions = mcqs.length;
                        resolve();
                    }};
                }});
            }}
            
            async function getData(page, query = '') {{
                return new Promise((resolve) => {{
                    const transaction = db.transaction(STORE_NAME, 'readonly');
                    const store = transaction.objectStore(STORE_NAME);
                    const results = [];
                    let count = 0;
                    const lowerQuery = query.toLowerCase();
                    const range = IDBKeyRange.bound((page - 1) * MCQS_PER_PAGE, page * MCQS_PER_PAGE);

                    store.openCursor().onsuccess = (event) => {{
                        const cursor = event.target.result;
                        if (cursor) {{
                            const question = cursor.value;
                            if (query === '' || question.question.toLowerCase().includes(lowerQuery)) {{
                                results.push(question);
                            }}
                            cursor.continue();
                        }} else {{
                            resolve(results);
                        }}
                    }};
                }});
            }}
            
             async function getFilteredData(page, query) {{
                return new Promise((resolve) => {{
                    const transaction = db.transaction(STORE_NAME, 'readonly');
                    const store = transaction.objectStore(STORE_NAME);
                    const results = [];
                    const lowerQuery = query.toLowerCase();

                    store.openCursor().onsuccess = (event) => {{
                        const cursor = event.target.result;
                        if(cursor) {{
                            if(cursor.value.question.toLowerCase().includes(lowerQuery)) {{
                                results.push(cursor.value);
                            }}
                            cursor.continue();
                        }} else {{
                            const startIndex = (page - 1) * MCQS_PER_PAGE;
                            const endIndex = startIndex + MCQS_PER_PAGE;
                            resolve({{
                                data: results.slice(startIndex, endIndex),
                                total: results.length
                            }});
                        }}
                    }};
                }});
            }}

            // --- UI RENDERING ---
            function renderMCQs(mcqs) {{
                mcqContainer.innerHTML = '';
                for (const mcq of mcqs) {{
                    let optionsHTML = mcq.options.map(opt => 
                        `<li class="${{opt.correct ? 'correct-answer' : ''}}">${{opt.text}}</li>`
                    ).join('');

                    mcqContainer.innerHTML += `
                        <div class="mcq-block">
                            <p class="question">${{mcq.id}}. ${{mcq.question}}</p>
                            <div class="options"><ul>${{optionsHTML}}</ul></div>
                            <button class="show-answer-btn">Show Answer</button>
                        </div>
                    `;
                }}
            }}

            function renderPagination(totalItems, page) {{
                paginationContainer.innerHTML = '';
                const pageCount = Math.ceil(totalItems / MCQS_PER_PAGE);
                if (pageCount <= 1) return;

                // Simplified pagination for performance
                let start = Math.max(1, page - 2);
                let end = Math.min(pageCount, page + 2);
                
                const buttons = [];
                if(page > 1) buttons.push(`<button data-page="${{page-1}}">«</button>`);
                if(start > 1) buttons.push(`<button data-page="1">1</button><button disabled>...</button>`);
                
                for(let i=start; i<=end; i++) {{
                    buttons.push(`<button class="${{i === page ? 'active' : ''}}" data-page="${{i}}">${{i}}</button>`);
                }}
                
                if(end < pageCount) buttons.push(`<button disabled>...</button><button data-page="${{pageCount}}">${{pageCount}}</button>`);
                if(page < pageCount) buttons.push(`<button data-page="${{page+1}}">»</button>`);
                
                paginationContainer.innerHTML = buttons.join('');
            }}

            async function updateView(page = 1, query = '') {{
                const {{data, total}} = await getFilteredData(page, query);
                renderMCQs(data);
                renderPagination(total, page);
                const startItem = (page - 1) * MCQS_PER_PAGE + 1;
                const endItem = startItem + data.length - 1;
                statusBar.textContent = total > 0 ? `Showing ${{startItem}}-${{endItem}} of ${{total}} questions.` : 'No questions found.';
            }}

            // --- INITIALIZATION & EVENT LISTENERS ---
            try {{
                db = await openDB();
                const storedVersion = parseInt(localStorage.getItem('db_version'));
                if (storedVersion !== DB_VERSION) {{
                    await populateDB();
                }} else {{
                    totalQuestions = parseInt(localStorage.getItem('total_questions')) || totalQuestions;
                }}
                
                loadingOverlay.style.display = 'none';
                await updateView();

            }} catch (error) {{
                loadingText.textContent = 'Error: Could not initialize the application.';
                console.error(error);
            }}
            
            searchInput.addEventListener('input', () => updateView(1, searchInput.value));
            
            paginationContainer.addEventListener('click', (e) => {{
                if (e.target.tagName === 'BUTTON' && e.target.dataset.page) {{
                    updateView(parseInt(e.target.dataset.page), searchInput.value);
                }}
            }});
            
            mcqContainer.addEventListener('click', (e) => {{
                if (e.target.classList.contains('show-answer-btn')) {{
                    const optionsDiv = e.target.previousElementSibling;
                    const isRevealed = optionsDiv.classList.toggle('revealed');
                    e.target.textContent = isRevealed ? 'Hide Answer' : 'Show Answer';
                }}
            }});
            
            // Dark Mode
            const themeToggleBtn = document.getElementById('theme-toggle-btn');
            themeToggleBtn.addEventListener('click', () => {{
                document.body.classList.toggle('dark-mode');
                const isDark = document.body.classList.contains('dark-mode');
                localStorage.setItem('theme', isDark ? 'dark' : 'light');
                themeToggleBtn.textContent = isDark ? '☀️' : '🌙';
            }});
            if (localStorage.getItem('theme') === 'dark') {{
                document.body.classList.add('dark-mode');
                themeToggleBtn.textContent = '☀️';
            }}
        }});
    </script>
</body>
</html>
    """
    
    print(f"Creating HTML app shell: {html_filename}")
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_shell)

# --- Main Execution ---
INPUT_FILENAME = "pakmcqs_all_questions_fast.txt"
JSON_OUTPUT = "mcqs_data.json"
HTML_OUTPUT = "PakMCQs_App.html"

print("Starting process...")
mcq_data = parse_mcqs_from_txt(INPUT_FILENAME)

if mcq_data:
    create_app_files(mcq_data, JSON_OUTPUT, HTML_OUTPUT)
    print("\nProcess finished successfully!")
    print(f"Two files were created: '{JSON_OUTPUT}' and '{HTML_OUTPUT}'.")
    print("Just double-click 'PakMCQs_App.html' to run your new application!")