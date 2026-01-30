import re
import math
from paddleocr import PaddleOCR
from app.services.ocr_engines.ocr_engine import OcrEngine

class PaddleEngine(OcrEngine):
    def __init__(self):
        # use_angle_cls=True detects if the receipt is upside down or rotated
        self.ocr_engine = PaddleOCR(use_angle_cls=True, lang='pt', show_log=False)

    def process(self, image):
        # 1. Raw OCR
        try:
            result = self.ocr_engine.ocr(image, cls=True)
        except Exception as e:
            return {"itens": []}

        if not result or result[0] is None:
            return {"itens": []}

        # 2. Intelligent Line Grouping (Fixes paper "wrinkling")
        organized_lines = self._organize_lines_by_y(result[0])

        # 3. Price-anchored Extraction
        items = self._extract_items_generic(organized_lines)

        return {"itens": items}

    def _organize_lines_by_y(self, raw_result, threshold_y=10):
        """
        Groups words that are at the same height (same visual line),
        even if the paper is slightly tilted.
        """
        # Extracts data: [text, y_center, x_min]
        words = []
        for line in raw_result:
            box = line[0]
            text = line[1][0]
            y_center = (box[0][1] + box[2][1]) / 2
            x_min = box[0][0]
            words.append({'text': text, 'y': y_center, 'x': x_min})

        # Sorts by Y (height)
        words.sort(key=lambda k: k['y'])

        lines = []
        if not words: return []

        current_line = [words[0]]
        
        for i in range(1, len(words)):
            p = words[i]
            prev = current_line[-1]

            # If height difference is small, it's the same line
            if abs(p['y'] - prev['y']) < threshold_y:
                current_line.append(p)
            else:
                # New line detected: sorts the previous one by X (left to right) and saves
                current_line.sort(key=lambda k: k['x'])
                lines.append(current_line)
                current_line = [p]
        
        # Adds the last one
        current_line.sort(key=lambda k: k['x'])
        lines.append(current_line)

        return lines

    def _extract_items_generic(self, lines):
        final_items = []
        description_buffer = []
        
        # Powerful regex
        # Captures money: 1.000,00 or 10,50
        re_monetary = r'(\d{1,3}(?:\.?\d{3})*,\d{2})'
        # Captures quantity: 2 UN, 2,500 KG, or just "2" isolated before UN
        re_qty = r'(\d+(?:[.,]\d+)?)\s*(UN|PC|KG|L|M|M2|CX)?'

        # Words to ignore (Header/Footer)
        blacklist = ["TOTAL", "SUBTOTAL", "TROCO", "DINHEIRO", "CARTAO", "CREDITO", "DEBITO", "CNPJ", "CPF", "PAGAR", "TRIB", "SOMA"]

        for line_objs in lines:
            # Reconstructs the text line
            line_text = " ".join([p['text'] for p in line_objs]).upper()
            
            # Skips garbage lines (obvious header/footer)
            if any(b in line_text for b in blacklist):
                description_buffer = [] # Clears buffer for safety
                continue

            # Searches for monetary values in the line
            values = re.findall(re_monetary, line_text)
            
            # --- DECISION LOGIC ---
            
            # SCENARIO A: Item Closing Line (Has price at the end)
            # Usually the last value in the line is the Item Total
            if values:
                total_value = self._parse_float(values[-1])
                
                # If value is too high (e.g., access key that looks like money) or zero, ignore
                if total_value <= 0 or total_value > 50000:
                    description_buffer.append(line_text)
                    continue

                # Tries to find unit price and quantity on the same line
                qty = 1.0
                unit_price = total_value

                # Removes monetary values from text to leave description/qty
                text_without_price = re.sub(re_monetary, '', line_text)
                
                # Searches for quantity (e.g., "2 UN")
                match_qty = re.search(re_qty, text_without_price)
                if match_qty:
                    try:
                        qty_raw = match_qty.group(1).replace(',', '.')
                        qty = float(qty_raw)
                        # If qty found, tries to deduce unit price
                        if len(values) >= 2:
                            unit_price = self._parse_float(values[-2]) # Second to last value is the unit price
                        else:
                            unit_price = round(total_value / qty, 4) if qty > 0 else total_value
                    except:
                        pass

                # If current line has little text (only numbers), description is in buffer
                # If current line has text (e.g., "COCA COLA 2L ... 10,00"), it is the description
                
                text_part = re.sub(r'[\d.,]+', '', line_text).strip()
                
                final_desc = ""
                if len(text_part) > 3:
                    # Description is on the price line itself
                    final_desc = (" ".join(description_buffer) + " " + line_text).strip()
                else:
                    # Description is all in previous lines (case of DECA receipt)
                    final_desc = " ".join(description_buffer).strip()
                    # Adds product code if it's on the price line (e.g., "30804")
                    codes = re.findall(r'\b\d{4,14}\b', line_text)
                    if codes: final_desc = f"{codes[0]} {final_desc}"

                # Final description cleanup (removes prices and quantities that remained in text)
                final_desc = re.sub(re_monetary, '', final_desc)
                final_desc = re.sub(r'\b\d+(?:[.,]\d+)?\s*(UN|KG|PC)\b', '', final_desc).strip()

                if final_desc:
                    final_items.append({
                        "descricao": final_desc,
                        "quantidade": qty,
                        "preco_unitario": unit_price,
                        "total": total_value
                    })
                
                # Resets buffer because we closed an item
                description_buffer = []

            # SCENARIO B: Description Line (No price)
            else:
                # Just accumulates text, ignoring useless isolated numbers
                if len(line_text) > 2:
                    description_buffer.append(line_text)

        return final_items

    def _parse_float(self, val_str):
        try:
            clean = val_str.replace('.', '').replace(',', '.')
            return float(clean)
        except:
            return 0.0