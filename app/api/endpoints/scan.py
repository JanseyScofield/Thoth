#Classe que contém os endpoints do scan

from fastapi import APIRouter, File, UploadFile

router = APIRouter()

@router.post("/scan")
async def scan(file: UploadFile = File(...)):
    try:       
       content = await file.read()
       
       return {
           "filename": file.filename,
           "content_type": file.content_type,
           "tamanho_bytes": len(content)
        }
    except Exception as e:
        return {"error": str(e)}