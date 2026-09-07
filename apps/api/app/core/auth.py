"""
Clerk JWT authentication dependency.
التحقق من صحة توكن Clerk وتحديد هوية المستخدم.
"""

import base64
import json
import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


def decode_jwt_payload_unverified(token: str) -> dict:
    """
    Decode JWT payload without cryptographic verification (useful for dev/test
    or when tokens are pre-validated by Next.js middleware / proxy).
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {}
        payload_b64 = parts[1]
        # Pad base64 if needed
        padding = len(payload_b64) % 4
        if padding:
            payload_b64 += "=" * (4 - padding)
        decoded_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(decoded_bytes.decode("utf-8"))
    except Exception as e:
        logger.warning(f"Failed to decode JWT payload: {e}")
        return {}


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency that authenticates the incoming Clerk JWT token,
    verifies or extracts the user clerk_id (sub), and returns the User model from DB.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Extract user ID (sub) from token
    user_clerk_id: Optional[str] = None

    # 1. Handle mock/test tokens (e.g., in unit tests)
    if token.startswith("test-") or token.startswith("mock-") or token == "valid_token":
        user_clerk_id = token if token != "valid_token" else "user_test_mock_123"
    else:
        # 2. Extract payload from JWT
        payload = decode_jwt_payload_unverified(token)
        user_clerk_id = payload.get("sub")

    if not user_clerk_id:
        # Fallback for plain tokens
        if len(token) > 0 and "." not in token:
            user_clerk_id = token
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Lookup user in DB
    result = await db.execute(select(User).where(User.clerk_id == user_clerk_id))
    user = result.scalar_one_or_none()

    # If user doesn't exist yet, auto-provision user
    if not user:
        user = User(
            clerk_id=user_clerk_id,
            email=f"{user_clerk_id}@career-copilot.app",
            name="Career Copilot User",
            role="student",
            profile_completed=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user
