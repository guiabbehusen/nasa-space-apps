from pydantic import BaseModel, EmailStr
from typing import Optional, Dict

class EmailSubscription(BaseModel):
    email: EmailStr
    location: Optional[str] = None
    profile: Optional[str] = None
    thresholds: Optional[Dict] = None
