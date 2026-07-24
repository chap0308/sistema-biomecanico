"""Authentication tests for the bilateral-squat API."""

from __future__ import annotations

import asyncio

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from api.auth import SquatApiUser, get_squat_api_user
from app.config import Settings
from app.main import app


def test_auth_dependency_uses_local_investigator_when_disabled() -> None:
    user = asyncio.run(
        get_squat_api_user(
            authorization=None,
            settings=Settings(squat_auth_required=False),
        )
    )

    assert user.user_id == "local-researcher"
    assert user.role == "investigator"


def test_auth_dependency_requires_token_when_enabled() -> None:
    with pytest.raises(HTTPException) as exception:
        asyncio.run(
            get_squat_api_user(
                authorization=None,
                settings=Settings(squat_auth_required=True),
            )
        )

    assert exception.value.status_code == 401


def test_expert_cannot_register_a_case() -> None:
    async def expert_user() -> SquatApiUser:
        return SquatApiUser(
            user_id="expert-1",
            email="expert@example.test",
            role="expert",
        )

    app.dependency_overrides[get_squat_api_user] = expert_user
    try:
        response = TestClient(app).post(
            "/api/v1/squat/cases",
            data={"case_id": "caso_experto_001"},
            files={"video": ("squat.mp4", b"video", "video/mp4")},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
