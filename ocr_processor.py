import cv2
import numpy as np
import pytesseract
from PIL import Image

class ReceiptOCR:
    def __init__(self):
        # You may need to set the tesseract path on Windows
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def preprocess_image(self, image):
        """
        Preprocess the image for better OCR results
        - Convert to grayscale
        - Denoise
        - Increase contrast
        - Binarization
        """
        # Convert PIL Image to numpy array if needed
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Increase contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(denoised)
        
        # Apply adaptive thresholding for binarization
        binary = cv2.adaptiveThreshold(
            contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Optional: Morphological operations to remove noise
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def extract_text(self, image):
        """
        Extract text from receipt image
        Returns: raw OCR text
        """
        # Preprocess the image
        processed_image = self.preprocess_image(image)
        
        # Configure Tesseract
        custom_config = r'--oem 3 --psm 6'
        
        # Perform OCR
        text = pytesseract.image_to_string(processed_image, config=custom_config)
        
        return text
    
    def get_processed_image(self, image):
        """
        Return the preprocessed image for display/debugging
        """
        return self.preprocess_image(image)