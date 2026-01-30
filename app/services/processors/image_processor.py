import cv2
import numpy as np
from app.services.processors.processor import Processor

class ImageProcessor(Processor):
    def __init__(self):
        super().__init__()

    # ---------------------------------------------------------
    # 1. Métodos Obrigatórios da Interface (Correção do Erro)
    # ---------------------------------------------------------
    # Estes métodos satisfazem a classe abstrata 'Processor'.
    # Eles recebem bytes (o padrão antigo) e usam a nova lógica.
    
    def process_to_ocr(self, data: bytes):
        # Converte bytes -> Matriz e chama a nova lógica
        matrix = self.bytes_to_matrix(data)
        if matrix is None:
            return None
        return self.process_matrix_to_ocr(matrix)

    def process_to_qrcode(self, data: bytes):
        # Converte bytes -> Matriz e chama a nova lógica
        matrix = self.bytes_to_matrix(data)
        if matrix is None:
            return None
        return self.process_matrix_to_qrcode(matrix)

    # ---------------------------------------------------------
    # 2. Novos Métodos para lidar com Matrizes (PDF/OpenCV)
    # ---------------------------------------------------------

    def bytes_to_matrix(self, data: bytes):
        """Decodifica bytes brutos (JPG/PNG) para matriz OpenCV"""
        if not data:
            return None
        nparr = np.frombuffer(data, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    def process_matrix_to_qrcode(self, img_matrix: np.ndarray):
        # Garante que a matriz é válida antes de processar
        if img_matrix is None or img_matrix.size == 0:
            return None
            
        if len(img_matrix.shape) == 3:
            return cv2.cvtColor(img_matrix, cv2.COLOR_BGR2GRAY)
        return img_matrix
    
    def process_matrix_to_ocr(self, img_matrix: np.ndarray):
        # Garante que a matriz é válida
        if img_matrix is None or img_matrix.size == 0:
            return None

        if len(img_matrix.shape) == 3:
            img_gray = cv2.cvtColor(img_matrix, cv2.COLOR_BGR2GRAY)
        else:
            img_gray = img_matrix

        height, width = img_gray.shape
        scale = 2
        
        # Evita crash de memória em imagens muito grandes (comum em PDF convertidos)
        if height > 2500 or width > 2500: 
            scale = 1
            
        return cv2.resize(img_gray, (width * scale, height * scale), interpolation=cv2.INTER_CUBIC)