from dataclasses import dataclass
from typing import Any

from scripts import seed_squat_local_accounts as seed_module
from scripts.seed_squat_local_accounts import LOCAL_ACCOUNTS


def test_local_accounts_define_one_investigator_and_three_experts() -> None:
    roles = [role for _, _, role in LOCAL_ACCOUNTS]
    emails = [email for email, _, _ in LOCAL_ACCOUNTS]

    assert roles.count("investigator") == 1
    assert roles.count("expert") == 3
    assert len(emails) == len(set(emails))


@dataclass
class _Response:
    payload: dict[str, Any]

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self.payload


def test_seed_accounts_upserts_auth_users_and_profiles(monkeypatch) -> None:
    profile_payloads: list[dict[str, Any]] = []
    auth_posts = 0

    monkeypatch.setattr(
        seed_module,
        "_supabase_environment",
        lambda: {"API_URL": "http://local", "SERVICE_ROLE_KEY": "service"},
    )
    monkeypatch.setattr(
        seed_module.requests,
        "get",
        lambda *args, **kwargs: _Response(
            {
                "users": [
                    {
                        "id": "existing-id",
                        "email": "investigator@sentadilla.local",
                    }
                ]
            }
        ),
    )

    def fake_post(url: str, **kwargs) -> _Response:
        nonlocal auth_posts
        if url.endswith("/rest/v1/profiles"):
            profile_payloads.append(kwargs["json"])
            return _Response({})
        auth_posts += 1
        return _Response({"id": f"new-id-{auth_posts}"})

    monkeypatch.setattr(seed_module.requests, "post", fake_post)
    monkeypatch.setattr(
        seed_module.requests,
        "put",
        lambda *args, **kwargs: _Response({"id": "existing-id"}),
    )

    seed_module.seed_accounts("local-password")

    assert auth_posts == 3
    assert len(profile_payloads) == 4
    assert profile_payloads[0]["user_id"] == "existing-id"
    assert {profile["squat_role"] for profile in profile_payloads} == {
        "investigator",
        "expert",
    }
