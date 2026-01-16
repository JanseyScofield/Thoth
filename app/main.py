import base64
from fastapi import FastAPI, File, UploadFile

app = FastAPI(docs_url="/docs", redoc_url=None)

@app.get("/")
def health_check():
    return {"message" : "API is running!"}

@app.post("/read-coupon")
async def read_coupon(file : UploadFile = File(...)):
    try:       
       content = await file.read()
       return {
           "filename" : content,
           "filelenght" : len(content)
        }
    except Exception as e:
        return {"error": str(e)}