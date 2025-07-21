import json

# Path to the JSON file
file_path = 'output_text/rewritten_final-Grantha.json'

# Read and load the JSON file
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print("File loaded successfully.")
        supersections = data.get('supersection', {})
        # Iterate through the data to find 'mantra_sets'
        for i, supersection in enumerate(supersections):
            for j, section in enumerate(supersections[supersection].get('sections', [])):
                sections = supersections[supersection].get('sections', [])
                for k, subsection in enumerate(sections[section].get('subsections', [])):
                        subsections = sections[section].get('subsections', [])
                        mantra_sets = subsections[subsection].get('mantra_sets', [])
                        for l, mantra_set in enumerate(mantra_sets):
                            if mantra_set.get('probableError') is True:
                                    image_ref = mantra_set.get('image-ref', '')
                                    mantra_words = [word_hash.get('word', '') for word_hash in mantra_set.get('mantra-words', [])]
                                    mantra_string = ' '.join(mantra_words)
                                    print(f"{image_ref} Mantra string: {mantra_string}")

except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
except json.JSONDecodeError:
    print(f"Error: Failed to decode JSON from the file '{file_path}'.")