#Classe que contém os endpoints do scan

from fastapi import APIRouter, File, UploadFile
from app.services.receipt_service import ReceiptService
from app.services.ocr_engines.paddle_engine import PaddleEngine
from app.services.processors.image_processor import ImageProcessor

router = APIRouter()
ocr_engine = PaddleEngine()
processor = ImageProcessor()
receipt_service  = ReceiptService(ocr_engine=ocr_engine, processor=processor)

@router.post("/scan")
async def scan(file: UploadFile = File(...)):
    try:       
       content = await file.read()
       cupon_response = receipt_service.process_cupon(content)
       return {
        "length_before_pre-processing": len(content),
        "length_after_pre-processing": len(cupon_response),
        "cupon_response": cupon_response
       }
    except Exception as e:
        return {"error": str(e)}
