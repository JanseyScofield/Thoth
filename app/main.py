from fastapi import FastAPI
from app.api.endpoints import scan

app = FastAPI(
    title= "Thoth API",
    docs_url="/docs", 
    redoc_url=None)

@app.get("/", tags=["Status"])
def health_check():
    return {"message": "API Thoth Online! Access /docs to test."}

app.include_router(scan.router, tags=["Scan"])