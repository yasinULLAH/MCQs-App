import os
import json
import random
from tqdm import tqdm
import nltk
from nltk.corpus import wordnet

# Ensure you have run the NLTK downloader script before this.

def get_synonyms(word, pos_tag):
    """
    Gets synonyms for a word given its part-of-speech tag.
    """
    # Convert NLTK's POS tag to a format WordNet understands
    if pos_tag.startswith('J'): pos = wordnet.ADJ
    elif pos_tag.startswith('V'): pos = wordnet.VERB
    elif pos_tag.startswith('N'): pos = wordnet.NOUN
    elif pos_tag.startswith('R'): pos = wordnet.ADV
    else: return []

    synsets = wordnet.synsets(word, pos=pos)
    synonyms = set()
    for syn in synsets:
        for lemma in syn.lemmas():
            synonym = lemma.name().replace('_', ' ')
            if synonym.lower() != word.lower():
                synonyms.add(synonym)
    return list(synonyms)

def rewrite_text_with_synonyms(text_to_rewrite):
    """
    Rewrites a sentence by replacing some words with their synonyms.
    Crucially, it now attempts to skip Proper Nouns (NNP, NNPS).
    """
    if not text_to_rewrite:
        return ""

    words = nltk.word_tokenize(text_to_rewrite)
    tagged_words = nltk.pos_tag(words)
    
    new_words = []
    for word, tag in tagged_words:
        # --- SAFETY CHECK: Skip proper nouns ---
        if tag in ['NNP', 'NNPS']:
            new_words.append(word)
            continue
            
        # Try to replace other nouns, verbs, and adjectives
        if tag.startswith('N') or tag.startswith('V') or tag.startswith('J'):
            synonyms = get_synonyms(word, tag)
            if synonyms:
                new_word = random.choice(synonyms)
                new_words.append(new_word)
                continue
                
        # If no synonym is found or the word is not a candidate, keep the original
        new_words.append(word)

    # Rejoin the words into a sentence, cleaning up spacing around punctuation
    return ' '.join(new_words).replace(' .', '.').replace(' ?', '?').replace(' !', '!')


# --- MAIN EXECUTION ---
INPUT_FILENAME = "mcqs_data.json"
OUTPUT_FILENAME = "rewritten_mcqs_and_answers.json"

if not os.path.exists(INPUT_FILENAME):
    print(f"Error: Input file '{INPUT_FILENAME}' not found.")
    exit()

print(f"Loading questions from '{INPUT_FILENAME}'...")
with open(INPUT_FILENAME, 'r', encoding='utf-8') as f:
    original_mcqs = json.load(f)

print(f"Starting to rewrite {len(original_mcqs)} questions AND their options...")

rewritten_mcqs = []
for mcq in tqdm(original_mcqs, desc="Rewriting MCQs"):
    # Create a copy to work with
    new_mcq = mcq.copy()
    
    # 1. Rewrite the question
    new_mcq['question'] = rewrite_text_with_synonyms(mcq['question'])
    
    # 2. Rewrite the options (the new part)
    rewritten_options = []
    for option in mcq['options']:
        # Rewrite the text of the option
        rewritten_text = rewrite_text_with_synonyms(option['text'])
        rewritten_options.append({
            "text": rewritten_text,
            "correct": option['correct'] # The 'correct' flag is preserved
        })
    new_mcq['options'] = rewritten_options
    
    rewritten_mcqs.append(new_mcq)

print(f"\nSaving rewritten data to '{OUTPUT_FILENAME}'...")
with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
    json.dump(rewritten_mcqs, f, indent=2)

print("Process complete!")
print("A new file with rewritten questions and answers has been created.")
print(f"IMPORTANT: Please manually review '{OUTPUT_FILENAME}' for factual accuracy.")