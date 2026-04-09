"""Small Supabase Storage REST helper for chat media artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import requests

from app.config import get_settings


@dataclass(slots=True, frozen=True)
class UploadedStorageObject:
    """Metadata returned after uploading one file to Supabase Storage."""

    bucket: str
    path: str
    public_url: str
    content_type: str
    size_bytes: int


class SupabaseStorageError(RuntimeError):
    """Raised when the storage REST API returns an unexpected response."""


class SupabaseStorageClient:
    """Thin REST wrapper around Supabase Storage using the service key."""

    def __init__(
        self,
        *,
        supabase_url: str | None = None,
        service_key: str | None = None,
        bucket: str | None = None,
    ) -> None:
        settings = get_settings()
        self.supabase_url = (supabase_url or settings.supabase_url).rstrip("/")
        self.service_key = service_key or settings.supabase_secret_key or settings.supabase_service_key
        self.bucket = bucket or settings.supabase_chat_bucket

    @property
    def is_configured(self) -> bool:
        """Return True when the required Supabase Storage settings are available."""
        return bool(self.supabase_url and self.service_key and self.bucket)

    def ensure_public_bucket(self, bucket: str | None = None) -> None:
        """Create the bucket if needed and ensure it can serve public URLs."""
        self._require_configuration()
        target_bucket = bucket or self.bucket
        response = requests.get(
            f"{self.supabase_url}/storage/v1/bucket/{target_bucket}",
            headers=self._headers(),
            timeout=30,
        )
        if response.status_code == 200:
            return
        if response.status_code not in {400, 404} and "Bucket not found" not in response.text:
            raise SupabaseStorageError(
                f"Failed to inspect storage bucket '{target_bucket}': {response.status_code} {response.text}"
            )
        create_response = requests.post(
            f"{self.supabase_url}/storage/v1/bucket",
            headers={**self._headers(), "Content-Type": "application/json"},
            json={"id": target_bucket, "name": target_bucket, "public": True},
            timeout=30,
        )
        if create_response.status_code not in {200, 201, 409}:
            raise SupabaseStorageError(
                f"Failed to create storage bucket '{target_bucket}': {create_response.status_code} {create_response.text}"
            )

    def upload_bytes(
        self,
        *,
        path: str,
        payload: bytes,
        content_type: str,
        upsert: bool = True,
        bucket: str | None = None,
    ) -> UploadedStorageObject:
        """Upload raw bytes to the configured bucket and return its public URL."""
        self._require_configuration()
        target_bucket = bucket or self.bucket
        self.ensure_public_bucket(target_bucket)
        normalized_path = path.strip("/").replace("\\", "/")
        upload_response = requests.post(
            f"{self.supabase_url}/storage/v1/object/{target_bucket}/{quote(normalized_path, safe='/')}",
            headers={
                **self._headers(),
                "Content-Type": content_type,
                "x-upsert": "true" if upsert else "false",
            },
            data=payload,
            timeout=60,
        )
        if upload_response.status_code not in {200, 201}:
            raise SupabaseStorageError(
                f"Failed to upload '{normalized_path}' to bucket '{target_bucket}': "
                f"{upload_response.status_code} {upload_response.text}"
            )
        return UploadedStorageObject(
            bucket=target_bucket,
            path=normalized_path,
            public_url=self.public_url(normalized_path, bucket=target_bucket),
            content_type=content_type,
            size_bytes=len(payload),
        )

    def upload_file(
        self,
        *,
        local_path: Path,
        path: str,
        content_type: str,
        upsert: bool = True,
        bucket: str | None = None,
    ) -> UploadedStorageObject:
        """Upload one local file to the configured bucket."""
        return self.upload_bytes(
            path=path,
            payload=local_path.read_bytes(),
            content_type=content_type,
            upsert=upsert,
            bucket=bucket,
        )

    def public_url(self, path: str, *, bucket: str | None = None) -> str:
        """Build the public URL for one bucket object path."""
        normalized_path = path.strip("/").replace("\\", "/")
        target_bucket = bucket or self.bucket
        return f"{self.supabase_url}/storage/v1/object/public/{target_bucket}/{quote(normalized_path, safe='/')}"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.service_key}",
            "apikey": self.service_key,
        }

    def _require_configuration(self) -> None:
        if self.is_configured:
            return
        raise SupabaseStorageError("Supabase Storage is not configured. Check SUPABASE_URL, key, and bucket settings.")
