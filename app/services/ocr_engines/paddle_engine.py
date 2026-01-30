import re
import math
from paddleocr import PaddleOCR
from app.services.ocr_engines.ocr_engine import OcrEngine

class PaddleEngine(OcrEngine):
    def __init__(self):
        self.ocr_engine = PaddleOCR(use_angle_cls=True, lang='pt', show_log=False)

    def process(self, image):
        try:
            result = self.ocr_engine.ocr(image, cls=True)
        except Exception as e:
            return {"itens": []}

        if not result or result[0] is None:
            return {"itens": []}

        organized_lines = self._organize_lines_by_y(result[0])
        items = self._extract_items_generic(organized_lines)

        return {"itens": items}

    def _organize_lines_by_y(self, raw_result, threshold_y=10):
        words = []
        for line in raw_result:
            box = line[0]
            text = line[1][0]
            y_center = (box[0][1] + box[2][1]) / 2
            x_min = box[0][0]
            words.append({'text': text, 'y': y_center, 'x': x_min})

        words.sort(key=lambda k: k['y'])

        lines = []
        if not words: return []

        current_line = [words[0]]
        
        for i in range(1, len(words)):
            p = words[i]
            prev = current_line[-1]

            if abs(p['y'] - prev['y']) < threshold_y:
                current_line.append(p)
            else:
                current_line.sort(key=lambda k: k['x'])
                lines.append(current_line)
                current_line = [p]
        
        current_line.sort(key=lambda k: k['x'])
        lines.append(current_line)

        return lines

    def _extract_items_generic(self, lines):
        final_items = []
        description_buffer = []
        
        re_monetary = r'(\d{1,3}(?:\.?\d{3})*,\d{2})'
        re_qty = r'(\d+(?:[.,]\d+)?)\s*(UN|PC|KG|L|M|M2|CX)?'

        blacklist = ["TOTAL", "SUBTOTAL", "TROCO", "DINHEIRO", "CARTAO", "CREDITO", "DEBITO", "CNPJ", "CPF", "PAGAR", "TRIB", "SOMA"]

        for line_objs in lines:
            line_text = " ".join([p['text'] for p in line_objs]).upper()
            
            if any(b in line_text for b in blacklist):
                description_buffer = []
                continue

            values = re.findall(re_monetary, line_text)
            
            if values:
                total_value = self._parse_float(values[-1])
                
                if total_value <= 0 or total_value > 50000:
                    description_buffer.append(line_text)
                    continue

                qty = 1.0
                unit_price = total_value

                text_without_price = re.sub(re_monetary, '', line_text)
                
                match_qty = re.search(re_qty, text_without_price)
                if match_qty:
                    try:
                        qty_raw = match_qty.group(1).replace(',', '.')
                        qty = float(qty_raw)
                        if len(values) >= 2:
                            unit_price = self._parse_float(values[-2])
                        else:
                            unit_price = round(total_value / qty, 4) if qty > 0 else total_value
                    except:
                        pass

                text_part = re.sub(r'[\d.,]+', '', line_text).strip()
                
                final_desc = ""
                if len(text_part) > 3:
                    final_desc = (" ".join(description_buffer) + " " + line_text).strip()
                else:
                    final_desc = " ".join(description_buffer).strip()
                    codes = re.findall(r'\b\d{4,14}\b', line_text)
                    if codes: final_desc = f"{codes[0]} {final_desc}"

                final_desc = re.sub(re_monetary, '', final_desc)
                final_desc = re.sub(r'\b\d+(?:[.,]\d+)?\s*(UN|KG|PC)\b', '', final_desc).strip()

                if final_desc:
                    final_items.append({
                        "descricao": final_desc,
                        "quantidade": qty,
                        "preco_unitario": unit_price,
                        "total": total_value
                    })
                
                description_buffer = []

            else:
                if len(line_text) > 2:
                    description_buffer.append(line_text)

        return final_items

    def _parse_float(self, val_str):
        try:
            clean = val_str.replace('.', '').replace(',', '.')
            return float(clean)
        except:
            return 0.0
