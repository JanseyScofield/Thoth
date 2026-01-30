# Base class for OCR engines. If we want to switch engines in the future,
# they just need to implement this class and the facade code will work the same way

from abc import ABC, abstractmethod

class OcrEngine(ABC):
    @abstractmethod
    def process(self, data):
        pass