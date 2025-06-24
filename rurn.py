import nltk

# List of all required NLTK packages for your script
required_packages = [
    'punkt',
    'punkt_tab',
    'averaged_perceptron_tagger',
    'averaged_perceptron_tagger_eng', # The new one from the error
    'wordnet'
]

print("--- Starting NLTK Data Download ---")
for package in required_packages:
    try:
        print(f"Downloading '{package}'...")
        nltk.download(package)
        print(f"Successfully downloaded '{package}'.")
    except Exception as e:
        print(f"Error downloading {package}: {e}")
print("\n--- All downloads attempted. You can now run your main script. ---")