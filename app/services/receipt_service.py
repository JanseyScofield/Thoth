# Classe que orquestra a chamada dos serviços, um facade que recebe um OCR no construtor.
# Ele tem o método que vai ser chamado na controller, vai chamar os serviços e retornar o resultado.

from app.services.ocr_engines.ocr_engine import OcrEngine

class ReceiptService:
    def __init__(self, ocr_engine : OcrEngine):
        self.__ocr_engine = ocr_engine

    def process_cupon(self, cupon):
        pass