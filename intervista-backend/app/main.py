from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoints import router as api_router
from dotenv import load_dotenv
from pathlib import Path
import os

# Load .env from project root
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path)

# Debug environment
print("API_KEY:", os.getenv("API_KEY"))
print("API_BASE:", os.getenv("API_BASE"))
print("MODEL:", os.getenv("MODEL"))

app = FastAPI(title="InterVista AI - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok"}
