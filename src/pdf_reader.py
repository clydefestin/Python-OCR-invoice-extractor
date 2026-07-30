import io
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image


class PDFReader:

    def __init__(self, dpi=300):
 
        self.dpi = dpi

    def load_pdf(self, pdf_path):

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF file not found:\n{pdf_path}"
            )

        try:
            document = fitz.open(str(pdf_path))

            print(f"[INFO] Loaded: {pdf_path.name}")
            print(f"[INFO] Pages : {len(document)}")

            return document

        except Exception as e:
            raise RuntimeError(
                f"Failed to open PDF:\n{e}"
            )

    def convert_pages_to_images(self, document):

        images = []

        for page_number in range(len(document)):

            page = document.load_page(page_number)

            pix = page.get_pixmap(
                dpi=self.dpi,
                alpha=False
            )

            image = Image.open(
                io.BytesIO(
                    pix.tobytes("png")
                )
            )

            images.append(image)

            print(
                f"[INFO] Converted Page {page_number + 1}"
            )

        return images

    def close_pdf(self, document):

        if document:
            document.close()

            print("[INFO] PDF closed.")