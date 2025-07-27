from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.subscriptions import router as subscriptions_router
from app.api.upgrade_request import router as upgrade_request_router
from app.api.users import router as users_router
from app.api.predict import router as predict_router

app = FastAPI()

app.include_router(auth_router, prefix="/api/auth")
app.include_router(subscriptions_router, prefix="/api/subscriptions")
app.include_router(upgrade_request_router, prefix="/api/upgrade-requests")
app.include_router(users_router, prefix="/api/users")
app.include_router(predict_router, prefix="/api/predict")

@app.get("/")
def read_root():
    return {"message": "HAB Backend is running"}