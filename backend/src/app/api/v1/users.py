from fastapi import APIRouter, Depends
from app.schemas.user import UserOut
from app.auth.jwt import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserOut)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
