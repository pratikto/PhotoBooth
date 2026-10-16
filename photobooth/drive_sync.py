# PhotoBooth source file
# Background worker that prepares Drive slots, acknowledges assignments, and retries queued file uploads.

"""Resumable background sync for assigned Drive folders and local manifests."""

from __future__ import annotations

import json
from pathlib import Path
import threading
from typing import Any

from photobooth.drive_pool import DriveSlotPool
from photobooth.drive_storage import DriveApiError, GoogleDriveClient
from photobooth.manifest_io import manifest_lock, write_json_atomic
from photobooth.retention import local_photos_expired, mark_local_expired, register_drive_retention


def sync_manifest(manifest_path: Path, client: GoogleDriveClient) -> dict[str, Any]:
    """Upload pending files for one transaction and persist verification per file."""
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if local_photos_expired(manifest):
        with manifest_lock(manifest_path):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            mark_local_expired(manifest)
            write_json_atomic(manifest_path, manifest)
        return manifest
    register_drive_retention(manifest_path, client)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    folder_id = manifest.get("drive_folder_id")
    transaction_id = manifest.get("transaction_id")
    upload_files: dict[str, dict[str, Any]] = manifest.get("upload_files", {})
    if not folder_id or not transaction_id or not upload_files:
        return manifest

    for relative_path in list(upload_files):
        if manifest.get('local_photos_expired_at'):
            return manifest
        record = upload_files[relative_path]
        if record.get("status") == "VERIFIED":
            continue
        if record.get("status") == "ACTION_REQUIRED":
            continue

        local_path = (manifest_path.parent / relative_path).resolve()
        try:
            local_path.relative_to(manifest_path.parent.resolve())
        except ValueError:
            record["status"] = "ACTION_REQUIRED"
            record["error"] = "Upload path is outside the transaction folder."
            _persist_upload_progress(manifest_path, manifest)
            continue

        if not local_path.is_file():
            record["status"] = "ACTION_REQUIRED"
            record["error"] = "Local transaction file is missing."
            _persist_upload_progress(manifest_path, manifest)
            continue

        record["status"] = "UPLOADING"
        record.pop("error", None)
        manifest["upload_status"] = "UPLOADING"
        _persist_upload_progress(manifest_path, manifest)
        if upload_files[relative_path] is not record or record.get("status") != "UPLOADING":
            # The merge may discover a newer save or an already verified copy.
            # Do not start a stale upload; the replacement stays queued for the
            # next pass. An upload already in flight is guarded at every later
            # session/progress merge below instead of blocking the GUI thread.
            continue

        def save_session_url(value: str | None) -> None:
            # Persist the current resumable-upload session URL so a later retry can continue the same
            # upload instead of starting over.
            record["upload_session_url"] = value
            _persist_upload_progress(manifest_path, manifest)

        try:
            remote_file = client.upload_file(
                folder_id,
                transaction_id,
                relative_path,
                local_path,
                resume_url=record.get("upload_session_url"),
                on_session_url=save_session_url,
            )
            record.update(
                {
                    "status": "VERIFIED",
                    "drive_file_id": remote_file["id"],
                    "size_bytes": int(remote_file["size"]),
                    "md5_checksum": remote_file["md5Checksum"],
                    "upload_session_url": None,
                    "verified": True,
                }
            )
        except DriveApiError as error:
            record["status"] = "UPLOAD_RETRY" if error.transient else "ACTION_REQUIRED"
            record["error"] = str(error)
        _refresh_upload_status(manifest)
        _persist_upload_progress(manifest_path, manifest)

    _refresh_upload_status(manifest)
    _persist_upload_progress(manifest_path, manifest)
    return manifest


def _refresh_upload_status(manifest: dict[str, Any]) -> None:
    # Derive the transaction-level upload status from the individual file states, so the result screen
    # can show one clear summary.
    records = list(manifest.get("upload_files", {}).values())
    if manifest.get('local_photos_expired_at') and any(record.get('status') != 'VERIFIED' for record in records):
        manifest['upload_status'] = 'LOCAL_EXPIRED'
        return
    if any(record.get("status") == "ACTION_REQUIRED" for record in records):
        manifest["upload_status"] = "ACTION_REQUIRED"
    elif records and all(record.get("status") == "VERIFIED" for record in records):
        manifest["upload_status"] = (
            "UPLOAD_COMPLETE" if manifest.get("status") == "COMPLETED" else "PENDING_UPLOAD"
        )
    elif any(record.get("status") == "UPLOADING" for record in records):
        manifest["upload_status"] = "UPLOADING"
    elif records:
        manifest["upload_status"] = "UPLOAD_RETRY" if any(
            record.get("status") == "UPLOAD_RETRY" for record in records
        ) else "PENDING_UPLOAD"


def _persist_upload_progress(path: Path, working: dict[str, Any]) -> None:
    # Merge worker-updated upload fields into the newest manifest while holding the shared file lock,
    # preventing capture code from overwriting sync progress.
    """Merge progress only into the same saved-file revision under the lock.

    A filename is stable across a save retry, but its bytes need not be. Never
    move an old resume URL, error, or VERIFIED result onto a replacement file.
    Missing revision fields on both sides keep existing manifests compatible.
    """
    path = Path(path)
    with manifest_lock(path):
        latest = json.loads(path.read_text(encoding="utf-8"))
        if latest.get('local_photos_expired_at'):
            # Cleanup wins over late upload callbacks. Never resurrect an old
            # queue or replace its tombstone with an in-flight success/error.
            working.clear()
            working.update(latest)
            return
        working_files: dict[str, dict[str, Any]] = working.setdefault("upload_files", {})
        latest_files: dict[str, dict[str, Any]] = latest.setdefault("upload_files", {})

        for relative_path, persisted_record in latest_files.items():
            working_files.setdefault(relative_path, dict(persisted_record))

        for relative_path, progress_record in working_files.items():
            persisted_record = latest_files.setdefault(relative_path, dict(progress_record))
            if persisted_record.get("content_version") != progress_record.get("content_version"):
                # Replace the working dictionary entry, not the old record
                # object held by upload_file's callback. Its delayed response
                # must continue to mutate only the retired revision. Updating
                # working in place also makes sync_manifest return current
                # queue state rather than a misleading stale success.
                working_files[relative_path] = dict(persisted_record)
            elif persisted_record.get("status") == "VERIFIED" and progress_record.get("status") != "VERIFIED":
                progress_record.update(persisted_record)
            else:
                persisted_record.update(progress_record)

        working["status"] = latest.get("status", working.get("status"))
        _refresh_upload_status(latest)
        working["upload_status"] = latest.get("upload_status")
        write_json_atomic(path, latest)


class DriveSyncWorker:
    """Run Drive pool maintenance and upload retries away from Tk's event loop."""

    def __init__(
        self,
        photos_root: Path,
        client: GoogleDriveClient,
        pool: DriveSlotPool,
        interval_seconds: int = 8,
    ) -> None:
        # Create the background worker state, synchronization lock, stop event, and lightweight
        # trigger used to wake the worker.
        self.photos_root = Path(photos_root)
        self.client = client
        self.pool = pool
        self.interval_seconds = interval_seconds
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._thread = threading.Thread(
            target=self._run,
            name="photobooth-drive-sync",
            daemon=True,
        )

    def start(self) -> None:
        # Start one daemon thread that performs Drive work without freezing Tkinter's customer-facing
        # interface.
        if not self._thread.is_alive():
            self._thread.start()

    def kick(self) -> None:
        # Wake the background worker after a transaction or capture adds work to the upload queue.
        self._wake.set()

    def stop(self) -> None:
        # Signal the worker to stop and wait briefly for the current network operation to finish.
        self._stop.set()
        self._wake.set()

    def _run(self) -> None:
        # Run pool recovery, assignment, refresh, and queued uploads in a loop, waiting between passes
        # instead of busy-spinning.
        while not self._stop.is_set():
            self.pool.recover_incomplete_claims()
            self._process_pending_assignments()
            self._process_pending_uploads()
            if self.pool.ready_count < self.pool.target_ready:
                try:
                    self.pool.refresh(self.client)
                except (DriveApiError, OSError, ValueError) as error:
                    self.pool.record_refresh_error(error)
            self._wake.wait(self.interval_seconds)
            self._wake.clear()

    def _process_pending_assignments(self) -> None:
        # Send locally claimed slots to Drive and clear each pending flag only after the backend
        # confirms the assignment.
        for slot in self.pool.pending_assignments():
            if not slot.transaction_id:
                continue
            try:
                self.client.assign_slot(
                    slot.folder_id,
                    slot.transaction_id,
                    self.pool.booth_id,
                    slot.slot_key,
                )
                self.pool.mark_assigned(slot.folder_id)
            except DriveApiError as error:
                self.pool.record_refresh_error(error)

    def _process_pending_uploads(self) -> None:
        # Find manifests with queued files and upload them one transaction at a time while retaining
        # local copies for retry.
        try:
            manifests = list(self.photos_root.glob("*/manifest.json"))
        except OSError:
            return
        for manifest_path in manifests:
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                upload_status = manifest.get("upload_status")
                if upload_status in {"UPLOAD_COMPLETE", "LOCAL_ONLY", "ACTION_REQUIRED", "LOCAL_EXPIRED"}:
                    continue
                if manifest.get("drive_folder_id"):
                    sync_manifest(manifest_path, self.client)
            except (DriveApiError, OSError, ValueError, TypeError, json.JSONDecodeError):
                continue
