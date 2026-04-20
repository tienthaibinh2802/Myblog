import os
import posixpath
from pathlib import Path
from uuid import uuid4
from urllib.parse import quote

import requests
from django.core.files.storage import Storage


class SupabaseStorage(Storage):
    """Store uploaded media files in Supabase Storage."""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        self.bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "media").strip()

    def _check_config(self):
        if not self.supabase_url or not self.service_key or not self.bucket:
            raise RuntimeError(
                "Supabase storage is not configured. "
                "Set SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_STORAGE_BUCKET."
            )

    def _build_object_name(self, name):
        normalized_name = str(Path(name).as_posix()).lstrip("/")
        root, ext = posixpath.splitext(normalized_name)
        return f"{root}_{uuid4().hex[:10]}{ext}"

    def _headers(self):
        return {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
        }

    def _save(self, name, content):
        self._check_config()
        object_name = self._build_object_name(name)
        upload_url = (
            f"{self.supabase_url}/storage/v1/object/"
            f"{self.bucket}/{quote(object_name, safe='/')}"
        )

        content.seek(0)
        response = requests.post(
            upload_url,
            headers={
                **self._headers(),
                "x-upsert": "false",
                "Content-Type": "application/octet-stream",
            },
            data=content.read(),
            timeout=30,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Supabase upload failed: {response.status_code} {response.text}")
        return object_name

    def url(self, name):
        self._check_config()
        return (
            f"{self.supabase_url}/storage/v1/object/public/"
            f"{self.bucket}/{quote(name, safe='/')}"
        )

    def exists(self, name):
        return False

    def delete(self, name):
        self._check_config()
        delete_url = (
            f"{self.supabase_url}/storage/v1/object/"
            f"{self.bucket}/{quote(name, safe='/')}"
        )
        response = requests.delete(delete_url, headers=self._headers(), timeout=30)
        if response.status_code not in (200, 204, 404):
            raise RuntimeError(f"Supabase delete failed: {response.status_code} {response.text}")

