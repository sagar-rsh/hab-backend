from fastapi import APIRouter, Depends, HTTPException, Request
from app.services.firestore import get_firestore_client
from app.utils.deps import get_current_user
import requests
from app.config import TIER_LIMITS
import os

router = APIRouter()

PREDICTION_API_URL = "http://127.0.0.1:8080/predict"
PREDICTION_API_KEY = os.getenv("PREDICTION_API_KEY")

@router.post("/")
async def predict(request: Request, current_user: str = Depends(get_current_user)):
    db = get_firestore_client()
    users_ref = db.collection("users")
    subs_ref = db.collection("subscriptions")

    # Get user and subscription
    user_doc = users_ref.document(current_user).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")

    sub_doc = subs_ref.document(current_user).get()
    if not sub_doc.exists:
        raise HTTPException(status_code=404, detail="Subscription not found")
    sub_data = sub_doc.to_dict()
    tier = sub_data.get("tier", "free")
    api_calls_used = sub_data.get("apiCallsUsed", 0)
    api_calls_limit = TIER_LIMITS.get(tier, 3)

    if api_calls_used >= api_calls_limit:
        raise HTTPException(status_code=403, detail="API call limit reached for your subscription tier")

    # Get prediction request body
    req_body = await request.json()
    # Forward request to external prediction API
    try:
        response = requests.post(
            PREDICTION_API_URL,
            json=req_body,
            headers={"x-api-key": PREDICTION_API_KEY}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Prediction failed"))
        result = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction service error: {str(e)}")

    # Increment API usage
    sub_data["apiCallsUsed"] = api_calls_used + 1
    subs_ref.document(current_user).set(sub_data)

    result["apiCallsUsed"] = sub_data["apiCallsUsed"]
    result["apiCallsLimit"] = api_calls_limit
    return result