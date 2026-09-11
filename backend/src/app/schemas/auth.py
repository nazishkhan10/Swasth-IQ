from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserOut

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
