from abc import ABC, abstractmethod

class OcrEngine(ABC):
    @abstractmethod
    def process(self, data):
        pass
