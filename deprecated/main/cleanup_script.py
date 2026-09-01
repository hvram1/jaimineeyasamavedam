import os
import shutil
from pathlib import Path

# Config
DEPRECATED_DIR = "deprecated"
KEEP_FILES = {
    "src", "data", "templates", "fonts", "website_configuration", 
    "CLI_USAGE.md", "README.md", "LICENSE", "requirements.txt", 
    ".gitignore", ".git", ".venv", ".gemini", "task.md", "project_overview.md", "implementation_plan.md", "walkthrough.md" # Brain files potentially
}
# Note: Artifacts like task.md might be in .gemini/..., not root, but good to be safe if they exist in root. 
# The user's root is c:\Users\sekha\OneDrive\Documents\GitHub\jaimineeyasamavedam
# The brain is external: c:\Users\sekha\.gemini\antigravity\brain\...
# So we only need to worry about files actually IN the repo root.

def deprecate_files():
    root = Path('.')
    deprecated_path = root / DEPRECATED_DIR
    deprecated_path.mkdir(exist_ok=True)
    
    # Get all items in root
    items = list(root.iterdir())
    
    for item in items:
        # Skip the deprecated dir itself
        if item.name == DEPRECATED_DIR:
            continue
            
        # Skip items in the KEEP list
        if item.name in KEEP_FILES:
            print(f"Skipping (Keep): {item.name}")
            continue
            
        # Move everything else
        try:
            dest = deprecated_path / item.name
            print(f"Moving: {item.name} -> {dest}")
            shutil.move(str(item), str(dest))
        except Exception as e:
            print(f"Error moving {item.name}: {e}")

if __name__ == "__main__":
    deprecate_files()
