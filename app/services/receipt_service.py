# Classe que orquestra a chamada dos serviços, um facade que recebe um Paddle no construtor.
# Ele tem o método que vai ser chamado na controller, vai chamar os serviços e retornar o resultado.

from paddle_engines.paddle_engine import PaddleEngine

class ReceiptService:
    def __init__(self, paddleEngine : PaddleEngine):
        self._paddleEngine = paddleEngine

    def process_cupon(self, cupon):
        pass