from fastapi import APIRouter, HTTPException, Request
from app.services.firestore import get_firestore_client

router = APIRouter()

@router.get("/")
def get_subscriptions():
    db = get_firestore_client()
    subs_ref = db.collection("subscriptions")
    docs = subs_ref.stream()
    subscriptions = {}
    for doc in docs:
        subscriptions[doc.id] = doc.to_dict()
    return subscriptions

@router.post("/")
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