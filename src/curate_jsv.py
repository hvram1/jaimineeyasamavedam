import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime


def to_devanagari_num(n):
    """Convert an integer to Devanagari numeral string."""
    deva_digits = '०१२३४५६७८९'
    return ''.join(deva_digits[int(d)] for d in str(n))


def get_samam_numbers(sub_data):
    """
    Extract all Samam numbers from the corrected-mantra text of a subsection.
    Samam boundaries are marked by ॥N॥ where N is in Devanagari digits.
    Returns a list of integer Samam numbers found.
    """
    mantras = sub_data.get('corrected-mantra_sets', [])
    mantra_text = ' '.join(
        m.get('corrected-mantra', '') for m in mantras if isinstance(m, dict)
    )
    # Match ॥ followed by optional spaces, Devanagari digits, optional spaces, followed by ॥
    matches = re.findall(r'॥\s*([०-९\d]+)\s*॥', mantra_text)
    result = []
    for m in matches:
        # Convert Devanagari digits to int
        arabic = m.translate(str.maketrans('०१२३४५६७८९', '0123456789'))
        try:
            result.append(int(arabic))
        except ValueError:
            continue
    return result


def build_lookup_index(all_data, filter_type='samam'):
    """
    Build mapping: (p_num, k_num, id) -> source_subsection_key
    The 'id' is either a Samam number (from text) or a Rik ID (from metadata).
    """
    idx = {}
    ss_map = all_data.get("supersection", {})
    for ss_key, ss_data in ss_map.items():
        if not isinstance(ss_data, dict): continue
        
        # Try to get Parva number from metadata, fallback to key name (e.g. supersection_1 -> 1)
        p_num = ss_data.get("supersection_number")
        if p_num is None:
            try:
                p_num = int(ss_key.split('_')[-1])
            except:
                p_num = 1
        
        sections_dict = ss_data.get("sections", {})
        # Sort section keys to ensure we assign the correct ordinal numbers matching the user's view
        sec_keys = sorted(
            [k for k in sections_dict.keys() if k.startswith('section_')],
            key=lambda x: int(x.split('_')[1]) if '_' in x else 0
        )
        
        for k_idx, sec_key in enumerate(sec_keys, 1):
            sec_data = sections_dict[sec_key]
            
            # Use explicit 'section_number' if available, else use ordinal position (1-based)
            k_num = sec_data.get("section_number")
            if k_num is None:
                k_num = k_idx
            
            old_sub_sections = sec_data.get("subsections", {})
            for sub_key, sub_data in old_sub_sections.items():
                address = (ss_key, sec_key, sub_key)
                if filter_type == 'rik':
                    # Use the rik_id metadata field
                    rik_id = sub_data.get('rik_id')
                    if rik_id is not None:
                        # Convert to int if it's a number, or keep as is
                        try:
                            ri = int(rik_id)
                            idx[(p_num, k_num, ri)] = address
                        except:
                            idx[(p_num, k_num, rik_id)] = address
                else:
                    # Default: Use samam numbers extracted from mantra text
                    samam_nums = get_samam_numbers(sub_data)
                    for sn in samam_nums:
                        idx[(p_num, k_num, sn)] = address
    return idx


def parse_p_k_s(content):
    """
    Extract P.K.S identifiers from text using regex.
    P = Parva (Supersection), K = Kandah (literal global section ID), S = Samam number.
    Handles both single IDs (X.Y.Z) and ranges (X.Y.A-X.Y.B).
    """
    results = []
    
    # Extract ranges first
    range_pattern = re.compile(r'(\d+)\.(\d+)\.(\d+)\s*-\s*(\d+)\.(\d+)\.(\d+)')
    for match in range_pattern.finditer(content):
        p1, k1, s1, p2, k2, s2 = map(int, match.groups())
        if p1 == p2 and k1 == k2 and s1 <= s2:
            results.extend([(p1, k1, s, "") for s in range(s1, s2 + 1)])
        else:
            print(f"Warning: Invalid range {p1}.{k1}.{s1}-{p2}.{k2}.{s2}")
            
    # Remove ranges so we don't process them again as single IDs
    content_no_ranges = range_pattern.sub('', content)
    
    # Process lines to get metadata
    for line in content_no_ranges.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'): continue
        
        # Match P.K.S and capture rest of line
        m = re.search(r'(\d+)\.(\d+)\.(\d+)\s*(.*)', line)
        if m:
            p, k, s, meta = m.groups()
            results.append((int(p), int(k), int(s), meta.strip()))
    
    return results


def parse_filter_file(content):
    """
    Parse filter file, extracting Devanagari-numeral section headers and P.K.S IDs.
    Section headers are lines matching: १) Title or २) Title etc.
    Returns: list of {'title': str, 'ids': [(P, K, S), ...]}
    """
    sections = []
    current_section = {"title": "सङ्ग्रहः", "ids": []}
    section_pattern = re.compile(r'^([०-९]+)\)\s*(.*)$')
    pks_pattern = re.compile(r'(\d+)\.(\d+)\.(\d+)')
    range_pattern = re.compile(r'(\d+)\.(\d+)\.(\d+)\s*-\s*(\d+)\.(\d+)\.(\d+)')
    has_seen_header = False

    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Check for section header (ordinal like १) or 1))
        # But we don't necessarily want to treat numbered items as sections if they contain IDs
        sec_match = section_pattern.match(line)
        pks_m = re.search(r'(\d+)\.(\d+)\.(\d+)\s*(.*)', line)
        
        if sec_match and not pks_m:
            if has_seen_header or current_section["ids"]:
                sections.append(current_section)
            current_section = {"title": line, "ids": []}
            has_seen_header = True
            continue
            
        # Process ranges
        range_found = False
        for match in range_pattern.finditer(line):
            p1, k1, s1, p2, k2, s2 = map(int, match.groups())
            if p1 == p2 and k1 == k2 and s1 <= s2:
                current_section["ids"].extend([(p1, k1, s, "") for s in range(s1, s2 + 1)])
                range_found = True
            else:
                print(f"Warning: Invalid or cross-section range pattern {match.group(0)}")
        
        if range_found:
            continue

        # Process single IDs with metadata
        if pks_m:
            p, k, s, meta = pks_m.groups()
            current_section["ids"].append((int(p), int(k), int(s), meta.strip()))

    if current_section["ids"] or has_seen_header:
        sections.append(current_section)

    # If no section headers found, return the flat list as one section
    if not sections:
        all_ids = parse_p_k_s(content)
        return [{"title": "सङ्ग्रहः", "ids": all_ids}]
    return sections


def extract_specific_samam(mantra_text, target_s_val):
    """
    Extract only the part of the mantra text that corresponds to a specific Samam number.
    Assumes Samams end with ॥N॥.
    """
    if not mantra_text:
        return ""
    # Match ॥ followed by optional spaces, Devanagari or ASCII digits, optional spaces, followed by ॥
    pattern = r'॥\s*([०-९\d]+)\s*॥'
    matches = list(re.finditer(pattern, mantra_text))
    
    prev_end = 0
    for m in matches:
        # Convert Devanagari digits to int
        deva_num = m.group(1)
        arabic = deva_num.translate(str.maketrans('०१२३४५६७८९', '0123456789'))
        try:
            current_val = int(arabic)
        except ValueError:
            continue
            
        if current_val == target_s_val:
            # We found our Samam. It starts after the previous Samam's marker (or at 0)
            # and ends at the end of its own marker.
            return mantra_text[prev_end:m.end()].strip()
        
        prev_end = m.end()
    
    return None


def main():
    # 0. Load Configuration
    from utils import load_pipeline_config
    pipeline_cfg = load_pipeline_config()
    curate_cfg = pipeline_cfg.get('curate_jsv', {})

    parser = argparse.ArgumentParser(
        description='Curate a subset of JSV JSON (Samhita/Aaranam) based on P.K.S filters.\n'
                    'P = Parva, K = Kandah (ordinal), S = Samam number (from mantra text ॥N॥).'
    )
    parser.add_argument('--sources', nargs='+', default=None, help='Source JSON files')
    parser.add_argument('--filter', default=None, help='Filter text file with P.K.S identifiers')
    parser.add_argument('--output', default=None, help='Output JSON file')
    parser.add_argument('--title', default=None, help='Title for the curated collection')
    parser.add_argument('--mode', choices=['samam', 'rik', 'both', 'rik_nometa'], default=None, help='Text mode: samam (default), rik, both, or rik_nometa')

    parser.add_argument('--filter-type', choices=['samam', 'rik'], default='samam',
                        help="Whether filter IDs refer to Samam numbers or Rik numbers (default: samam)")
    args = parser.parse_args()

    # Priority: CLI > Config > Defaults
    sources = args.sources or curate_cfg.get('sources')
    if not sources:
        print("Error: No source files provided. Use --sources or configure in pipeline_config.yaml")
        sys.exit(1)

    filter_file = args.filter or curate_cfg.get('filter')
    if not filter_file:
        print("Error: No filter file provided. Use --filter or configure in pipeline_config.yaml")
        sys.exit(1)

    output_file = args.output or curate_cfg.get('output')
    if not output_file:
        print("Error: No output file provided. Use --output or configure in pipeline_config.yaml")
        sys.exit(1)

    title = args.title or curate_cfg.get('title', 'जैमिनीय साम सूक्तमाला')
    mode = args.mode or curate_cfg.get('mode', 'samam')

    # 1. Load and Merge Source JSONs
    source_data = {"supersection": {}, "closing_mantras": []}
    for src in sources:
        source_path = Path(src)
        if not source_path.exists():
            print(f"Error: Source file {src} not found.")
            return

        print(f"Loading source: {source_path}", flush=True)
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Merge supersections
                for ss_id, ss_content in data.get("supersection", {}).items():
                    if ss_id not in source_data["supersection"]:
                        source_data["supersection"][ss_id] = ss_content
                    else:
                        for sec_id, sec_content in ss_content.get("sections", {}).items():
                            if "sections" not in source_data["supersection"][ss_id]:
                                source_data["supersection"][ss_id]["sections"] = {}
                            source_data["supersection"][ss_id]["sections"][sec_id] = sec_content
                            
                # Merge closing mantras
                cm = data.get("closing_mantras", [])
                if cm:
                    source_data["closing_mantras"].extend(cm)
        except Exception as e:
            print(f"Error loading JSON from {src}: {e}")
            return
    print("All sources loaded and merged.", flush=True)

    # 2. Parse Filter File
    filter_path = Path(filter_file)
    if not filter_path.exists():
        print(f"Error: Filter file {filter_file} not found.")
        return

    print(f"Reading filter: {filter_path}", flush=True)
    with open(filter_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title from filter file if present
    title_match = re.search(r'#\s*Title\s*\n(.+?)\n\s*#\s*End\s*Title', content, re.IGNORECASE)
    if title_match:
        extracted_title = title_match.group(1).strip()
        if extracted_title:
            title = extracted_title

    sections_list = parse_filter_file(content)
    total_ids = sum(len(s['ids']) for s in sections_list)
    if not total_ids:
        print(f"Warning: No valid P.K.S identifiers found in {filter_file}")
        return
    print(f"Found {total_ids} identifiers in {len(sections_list)} section(s).", flush=True)


    # 3. Build Curated Structure
    curated_data = {
        "meta": {
            "version": "1.1",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_file": ", ".join(sources),
            "filter_file": str(filter_file),
            "title": title,
            "mode": mode
        },
        "supersection": {
            "supersection_1": {
                "supersection_title": title,
                "sections": {
                    "section_1": {
                        "section_title": "सङ्ग्रहः",
                        "subsections": {}
                    }
                }
            }
        },
        "closing_mantras": source_data.get("closing_mantras", [])
    }

    output_sections_root = curated_data["supersection"]["supersection_1"]["sections"]
    # Build all output sections from the filter's section headers
    for sec_idx, filter_sec in enumerate(sections_list, 1):
        output_sections_root[f"section_{sec_idx}"] = {
            "section_title": filter_sec["title"],
            "subsections": {}
        }

    source_super = source_data.get("supersection", {})

    # Pre-map ordinal sections for each Parva
    parva_section_map = {}
    for ss_key, ss_data in source_super.items():
        if not isinstance(ss_data, dict):
            continue
        sec_keys = sorted(
            [k for k in ss_data.get('sections', {}).keys() if k.lower() != 'count'],
            key=lambda x: int(x.split('_')[1]) if '_' in x else 0
        )
        parva_section_map[ss_key] = sec_keys

    # Pre-build a Samam-number index: (ss_key, sec_key) -> { samam_num -> sub_key }
    print(f"Building {args.filter_type} index...")
    lookup_index = build_lookup_index(source_data, filter_type=args.filter_type)
    print(f"{args.filter_type.capitalize()} index built.")

    found_count = 0
    missing_ids = []
    added_subsections = set()

    for sec_idx, filter_sec in enumerate(sections_list, 1):
        target_sec = output_sections_root[f"section_{sec_idx}"]
        target_subsections = target_sec["subsections"]
        last_source_id = None
        current_target_sub = None

        for p_val, k_val, s_val, extra_meta in filter_sec["ids"]:
            # Look up the ID
            lookup_key = (p_val, k_val, s_val)
            if lookup_key not in lookup_index:
                print(f"  Warning: ID {p_val}.{k_val}.{s_val} not found in sources.")
                missing_ids.append(f"{p_val}.{k_val}.{s_val}")
                continue

            ss_key, sec_key, sub_key = lookup_index[lookup_key]

            # Access the Source data using keys from index
            ss_data = source_super.get(ss_key)
            sec_data = ss_data.get("sections", {}).get(sec_key)
            sub_data = sec_data["subsections"][sub_key]

            # Avoid duplicate Samam entries
            full_key = (ss_key, sec_key, sub_key, s_val)
            # If we have metadata in the filter, it might not be a duplicate if we want different metadata for same PKS
            # But usually it's a mistake. However, for metadata update we should allow it or pick the last.
            if full_key in added_subsections and not extra_meta:
                print(f"  Samam {s_val} (already added, skipping duplicate)", flush=True)
                continue

            added_subsections.add(full_key)
            current_source_id = (ss_key, sec_key, sub_key)
        
            if current_source_id == last_source_id and current_target_sub is not None:
                # If in Samam or Both mode, we might need to add another Samam to the existing subsection
                if mode != 'rik':
                    print(f"  Grouping Samam {s_val} into existing Arsheyam {sub_key}", flush=True)
                    source_sub_data = sec_data["subsections"][sub_key]
                    if "corrected-mantra_sets" in source_sub_data:
                        for mset in source_sub_data["corrected-mantra_sets"]:
                            if not isinstance(mset, dict): continue
                            raw_text = mset.get("corrected-mantra", "")
                            specific_text = extract_specific_samam(raw_text, s_val)
                            if specific_text:
                                import copy
                                mset_copy = copy.deepcopy(mset)
                                mset_copy["corrected-mantra"] = specific_text
                                current_target_sub["corrected-mantra_sets"].append(mset_copy)
                continue

            # New Arsheyam Entry
            sub_data = sec_data["subsections"][sub_key]
            import copy
            found_count += 1
            target_sub_key = f"subsection_{found_count}"
            sub_copy = copy.deepcopy(sub_data)

            # Extract target Samam if in samam or both mode
            if mode in ['samam', 'both']:
                new_mantra_sets = []
                if "corrected-mantra_sets" in sub_copy:
                    for mset in sub_copy["corrected-mantra_sets"]:
                        if not isinstance(mset, dict): continue
                        raw_text = mset.get("corrected-mantra", "")
                        specific_text = extract_specific_samam(raw_text, s_val)
                        if specific_text:
                            mset["corrected-mantra"] = specific_text
                            new_mantra_sets.append(mset)
                sub_copy["corrected-mantra_sets"] = new_mantra_sets
            else:
                # In Rik modes, we don't need the Samam mantra sets
                if "corrected-mantra_sets" in sub_copy:
                    del sub_copy["corrected-mantra_sets"]

            # Ensure rik_id is unique across parvas for rendering deduplication
            # We use P.K.Rik format as a string ID
            source_rik_id = sub_copy.get('rik_id')
            if source_rik_id is not None:
                sub_copy['rik_id'] = f"{p_val}.{k_val}.{source_rik_id}"
                if 'rik_ids' in sub_copy:
                    sub_copy['rik_ids'] = [f"{p_val}.{k_val}.{rid}" for rid in sub_copy['rik_ids']]

            # Handle Rik and Metadata keys based on mode
            rik_keys = ['rik_text', 'rik_metadata', 'rik_classifications', 'rik_id', 'rik_ids']
            
            if mode == 'samam':
                # Drop Rik fields in Samam-only mode
                for kk in rik_keys:
                    if kk in sub_copy:
                        del sub_copy[kk]
            elif mode == 'rik_nometa':
                # Drop all metadata fields, keep ONLY rik_text (KEEP rik_id/ids for rendering logic)
                metadata_keys = ['rik_metadata', 'rik_classifications', 'saman_metadata', 
                                 'saman_rishi', 'saman_devata', 'saman_chandas',
                                 'rik_rishi', 'rik_devata', 'rik_chandas']
                for kk in metadata_keys:
                    if kk in sub_copy:
                        del sub_copy[kk]
                
                # Apply metadata from filter if present
                if extra_meta:
                    sub_copy['rik_metadata'] = extra_meta
                    
                # Keep header object but empty out the title for rik_nometa
                if 'header' in sub_copy:
                    sub_copy['header']['header'] = ""
                else:
                    sub_copy['header'] = {"header": ""}
            
            # Always drop 'mantra_sets' (legacy)
            if 'mantra_sets' in sub_copy:
                del sub_copy['mantra_sets']
            
            # Renumber and attach to target (unless header was deleted in rik_nometa)
            if mode != 'rik_nometa':
                if "header" not in sub_copy or not isinstance(sub_copy["header"], dict):
                    sub_copy["header"] = {"header": ""}
                sub_copy["header"]["header_number"] = found_count
            
            target_subsections[target_sub_key] = sub_copy

            last_source_id = current_source_id
            current_target_sub = sub_copy

    # 4. Save Output
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(curated_data, f, ensure_ascii=False, indent=4)
        print(f"\nSuccessfully created curated file with {found_count} Arsheyams at {output_path}", flush=True)
    except Exception as e:
        print(f"Error saving output: {e}", flush=True)

    if missing_ids:
        print(f"Notice: {len(missing_ids)} identifiers not found: {', '.join(missing_ids[:15])}{'...' if len(missing_ids) > 15 else ''}")


if __name__ == "__main__":
    main()

