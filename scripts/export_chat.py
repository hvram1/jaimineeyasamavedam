#!/usr/bin/env python3
"""
Export Antigravity Conversation Transcript to clean, formatted Markdown.
"""

import json
import os
import re
from datetime import datetime

TRANSCRIPT_PATH = r"C:\Users\sekha\.gemini\antigravity-ide\brain\2c4604c7-af52-4f94-8cf1-3032a9cf77a0\.system_generated\logs\transcript_full.jsonl"
OUTPUT_MD = r"c:\Users\sekha\OneDrive\Documents\GitHub\jaimineeyasamavedam\conversation_export.md"

def clean_user_content(content: str) -> str:
    """Extract clean user message from raw payload."""
    if not content:
        return ""
    
    # Check for <USER_REQUEST> tags
    req_match = re.search(r"<USER_REQUEST>\s*([\s\S]*?)\s*</USER_REQUEST>", content)
    if req_match:
        text = req_match.group(1).strip()
    else:
        # Strip system XML tags
        text = re.sub(r"<ADDITIONAL_METADATA>[\s\S]*?</ADDITIONAL_METADATA>", "", content)
        text = re.sub(r"<SYSTEM_[A-Z_]+>[\s\S]*?</SYSTEM_[A-Z_]+>", "", text)
        text = text.strip()
    
    # Check for user actions / file view indications
    user_action_match = re.search(r"The USER performed the following action:\s*([\s\S]*?)(?:File Path:|$)", content)
    action_note = ""
    if user_action_match:
        action_note = f"> *Action: {user_action_match.group(1).strip()}*\n\n"
    
    return action_note + text

def export_transcript():
    if not os.path.exists(TRANSCRIPT_PATH):
        print(f"Error: Transcript not found at {TRANSCRIPT_PATH}")
        return

    turns = []
    current_turn = None
    
    with open(TRANSCRIPT_PATH, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            
            source = entry.get("source")
            entry_type = entry.get("type")
            content = entry.get("content", "")
            step_index = entry.get("step_index", 0)
            
            if entry_type == "USER_INPUT":
                cleaned = clean_user_content(content)
                if cleaned:
                    turns.append({
                        "role": "User",
                        "content": cleaned,
                        "step": step_index,
                    })
            elif entry_type == "PLANNER_RESPONSE":
                cleaned = content.strip()
                if cleaned:
                    turns.append({
                        "role": "Antigravity Assistant",
                        "content": cleaned,
                        "step": step_index,
                    })

    # Build Markdown document
    out_lines = [
        "# Antigravity Conversation Transcript",
        "",
        f"- **Project**: Jaimineeya Samavedam (`sekharnarayanaswamy-del/jaimineeyasamavedam`)",
        f"- **Conversation ID**: `2c4604c7-af52-4f94-8cf1-3032a9cf77a0`",
        f"- **Export Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Total Dialogue Turns**: {len(turns)}",
        "",
        "---",
        "",
        "## Table of Contents & Chronological Turns",
        "",
    ]
    
    turn_counter = 1
    for turn in turns:
        role = turn["role"]
        body = turn["content"]
        
        if role == "User":
            out_lines.append(f"### Turn {turn_counter}: 👤 User Request")
            out_lines.append("")
            out_lines.append(body)
            out_lines.append("")
            out_lines.append("---")
            out_lines.append("")
            turn_counter += 1
        else:
            out_lines.append(f"#### 🤖 Assistant Response")
            out_lines.append("")
            out_lines.append(body)
            out_lines.append("")
            out_lines.append("---")
            out_lines.append("")

    # Save file
    os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
    with open(OUTPUT_MD, "w", encoding="utf-8") as out_f:
        out_f.write("\n".join(out_lines))
        
    print(f"Successfully exported {len(turns)} conversation turns to:")
    print(f"  {OUTPUT_MD}")
    print(f"  File size: {os.path.getsize(OUTPUT_MD):,} bytes")

if __name__ == "__main__":
    export_transcript()
