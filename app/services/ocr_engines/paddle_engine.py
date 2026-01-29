import re
from paddleocr import PaddleOCR
from app.services.ocr_engines.ocr_engine import OcrEngine

class PaddleEngine(OcrEngine):
    def __init__(self):
        # Versão 2.7.3: Simples, estável e aceita show_log.
        # use_angle_cls=True: corrige rotação do cupom
        self.ocr_engine = PaddleOCR(use_angle_cls=True, lang='pt', show_log=False)

    def _limpar_valor(self, texto_valor):
        """Converte string financeira suja para float."""
        if not texto_valor: return 0.0
        txt = str(texto_valor)
        # Remove tudo que não é dígito, ponto ou vírgula
        limpo = re.sub(r'[^\d.,]', '', txt)
        
        # Resolve confusão 1.000,00 vs 1,000.00
        if ',' in limpo and '.' in limpo:
            limpo = limpo.replace('.', '') 
        limpo = limpo.replace(',', '.')    
        
        try:
            return float(limpo)
        except ValueError:
            return 0.0

    def process(self, image_binarizada):
        # 1. OCR -> Retorna lista de caixas e textos
        try:
            result = self.ocr_engine.ocr(image_binarizada, cls=True)
        except Exception as e:
            print(f"Erro Fatal no Paddle: {e}")
            return {"itens": []}
        
        if not result or result[0] is None:
            return {"itens": []}

        # 2. Achatar resultado
        deteccoes = []
        for line in result[0]:
            box = line[0]
            texto = line[1][0]
            
            # Centro Y para definir a linha
            y_centro = (box[0][1] + box[2][1]) / 2
            x_inicio = box[0][0]
            
            deteccoes.append({'text': texto, 'y': y_centro, 'x': x_inicio})

        # 3. Agrupamento e Parsing
        linhas_visuais = self._agrupar_por_y(deteccoes)
        produtos = self._parse_linhas_para_json(linhas_visuais)
        
        return {"itens": produtos}

    def _agrupar_por_y(self, deteccoes, margem_y=10):
        """Agrupa textos na mesma altura vertical."""
        deteccoes.sort(key=lambda d: d['y'])
        linhas = []
        if not deteccoes: return []

        linha_atual = [deteccoes[0]]
        for i in range(1, len(deteccoes)):
            item = deteccoes[i]
            referencia = linha_atual[-1]
            
            if abs(item['y'] - referencia['y']) <= margem_y:
                linha_atual.append(item)
            else:
                linha_atual.sort(key=lambda d: d['x'])
                linhas.append(linha_atual)
                linha_atual = [item]

        if linha_atual:
            linha_atual.sort(key=lambda d: d['x'])
            linhas.append(linha_atual)
        return linhas

    def _parse_linhas_para_json(self, linhas_visuais):
        """Lógica de Cupom: Acumula texto até achar preço."""
        lista_final = []
        item_buffer = {"descricao": "", "quantidade": 0.0, "preco_unitario": 0.0, "total": 0.0}
        regex_fin = r'(\d+[.,]\d{2,3})'

        for linha in linhas_visuais:
            frase = " ".join([obj['text'] for obj in linha]).upper()
            valores = re.findall(regex_fin, frase)
            
            # Se tem 2 ou mais valores financeiros, é o fechamento do item
            if len(valores) >= 2:
                item_buffer["total"] = self._limpar_valor(valores[-1])
                item_buffer["preco_unitario"] = self._limpar_valor(valores[-2])
                item_buffer["quantidade"] = self._limpar_valor(valores[0])
                
                if item_buffer["descricao"].strip():
                    lista_final.append(item_buffer.copy())
                
                item_buffer = {"descricao": "", "quantidade": 0.0, "preco_unitario": 0.0, "total": 0.0}
            else:
                item_buffer["descricao"] += " " + frase

        return lista_final