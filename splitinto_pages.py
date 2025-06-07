import os
import sys
from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_pdf, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    reader = PdfReader(input_pdf)
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        output_path = os.path.join(output_dir, f"page_{i+1}.pdf")
        with open(output_path, "wb") as out_file:
            writer.write(out_file)
        print(f"Saved: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python splitinto_pages.py <input_pdf>")
        sys.exit(1)
    input_pdf = sys.argv[1]
    output_dir = "pages"
    split_pdf(input_pdf, output_dir)