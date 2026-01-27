# Classe base das engines de paddle, pois, caso a gente queira trocar futuramente, basta ela implementar 
# dessa classe que o código do main funcionará igualmente

from abc import ABC, abstractmethod

class PaddleEngine(ABC):
    @abstractmethod
    def process(self, data):
        pass