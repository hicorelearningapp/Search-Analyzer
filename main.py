# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "🚀 FastAPI is running on Azure!"}

@app.get("/health")
def health():
    return {"status": "healthy"}
