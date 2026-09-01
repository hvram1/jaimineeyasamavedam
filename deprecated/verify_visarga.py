
import json
import re
import sys

def verify_visarga(filepath):
    print(f"Verifying {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    issues = []
    
    def check_text(key_path, text):
        if not isinstance(text, str): return
        
        # Check for space before visarga
        if ' ः' in text:
            issues.append(f"{key_path}: Found space before Visarga (' ः')")
            
        # Check for space before colon
        if ' :' in text:
            issues.append(f"{key_path}: Found space before Colon (' :')")
            
        # Check for Visarga followed by open paren (should be swapped)
        # We allow space between them just in case, but usually it's disallowed
        if re.search(r'ः\s*\(', text):
            issues.append(f"{key_path}: Found Visarga followed by accent ('ः(')")

    def traverse(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                traverse(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                traverse(item, f"{path}[{i}]")
        elif isinstance(obj, str):
            check_text(path, obj)

    traverse(data)

    if issues:
        print(f"Found {len(issues)} issues:")
        for issue in issues[:20]:
            print(f"  - {issue}")
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more.")
    else:
        print("No Visarga/Colon formatting issues found!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        verify_visarga(sys.argv[1])
    else:
        verify_visarga("data/output/Aaranam_latest_out.json")
