from fastapi import APIRouter, HTTPException, Request
from app.services.firestore import get_firestore_client
from app.utils.deps import get_current_user
from fastapi import Depends

router = APIRouter()

@router.get("/")
def get_subscriptions(current_user: str = Depends(get_current_user)):
    db = get_firestore_client()
    users_ref = db.collection("users")
    user_doc = users_ref.document(current_user).get()
    user_data = user_doc.to_dict()
    is_admin = user_data.get("tier") == "admin"

    subs_ref = db.collection("subscriptions")
    if is_admin:
        docs = subs_ref.stream()
        subscriptions = {doc.id: doc.to_dict() for doc in docs}
        return subscriptions
    else:
        sub_doc = subs_ref.document(current_user).get()
        if not sub_doc.exists:
            return {}
        return {current_user: sub_doc.to_dict()}

@router.post("/", dependencies=[Depends(get_current_user)])
async def update_subscriptions(request: Request):
    db = get_firestore_client()
    subscriptions = await request.json()
    subs_ref = db.collection("subscriptions")
    users_ref = db.collection("users")
    not_found = []

    try:
        for username, sub_data in subscriptions.items():
            user_doc = users_ref.document(username).get()
            if not user_doc.exists:
                not_found.append(username)
                continue
            subs_ref.document(username).set(sub_data)
        if not_found:
            raise HTTPException(
                status_code=400,
                detail=f"Subscriptions not updated for non-existent users: {', '.join(not_found)}"
            )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save subscriptions: {str(e)}")