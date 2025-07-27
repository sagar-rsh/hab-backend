from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.auth import router as auth_router

app = FastAPI()

app.include_router(auth_router, prefix="/api/auth")

@app.get("/")
def read_root():
    return {"message": "HAB Backend is running"}