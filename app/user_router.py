from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, constr
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional

from utils.auth_helpers import verify_firebase_token, upsert_user_from_token
from utils.db import async_session
from utils.models import User, PrivacyLevel


user_router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    display_name: Optional[constr(max_length=150)] = None
    privacy_level: Optional[PrivacyLevel] = None
    consent_version_id: Optional[str] = None


@user_router.post("/login")
async def login_route(token_payload: dict = Depends(verify_firebase_token)):
    """
    Login endpoint: verifies token (via dependency) and returns the upserted user.
    - clients should call Firebase Auth on client and pass the ID token in Authorization header.
    """
    async with async_session() as session:
        user = await upsert_user_from_token(token_payload, session)
        return user.public_dict()


@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup_route(
    body: SignupRequest,
    token_payload: dict = Depends(verify_firebase_token),
):
    """
    Signup endpoint: create user (if not exists) and apply onboarding fields.
    If user exists, will update allowed fields (display_name, privacy_level, consent_version_id).
    """
    async with async_session() as session:
        user = await upsert_user_from_token(token_payload, session, set_last_login=True)
        updated = False

        if body.display_name and user.display_name != body.display_name:
            user.display_name = body.display_name
            updated = True

        if body.privacy_level and user.privacy_level != body.privacy_level:
            user.privacy_level = body.privacy_level
            updated = True

        if body.consent_version_id:
            # simple assignment; validate existence of consent_version if you have that table
            user.consent_version_id = body.consent_version_id
            updated = True

        if updated:
            session.add(user)
            await session.commit()
            await session.refresh(user)

        return user.public_dict()
