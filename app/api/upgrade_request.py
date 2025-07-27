from fastapi import APIRouter, HTTPException, Request, Depends
from app.models.upgrade_request import UpgradeRequest
from app.services.firestore import get_firestore_client
from app.utils.deps import get_current_user

router = APIRouter()

@router.get("/", dependencies=[Depends(get_current_user)])
def get_upgrade_requests():
    db = get_firestore_client()
    requests_ref = db.collection("upgrade_requests")
    docs = requests_ref.stream()
    requests = [doc.to_dict() for doc in docs]
    return requests

@router.post("/", dependencies=[Depends(get_current_user)])
async def handle_upgrade_request(request: Request, current_user: str = Depends(get_current_user)):
    db = get_firestore_client()
    body = await request.json()
    action = body.get("action")
    data = {k: v for k, v in body.items() if k != "action"}
    requests_ref = db.collection("upgrade_requests")
    users_ref = db.collection("users")
    subs_ref = db.collection("subscriptions")

    # Check if current user is admin for approve/reject actions
    user_doc = users_ref.document(current_user).get()
    user_data = user_doc.to_dict()
    is_admin = user_data.get("tier") == "admin"

    if action == "create":
        # Check if target user exists
        target_user_doc = users_ref.document(data["username"]).get()
        if not target_user_doc.exists:
            raise HTTPException(status_code=404, detail="Target user does not exist")
        
        # Check for existing pending request
        existing = requests_ref.where("username", "==", data["username"]).where("status", "==", "pending").stream()
        if any(existing):
            raise HTTPException(status_code=400, detail="You already have a pending upgrade request")
        new_request = UpgradeRequest(
            id=str(int(__import__("time").time() * 1000)),
            username=data["username"],
            currentTier=data["currentTier"],
            requestedTier=data["requestedTier"],
            requestDate=__import__("datetime").datetime.utcnow().isoformat(),
            status="pending",
            financialAidReason=data.get("financialAidReason"),
            currentSituation=data.get("currentSituation"),
            howItHelps=data.get("howItHelps"),
            additionalInfo=data.get("additionalInfo", ""),
        )
        requests_ref.document(new_request.id).set(new_request.dict())
        return {"success": True}

    elif action == "approve":
        if not is_admin:
            raise HTTPException(status_code=403, detail="Only admins can approve requests")
        request_id = data["requestId"]
        admin_notes = data.get("adminNotes", "")
        req_doc = requests_ref.document(request_id).get()
        if not req_doc.exists:
            raise HTTPException(status_code=404, detail="Request not found")
        req_data = req_doc.to_dict()
        req_data["status"] = "approved"
        req_data["adminNotes"] = admin_notes
        requests_ref.document(request_id).set(req_data)
        # Update user and subscription tier
        username = req_data["username"]
        requested_tier = req_data["requestedTier"]
        # Update user
        user_doc = users_ref.document(username).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            user_data["tier"] = requested_tier
            users_ref.document(username).set(user_data)
        # Update subscription
        sub_doc = subs_ref.document(username).get()
        if sub_doc.exists:
            sub_data = sub_doc.to_dict()
            sub_data["tier"] = requested_tier
            subs_ref.document(username).set(sub_data)
        return {"success": True}

    elif action == "reject":
        if not is_admin:
            raise HTTPException(status_code=403, detail="Only admins can reject requests")
        request_id = data["requestId"]
        admin_notes = data.get("adminNotes", "")
        req_doc = requests_ref.document(request_id).get()
        if not req_doc.exists:
            raise HTTPException(status_code=404, detail="Request not found")
        req_data = req_doc.to_dict()
        req_data["status"] = "rejected"
        req_data["adminNotes"] = admin_notes
        requests_ref.document(request_id).set(req_data)
        return {"success": True}

    raise HTTPException(status_code=400, detail="Invalid action")