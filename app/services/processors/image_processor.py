import cv2
import numpy as np
from app.services.processors.processor import Processor

class ImageProcessor(Processor):
    def __init__(self):
        super().__init__()

    # ---------------------------------------------------------
    # 1. Required Interface Methods (Error Fix)
    # ---------------------------------------------------------
    # These methods satisfy the abstract 'Processor' class.
    # They receive bytes (the old standard) and use the new logic.
    
    def process_to_ocr(self, data: bytes):
        # Converts bytes -> Matrix and calls the new logic
        matrix = self.bytes_to_matrix(data)
        if matrix is None:
            return None
        return self.process_matrix_to_ocr(matrix)

    def process_to_qrcode(self, data: bytes):
        # Converts bytes -> Matrix and calls the new logic
        matrix = self.bytes_to_matrix(data)
        if matrix is None:
            return None
        return self.process_matrix_to_qrcode(matrix)

    # ---------------------------------------------------------
    # 2. New Methods to Handle Matrices (PDF/OpenCV)
    # ---------------------------------------------------------

    def bytes_to_matrix(self, data: bytes):
        """Decodes raw bytes (JPG/PNG) to OpenCV matrix"""
        if not data:
            return None
        nparr = np.frombuffer(data, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    def process_matrix_to_qrcode(self, img_matrix: np.ndarray):
        # Ensures the matrix is valid before processing
        if img_matrix is None or img_matrix.size == 0:
            return None
            
        if len(img_matrix.shape) == 3:
            return cv2.cvtColor(img_matrix, cv2.COLOR_BGR2GRAY)
        return img_matrix
    
    def process_matrix_to_ocr(self, img_matrix: np.ndarray):
        # Ensures the matrix is valid
        if img_matrix is None or img_matrix.size == 0:
            return None

        if len(img_matrix.shape) == 3:
            img_gray = cv2.cvtColor(img_matrix, cv2.COLOR_BGR2GRAY)
        else:
            img_gray = img_matrix

        height, width = img_gray.shape
        scale = 2
        
        # Prevents memory crash on very large images (common in converted PDFs)
        if height > 2500 or width > 2500:
            scale = 1
            
        return cv2.resize(img_gray, (width * scale, height * scale), interpolation=cv2.INTER_CUBIC)