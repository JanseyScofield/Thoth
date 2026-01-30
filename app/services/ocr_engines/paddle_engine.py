import re
import math
from paddleocr import PaddleOCR
from app.services.ocr_engines.ocr_engine import OcrEngine

class PaddleEngine(OcrEngine):
    def __init__(self):
        # use_angle_cls=True detecta se o cupom está de cabeça para baixo ou girado
        self.ocr_engine = PaddleOCR(use_angle_cls=True, lang='pt', show_log=False)

    def process(self, image):
        # 1. OCR Bruto
        try:
            result = self.ocr_engine.ocr(image, cls=True)
        except Exception as e:
            return {"itens": []}

        if not result or result[0] is None:
            return {"itens": []}

        # 2. Agrupamento Inteligente de Linhas (Corrige o "amassado" do papel)
        linhas_organizadas = self._organizar_linhas_por_y(result[0])

        # 3. Extração baseada em Ancoragem de Preço
        itens = self._extrair_itens_generico(linhas_organizadas)

        return {"itens": itens}

    def _organizar_linhas_por_y(self, raw_result, threshold_y=10):
        """
        Agrupa palavras que estão na mesma altura (mesma linha visual),
        mesmo que o papel esteja levemente torto.
        """
        # Extrai dados: [texto, y_centro, x_min]
        palavras = []
        for line in raw_result:
            box = line[0]
            texto = line[1][0]
            y_centro = (box[0][1] + box[2][1]) / 2
            x_min = box[0][0]
            palavras.append({'text': texto, 'y': y_centro, 'x': x_min})

        # Ordena por Y (altura)
        palavras.sort(key=lambda k: k['y'])

        linhas = []
        if not palavras: return []

        linha_atual = [palavras[0]]
        
        for i in range(1, len(palavras)):
            p = palavras[i]
            prev = linha_atual[-1]

            # Se a diferença de altura for pequena, é a mesma linha
            if abs(p['y'] - prev['y']) < threshold_y:
                linha_atual.append(p)
            else:
                # Nova linha detectada: ordena a anterior por X (esquerda p/ direita) e salva
                linha_atual.sort(key=lambda k: k['x'])
                linhas.append(linha_atual)
                linha_atual = [p]
        
        # Adiciona a última
        linha_atual.sort(key=lambda k: k['x'])
        linhas.append(linha_atual)

        return linhas

    def _extrair_itens_generico(self, linhas):
        itens_finais = []
        buffer_descricao = []
        
        # Regex poderosos
        # Captura dinheiro: 1.000,00 ou 10,50
        re_monetario = r'(\d{1,3}(?:\.?\d{3})*,\d{2})'
        # Captura quantidade: 2 UN, 2,500 KG, ou apenas "2" isolado antes de UN
        re_qtd = r'(\d+(?:[.,]\d+)?)\s*(UN|PC|KG|L|M|M2|CX)?'

        # Palavras para ignorar (Cabeçalho/Rodapé)
        blacklist = ["TOTAL", "SUBTOTAL", "TROCO", "DINHEIRO", "CARTAO", "CREDITO", "DEBITO", "CNPJ", "CPF", "PAGAR", "TRIB", "SOMA"]

        for linha_objs in linhas:
            # Reconstrói a linha de texto
            texto_linha = " ".join([p['text'] for p in linha_objs]).upper()
            
            # Pula linhas de lixo (cabeçalho/rodapé óbvios)
            if any(b in texto_linha for b in blacklist):
                buffer_descricao = [] # Limpa buffer por segurança
                continue

            # Busca valores monetários na linha
            valores = re.findall(re_monetario, texto_linha)
            
            # --- LÓGICA DE DECISÃO ---
            
            # CENÁRIO A: Linha de Fechamento de Item (Tem preço no final)
            # Geralmente o último valor da linha é o Total do Item
            if valores:
                valor_total = self._parse_float(valores[-1])
                
                # Se o valor for muito alto (ex: chave de acesso que parece dinheiro) ou zero, ignora
                if valor_total <= 0 or valor_total > 50000: 
                    buffer_descricao.append(texto_linha)
                    continue

                # Tenta achar unitário e quantidade na mesma linha
                qtd = 1.0
                unitario = valor_total

                # Remove os valores monetários do texto para sobrar a descrição/qtd
                texto_sem_preco = re.sub(re_monetario, '', texto_linha)
                
                # Busca quantidade (ex: "2 UN")
                match_qtd = re.search(re_qtd, texto_sem_preco)
                if match_qtd:
                    try:
                        qtd_raw = match_qtd.group(1).replace(',', '.')
                        qtd = float(qtd_raw)
                        # Se achou qtd, tenta deduzir unitário
                        if len(valores) >= 2:
                            unitario = self._parse_float(valores[-2]) # Penúltimo valor é o unitário
                        else:
                            unitario = round(valor_total / qtd, 4) if qtd > 0 else valor_total
                    except:
                        pass

                # Se a linha atual tem pouco texto (só numeros), a descrição está no buffer
                # Se a linha atual tem texto (ex: "COCA COLA 2L ... 10,00"), ela é a descrição
                
                parte_texto = re.sub(r'[\d.,]+', '', texto_linha).strip()
                
                desc_final = ""
                if len(parte_texto) > 3:
                    # Descrição está na própria linha do preço
                    desc_final = (" ".join(buffer_descricao) + " " + texto_linha).strip()
                else:
                    # Descrição está toda nas linhas anteriores (caso do seu cupom DECA)
                    desc_final = " ".join(buffer_descricao).strip()
                    # Adiciona o código do produto se estiver na linha do preço (ex: "30804")
                    codigos = re.findall(r'\b\d{4,14}\b', texto_linha) 
                    if codigos: desc_final = f"{codigos[0]} {desc_final}"

                # Limpeza final da descrição (tira preços e quantidades que sobraram no texto)
                desc_final = re.sub(re_monetario, '', desc_final)
                desc_final = re.sub(r'\b\d+(?:[.,]\d+)?\s*(UN|KG|PC)\b', '', desc_final).strip()

                if desc_final:
                    itens_finais.append({
                        "descricao": desc_final,
                        "quantidade": qtd,
                        "preco_unitario": unitario,
                        "total": valor_total
                    })
                
                # Reseta buffer pois fechamos um item
                buffer_descricao = []

            # CENÁRIO B: Linha de Descrição (Sem preço)
            else:
                # Apenas acumula texto, ignorando números soltos inúteis
                if len(texto_linha) > 2:
                    buffer_descricao.append(texto_linha)

        return itens_finais

    def _parse_float(self, val_str):
        try:
            clean = val_str.replace('.', '').replace(',', '.')
            return float(clean)
        except:
            return 0.0