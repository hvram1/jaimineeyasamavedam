import sys
import os

def format_arsheyam_lines(input_path, output_path=None):
    """
    Reads a text file and reformats lines that are terminated by a single danda (| or ।).
    Converts:
        <String>। 
    To:
        ॥ <String> ॥
        
    The utility treats lines ending with a single Danda (U+0964) or Pipe (|) as Arsheyam lines
    ignoring whitespace.
    """
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found.")
        return

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_formatted{ext}"

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        formatted_lines = []
        count = 0

        for line in lines:
            stripped = line.strip()
            
            # Check for suffixes: Devanagari Danda (।) or ASCII Pipe (|)
            # Ensure it does NOT end with Double Danda (॥) or ||
            if (stripped.endswith('।') or stripped.endswith('|')) and \
               not stripped.endswith('॥') and not stripped.endswith('||'):
                
                # Identify the character used
                char_to_strip = '।' if stripped.endswith('।') else '|'
                
                # Extract content
                content = stripped.rstrip(char_to_strip).strip()
                
                if content:
                    # Create new line with Double Dandas (using Devanagari Double Danda)
                    # We assume standardizing to Devanagari Double Danda (॥) is preferred 
                    # for Sanskrit text.
                    new_line = f"॥ {content} ॥\n"
                    formatted_lines.append(new_line)
                    count += 1
                else:
                    # Empty line with just a danda?
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(formatted_lines)

        print(f"Successfully processed {len(lines)} lines.")
        print(f"Formatted {count} Arsheyam lines.")
        print(f"Output saved to: {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Format Arsheyam lines in a text file.")
    parser.add_argument("input_file", help="Path to the input text file")
    parser.add_argument("-o", "--output_file", help="Path to the output file (optional)", default=None)
    
    args = parser.parse_args()
    
    format_arsheyam_lines(args.input_file, args.output_file)
