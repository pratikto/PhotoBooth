# PhotoBooth source file
# Direct Google Drive and Apps Script Web App clients, including folder validation, upload, and retry support.

"""Google Drive API client for folder pools and resumable photo uploads.

The booth authenticates with a refresh token supplied through environment
variables. No credential file or access token is written to the repository.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import time
from typing import Any, Callable
from urllib.parse import urlencode

import requests

from photobooth.retention import read_drive_retention, retention_metadata, utc_datetime


API_ROOT = "https://www.googleapis.com/drive/v3"
UPLOAD_ROOT = "https://www.googleapis.com/upload/drive/v3"
TOKEN_URL = "https://oauth2.googleapis.com/token"
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
CHUNK_SIZE = 256 * 1024 * 4


class DriveApiError(RuntimeError):
    """A Drive operation failed, with retryability for the local upload queue."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        # Store a readable Drive error and its HTTP status. The status is used to distinguish
        # temporary failures from errors that need staff attention.
        super().__init__(message)
        self.status_code = status_code
        self.transient = status_code in {408, 429} or (
            status_code is not None and status_code >= 500
        )


@dataclass(frozen=True)
class RemoteDriveSlot:
    # Describe a folder slot as returned by the remote Drive backend, before it is merged into the
    # local pool cache.
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
        # Keep the OAuth credentials, parent-folder ID, and HTTP session used for direct Google Drive
        # API calls.
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
        # Refresh and cache the short-lived Google access token using the saved refresh token,
        # refreshing again when forced or expired.
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
        # Send an authenticated Drive API request and convert HTTP or network failures into
        # DriveApiError so the sync worker can retry when appropriate.
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
        # Extract Google's human-readable error text from a response, falling back to the raw body
        # when it is not JSON.
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
        # Read matching Drive files and follow pagination tokens until the full result set has been
        # collected.
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
        # Use Drive's browser link when available, otherwise construct the standard folder URL from
        # its ID.
        url = folder.get("webViewLink")
        if not isinstance(url, str) or not url.strip():
            url = f"https://drive.google.com/drive/folders/{folder['id']}"
        resource_key = folder.get("resourceKey")
        if resource_key and "resourcekey=" not in url:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}resourcekey={resource_key}"
        return url

    def _permission_ready(self, folder_id: str) -> bool:
        # Verify that a folder has an anyone-with-the-link viewer permission before treating it as a
        # usable QR destination.
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
        # Check that a candidate slot has no child files or folders, because a ready slot must not
        # contain another transaction's data.
        children = self._list_files(
            f"'{folder_id}' in parents and trashed = false",
            "id",
        )
        return not children

    def _validate_slot(self, folder: dict[str, Any]) -> tuple[bool, str | None, str]:
        # Verify the folder type, link permission, and emptiness. The Drive search that called this
        # method already limits candidates to the configured parent folder.
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
        # Continue after the largest ID already present so names are incrementing and never reused.
        next_sequence = 1
        for folder in folders:
            props = folder.get("appProperties", {})
            status = props.get("photoboothStatus", "ACTION_REQUIRED")
            transaction_id = props.get("photoboothTransactionId")
            if not transaction_id:
                match = re.fullmatch(rf"{re.escape(booth_id)}_(\d{{8}})", folder.get("name", ""))
                transaction_id = f"{booth_id}_{match.group(1)}" if match else None
            if transaction_id and transaction_id.startswith(f"{booth_id}_"):
                try:
                    next_sequence = max(next_sequence, int(transaction_id.rsplit("_", 1)[1]) + 1)
                except ValueError:
                    pass
            if status == "READY":
                verified, issue, url = self._validate_slot(folder)
                if not transaction_id:
                    verified = False
                    issue = "Drive slot has no preassigned transaction ID."
                if verified:
                    ready_count += 1
                slots[folder["id"]] = RemoteDriveSlot(
                    folder_id=folder["id"],
                    folder_url=url,
                    slot_key=props.get("photoboothSlotKey", folder["id"]),
                    status="READY" if verified else "ACTION_REQUIRED",
                    folder_name=folder.get("name", ""),
                    transaction_id=transaction_id,
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
                    transaction_id=transaction_id,
                    verified=False,
                )

        while ready_count < target_ready:
            transaction_id = f"{booth_id}_{next_sequence:08d}"
            next_sequence += 1
            slot_key = transaction_id
            # Store the final ID as Drive metadata at creation time; there is no rename step later.
            metadata = {
                "name": transaction_id,
                "mimeType": FOLDER_MIME_TYPE,
                "parents": [self.parent_folder_id],
                "appProperties": {
                    "photoboothSlot": "true",
                    "photoboothSlotKey": slot_key,
                    "photoboothBoothId": booth_id,
                    "photoboothStatus": "READY",
                    "photoboothTransactionId": transaction_id,
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
                transaction_id=transaction_id,
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
        # Kept as a compatibility shim for existing callers. Folder slots are
        # created with their final transaction IDs, so assignment never renames.
        # Keep compatibility with older callers while delegating to assignment; transaction folder
        # names are final when created and are never renamed.
        self.assign_slot(folder_id, transaction_id, booth_id, slot_key)

    def assign_slot(
        self,
        folder_id: str,
        transaction_id: str,
        booth_id: str,
        slot_key: str,
    ) -> None:
        # Mark a pre-created slot as assigned to the transaction using Drive metadata; the visible
        # folder name stays unchanged.
        self._request(
            "PATCH",
            f"{API_ROOT}/files/{folder_id}",
            params={"fields": "id,appProperties", "supportsAllDrives": "true"},
            json_body={
                "appProperties": {
                    "photoboothSlot": "true",
                    "photoboothSlotKey": slot_key,
                    "photoboothBoothId": booth_id,
                    "photoboothStatus": "ASSIGNED",
                    "photoboothTransactionId": transaction_id,
                },
            },
        )

    def register_retention(self, folder_id, transaction_id, started_at):
        """Bind 30-day expiry to the transaction, preserving an earlier deadline."""
        metadata = self._request('GET', f'{API_ROOT}/files/{folder_id}',
                                 params={'fields': 'id,name,mimeType,parents,description,trashed,appProperties',
                                         'supportsAllDrives': 'true'}).json()
        if (metadata.get('name') != transaction_id or metadata.get('mimeType') != FOLDER_MIME_TYPE
                or self.parent_folder_id not in metadata.get('parents', []) or metadata.get('trashed')):
            raise DriveApiError('Retention folder is outside this booth transaction.', 409)
        policy = retention_metadata(transaction_id, started_at)
        existing = read_drive_retention(metadata.get('description'), transaction_id)
        if metadata.get('description') and existing is None:
            raise DriveApiError('Unrecognized folder description; retention was not overwritten.', 409)
        updates = {}
        if existing and utc_datetime(existing['started_at']) <= utc_datetime(started_at):
            policy = existing
        else:
            updates['description'] = json.dumps(policy)
        if metadata.get('appProperties', {}).get('photoboothStatus') == 'READY':
            # Registration proves that the booth has claimed this slot even if
            # its original assignment acknowledgement is still being retried.
            updates['appProperties'] = dict(metadata['appProperties'], photoboothStatus='ASSIGNED')
        if updates:
            self._request('PATCH', f'{API_ROOT}/files/{folder_id}',
                          params={'fields': 'id', 'supportsAllDrives': 'true'},
                          json_body=updates)
        return policy

    def cleanup_expired(self):
        """Delete only marked transaction folders under this configured parent.

        This is the direct-OAuth fallback's online sweep. The Apps Script backend
        has its own clock trigger so it also works while a booth is switched off.
        Drive files.delete permanently removes a folder and its owned descendants;
        moving it to Trash would keep the image bytes beyond the requested period.
        """
        folders = self._list_files(
            f"'{self._quote_query(self.parent_folder_id)}' in parents and trashed = false "
            f"and mimeType = '{FOLDER_MIME_TYPE}'",
            'id,name,mimeType,parents,description,appProperties')
        deleted = []
        for folder in folders:
            if (self.parent_folder_id not in folder.get('parents', [])
                    or folder.get('mimeType') != FOLDER_MIME_TYPE
                    or folder.get('appProperties', {}).get('photoboothStatus') == 'READY'):
                continue
            policy = read_drive_retention(folder.get('description'), folder.get('name'))
            if policy and datetime.now(timezone.utc) >= utc_datetime(policy['expires_at']):
                self._request('DELETE', f"{API_ROOT}/files/{folder['id']}",
                              params={'supportsAllDrives': 'true'})
                deleted.append(folder['id'])
        return {'deleted': deleted}

    @staticmethod
    def _quote_query(value: str) -> str:
        # Escape characters that have special meaning in Drive's query language before inserting a
        # value into a search expression.
        return value.replace("\\", "\\\\").replace("'", "\\'")

    def _find_existing_upload(
        self,
        folder_id: str,
        relative_path: str,
    ) -> dict[str, Any] | None:
        # Look up a file by transaction-relative path metadata so a retry can verify or resume the
        # existing file instead of creating a duplicate.
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
        # The path and checksum make retries safe: the server can recognize the exact same file.
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
                # Check which bytes Drive already received before sending the next chunk.
                offset, finished = self._query_upload_status(resume_url, file_size)
                if finished is not None:
                    if on_session_url:
                        on_session_url(None)
                    return self._verify_uploaded_file(finished, file_size, checksum)
            except DriveApiError as error:
                if error.status_code != 410:
                    raise
                # HTTP 410 means Drive expired the old upload session; create a fresh one below.
                resume_url = None
                if on_session_url:
                    on_session_url(None)

        if resume_url is None:
            # Start a resumable session before transferring binary data in chunks.
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
                    # Drive returns 308 while more bytes are needed, including the accepted range.
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
        # Send one chunk of a resumable upload and return Google's response for the upload-state
        # machine to interpret.
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
        # Ask the resumable-upload session how many bytes it has accepted, allowing a retry to
        # continue at the correct offset.
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
        # Convert Google's Range header into the index of the next byte to send; an empty or missing
        # range means start at byte zero.
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
        # Fetch the completed Drive file metadata and compare its size and MD5 checksum with the local
        # source before marking it verified.
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


class AppsScriptDriveClient:
    """Drive client that uses the booth's existing Google Apps Script Web App.

    The Web App URL and upload token remain in the ignored local_settings.py
    file, or can be supplied through environment variables. The Apps Script
    project must expose the transaction-folder actions in apps_script/Code.gs.
    """

    def __init__(
        self,
        web_app_url: str,
        upload_token: str,
        *,
        session: requests.Session | None = None,
    ) -> None:
        # Store the existing Web App URL and upload token, plus an injectable HTTP session for
        # production calls or isolated tests.
        self.web_app_url = web_app_url.strip()
        self.upload_token = upload_token.strip()
        if not self.web_app_url.startswith("https://") or not self.web_app_url.endswith("/exec"):
            raise ValueError("Apps Script Web App URL must be an HTTPS /exec URL.")
        if not self.upload_token or "PASTE_" in self.upload_token:
            raise ValueError("Apps Script upload token is not configured.")
        self.session = session or requests.Session()

    @classmethod
    def from_configuration(cls) -> AppsScriptDriveClient | None:
        """Read the existing local Apps Script settings without exposing them."""
        web_app_url = os.environ.get("PHOTOBOOTH_WEB_APP_URL", "").strip()
        upload_token = os.environ.get("PHOTOBOOTH_UPLOAD_TOKEN", "").strip()
        if not web_app_url or not upload_token:
            try:
                from photobooth.local_settings import UPLOAD_TOKEN, WEB_APP_URL

                web_app_url = web_app_url or str(WEB_APP_URL).strip()
                upload_token = upload_token or str(UPLOAD_TOKEN).strip()
            except (ImportError, AttributeError):
                pass
        if not web_app_url or not upload_token or "PASTE_" in web_app_url or "PASTE_" in upload_token:
            return None
        return cls(web_app_url, upload_token)

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        # Send one JSON action to the Apps Script /exec endpoint, validate its JSON response, and
        # classify errors for safe retries.
        request_body = {"token": self.upload_token, **payload}
        try:
            response = self.session.post(
                self.web_app_url,
                json=request_body,
                timeout=(10, 120),
            )
            if response.status_code >= 400:
                raise DriveApiError(
                    f"Apps Script Web App returned HTTP {response.status_code}.",
                    response.status_code,
                )
            result = response.json()
        except DriveApiError:
            raise
        except requests.Timeout as error:
            raise DriveApiError("Apps Script request timed out; it is safe to retry.", 503) from error
        except requests.RequestException as error:
            raise DriveApiError("Could not reach the Apps Script Web App.", 503) from error
        except ValueError as error:
            raise DriveApiError("Apps Script returned an invalid JSON response.", 502) from error

        if not isinstance(result, dict) or result.get("ok") is not True:
            code = result.get("code") if isinstance(result, dict) else None
            message = result.get("error", "Apps Script request failed.") if isinstance(result, dict) else "Unexpected Apps Script response."
            status_code = int(code) if isinstance(code, int) else 400
            raise DriveApiError(str(message), status_code)
        return result

    def ensure_folder_pool(
        self,
        booth_id: str,
        target_ready: int = 25,
    ) -> list[RemoteDriveSlot]:
        # Ask the Apps Script backend to verify or create the target number of ready folders and
        # convert its response into remote slot records.
        result = self._post(
            {
                "action": "ensure_folder_pool",
                "booth_id": booth_id,
                "target_ready": target_ready,
            }
        )
        # Missing `slots` is a protocol mismatch, not an empty inventory. Treating
        # it as [] used to mark every cached READY folder as ACTION_REQUIRED.
        # Reject before the pool mutates any local records. A common cause is an
        # older /exec deployment that has not been updated to the folder API.
        if not isinstance(result.get("slots"), list):
            raise DriveApiError(
                "Apps Script response is missing the slots list. Deploy the current "
                "apps_script/Code.gs as a new version and verify WEB_APP_URL.",
                502,
            )
        remote_slots: list[RemoteDriveSlot] = []
        for item in result["slots"]:
            if not isinstance(item, dict):
                continue
            remote_slots.append(
                RemoteDriveSlot(
                    folder_id=str(item.get("folder_id", "")),
                    folder_url=str(item.get("folder_url", "")),
                    slot_key=str(item.get("slot_key", "")),
                    status=str(item.get("status", "ACTION_REQUIRED")),
                    folder_name=str(item.get("folder_name", "")),
                    transaction_id=item.get("transaction_id"),
                    verified=bool(item.get("verified", False)),
                    issue=item.get("issue"),
                )
            )
        return remote_slots

    def assign_slot(
        self,
        folder_id: str,
        transaction_id: str,
        booth_id: str,
        slot_key: str,
    ) -> None:
        # Tell Apps Script that a preassigned folder is being used by this transaction; no Drive
        # folder rename is requested.
        self._post(
            {
                "action": "assign_slot",
                "folder_id": folder_id,
                "transaction_id": transaction_id,
                "booth_id": booth_id,
                "slot_key": slot_key,
            }
        )

    def rename_assigned_folder(
        self,
        folder_id: str,
        transaction_id: str,
        booth_id: str,
        slot_key: str,
    ) -> None:
        """Compatibility alias; assignment only changes slot state, never its name."""
        self.assign_slot(folder_id, transaction_id, booth_id, slot_key)

    def register_retention(self, folder_id, transaction_id, started_at):
        """Send the original transaction date; backend retries cannot renew it."""
        result = self._post({'action': 'register_retention', 'folder_id': folder_id,
                             'transaction_id': transaction_id, 'started_at': started_at})
        if result.get('retention_enabled') is not True:
            raise DriveApiError('Run setupPhotoRetention in Apps Script and redeploy the Web App.', 409)
        return result.get('retention')

    def cleanup_expired(self):
        """Supplement the backend's independently scheduled hourly cleanup."""
        result = self._post({'action': 'cleanup_retention'})
        if result.get('enabled') is not True:
            raise DriveApiError('Drive retention is not enabled; run setupPhotoRetention in Apps Script.', 409)
        return result

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
        # Send a transaction-relative file to Apps Script as Base64, then verify the returned size and
        # checksum against the local file.
        del resume_url
        local_path = Path(local_path)
        if not local_path.is_file():
            raise DriveApiError(f"Upload file is missing: {local_path}")
        data = local_path.read_bytes()
        checksum = hashlib.md5(data).hexdigest()
        mime_type = mimetypes.guess_type(local_path.name)[0] or "application/octet-stream"
        if on_session_url is not None:
            on_session_url(None)
        result = self._post(
            {
                "action": "upload_file",
                "folder_id": folder_id,
                "transaction_id": transaction_id,
                "relative_path": relative_path,
                "filename": local_path.name,
                "mime_type": mime_type,
                "size_bytes": len(data),
                "md5_checksum": checksum,
                "image_base64": base64.b64encode(data).decode("ascii"),
            }
        )
        remote_file = result.get("file", {})
        if (
            not remote_file.get("id")
            or int(remote_file.get("size_bytes", -1)) != len(data)
            or remote_file.get("md5_checksum") != checksum
        ):
            raise DriveApiError("Apps Script upload verification did not match the local file.")
        return {
            "id": remote_file["id"],
            "size": str(remote_file["size_bytes"]),
            "md5Checksum": remote_file["md5_checksum"],
        }
