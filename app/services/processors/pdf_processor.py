from pdf2image import convert_from_bytes
import numpy as np
import cv2

class PdfProcessor:
    def process_to_images(self, file_bytes: bytes) -> list:
        """
        Retorna uma lista de imagens em formato numpy/OpenCV (BGR).
        """
        try:
            # Converte bytes do PDF para objetos PIL Image
            pil_images = convert_from_bytes(file_bytes)
            
            opencv_images = []
            for pil_img in pil_images:
                # 1. Converte PIL para Numpy (Isso gera RGB)
                numpy_img = np.array(pil_img)
                
                # 2. Converte RGB para BGR (Padrão do OpenCV/cv2)
                bgr_img = cv2.cvtColor(numpy_img, cv2.COLOR_RGB2BGR)
                
                opencv_images.append(bgr_img)
            
            return opencv_images
        except Exception as e:
            print(f"Erro ao processar PDF: {e}")
            return []

    def is_pdf(self, file_bytes: bytes) -> bool:
        """
        Checa se um arquivo é PDF.
        """
        # Checa se os primeiros 4 bytes correspondem à assinatura de um PDF
        return file_bytes.startswith(b'%PDF')