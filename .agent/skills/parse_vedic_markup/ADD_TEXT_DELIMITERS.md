# Add Text Delimiters Utility

A Python utility to automatically add structural delimiters (markers/comments) around structural elements in Jaimineeyasamaveda text files for further processing.

## Purpose

This utility processes Sanskrit text files and adds comment-based delimiters around:
- **SuperSections** - Major divisions like "व्रत पर्व" (Parvas)
- **Sections** - Chapters/Khandas containing "खण्डः"
- **SubSections** - Individual items marked with `||title||` or `।।title।।`
- **Mantra Sets** - Grouped mantra content within each subsection

## Delimiter Formats

The utility adds the following delimiter patterns:

```
# Start of SuperSection Title -- supersection_N ## DO NOT EDIT
॥ व्रत पर्व ॥
# End of SuperSection Title -- supersection_N ## DO NOT EDIT

# Start of Section Title -- section_N ## DO NOT EDIT
॥ अथ द्वितीय खण्डः ॥
# End of Section Title -- section_N ## DO NOT EDIT

# Start of SubSection Title -- subsection_N ## DO NOT EDIT
||वाचो व्रते द्वे||
# End of SubSection Title -- subsection_N ## DO NOT EDIT

#Start of Mantra Sets -- subsection_N ## DO NOT EDIT
[mantra content]
#End of Mantra Sets -- subsection_N ## DO NOT EDIT
```

## Usage

### Method 1: Command Line (Basic)

```bash
cd c:\Users\sekha\OneDrive\Documents\GitHub\jaimineeyasamavedam

# Process file and create a new output file
python src/add_text_delimiters.py "data/input/Aaranam - Part 1.txt" "output_file.txt"

# Process file in-place (creates backup automatically)
python src/add_text_delimiters.py "data/input/Aaranam - Part 1.txt"
```

### Method 2: Python Script

```python
import sys
sys.path.insert(0, 'src')

from add_text_delimiters import TextDelimiterProcessor

# Create processor instance
processor = TextDelimiterProcessor()

# Process a file
stats = processor.process_file(
    input_path='data/input/Aaranam - Part 1.txt',
    output_path='data/input/Aaranam - Part 1_with_delimiters.txt',
    skip_header_lines=5,      # Preserve first 5 lines as header
    strip_existing=True       # Remove existing delimiters before processing
)

print(f"Supersections found: {stats['supersections']}")
print(f"Sections found: {stats['sections']}")
print(f"Subsections found: {stats['subsections']}")
print(f"Mantra sets wrapped: {stats['mantra_sets']}")
```

### Method 3: Using the Helper Script

A helper script `run_delimiter_processor.py` is available in the project root:

```bash
python run_delimiter_processor.py
```

This script:
1. Processes `data/input/Aaranam - Part 1.txt`
2. Outputs to `data/input/Aaranam - Part 1_with_delimiters.txt`
3. Preserves the header (first 5 lines)
4. Strips any existing delimiters before reprocessing

## API Reference

### `TextDelimiterProcessor` Class

#### `__init__()`
Initializes the processor with regex patterns for identifying structural elements.

#### `process_file(input_path, output_path=None, start_supersection=1, start_section=1, start_subsection=1, strip_existing=True, skip_header_lines=5)`

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_path` | str | required | Path to the input file |
| `output_path` | str | None | Path to output file. If None, overwrites input |
| `start_supersection` | int | 1 | Starting counter for supersection IDs |
| `start_section` | int | 1 | Starting counter for section IDs |
| `start_subsection` | int | 1 | Starting counter for subsection IDs |
| `strip_existing` | bool | True | Remove existing delimiters before processing |
| `skip_header_lines` | int | 5 | Number of header lines to preserve as-is |

**Returns:**
Dictionary with processing statistics:
```python
{
    'supersections': int,    # Count of supersections found
    'sections': int,         # Count of sections found
    'subsections': int,      # Count of subsections found
    'mantra_sets': int,      # Count of mantra sets wrapped
    'lines_processed': int   # Total lines in original file
}
```

#### `identify_line_type(line)`
Identifies the type of a given line.

**Returns:** Tuple `(type, title)` where type is one of:
- `'supersection'` - Lines matching `॥ title ॥` (without खण्डः)
- `'section'` - Lines containing `खण्डः`
- `'subsection'` - Lines matching `||title||` or `।।title।।`
- `'mantra'` - Sanskrit content lines
- `'blank'` - Empty lines
- `'delimiter'` - Existing delimiter comments
- `'other'` - Other content

#### `strip_existing_delimiters(lines)`
Removes all existing delimiter lines from the content.

**Parameters:**
- `lines`: List of lines from the file

**Returns:** List of lines with delimiter comments removed

### Standalone Functions

#### `add_delimiters_to_file(input_file, output_file=None, start_supersection=1, start_section=1, start_subsection=1)`

Main utility function to add text delimiters to a file. Creates a backup if overwriting.

#### `preview_delimiters(input_file, num_lines=100)`

Preview the delimiter additions without modifying the file.

## Pattern Recognition

### SuperSection Pattern
- Format: `॥ Title ॥` (double dandas with spaces around title)
- Example: `॥ व्रत पर्व ॥`
- Note: Lines containing `खण्डः` are NOT supersections

### Section Pattern  
- Format: Any line containing `खण्डः`
- Examples:
  - `प्रथम खण्डः (191)`
  - `॥ अथ द्वितीय खण्डः ॥`
  - `|| अथ दशमः खण्डः ॥`

### SubSection Pattern
- Format: `||title||` or `।।title।।`
- Examples:
  - `||वाचो व्रते द्वे||`
  - `।। प्रजापतेश्च व्याहृतिः ।।`

### Mantra Lines
- Any line containing Devanagari characters that is not a structural marker
- Consecutive mantra lines are grouped together

## File Structure Example

**Before Processing:**
```
जैमिनीय  साम  प्रकृति  गानम्

Version 2.5 29th January 2026

॥ व्रत पर्व ॥ 

प्रथम खण्डः (191)

।। वाचो व्रते द्वे ।।

हुवे वाचाम् । वाच वाचा हुवे वाक् ॥ १ ॥
```

**After Processing:**
```
जैमिनीय  साम  प्रकृति  गानम्

Version 2.5 29th January 2026

# Start of SuperSection Title -- supersection_1 ## DO NOT EDIT
॥ व्रत पर्व ॥ 
# End of SuperSection Title -- supersection_1 ## DO NOT EDIT

# Start of Section Title -- section_1 ## DO NOT EDIT
प्रथम खण्डः (191)
# End of Section Title -- section_1 ## DO NOT EDIT

# Start of SubSection Title -- subsection_1 ## DO NOT EDIT
।। वाचो व्रते द्वे ।।
# End of SubSection Title -- subsection_1 ## DO NOT EDIT

#Start of Mantra Sets -- subsection_1 ## DO NOT EDIT
हुवे वाचाम् । वाच वाचा हुवे वाक् ॥ १ ॥
#End of Mantra Sets -- subsection_1 ## DO NOT EDIT
```

## Notes

1. **Idempotent Processing**: The utility can be run multiple times on the same file. It strips existing delimiters before adding new ones (when `strip_existing=True`).

2. **Header Preservation**: The first N lines (default 5) are preserved as-is without processing. This protects document headers.

3. **Backup Creation**: When processing in-place (no output file specified), a `.backup` file is automatically created.

4. **Encoding**: All files are read and written with UTF-8 encoding to properly handle Sanskrit/Devanagari text.

## Troubleshooting

**Issue: SuperSection and Section confusion**
- Lines containing `खण्डः` are always treated as Sections, even if wrapped in `॥ ... ॥`

**Issue: Mantra sets not being grouped**
- Mantra sets are only created when there's a current subsection context
- Ensure subsections are properly identified before mantra content

**Issue: Encoding errors**
- Ensure input files are saved with UTF-8 encoding
- The utility explicitly uses UTF-8 for all file operations
