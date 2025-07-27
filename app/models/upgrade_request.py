from pydantic import BaseModel
from typing import Optional

class UpgradeRequest(BaseModel):
    id: str
    username: str
    currentTier: str
    requestedTier: str
    requestDate: str
    status: str  # "pending", "approved", "rejected"
    financialAidReason: Optional[str] = None
    currentSituation: Optional[str] = None
    howItHelps: Optional[str] = None
    additionalInfo: Optional[str] = ""
    adminNotes: Optional[str] = ""