import re
import argparse
import sys
import json
from pathlib import Path

VERSION_FILE = Path("src/VERSION")
DEVANAGARI_DIGIT_CLASS = r'[०-९]'

def get_project_version():
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()
    return "1.0.0"

def set_project_version(version):
    VERSION_FILE.write_text(version.strip())

def increment_project_version():
    v = get_project_version()
    parts = v.split('.')
    if len(parts) == 3:
        parts[2] = str(int(parts[2]) + 1)
        new_v = ".".join(parts)
        set_project_version(new_v)
        return new_v
    return v

def int_to_devanagari(n):
    devanagari_digits = "०१२३४५६७८९"
    return "".join(devanagari_digits[int(d)] for d in str(n))

def inject_metadata_to_text(content, version, timestamp):
    # Regex to find existing metadata block
    meta_pattern = r'# \[JSV METADATA\].*?# \[END METADATA\]\s*'
    new_meta = f"# [JSV METADATA]\n# Version: {version}\n# Generated At: {timestamp}\n# [END METADATA]\n\n"
    
    if re.search(meta_pattern, content, re.DOTALL):
        # Substitute existing metadata
        return re.sub(meta_pattern, new_meta, content, flags=re.DOTALL)
    else:
        # Prepend new metadata
        return new_meta + content

def get_generated_metadata():
    from datetime import datetime
    return {
        "version": get_project_version(),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def validate_structural_tags(lines):
    """
    Checks if all # Start and # End tags for SuperSections, Sections, SubSections,
    Rik Metadata, Rik Text, and Mantra Sets are correctly paired and balanced.
    If an error is found, it prints the location and exits to prevent corruption.
    """
    print("  Structural Integrity Check...")
    stack = []
    errors = []
    
    tag_types = [
        "SuperSection Title", "Section Title", "SubSection Title",
        "Rik Metadata", "Rik Text", "Mantra Sets", "Footnote"
    ]
    
    start_pattern = re.compile(r'#\s*Start of (.*?) -- (.*?) ##')
    end_pattern = re.compile(r'#\s*End of (.*?) -- (.*?) ##')
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        start_m = start_pattern.search(line)
        if start_m:
            tag_name = start_m.group(1).strip()
            tag_id = start_m.group(2).strip()
            if tag_name in tag_types:
                stack.append({"name": tag_name, "id": tag_id, "line": line_num})
        
        end_m = end_pattern.search(line)
        if end_m:
            tag_name = end_m.group(1).strip()
            tag_id = end_m.group(2).strip()
            if tag_name in tag_types:
                if not stack:
                    errors.append(f"Line {line_num}: Found '# End of {tag_name}' but no Start tag is open.")
                else:
                    last = stack.pop()
                    if last["name"] != tag_name:
                        errors.append(f"Line {line_num}: Tag mismatch! Expected '# End of {last['name']}' (opened at line {last['line']}), but found '# End of {tag_name}'.")

    while stack:
        last = stack.pop()
        errors.append(f"Line {last['line']}: Unclosed block! '# Start of {last['name']}' (id: {last['id']}) was never closed.")
        
    if errors:
        print("\n[CRITICAL ERROR] Structural Integrity compromised:")
        for err in errors:
            print(f"  - {err}")
        print("\nRenumbering ABORTED to prevent data corruption. Please fix these tags in the text file and try again.")
        sys.exit(1)
    
    print("  Integrity verified. Proceeding to renumbering...")

def renumber_text_file(input_file, output_file=None, preserve_super=False, reset_per_super=False, reset_samam_per_section=True, reset_samam_per_super=True, start_sup=1, start_sec=1, start_sub=1, preserve_all=False, no_renumber=False, custom_version=None):
    print(f"Renumbering TEXT file: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Pre-flight Validation
    validate_structural_tags(lines)

    if no_renumber:
        final_lines_str = "".join(lines)
    else:
        # ─── Pass 1: Global Sequence Identifiers (section_N, subsection_N) ───
        current_sup = start_sup - 1
        current_sec = start_sec - 1
        current_sub = start_sub - 1
        
        new_lines = []
        for line in lines:
            if re.search(r'#\s*Start of SuperSection Title', line):
                current_sup += 1
                if reset_per_super:
                    current_sec = 0 # Will be incremented to 1 at next Section
                    current_sub = 0
                if not preserve_super:
                    line = re.sub(r'supersection_\d+', f'supersection_{current_sup}', line)
            elif re.search(r'#\s*End of SuperSection Title', line):
                if not preserve_super:
                    line = re.sub(r'supersection_\d+', f'supersection_{current_sup}', line)
            
            elif re.search(r'#\s*Start of Section Title', line):
                current_sec += 1
                if not preserve_all:
                    line = re.sub(r'section_\d+', f'section_{max(1, current_sec)}', line)
            elif re.search(r'#\s*End of Section Title', line):
                if not preserve_all:
                    line = re.sub(r'section_\d+', f'section_{max(1, current_sec)}', line)
            
            elif re.search(r'#\s*Start of SubSection Title', line):
                current_sub += 1
                if not preserve_all:
                    line = re.sub(r'subsection_\d+', f'subsection_{max(1, current_sub)}', line)
            elif re.search(r'#\s*End of SubSection Title', line):
                if not preserve_all:
                    line = re.sub(r'subsection_\d+', f'subsection_{max(1, current_sub)}', line)

            new_lines.append(line)

        print(f"  Pass 1 done: {max(0, current_sup)} SuperSections, {max(0, current_sec)} Sections, {max(0, current_sub)} SubSections.")

        # ─── Pass 2: Align Rik / Metadata / Mantra blocks ───
        pass2_lines = []
        subsection_pattern = r'#\s*Start of SubSection Title\s*--\s*subsection_(\d+)'

        for i, line in enumerate(new_lines):
            if re.search(r'#\s*(Start|End) of (Mantra Sets)', line):
                prev_sub_num = None
                for j in range(i - 1, -1, -1):
                    m = re.search(subsection_pattern, new_lines[j])
                    if m:
                        prev_sub_num = m.group(1)
                        break
                if prev_sub_num is not None:
                    line = re.sub(r'subsection_\d+', f'subsection_{prev_sub_num}', line)

            elif re.search(r'#\s*(Start|End) of (Rik Text|Rik Metadata)', line):
                next_sub_num = None
                for j in range(i + 1, len(new_lines)):
                    m = re.search(subsection_pattern, new_lines[j])
                    if m:
                        next_sub_num = m.group(1)
                        break
                if next_sub_num is not None:
                    line = re.sub(r'subsection_\d+', f'subsection_{next_sub_num}', line)

            pass2_lines.append(line)
        print(f"  Pass 2 done: Multi-directional block alignment complete.")

        # ─── Pass 3: Renumber Samam and Rik verse counters ───
        final_lines = []
        in_mantra_set = False
        in_rik_text = False
        in_subsection_title = False

        samam_counter = 1
        rik_counter = 1
        global_samam_total = 0
        global_rik_total = 0

        # Recognize standard dandals and the heavy bar for recovery
        verse_marker = r'(?:॥|\|\||।।।|┃|।)'
        # Pattern for renumbering
        verse_pattern = rf'({verse_marker})\s*{DEVANAGARI_DIGIT_CLASS}+\s*({verse_marker})'

        for line in pass2_lines:
            # Handle block resets
            if re.search(r'#\s*Start of SuperSection Title', line):
                if reset_samam_per_section or reset_samam_per_super:
                    samam_counter = 1
                    rik_counter = 1
            elif re.search(r'#\s*Start of Section Title', line):
                if reset_samam_per_section:
                    samam_counter = 1
                    rik_counter = 1

            # Determine Mode (Mantra vs Rik)
            if re.search(r'#\s*Start of Mantra Sets', line):
                in_mantra_set = True
            elif re.search(r'#\s*End of Mantra Sets', line):
                # Close after processing this line (in case tag is joined)
                pass 
            elif re.search(r'#\s*Start of Rik Text', line):
                in_rik_text = True
            elif re.search(r'#\s*End of Rik Text', line):
                pass

            # Handle Titling danda cleanup
            if re.search(r'#\s*Start of SubSection Title', line):
                in_subsection_title = True
            elif re.search(r'#\s*End of SubSection Title', line):
                in_subsection_title = False
            
            if in_subsection_title and line.strip() and not line.strip().startswith('#'):
                text = line.strip()
                if (text.startswith('॥') or text.startswith('┃')) and (text.endswith('॥') or text.endswith('┃') or text.endswith(')')):
                    prefix = line[:line.find('॥')] if '॥' in line else line[:line.find('┃')]
                    clean_text = re.sub(rf'{DEVANAGARI_DIGIT_CLASS}|\d+-', '', text).replace('॥', '').replace('┃', '').replace('(', '').replace(')', '').strip()
                    line = f"{prefix}॥ {clean_text} ॥\n"

            # Apply Renumbering
            if in_mantra_set or in_rik_text:
                def verse_repl(m):
                    nonlocal samam_counter, rik_counter, global_samam_total, global_rik_total
                    if in_mantra_set:
                        num = int_to_devanagari(samam_counter)
                        samam_counter += 1
                        global_samam_total += 1
                    else:
                        num = int_to_devanagari(rik_counter)
                        rik_counter += 1
                        global_rik_total += 1
                    return f"॥ {num} ॥"
                
                # Check for joined tags
                if '#' in line:
                    parts = line.split('#', 1)
                    parts[0] = re.sub(verse_pattern, verse_repl, parts[0])
                    line = f"{parts[0].rstrip()}\n#{parts[1]}"
                else:
                    line = re.sub(verse_pattern, verse_repl, line)

            # Close blocks AFTER processing the line to ensure joined tags are caught
            if re.search(r'#\s*End of Mantra Sets', line):
                in_mantra_set = False
            elif re.search(r'#\s*End of Rik Text', line):
                in_rik_text = False

            final_lines.append(line)
    
        final_lines_str = "".join(final_lines)
        print(f"  Pass 3 done: {global_samam_total} Samams, {global_rik_total} Riks renumbered.")

    # Get metadata and inject
    meta = get_generated_metadata()
    version_to_use = custom_version if custom_version else meta["version"]
    final_content = inject_metadata_to_text(final_lines_str, version_to_use, meta["generated_at"])

    if not output_file: output_file = input_file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"Success! Final state: {max(0, current_sup)} SuperSections, {max(0, current_sec)} Sections, {max(0, current_sub)} SubSections. Total Samams: {global_samam_total}, Total Riks: {global_rik_total}")

def main():
    import yaml
    config_path = Path("src/pipeline_config.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    renum_cfg = config.get('renumber_sooktam', {})
    defaults = renum_cfg.get('defaults', {})

    parser = argparse.ArgumentParser(description="Renumber JSV files.")
    parser.add_argument('input_file', help="Path to input file")
    parser.add_argument('--output', help="Output file path")
    parser.add_argument('--type', '-t', choices=['samhita', 'aaranam'], help="Type of text")
    parser.add_argument('--jsv-version', help="Manual version")
    parser.add_argument('--no-increment', action='store_true', help="Don't increment version")
    parser.add_argument('--no-renumber', action='store_true', help="Only update metadata")
    
    args = parser.parse_args()

    type_cfg = renum_cfg.get(args.type, {}) if args.type else {}
    
    def resolve(cli_val, yaml_val, global_val, fallback):
        if cli_val is not None: return cli_val
        if yaml_val is not None: return yaml_val
        if global_val is not None: return global_val
        return fallback

    reset_sup = resolve(None, type_cfg.get('reset_per_super'), None, False)
    target_version = args.jsv_version or (get_project_version() if args.no_increment else increment_project_version())

    renumber_text_file(args.input_file, 
                       output_file=args.output,
                       start_sup=type_cfg.get('start_super', 1),
                       start_sec=type_cfg.get('start_section', 1),
                       start_sub=type_cfg.get('start_subsection', 1),
                       reset_per_super=reset_sup,
                       no_renumber=args.no_renumber,
                       custom_version=target_version)

if __name__ == "__main__":
    main()
