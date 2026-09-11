from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.schemas.auth import AuthResponse
from app.services import auth_service, user_service
from app.auth.jwt import create_access_token, get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user, access_token = auth_service.register_user(db, user_in=user_in)
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user)
    )

@router.post("/login", response_model=AuthResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, credentials=credentials)
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user)
    )

@router.get("/demo", response_model=AuthResponse)
@router.post("/demo", response_model=AuthResponse)
def demo_login(db: Session = Depends(get_db)):
    """Auto-provisions or authenticates a default demo user for seamless testing."""
    demo_email = "demo@cliniclens.ai"
    user = user_service.get_user_by_email(db, email=demo_email)
    if not user:
        demo_in = UserCreate(email=demo_email, password="DemoPassword123!", name="Demo Patient")
        user = user_service.create_user(db, user_in=demo_in)
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user)
    )

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
