# Classe que orquestra a chamada dos serviços, um facade que recebe um OCR no construtor.
# Ele tem o método que vai ser chamado na controller, vai chamar os serviços e retornar o resultado.

from app.services.ocr_engines.ocr_engine import OcrEngine
from app.services.processors.processor import Processor

class ReceiptService:
    def __init__(self, ocr_engine : OcrEngine, processor : Processor):
        self.__ocr_engine = ocr_engine
        self.__processor = processor

    def process_cupon(self, cupon : bytes):
        return self.__processor.process_to_ocr(cupon)