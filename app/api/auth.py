from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.user import User
from app.utils.security import hash_password
from app.services.firestore import get_firestore_client
from app.utils.security import verify_password
from app.utils.jwt import create_access_token

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    password: str
    tier: str = "free"

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(req: RegisterRequest):
    db = get_firestore_client()
    user_ref = db.collection("users").document(req.username)
    if user_ref.get().exists:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=req.username,
        hashed_password=hash_password(req.password),
        tier=req.tier,
    )
    user_ref.set(user.dict())
    return {"success": True}

@router.post("/login")
def login(req: LoginRequest):
    db = get_firestore_client()
    user_ref = db.collection("users").document(req.username)
    user_doc = user_ref.get()
    if not user_doc.exists:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_data = user_doc.to_dict()
    if not verify_password(req.password, user_data["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": req.username})
    return {"access_token": token, "token_type": "bearer"}