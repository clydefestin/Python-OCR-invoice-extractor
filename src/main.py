"""
main.py

Purpose:
    Main entry point of the OCR Invoice Extractor.
"""

import os

# Disable oneDNN (helps avoid Paddle runtime issues)
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"

from pathlib import Path

from pdf_reader import PDFReader
from image_processor import ImageProcessor
from ocr_engine import OCREngine


def main():

    # Project root
    BASE_DIR = Path(__file__).resolve().parent.parent

    # Data folder
    DATA_FOLDER = BASE_DIR / "data"

    # Find PDFs
    pdf_files = sorted(DATA_FOLDER.glob("*.pdf"))

    if not pdf_files:
        print("[ERROR] No PDF files found in data folder.")
        return

    print("=" * 60)
    print(f"[INFO] Found {len(pdf_files)} PDF(s).")
    print("=" * 60)

    # Process every PDF
    for pdf_file in pdf_files:

        print()
        print("=" * 60)
        print(f"Processing: {pdf_file.name}")
        print("=" * 60)

        # Create fresh objects for every PDF
        reader = PDFReader()
        processor = ImageProcessor()
        ocr = OCREngine()

        document = None

        try:

            # Open PDF
            document = reader.load_pdf(pdf_file)

            # Convert PDF pages to images
            images = reader.convert_pages_to_images(document)

            if not images:
                print("[WARNING] No pages were converted.")
                continue

            # OCR every page
            for page_number, image in enumerate(images, start=1):

                print(f"\n[INFO] Processing Page {page_number}")

                processed = processor.preprocess(image)

                text = ocr.extract_text(processed)

                print("\n===== OCR RESULT =====")

                if text.strip():
                    print(text)
                else:
                    print("[WARNING] No text detected.")

                print("======================")

        except Exception as e:

            print(f"[ERROR] Failed to process {pdf_file.name}")
            print(e)

        finally:

            if document is not None:
                reader.close_pdf(document)

        print()

    print("=" * 60)
    print("[INFO] OCR processing completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()