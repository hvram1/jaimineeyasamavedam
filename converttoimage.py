import os
from pdf2image import convert_from_path

# Directory containing PDF files
pdf_dir = 'pdfs'
# Output directory for images
output_dir = 'images'
os.makedirs(output_dir, exist_ok=True)

# Process each PDF file in the directory
for filename in os.listdir(pdf_dir):
    if filename.lower().endswith('.pdf'):
        pdf_path = os.path.join(pdf_dir, filename)
        images = convert_from_path(pdf_path, dpi=1200)
        # Save the first page as xxx.png
        if images:
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_dir, f'{base_name}.png')
            images[0].save(output_path, 'PNG')
            print(f"Saved {output_path}")

print("Done converting PDFs to images.")
