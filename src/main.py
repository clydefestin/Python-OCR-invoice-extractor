"""
main.py

Purpose:
    Main program for the OCR Invoice Extractor.
"""

import os
from pathlib import Path

# Prevent Paddle runtime issues
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"

from pdf_reader import PDFReader
from image_processor import ImageProcessor
from ocr_engine import OCREngine
from receipt_parser import ReceiptParser


def main():

    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_FOLDER = BASE_DIR / "data"

    pdf_files = sorted(DATA_FOLDER.glob("*.pdf"))

    if not pdf_files:
        print("[ERROR] No PDF files found.")
        return

    print("=" * 70)
    print(f"[INFO] Found {len(pdf_files)} PDF(s)")
    print("=" * 70)

    # Create objects ONLY ONCE
    reader = PDFReader()
    processor = ImageProcessor()
    ocr = OCREngine()
    parser = ReceiptParser()

    extracted_records = []

    for pdf_file in pdf_files:

        print("\n" + "=" * 70)
        print(f"Processing: {pdf_file.name}")
        print("=" * 70)

        document = None

        try:

            document = reader.load_pdf(pdf_file)

            images = reader.convert_pages_to_images(document)

            if not images:
                print("[WARNING] No pages converted.")
                continue

            for page_number, image in enumerate(images, start=1):

                print(f"\n[INFO] Processing Page {page_number}")

                processed_image = processor.preprocess(image)

                # OCR should not stop the whole program
                try:
                    text = ocr.extract_text(processed_image)

                except Exception as e:
                    print(f"[ERROR] OCR failed on Page {page_number}")
                    print(e)
                    continue

                print("\n===== OCR RESULT =====")
                print(text)
                print("======================")

                record = parser.parse(
                    text=text,
                    page_number=page_number
                )

                extracted_records.append(record)

                print("\n===== PARSED DATA =====")

                for key, value in record.items():
                    print(f"{key}: {value}")

                print("=======================\n")

        except Exception as e:

            print(f"[ERROR] Failed to process {pdf_file.name}")
            print(e)

        finally:

            if document is not None:
                reader.close_pdf(document)

    print("\n" + "=" * 70)
    print("ALL EXTRACTED RECORDS")
    print("=" * 70)

    for record in extracted_records:
        print(record)

    print("\n[INFO] Total Records:", len(extracted_records))


if __name__ == "__main__":
    main()
