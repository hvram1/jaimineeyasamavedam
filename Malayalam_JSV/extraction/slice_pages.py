"""Render PDF pages into high-resolution PNG images using pypdfium2."""

import argparse
from pathlib import Path
import pypdfium2 as pdfium


def render_pdf_to_images(
    pdf_path: Path,
    output_dir: Path,
    scale: float = 300 / 72,
    start_page: int = 1,
    end_page: int | None = None,
):
    """Render a range of pages of a PDF to high-resolution PNG images.

    Args:
        pdf_path: Path to the PDF file.
        output_dir: Directory to save PNG files.
        scale: Render scale (300/72 ≈ 4.17 gives ~300 DPI from 72 DPI base).
        start_page: First page to render (1-indexed, inclusive).
        end_page: Last page to render (1-indexed, inclusive). None = last page.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_path))
    num_pages = len(pdf)
    end = min(end_page, num_pages) if end_page else num_pages
    start = max(1, start_page)

    print(f"Loading '{pdf_path.name}' ({num_pages} pages)...")
    print(f"Rendering pages {start}–{end} at scale={scale:.3f} (~{int(scale*72)} DPI)")

    for i in range(start - 1, end):  # pypdfium2 is 0-indexed
        page = pdf[i]
        bitmap = page.render(scale=scale)
        pil_image = bitmap.to_pil()
        out_file = output_dir / f"page_{i+1:04d}.png"
        if out_file.exists():
            print(f"  Skipping page {i+1} (already exists: {out_file.name})")
            continue
        pil_image.save(out_file, dpi=(int(scale * 72), int(scale * 72)))
        print(f"  Page {i+1}/{end} -> {out_file.name} ({pil_image.width}x{pil_image.height})")

    print("Done.")


def main():
    parser = argparse.ArgumentParser(description="Render PDF pages to PNGs")
    parser.add_argument("--pdf", required=True, help="Path to input PDF")
    parser.add_argument("--out", required=True, help="Output directory for PNG images")
    parser.add_argument("--dpi", type=int, default=300, help="Target DPI (default 300)")
    parser.add_argument("--start-page", type=int, default=1, help="First page to render (1-indexed)")
    parser.add_argument("--end-page", type=int, default=None, help="Last page to render (1-indexed, default: last)")
    args = parser.parse_args()

    scale = args.dpi / 72.0
    render_pdf_to_images(
        Path(args.pdf),
        Path(args.out),
        scale=scale,
        start_page=args.start_page,
        end_page=args.end_page,
    )


if __name__ == "__main__":
    main()
