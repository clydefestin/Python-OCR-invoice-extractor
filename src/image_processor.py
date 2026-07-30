"""

Purpose:
    Prepare scanned receipt images for OCR by improving
    image quality.
    
"""

import cv2
import numpy as np
from PIL import Image


class ImageProcessor:


    def preprocess(self, image):

        # Convert PIL Image to NumPy array
        image = np.array(image)

        # Convert RGB to BGR because OpenCV uses BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Remove small image noise
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # Automatically determine the best threshold
        processed = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

        # Convert NumPy array back to PIL Image
        processed = Image.fromarray(processed)

        return processed