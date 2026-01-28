# Classe que vai receber a imagem e fazer todo o pré-tratamento para passar ao paddle.
import cv2
import numpy as np
from app.services.processors.processor import Processor

class ImageProcessor(Processor):
    def __init__(self):
        super().__init__()

    def process_to_qrcode(self, data : bytes):
        return self.__to_gray(data)
    
    def process_to_ocr(self, data : bytes):
        img_gray = self.__to_gray(data)
        height, width = img_gray.shape
        img_resized = cv2.resize(img_gray, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC) 
        img_blur = cv2.medianBlur(img_resized, 3)
        img_bin = cv2.adaptiveThreshold(
            img_blur, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            15, 
            5 
        )

        return img_bin
    
    def __to_gray(self, image : bytes):
        nparr = np.frombuffer(image, np.uint8)
        img_matrix = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return cv2.cvtColor(img_matrix, cv2.COLOR_BGR2GRAY)