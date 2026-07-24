"""Authentication dependencies for the bilateral-squat API."""

from __future__ import annotations

from typing import Annotated, Literal

import httpx
from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel

from app.config import Settings, get_settings

SquatRole = Literal["investigator", "expert"]


class SquatApiUser(BaseModel):
    """Authenticated user context consumed by squat API routes."""

    user_id: str
    email: str | None = None
    role: SquatRole


def _bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


async def get_squat_api_user(
    authorization: Annotated[str | None, Header()] = None,
    settings: Settings = Depends(get_settings),
) -> SquatApiUser:
    """Validate a Supabase access token or return the local development user."""
    if not settings.squat_auth_required:
        return SquatApiUser(
            user_id="local-researcher",
            email=None,
            role="investigator",
        )

    token = _bearer_token(authorization)
    publishable_key = (
        settings.supabase_publishable_key or settings.supabase_anon_key
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid Supabase access token is required.",
        )
    if not settings.supabase_url or not publishable_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase authentication is not configured.",
        )

    try:
        async with httpx.AsyncClient(
            timeout=settings.request_timeout_seconds
        ) as client:
            response = await client.get(
                f"{settings.supabase_url.rstrip('/')}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": publishable_key,
                },
            )
            if response.status_code == status.HTTP_200_OK:
                user_payload = response.json()
                user_id = str(user_payload["id"])
                profile_response = await client.get(
                    f"{settings.supabase_url.rstrip('/')}/rest/v1/profiles",
                    params={
                        "select": "squat_role",
                        "user_id": f"eq.{user_id}",
                    },
                    headers={
                        "Authorization": f"Bearer {token}",
                        "apikey": publishable_key,
                    },
                )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The authentication service is unavailable.",
        ) from exc

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The Supabase access token is invalid or expired.",
        )

    payload = response.json()
    if profile_response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The study profile could not be verified.",
        )
    profiles = profile_response.json()
    role = profiles[0].get("squat_role") if profiles else None
    if role not in {"investigator", "expert"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The account has no role assigned for this study.",
        )

    return SquatApiUser(
        user_id=str(payload["id"]),
        email=payload.get("email"),
        role=role,
    )


SquatUserDependency = Annotated[SquatApiUser, Depends(get_squat_api_user)]

__all__ = [
    "SquatApiUser",
    "SquatRole",
    "SquatUserDependency",
    "get_squat_api_user",
]
