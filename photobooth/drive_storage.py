"""Google Drive API client for folder pools and resumable photo uploads.

The booth authenticates with a refresh token supplied through environment
variables. No credential file or access token is written to the repository.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any, Callable
from urllib.parse import urlencode
import uuid

import requests


API_ROOT = "https://www.googleapis.com/drive/v3"
UPLOAD_ROOT = "https://www.googleapis.com/upload/drive/v3"
TOKEN_URL = "https://oauth2.googleapis.com/token"
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
CHUNK_SIZE = 256 * 1024 * 4


class DriveApiError(RuntimeError):
    """A Drive operation failed, with retryability for the local upload queue."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.transient = status_code in {408, 429} or (
            status_code is not None and status_code >= 500
        )


@dataclass(frozen=True)
class RemoteDriveSlot:
    folder_id: str
    folder_url: str
    slot_key: str
    status: str
    folder_name: str
    transaction_id: str | None = None
    verified: bool = False
    issue: str | None = None


class GoogleDriveClient:
    """Small Drive v3 client with OAuth refresh and idempotent uploads."""

    def __init__(
        self,
        parent_folder_id: str,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        *,
        session: requests.Session | None = None,
    ) -> None:
        self.parent_folder_id = parent_folder_id.strip()
        self.client_id = client_id.strip()
        self.client_secret = client_secret.strip()
        self.refresh_token = refresh_token.strip()
        if not all((self.parent_folder_id, self.client_id, self.client_secret, self.refresh_token)):
            raise ValueError("Google Drive OAuth and parent-folder settings are required.")
        self.session = session or requests.Session()
        self._access_token: str | None = None
        self._token_expires_at = 0.0

    @classmethod
    def from_environment(cls) -> GoogleDriveClient | None:
        """Build a client from environment variables, or return None if unconfigured."""
        values = (
            os.environ.get("PHOTOBOOTH_DRIVE_PARENT_ID", ""),
            os.environ.get("GOOGLE_OAUTH_CLIENT_ID", ""),
            os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", ""),
            os.environ.get("GOOGLE_OAUTH_REFRESH_TOKEN", ""),
        )
        if not all(value.strip() for value in values):
            return None
        return cls(*values)

    def _get_access_token(self, force_refresh: bool = False) -> str:
        if (
            not force_refresh
            and self._access_token
            and time.monotonic() < self._token_expires_at - 60
        ):
            return self._access_token

        try:
            response = self.session.post(
                TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token",
                },
                timeout=(5, 20),
            )
            if response.status_code >= 400:
                raise DriveApiError(
                    "Google Drive sign-in needs attention. Check the booth OAuth settings.",
                    response.status_code,
                )
            body = response.json()
        except DriveApiError:
            raise
        except requests.RequestException as error:
            raise DriveApiError("Could not refresh the Google Drive access token.", 503) from error
        except ValueError as error:
            raise DriveApiError("Google returned an invalid access-token response.", 502) from error

        token = body.get("access_token") if isinstance(body, dict) else None
        if not isinstance(token, str) or not token:
            raise DriveApiError("Google did not return a usable Drive access token.")
        self._access_token = token
        self._token_expires_at = time.monotonic() + int(body.get("expires_in", 3600))
        return token

    def _request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        data: bytes | None = None,
        timeout: tuple[int, int] = (10, 60),
    ) -> requests.Response:
        for attempt in range(2):
            request_headers = dict(headers or {})
            request_headers["Authorization"] = f"Bearer {self._get_access_token(force_refresh=attempt == 1)}"
            try:
                response = self.session.request(
                    method,
                    url,
                    params=params,
                    json=json_body,
                    headers=request_headers,
                    data=data,
                    timeout=timeout,
                )
            except requests.RequestException as error:
                raise DriveApiError("Google Drive is unreachable.", 503) from error
            if response.status_code == 401 and attempt == 0:
                continue
            if response.status_code >= 400:
                message = self._error_message(response)
                raise DriveApiError(message, response.status_code)
            return response
        raise DriveApiError("Google Drive rejected the refreshed access token.", 401)

    @staticmethod
    def _error_message(response: requests.Response) -> str:
        try:
            data = response.json()
            error_body = data.get("error") if isinstance(data, dict) else None
            if isinstance(error_body, dict):
                reason = error_body.get("message")
            else:
                reason = error_body
        except ValueError:
            reason = None
        return str(reason or f"Google Drive returned HTTP {response.status_code}.")

    def _list_files(self, query: str, fields: str) -> list[dict[str, Any]]:
        files: list[dict[str, Any]] = []
        page_token: str | None = None
        while True:
            params: dict[str, Any] = {
                "q": query,
                "pageSize": 1000,
                "fields": f"nextPageToken,files({fields})",
                "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true",
            }
            if page_token:
                params["pageToken"] = page_token
            response = self._request("GET", f"{API_ROOT}/files", params=params)
            body = response.json()
            files.extend(body.get("files", []))
            page_token = body.get("nextPageToken")
            if not page_token:
                return files

    def _folder_link(self, folder: dict[str, Any]) -> str:
        url = folder.get("webViewLink")
        if not isinstance(url, str) or not url.strip():
            url = f"https://drive.google.com/drive/folders/{folder['id']}"
        resource_key = folder.get("resourceKey")
        if resource_key and "resourcekey=" not in url:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}resourcekey={resource_key}"
        return url

    def _permission_ready(self, folder_id: str) -> bool:
        response = self._request(
            "GET",
            f"{API_ROOT}/files/{folder_id}/permissions",
            params={"fields": "permissions(type,role,allowFileDiscovery)", "supportsAllDrives": "true"},
        )
        permissions = response.json().get("permissions", [])
        if any(p.get("type") == "anyone" and p.get("role") == "reader" for p in permissions):
            return True

        self._request(
            "POST",
            f"{API_ROOT}/files/{folder_id}/permissions",
            params={"fields": "id,type,role,allowFileDiscovery", "supportsAllDrives": "true"},
            json_body={"type": "anyone", "role": "reader", "allowFileDiscovery": False},
        )
        response = self._request(
            "GET",
            f"{API_ROOT}/files/{folder_id}/permissions",
            params={"fields": "permissions(type,role,allowFileDiscovery)", "supportsAllDrives": "true"},
        )
        permissions = response.json().get("permissions", [])
        return any(
            p.get("type") == "anyone"
            and p.get("role") == "reader"
            and p.get("allowFileDiscovery") is False
            for p in permissions
        )

    def _folder_is_empty(self, folder_id: str) -> bool:
        children = self._list_files(
            f"'{folder_id}' in parents and trashed = false",
            "id",
        )
        return not children

    def _validate_slot(self, folder: dict[str, Any]) -> tuple[bool, str | None, str]:
        folder_id = str(folder.get("id", ""))
        if not folder_id or folder.get("mimeType") != FOLDER_MIME_TYPE:
            return False, "Drive slot is not a folder.", ""
        try:
            if not self._permission_ready(folder_id):
                return False, "Folder link permission is not Anyone with the link · Viewer.", self._folder_link(folder)
            if not self._folder_is_empty(folder_id):
                return False, "Folder is not empty and cannot be used as a new slot.", self._folder_link(folder)
            metadata = self._request(
                "GET",
                f"{API_ROOT}/files/{folder_id}",
                params={"fields": "id,name,webViewLink,resourceKey", "supportsAllDrives": "true"},
            ).json()
            return True, None, self._folder_link(metadata)
        except DriveApiError as error:
            return False, str(error), self._folder_link(folder)

    def ensure_folder_pool(
        self,
        booth_id: str,
        target_ready: int = 25,
    ) -> list[RemoteDriveSlot]:
        """Validate existing tagged slots and create enough ready slots to reach the target."""
        escaped_booth_id = booth_id.replace("'", "\\'")
        query = (
            f"'{self.parent_folder_id}' in parents and mimeType = '{FOLDER_MIME_TYPE}' "
            f"and trashed = false and appProperties has {{ key='photoboothBoothId' "
            f"and value='{escaped_booth_id}' }} and appProperties has "
            "{ key='photoboothSlot' and value='true' }"
        )
        fields = "id,name,mimeType,webViewLink,resourceKey,appProperties,parents"
        folders = self._list_files(query, fields)
        slots: dict[str, RemoteDriveSlot] = {}
        ready_count = 0
        for folder in folders:
            props = folder.get("appProperties", {})
            status = props.get("photoboothStatus", "ACTION_REQUIRED")
            if status == "READY":
                verified, issue, url = self._validate_slot(folder)
                if verified:
                    ready_count += 1
                slots[folder["id"]] = RemoteDriveSlot(
                    folder_id=folder["id"],
                    folder_url=url,
                    slot_key=props.get("photoboothSlotKey", folder["id"]),
                    status="READY" if verified else "ACTION_REQUIRED",
                    folder_name=folder.get("name", ""),
                    transaction_id=props.get("photoboothTransactionId"),
                    verified=verified,
                    issue=issue,
                )
            else:
                slots[folder["id"]] = RemoteDriveSlot(
                    folder_id=folder["id"],
                    folder_url=self._folder_link(folder),
                    slot_key=props.get("photoboothSlotKey", folder["id"]),
                    status=status,
                    folder_name=folder.get("name", ""),
                    transaction_id=props.get("photoboothTransactionId"),
                    verified=False,
                )

        while ready_count < target_ready:
            slot_key = uuid.uuid4().hex
            metadata = {
                "name": f"PHOTOBOOTH_SLOT_{slot_key[:8]}",
                "mimeType": FOLDER_MIME_TYPE,
                "parents": [self.parent_folder_id],
                "appProperties": {
                    "photoboothSlot": "true",
                    "photoboothSlotKey": slot_key,
                    "photoboothBoothId": booth_id,
                    "photoboothStatus": "READY",
                },
            }
            folder = self._request(
                "POST",
                f"{API_ROOT}/files",
                params={"fields": fields, "supportsAllDrives": "true"},
                json_body=metadata,
            ).json()
            verified, issue, url = self._validate_slot(folder)
            slot = RemoteDriveSlot(
                folder_id=folder["id"],
                folder_url=url,
                slot_key=slot_key,
                status="READY" if verified else "ACTION_REQUIRED",
                folder_name=folder.get("name", ""),
                verified=verified,
                issue=issue,
            )
            slots[slot.folder_id] = slot
            if verified:
                ready_count += 1
            else:
                # A failed folder must not cause an infinite create loop.
                break
        return list(slots.values())

    def rename_assigned_folder(
        self,
        folder_id: str,
        transaction_id: str,
        booth_id: str,
        slot_key: str,
    ) -> None:
        self._request(
            "PATCH",
            f"{API_ROOT}/files/{folder_id}",
            params={"fields": "id,name,appProperties", "supportsAllDrives": "true"},
            json_body={
                "name": transaction_id,
                "appProperties": {
                    "photoboothSlot": "true",
                    "photoboothSlotKey": slot_key,
                    "photoboothBoothId": booth_id,
                    "photoboothStatus": "ASSIGNED",
                    "photoboothTransactionId": transaction_id,
                },
            },
        )

    @staticmethod
    def _quote_query(value: str) -> str:
        return value.replace("\\", "\\\\").replace("'", "\\'")

    def _find_existing_upload(
        self,
        folder_id: str,
        relative_path: str,
    ) -> dict[str, Any] | None:
        escaped_path = self._quote_query(relative_path)
        query = (
            f"'{folder_id}' in parents and trashed = false and appProperties has "
            f"{{ key='photoboothPath' and value='{escaped_path}' }}"
        )
        files = self._list_files(query, "id,name,size,md5Checksum,appProperties,parents")
        return files[0] if files else None

    def upload_file(
        self,
        folder_id: str,
        transaction_id: str,
        relative_path: str,
        local_path: Path,
        *,
        resume_url: str | None = None,
        on_session_url: Callable[[str | None], None] | None = None,
    ) -> dict[str, Any]:
        """Upload or verify one file, using Drive appProperties to make retries idempotent."""
        local_path = Path(local_path)
        if not local_path.is_file():
            raise DriveApiError(f"Upload file is missing: {local_path}")
        file_size = local_path.stat().st_size
        checksum = hashlib.md5(local_path.read_bytes()).hexdigest()
        existing = self._find_existing_upload(folder_id, relative_path)
        if existing and existing.get("md5Checksum") == checksum and int(existing.get("size", -1)) == file_size:
            return existing

        metadata: dict[str, Any] = {
            "name": Path(relative_path).name,
            "mimeType": "image/png" if local_path.suffix.lower() == ".png" else "image/jpeg",
            "appProperties": {
                "photoboothTransactionId": transaction_id,
                "photoboothPath": relative_path,
            },
        }
        if not existing:
            metadata["parents"] = [folder_id]
        file_id = existing.get("id") if existing else None

        if resume_url is not None:
            try:
                offset, finished = self._query_upload_status(resume_url, file_size)
                if finished is not None:
                    if on_session_url:
                        on_session_url(None)
                    return self._verify_uploaded_file(finished, file_size, checksum)
            except DriveApiError as error:
                if error.status_code != 410:
                    raise
                resume_url = None
                if on_session_url:
                    on_session_url(None)

        if resume_url is None:
            method = "PATCH" if file_id else "POST"
            endpoint = f"{UPLOAD_ROOT}/files/{file_id}" if file_id else f"{UPLOAD_ROOT}/files"
            params = {
                "uploadType": "resumable",
                "fields": "id,name,size,md5Checksum,appProperties,parents",
                "supportsAllDrives": "true",
            }
            headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Type": metadata["mimeType"],
                "X-Upload-Content-Length": str(file_size),
            }
            response = self._request(method, endpoint, params=params, json_body=metadata, headers=headers)
            resume_url = response.headers.get("Location")
            if not resume_url:
                raise DriveApiError("Drive did not return a resumable upload session URL.")
            if on_session_url:
                on_session_url(resume_url)
            offset = 0

        try:
            with local_path.open("rb") as stream:
                stream.seek(offset)
                while offset < file_size:
                    chunk = stream.read(min(CHUNK_SIZE, file_size - offset))
                    if not chunk:
                        break
                    end = offset + len(chunk) - 1
                    response = self._upload_request(
                        "PUT",
                        resume_url,
                        headers={
                            "Content-Type": metadata["mimeType"],
                            "Content-Length": str(len(chunk)),
                            "Content-Range": f"bytes {offset}-{end}/{file_size}",
                        },
                        data=chunk,
                    )
                    if response.status_code in {200, 201}:
                        if on_session_url:
                            on_session_url(None)
                        return self._verify_uploaded_file(response.json(), file_size, checksum)
                    if response.status_code != 308:
                        raise DriveApiError(self._error_message(response), response.status_code)
                    offset = self._next_offset(response.headers.get("Range"))
                    stream.seek(offset)
        except (requests.RequestException, OSError) as error:
            if on_session_url:
                on_session_url(resume_url)
            raise DriveApiError("The Drive upload was interrupted and can be resumed.", 503) from error

        if on_session_url:
            on_session_url(resume_url)
        raise DriveApiError("The Drive upload stopped before all bytes were confirmed.")

    def _upload_request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        data: bytes,
    ) -> requests.Response:
        for attempt in range(2):
            request_headers = dict(headers)
            request_headers["Authorization"] = f"Bearer {self._get_access_token(force_refresh=attempt == 1)}"
            try:
                response = self.session.request(
                    method,
                    url,
                    headers=request_headers,
                    data=data,
                    timeout=(10, 120),
                )
            except requests.RequestException:
                raise
            if response.status_code == 401 and attempt == 0:
                continue
            if response.status_code not in {200, 201, 308} and response.status_code >= 400:
                if response.status_code in {408, 429} or response.status_code >= 500:
                    raise requests.ConnectionError(f"Drive upload returned HTTP {response.status_code}.")
            return response
        return response

    def _query_upload_status(
        self,
        resume_url: str,
        file_size: int,
    ) -> tuple[int, dict[str, Any] | None]:
        try:
            response = self._upload_request(
                "PUT",
                resume_url,
                headers={
                    "Content-Length": "0",
                    "Content-Range": f"bytes */{file_size}",
                },
                data=b"",
            )
        except requests.RequestException:
            raise DriveApiError("Could not check the saved Drive upload session.", 503)
        if response.status_code in {200, 201}:
            return file_size, response.json()
        if response.status_code == 308:
            return self._next_offset(response.headers.get("Range")), None
        if response.status_code in {404, 410}:
            raise DriveApiError("The saved Drive upload session expired; retry to start a new session.", 410)
        if response.status_code >= 400:
            raise DriveApiError(self._error_message(response), response.status_code)
        return 0, None

    @staticmethod
    def _next_offset(range_header: str | None) -> int:
        if not range_header:
            return 0
        try:
            return int(range_header.rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            return 0

    def _verify_uploaded_file(
        self,
        response_file: dict[str, Any],
        expected_size: int,
        expected_checksum: str,
    ) -> dict[str, Any]:
        file_id = response_file.get("id")
        if not file_id:
            raise DriveApiError("Drive did not return an uploaded file ID.")
        metadata = self._request(
            "GET",
            f"{API_ROOT}/files/{file_id}",
            params={"fields": "id,name,size,md5Checksum,appProperties,parents", "supportsAllDrives": "true"},
        ).json()
        if int(metadata.get("size", -1)) != expected_size or metadata.get("md5Checksum") != expected_checksum:
            raise DriveApiError("Drive upload verification did not match the local file.")
        return metadata
