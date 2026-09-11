"""
API v1 Master Router.
Aggregates authentication, uploads, ocr, parser, and phase 5 validation endpoints.
"""

from fastapi import APIRouter
from app.api.v1 import auth, upload, ocr, parser, validation, analysis, chat

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(upload.router)
api_router.include_router(ocr.router)
api_router.include_router(parser.router)
api_router.include_router(validation.router)
api_router.include_router(analysis.router)
api_router.include_router(chat.router)


