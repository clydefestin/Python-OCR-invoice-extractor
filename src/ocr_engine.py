"""
ocr_engine.py

Purpose:
    OCR Engine using PaddleOCR
    Extracts text from scanned receipt images.
"""

import cv2
import numpy as np
from paddleocr import PaddleOCR


class OCREngine:
    """
    OCR Engine for scanned medical receipts.
    """

    def __init__(self):
        """
        Initialize PaddleOCR only once.
        """

        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang="en",
            use_gpu=False,
            show_log=False,
            enable_mkldnn=False
        )

    def extract_text(self, image):
        """
        Extract text from a PIL Image.

        Parameters
        ----------
        image : PIL.Image

        Returns
        -------
        str
            OCR extracted text.
        """

        # Convert PIL -> NumPy
        image = np.array(image)

        # Ensure image is RGB
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        # First OCR attempt
        try:
            result = self.ocr.ocr(image, cls=True)

        except RuntimeError as e:

            print(f"[WARNING] OCR failed: {e}")
            print("[INFO] Retrying using a smaller image...")

            # Resize image to reduce memory usage
            image = cv2.resize(
                image,
                None,
                fx=0.5,
                fy=0.5,
                interpolation=cv2.INTER_AREA
            )

            try:
                result = self.ocr.ocr(image, cls=True)

            except Exception as e:
                print(f"[ERROR] OCR retry failed: {e}")
                return ""

        except Exception as e:
            print(f"[ERROR] OCR Error: {e}")
            return ""

        # No OCR result
        if not result:
            return ""

        if result[0] is None:
            return ""

        lines = []

        for line in result[0]:

            try:
                text = line[1][0].strip()

                if text:
                    lines.append(text)

            except Exception:
                continue

        return "\n".join(lines)