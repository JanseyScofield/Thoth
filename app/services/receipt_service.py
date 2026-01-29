from app.services.ocr_engines.ocr_engine import OcrEngine
from app.services.processors.processor import Processor
import cv2

class ReceiptService:
    def __init__(self, ocr_engine : OcrEngine, processor : Processor):
        self.__ocr_engine = ocr_engine
        self.__processor = processor
        self.__qrcode_detector = cv2.QRCodeDetector()

    def process_cupon(self, cupon : bytes) -> dict:
        img_processed_qrcode = self.__processor.process_to_qrcode(cupon)
        qrcode_data = self.__get_by_qrcode(img_processed_qrcode)

        if qrcode_data:
            return {"data": qrcode_data, "message": "QR code detected successfully"}
        
        img_processed_ocr = self.__processor.process_to_ocr(cupon)
        ocr_data = self.__get_by_ocr(img_processed_ocr)

        if ocr_data:
            return {"data": ocr_data, "message": "Ocr engine processed successfully"}

        return {"data": None, "message": "Ocr engine not processed"}

    def __get_by_qrcode(self, img_processed_qrcode : bytes):
        qrcode_data, points, _ = self.__qrcode_detector.detectAndDecode(img_processed_qrcode)
        return qrcode_data

    def __get_by_ocr(self, image : bytes):
        return []
