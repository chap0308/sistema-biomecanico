"""Create the four deterministic local accounts used by the squat web app."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess

import requests


LOCAL_ACCOUNTS = (
    ("investigator@sentadilla.local", "Investigador local", "investigator"),
    ("expert1@sentadilla.local", "Experto local 1", "expert"),
    ("expert2@sentadilla.local", "Experto local 2", "expert"),
    ("expert3@sentadilla.local", "Experto local 3", "expert"),
)


def _supabase_environment() -> dict[str, str]:
    command = shutil.which("supabase")
    if not command:
        raise RuntimeError("Supabase CLI is not available in PATH.")
    result = subprocess.run(
        [command, "status", "-o", "env"],
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"Supabase local is not running: {result.stderr.strip()}")
    return dict(re.findall(r'^([A-Z_]+)="(.*)"$', result.stdout, re.MULTILINE))


def seed_accounts(password: str) -> None:
    """Create or update the canonical local research accounts."""
    environment = _supabase_environment()
    api_url = environment["API_URL"]
    service_key = environment["SERVICE_ROLE_KEY"]
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"{api_url}/auth/v1/admin/users",
        headers=headers,
        params={"page": 1, "per_page": 1000},
        timeout=30,
    )
    response.raise_for_status()
    existing = {user["email"]: user for user in response.json()["users"]}

    for email, display_name, role in LOCAL_ACCOUNTS:
        payload = {
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {
                "display_name": display_name,
                "squat_role": role,
            },
        }
        user = existing.get(email)
        if user:
            result = requests.put(
                f"{api_url}/auth/v1/admin/users/{user['id']}",
                headers=headers,
                json=payload,
                timeout=30,
            )
            action = "updated"
        else:
            result = requests.post(
                f"{api_url}/auth/v1/admin/users",
                headers=headers,
                json=payload,
                timeout=30,
            )
            action = "created"
        result.raise_for_status()
        user_id = result.json()["id"]
        profile_headers = {
            **headers,
            "Prefer": "resolution=merge-duplicates,return=minimal",
        }
        profile = requests.post(
            f"{api_url}/rest/v1/profiles",
            headers=profile_headers,
            params={"on_conflict": "user_id"},
            json={
                "user_id": user_id,
                "email": email,
                "display_name": display_name,
                "squat_role": role,
            },
            timeout=30,
        )
        profile.raise_for_status()
        print(f"{action}: {email} ({role})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--password",
        default="Sentadilla2026!",
        help="Local-only password assigned to every deterministic account.",
    )
    args = parser.parse_args()
    seed_accounts(args.password)


if __name__ == "__main__":
    main()
