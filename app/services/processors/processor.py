from abc import ABC, abstractmethod

class Processor(ABC):
    @abstractmethod
    def process_to_qrcode(self, data :bytes):
        pass

    @abstractmethod
    def process_to_ocr(self, data :bytes):
        pass