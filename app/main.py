from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.subscriptions import router as subscriptions_router


app = FastAPI()

app.include_router(auth_router, prefix="/api/auth")
app.include_router(subscriptions_router, prefix="/api/subscriptions")

@app.get("/")
def read_root():
    return {"message": "HAB Backend is running"}