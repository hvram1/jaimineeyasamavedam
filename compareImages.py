import os
import re
import sys
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import glob
import json

# Load pretrained ResNet50 model from a local file
local_model_path = os.path.join(os.path.dirname(__file__), 'resnet50-0676ba61.pth')
model = resnet50(pretrained=False)
model.load_state_dict(torch.load(local_model_path))
model = torch.nn.Sequential(*list(model.children())[:-1])  # Remove the classification layer
model.eval()  # Set the model to evaluation mode

# Define image preprocessing pipeline
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def get_files_by_pattern(directory, pattern):
    return [f for f in os.listdir(directory) if re.match(pattern, f)]

def extract_features(image_path):
    # Load and preprocess the image
    img = Image.open(image_path).convert("RGB")
    img_tensor = preprocess(img).unsqueeze(0)  # Add batch dimension
    with torch.no_grad():
        features = model(img_tensor).squeeze().numpy()  # Extract features and convert to numpy
    return features

def find_best_match(iword_features, word_features, word_files):
    best_match = None
    best_score = -1  # Higher cosine similarity is better
    for wf, wf_features in zip(word_files, word_features):
        score = cosine_similarity([iword_features], [wf_features])[0][0]
        if score > best_score:
            best_score = score
            best_match = wf
    return best_match, best_score

def main():
    
    # Load the JSON file containing mantra hash
    mantra_hash_path = os.path.join("output_text", "mantra_hash.json")
    if not os.path.exists(mantra_hash_path):
        print(f"File {mantra_hash_path} not found.")
        sys.exit(1)

    with open(mantra_hash_path, "r") as f:
        mantra_hash = json.load(f)
    print(f"Loaded mantra hash with {len(mantra_hash)} entries.")
    # Find all directories under output_text/lines/* that start with the pattern combined_
    directory_pattern = os.path.join("output_text", "lines", "page*","combined_*")
    directories = [d for d in glob.glob(directory_pattern) if os.path.isdir(d)]

    if not directories:
        print("No directories found matching the pattern combined_")
        sys.exit(1)
    print(f" Found {len(directories)} directories")
    # Sort directories primarily by the numerical order of page_nnn and then by combined_xx_yy
    directories.sort(key=lambda d: (
        int(re.search(r"page_(\d+)", d).group(1)),  # Extract and sort by page number
        tuple(map(int, re.search(r"combined_(\d+)_(\d+)", d).groups()))  # Extract and sort by xx_yy
    ))
    
    
    for directory in directories:
        
        print(f"Using directory: {directory}")
        key=f'{directory}.png'
        char_hash = {int(k): v for k, v in mantra_hash.get(key, {}).items()}
        if not char_hash:
            print(f"char_hash is empty for key: {key}. Skipping this directory.")
            continue
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist. Skipping.")
            continue
        print(f" using {char_hash} for {key}")
        iword_pattern = r"^i-word_(\d+)_(\d+)\.png$"
        word_pattern = r"^t-word_(\d+)\.png$"

        iword_files = get_files_by_pattern(directory, iword_pattern)
        word_files = get_files_by_pattern(directory, word_pattern)

        # Sort iword_files to start with i-word_0
        iword_files.sort()
        # Sort word_files alphabetically
        word_files.sort()

        # Keep track of used word files
        used_word_files = set()

        # Extract features for all word_z.png images
        word_features = [extract_features(os.path.join(directory, wf)) for wf in word_files]



        #char_hash={0: 0, 1: 1, 4: 2, 5: 3, 7: 4, 9: 5, 11: 6, 13: 7, 14: 8, 15: 9, 17: 10, 19: 11, 21: 12, 23: 13,25:14}
        for iwf in iword_files:
            iwf_path = os.path.join(directory, iwf)
            # Extract the first and second digits from the iword filename
            match = re.search(iword_pattern, iwf)
            if match:
                swara_number = int(match.group(1))
                mantra_character = int(match.group(2))
            else:
                print(f"Filename {iwf} does not match the expected pattern.")
                continue
            iword_features = extract_features(iwf_path)
            best_match, best_score = None, -1
            best_rank = float('inf')  # Lower rank is better
            c1=None
            if mantra_character in char_hash:
                c1 = char_hash[mantra_character]
            #else:
            lower_keys = [k for k in char_hash.keys() if k < mantra_character]
            higher_keys = [k for k in char_hash.keys() if k > mantra_character]
            lower_key = max(lower_keys) if lower_keys else None
            higher_key = min(higher_keys) if higher_keys else None
            char_value = (char_hash.get(lower_key),c1, char_hash.get(higher_key))
            print(f"Using char_value: {char_value} for {iwf}")
            # Filter word_files based on char_value
            filtered_word_files = [
                wf for wf in word_files
                if any(wf == f"t-word_{cv}.png" for cv in char_value if cv is not None )
            ]
            print(f" filtered_word_files are {filtered_word_files}")
            filtered_word_features = [
                wf_features for wf, wf_features in zip(word_files, word_features)
                if any(wf == f"t-word_{cv}.png" for cv in char_value if cv is not None)
            ]
            for rank, (wf, filtered_wf_features) in enumerate(zip(filtered_word_files, filtered_word_features)):
                if wf in used_word_files:
                    continue  # Skip already used word files

                score = cosine_similarity([iword_features], [filtered_wf_features])[0][0]
                if score > best_score or (score == best_score and rank < best_rank):
                    best_score = score
                    best_match = wf
                    best_rank = rank

            if best_match:
                used_word_files.add(best_match)  # Mark the best match as used
                print(f"Best match for {iwf}: {best_match} (Cosine Similarity: {best_score:.4f}, Rank: {best_rank})")
            else:
                print(f"No match found for {iwf}")

if __name__ == "__main__":
    main()