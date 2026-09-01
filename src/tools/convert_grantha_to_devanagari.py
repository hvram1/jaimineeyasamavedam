import argparse
import sys
import os
import zipfile
import xml.etree.ElementTree as ET
from aksharamukha import transliterate

def read_odt(file_path):
    """
    Extracts text from an ODT file.
    """
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            if 'content.xml' not in zf.namelist():
                raise ValueError("Invalid ODT file: content.xml not found.")
            
            with zf.open('content.xml') as content_file:
                tree = ET.parse(content_file)
                root = tree.getroot()
                
                # ODT text is in text:p (paragraphs) and text:h (headers)
                # Namespaces can be tricky, so we iterate and check tags ending in 'p' or 'h'
                # or use specific namespaces if needed.
                # A simple way that covers most 'text:p' and 'text:h'
                
                text_content = []
                
                # Define namespaces
                ns = {'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}
                
                # We want to preserve order. Iterating over all elements might be safest if we want all text.
                # But typically text is in text:p and text:h children of office:body/office:text
                
                for elem in root.iter():
                    if elem.tag.endswith('}p') or elem.tag.endswith('}h'):
                        # Extract all text from this element (including sub-elements like spans)
                        # itertext() works in Python 3.8+
                        if hasattr(elem, 'itertext'):
                            text = "".join(elem.itertext())
                        else:
                            # Fallback for older python if needed, but 3.8+ is standard now
                            text = "".join(elem.itertext())
                        
                        if text:
                            text_content.append(text)
                
                return "\n".join(text_content)
                
    except Exception as e:
        print(f"Error reading ODT file: {e}")
        return None

def convert_grantha_to_devanagari(input_path, output_path=None):
    """
    Converts a text or ODT file from Grantha script to Devanagari script.
    
    Args:
        input_path (str): Path to the input file containing Grantha text.
        output_path (str, optional): Path to the output file.
    """
    
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    content = None
    _, ext = os.path.splitext(input_path)
    ext = ext.lower()
    
    try:
        if ext == '.odt':
            print("Detected ODT file. Extracting text...")
            content = read_odt(input_path)
            if content is None:
                return # Error detected in read_odt
        else:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
        if not content:
            print("Warning: Input file appears to be empty or text could not be extracted.")
            # Continue anyway, result will be empty file
            content = ""
            
        # Transliterate
        print("Transliterating...")
        converted_content = transliterate.process('Grantha', 'Devanagari', content)
        
        # Determine output path
        if output_path is None:
            base, _ = os.path.splitext(input_path)
            # Default to .txt output for converted content unless specified
            output_path = f"{base}_devanagari.txt"
            
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(converted_content)
            
        print(f"Successfully converted '{input_path}' to Devanagari.")
        print(f"Output saved to: {output_path}")
        
    except Exception as e:
        print(f"An error occurred during conversion: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Grantha text/ODT file to Devanagari.")
    parser.add_argument("input_file", help="Path to the input Grantha file (.txt or .odt)")
    parser.add_argument("-o", "--output_file", help="Path to the output file (optional)", default=None)
    
    args = parser.parse_args()
    
    convert_grantha_to_devanagari(args.input_file, args.output_file)
