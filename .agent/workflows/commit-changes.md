---
description: How to commit and push changes to GitHub
---

## Pre-Commit Checklist

1. **Review `.cursorrules`** — Read the project rules file at the repo root to ensure compliance.

2. **Update `DEVELOPER_GUIDE.md`** — If any code logic, CLI arguments, or features were changed, update the relevant sections:
   - Section 2 (Architecture & Core Components) for structural changes
   - Section 3 (Workflows) for workflow changes
   - Section 4 (CLI Reference) for new/modified command-line options
   - Section 5 (Technical Reference) for rendering or data processing changes

3. **Check `git status`** to review all modified, deleted, and untracked files.

4. **Stage changes**: `git add -A` (or selectively stage).

5. **Commit** with a descriptive message:
   ```bash
   git commit -m "Summary of change" -m "- Detail 1" -m "- Detail 2"
   ```

6. **Push** to the current branch:
   ```bash
   git push origin <branch-name>
   ```
