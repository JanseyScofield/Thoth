import base64
from fastapi import FastAPI, File, UploadFile

app = FastAPI(docs_url="/docs", redoc_url=None)

@app.post("/scan")
async def scan(file : UploadFile = File(...)):
    try:       
       content = await file.read()
       return {
           "filename" : content,
           "filelenght" : len(content)
        }
    except Exception as e:
        return {"error": str(e)}