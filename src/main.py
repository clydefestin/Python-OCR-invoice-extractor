"""
main.py

Purpose:
    Main program for the OCR Doctor Receipt Extractor.

Workflow:
    PDF -> Image -> OCR -> Receipt Parser -> Excel Export
"""

import os
from pathlib import Path

# Prevent PaddleOCR runtime issues
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"

from pdf_reader import PDFReader
from image_processor import ImageProcessor
from ocr_engine import OCREngine
from receipt_parser import ReceiptParser
from excel_writer import ExcelWriter


def main():

    BASE_DIR = Path(__file__).resolve().parent.parent

    DATA_FOLDER = BASE_DIR / "data"
    OUTPUT_FOLDER = BASE_DIR / "output"

    OUTPUT_FOLDER.mkdir(exist_ok=True)

    pdf_files = sorted(DATA_FOLDER.glob("*.pdf"))

    if not pdf_files:
        print("[ERROR] No PDF files found.")
        return

    print("=" * 70)
    print(f"[INFO] Found {len(pdf_files)} PDF(s)")
    print("=" * 70)

    extracted_records = []

    reader = PDFReader()
    processor = ImageProcessor()
    ocr = OCREngine()
    parser = ReceiptParser()
    writer = ExcelWriter()

    # ----------------------------------------------------------
    # Process every PDF
    # ----------------------------------------------------------

    for pdf_file in pdf_files:

        print("\n" + "=" * 70)
        print(f"Processing: {pdf_file.name}")
        print("=" * 70)

        document = None

        try:

            # Load PDF
            document = reader.load_pdf(pdf_file)

            # Convert pages to images
            images = reader.convert_pages_to_images(document)

            if not images:
                print("[WARNING] No pages converted.")
                continue

            # OCR each page
            for page_number, image in enumerate(images, start=1):

                print(f"\n[INFO] Processing Page {page_number}")

                processed_image = processor.preprocess(image)

                text = ocr.extract_text(processed_image)

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

            if document:
                reader.close_pdf(document)

    # ----------------------------------------------------------
    # Export Results
    # ----------------------------------------------------------

    excel_path = OUTPUT_FOLDER / "extracted_receipts.xlsx"

    writer.export(
        extracted_records,
        excel_path
    )

    # ----------------------------------------------------------
    # Summary
    # ----------------------------------------------------------

    print("\n" + "=" * 70)
    print("ALL EXTRACTED RECORDS")
    print("=" * 70)

    for record in extracted_records:
        print(record)

    print("\n" + "=" * 70)
    print(f"Total Receipts Processed : {len(pdf_files)}")
    print(f"Total Records Extracted  : {len(extracted_records)}")
    print(f"Excel Output             : {excel_path}")
    print("=" * 70)

    print("\nProject Completed Successfully!")
    print("Doctor Receipt OCR Extraction Finished.")


if __name__ == "__main__":
    main()