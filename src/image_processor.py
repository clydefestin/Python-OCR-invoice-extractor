"""
image_processor.py

Purpose:
    Prepare receipt images for OCR.
"""

import numpy as np
from PIL import Image


class ImageProcessor:

    def preprocess(self, image):
        """
        Return a clean RGB image for PaddleOCR.
        """

        # Make a copy so we don't modify the original
        image = image.copy()

        # Ensure RGB
        if image.mode != "RGB":
            image = image.convert("RGB")

        return image