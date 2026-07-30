from pathlib import Path

from pdf_reader import PDFReader


def main():

    reader = PDFReader()

    BASE_DIR = Path(__file__).resolve().parent.parent

    DATA_FOLDER = BASE_DIR / "data"

    pdf_files = sorted(DATA_FOLDER.glob("*.pdf"))

    if not pdf_files:
        print("[ERROR] No PDF files found.")
        return

    print(f"[INFO] Found {len(pdf_files)} PDF(s).\n")

    for pdf_file in pdf_files:

        print(f"[INFO] Processing: {pdf_file.name}")

        document = reader.load_pdf(pdf_file)

        images = reader.convert_pages_to_images(document)

        print(f"[INFO] Total Pages: {len(images)}")

        # Testing only
        images[0].show()

        reader.close_pdf(document)

        print("-" * 50)


if __name__ == "__main__":
    main()