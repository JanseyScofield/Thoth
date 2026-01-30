from pdf2image import convert_from_bytes
import numpy as np
import cv2

class PdfProcessor:
    def process_to_images(self, file_bytes: bytes) -> list:
        try:
            pil_images = convert_from_bytes(file_bytes)
            
            opencv_images = []
            for pil_img in pil_images:
                numpy_img = np.array(pil_img)
                bgr_img = cv2.cvtColor(numpy_img, cv2.COLOR_RGB2BGR)
                opencv_images.append(bgr_img)
            
            return opencv_images
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return []

    def is_pdf(self, file_bytes: bytes) -> bool:
        return file_bytes.startswith(b'%PDF')
