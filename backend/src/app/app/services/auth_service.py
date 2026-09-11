from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.user import UserCreate, UserLogin
from app.services import user_service
from app.auth.password import verify_password
from app.auth.jwt import create_access_token
from app.models.user import User
from app.logs.logger import get_logger

logger = get_logger(__name__)

def authenticate_user(db: Session, credentials: UserLogin) -> User:
    user = user_service.get_user_by_email(db, email=credentials.email)
    if not user:
        logger.warning(f"Failed login attempt — email not found: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not verify_password(credentials.password, user.password_hash):
        logger.warning(f"Failed login attempt — wrong password for: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    logger.info(f"User logged in successfully: {credentials.email} (id={user.id})")
    return user

def register_user(db: Session, user_in: UserCreate) -> tuple[User, str]:
    existing_user = user_service.get_user_by_email(db, email=user_in.email)
    if existing_user:
        logger.warning(f"Registration failed — email already exists: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists"
        )

    if user_in.confirm_password and user_in.password != user_in.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    user = user_service.create_user(db, user_in=user_in)
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    logger.info(f"New user registered: {user.email} (id={user.id})")
    return user, access_token
