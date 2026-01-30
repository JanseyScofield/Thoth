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
        
        imgs_matrices = []
        
        if self.__pdf_processor.is_pdf(content):
            imgs_matrices = self.__pdf_processor.process_to_images(content)
        else:
            matrix = self.__processor.bytes_to_matrix(content)
            if matrix is not None:
                imgs_matrices = [matrix]

        if not imgs_matrices:
            return {"data": None, "message": "Could not process file or empty PDF"}

        result = self.__process_images_list(imgs_matrices)

        if result is None:
            return {"data": None, "message": "Data not processed"}
        else:
            return {"data": result["data"], "type": result["type"], "message": "Data processed successfully"}

    def __process_images_list(self, imgs: list) -> dict:
        qrcode_data = self.__try_process_qrcode(imgs[0])
        if qrcode_data is None and len(imgs) > 1:
            qrcode_data = self.__try_process_qrcode(imgs[-1])

        if qrcode_data:
            return {"data": qrcode_data, "type": "qrcode_data"}

        data = []
        for img in imgs:
            ocr_result = self.__process_single_img_ocr(img)
            if ocr_result:
                data.extend(ocr_result)

        if not data:
            return None
            
        return {"data": data, "type": "ocr_data"}

    def __process_single_img_ocr(self, img_matrix) -> list:
        img_processed_ocr = self.__processor.process_matrix_to_ocr(img_matrix)
        
        ocr_response = self.__ocr_engine.process(img_processed_ocr)
        
        if ocr_response and 'itens' in ocr_response:
            return ocr_response['itens']
        return []

    def __try_process_qrcode(self, img_matrix) -> dict:
        img_processed = self.__processor.process_matrix_to_qrcode(img_matrix)
        
        qrcode_data, points, _ = self.__qrcode_detector.detectAndDecode(img_processed)
        return qrcode_data if qrcode_data else None
