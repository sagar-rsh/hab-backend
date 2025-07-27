from fastapi import APIRouter, Depends, HTTPException
from app.services.firestore import get_firestore_client
from app.utils.deps import get_current_user

router = APIRouter()

@router.get("/")
def get_all_users(current_user: str = Depends(get_current_user)):
    db = get_firestore_client()
    users_ref = db.collection("users")
    user_doc = users_ref.document(current_user).get()
    user_data = user_doc.to_dict()
    is_admin = user_data.get("tier") == "admin"
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can view all users")

    docs = users_ref.stream()
    users = [doc.to_dict() for doc in docs]
    return users