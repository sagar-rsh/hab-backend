from pydantic import BaseModel

class Subscription(BaseModel):
    username: str
    tier: str
    apiCallsUsed: int
    lastResetDate: str