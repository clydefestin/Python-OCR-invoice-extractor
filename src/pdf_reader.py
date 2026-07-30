"""
pdf_reader.py

Purpose:
    Read PDF files and convert each page into PIL Images
    for OCR processing.
"""

from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image


class PDFReader:
    """
    PDF Reader using PyMuPDF.
    """

    def __init__(self, dpi=200):
        """
        Initialize the PDF Reader.

        Parameters
        ----------
        dpi : int
            Default rendering DPI.
        """

        self.dpi = dpi

    def load_pdf(self, pdf_path):
        """
        Open a PDF document.

        Parameters
        ----------
        pdf_path : str | Path

        Returns
        -------
        fitz.Document
        """

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
                f"Unable to open PDF.\n{e}"
            )

    def convert_pages_to_images(self, document):
        """
        Convert each PDF page into a PIL Image.

        The renderer automatically retries using a lower
        DPI if rendering fails due to memory limitations.

        Returns
        -------
        list[PIL.Image]
        """

        images = []

        dpi_levels = [
            self.dpi,
            150,
            100
        ]

        for page_number in range(len(document)):

            page = document.load_page(page_number)

            image = None

            for dpi in dpi_levels:

                try:

                    print(
                        f"[INFO] Rendering Page {page_number + 1} at {dpi} DPI"
                    )

                    pix = page.get_pixmap(
                        dpi=dpi,
                        alpha=False
                    )

                    image = Image.frombytes(
                        "RGB",
                        (pix.width, pix.height),
                        pix.samples
                    )

                    # Release memory immediately
                    del pix

                    print(
                        f"[INFO] Converted Page {page_number + 1}"
                    )

                    break

                except MemoryError:

                    print(
                        f"[WARNING] MemoryError at {dpi} DPI"
                    )

                except Exception as e:

                    print(
                        f"[WARNING] Rendering failed at {dpi} DPI"
                    )
                    print(e)

            if image is None:

                print(
                    f"[ERROR] Failed to render page {page_number + 1}"
                )

                continue

            images.append(image)

        return images

    def close_pdf(self, document):
        """
        Close the PDF document.
        """

        if document is not None:

            document.close()

            print("[INFO] PDF closed.")