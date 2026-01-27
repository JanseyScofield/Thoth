# Classe base das engines de ocr, pois, caso a gente queira trocar futuramente, basta ela implementar 
# dessa classe que o código do facade funcionará igualmente

from abc import ABC, abstractmethod

class OcrEngine(ABC):
    @abstractmethod
    def process(self, data):
        pass