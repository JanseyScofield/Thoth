from app.services.ocr_engines.ocr_engine import OcrEngine
from app.services.processors.processor import Processor
from app.services.processors.pdf_processor import PdfProcessor
import cv2
import numpy as np

class ReceiptService:
    def __init__(self, ocr_engine: OcrEngine, processor: Processor, pdfProcessor: PdfProcessor):
        self.__ocr_engine = ocr_engine
        self.__processor = processor
        self.__pdf_processor = pdfProcessor
        self.__qrcode_detector = cv2.QRCodeDetector()

    def process_receipt(self, content: bytes) -> dict:
        result = None
        
        # 1. Normalization: Everything becomes a list of matrices
        imgs_matrices = []
        
        if self.__pdf_processor.is_pdf(content):
            # Returns list of BGR matrices
            imgs_matrices = self.__pdf_processor.process_to_images(content)
        else:
            # Converts single bytes to a list with 1 matrix
            matrix = self.__processor.bytes_to_matrix(content)
            if matrix is not None:
                imgs_matrices = [matrix]

        if not imgs_matrices:
            return {"data": None, "message": "Could not process file or empty PDF"}

        # 2. Unified Processing
        result = self.__process_images_list(imgs_matrices)

        if result is None:
            return {"data": None, "message": "Data not processed"}
        else:
            return {"data": result["data"], "type": result["type"], "message": "Data processed successfully"}

    def __process_images_list(self, imgs: list) -> dict:
        # Try QR Code on first and last page (optimization for long PDFs)
        qrcode_data = self.__try_process_qrcode(imgs[0])
        if qrcode_data is None and len(imgs) > 1:
            qrcode_data = self.__try_process_qrcode(imgs[-1])

        if qrcode_data:
            return {"data": qrcode_data, "type": "qrcode_data"}

        # If QR not found, perform OCR on all pages (or filter the best ones)
        data = []
        for img in imgs:
            ocr_result = self.__process_single_img_ocr(img)
            if ocr_result:
                data.extend(ocr_result)

        if not data:
            return None
            
        return {"data": data, "type": "ocr_data"}

    def __process_single_img_ocr(self, img_matrix) -> list:
        # Here we fix the error: we pass the matrix, not bytes, and call the correct method
        img_processed_ocr = self.__processor.process_matrix_to_ocr(img_matrix)
        
        ocr_response = self.__ocr_engine.process(img_processed_ocr)
        
        # The engine returns {'itens': [...]}, we only get the list
        if ocr_response and 'itens' in ocr_response:
            return ocr_response['itens']
        return []

    def __try_process_qrcode(self, img_matrix) -> dict:
        # Prepares matrix for QR Code
        img_processed = self.__processor.process_matrix_to_qrcode(img_matrix)
        
        # Detects
        qrcode_data, points, _ = self.__qrcode_detector.detectAndDecode(img_processed)
        return qrcode_data if qrcode_data else None