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

    def process_cupon(self, content: bytes) -> dict:
        result = None
        
        # 1. Normalização: Tudo vira uma lista de matrizes
        imgs_matrices = []
        
        if self.__pdf_processor.is_pdf(content):
            # Retorna lista de matrizes BGR
            imgs_matrices = self.__pdf_processor.process_to_images(content)
        else:
            # Converte bytes únicos para uma lista com 1 matriz
            matrix = self.__processor.bytes_to_matrix(content)
            if matrix is not None:
                imgs_matrices = [matrix]

        if not imgs_matrices:
            return {"data": None, "message": "Could not process file or empty PDF"}

        # 2. Processamento Unificado
        result = self.__process_images_list(imgs_matrices)

        if result is None: 
            return {"data": None, "message": "Data not processed"}
        else: 
            return {"data": result["data"], "type": result["type"], "message": "Data processed successfully"}

    def __process_images_list(self, imgs: list) -> dict:
        # Tenta QR Code na primeira e última página (otimização para PDFs longos)
        qrcode_data = self.__try_process_qrcode(imgs[0])
        if qrcode_data is None and len(imgs) > 1:
            qrcode_data = self.__try_process_qrcode(imgs[-1])

        if qrcode_data: 
            return {"data": qrcode_data, "type": "qrcode_data"}

        # Se não achou QR, faz OCR em todas as páginas (ou filtra as melhores)
        data = []
        for img in imgs:
            ocr_result = self.__process_single_img_ocr(img)
            if ocr_result:
                data.extend(ocr_result)

        if not data: 
            return None
            
        return {"data": data, "type": "ocr_data"}

    def __process_single_img_ocr(self, img_matrix) -> list:
        # Aqui corrigimos o erro: passamos a matriz, não bytes, e chamamos o método certo
        img_processed_ocr = self.__processor.process_matrix_to_ocr(img_matrix)
        
        ocr_response = self.__ocr_engine.process(img_processed_ocr)
        
        # O engine retorna {'itens': [...]}, pegamos apenas a lista
        if ocr_response and 'itens' in ocr_response:
            return ocr_response['itens']
        return []

    def __try_process_qrcode(self, img_matrix) -> dict:
        # Prepara matriz para QR Code
        img_processed = self.__processor.process_matrix_to_qrcode(img_matrix)
        
        # Detecta
        qrcode_data, points, _ = self.__qrcode_detector.detectAndDecode(img_processed)
        return qrcode_data if qrcode_data else None