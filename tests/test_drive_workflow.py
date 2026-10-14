import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from photobooth.catalog import get_templates
from photobooth.drive_pool import DriveSlotPool
from photobooth.drive_storage import (
    API_ROOT,
    UPLOAD_ROOT,
    DriveApiError,
    GoogleDriveClient,
    RemoteDriveSlot,
)
from photobooth.drive_sync import sync_manifest
from photobooth.transaction_store import TransactionStore
from photobooth.workflow import build_session_plans


class DriveSlotPoolTests(unittest.TestCase):
    def test_cached_ready_slot_keeps_its_preassigned_name_and_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            photos_root = root / "photos"
            state_path = root / "data" / "drive_pool.json"
            pool = DriveSlotPool(photos_root, state_path, "PB001", target_ready=1)

            class FakeDrive:
                def ensure_folder_pool(self, booth_id, target_ready):
                    return [
                        RemoteDriveSlot(
                            folder_id="drive-folder-1",
                            folder_url="https://drive.google.com/drive/folders/drive-folder-1",
                            slot_key="slot-1",
                            status="READY",
                            folder_name="PB001_00000001",
                            transaction_id="PB001_00000001",
                            verified=True,
                        )
                    ]

            pool.refresh(FakeDrive())
            self.assertEqual(pool.ready_count, 1)
            slot = pool.claim()
            self.assertEqual(slot.status, "ASSIGNED")
            self.assertEqual(Path(slot.staging_path), photos_root / "PB001_00000001")
            self.assertTrue(Path(slot.staging_path).is_dir())
            self.assertEqual(pool.ready_count, 0)

            restarted = DriveSlotPool(photos_root, state_path, "PB001", target_ready=1)
            self.assertEqual(restarted.ready_count, 0)
            self.assertEqual(restarted.pending_assignments()[0].folder_id, "drive-folder-1")
            self.assertEqual(restarted.pending_assignments()[0].transaction_id, "PB001_00000001")


class DriveUploadTests(unittest.TestCase):
    def test_resumable_upload_is_verified_and_persists_session_url(self):
        with tempfile.TemporaryDirectory() as directory:
            photo = Path(directory) / "capture.jpg"
            photo.write_bytes(b"photo-bytes")
            checksum = hashlib.md5(photo.read_bytes()).hexdigest()

            class Response:
                def __init__(self, status_code, payload=None, headers=None):
                    self.status_code = status_code
                    self._payload = payload or {}
                    self.headers = headers or {}

                def json(self):
                    return self._payload

            class FakeSession:
                def __init__(self):
                    self.upload_chunks = []

                def post(self, url, **kwargs):
                    return Response(200, {"access_token": "test-token", "expires_in": 3600})

                def request(self, method, url, **kwargs):
                    if method == "GET" and url == f"{API_ROOT}/files":
                        return Response(200, {"files": []})
                    if method == "POST" and url == f"{UPLOAD_ROOT}/files":
                        return Response(200, headers={"Location": "https://upload.example/session/1"})
                    if method == "PUT" and url == "https://upload.example/session/1":
                        content_range = kwargs["headers"].get("Content-Range", "")
                        if content_range.startswith("bytes */"):
                            return Response(308)
                        self.upload_chunks.append(kwargs.get("data"))
                        return Response(201, {"id": "uploaded-file-1"})
                    if method == "GET" and url == f"{API_ROOT}/files/uploaded-file-1":
                        return Response(
                            200,
                            {
                                "id": "uploaded-file-1",
                                "name": "capture.jpg",
                                "size": str(photo.stat().st_size),
                                "md5Checksum": checksum,
                            },
                        )
                    raise AssertionError(f"Unexpected Drive request: {method} {url}")

            session = FakeSession()
            client = GoogleDriveClient(
                "parent-folder",
                "client-id",
                "client-secret",
                "refresh-token",
                session=session,
            )
            saved_urls = []
            uploaded = client.upload_file(
                "drive-folder",
                "PB001_00000001",
                "raw/session_001/capture_01.jpg",
                photo,
                on_session_url=saved_urls.append,
            )

            self.assertEqual(uploaded["id"], "uploaded-file-1")
            self.assertEqual(uploaded["md5Checksum"], checksum)
            self.assertEqual(session.upload_chunks, [b"photo-bytes"])
            self.assertEqual(saved_urls, ["https://upload.example/session/1", None])

    def test_offline_upload_stays_queued_and_keeps_the_local_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            photos_root = root / "photos"
            store = TransactionStore(photos_root, root / "data" / "booth_state.json", "PB001")
            plans = build_session_plans(get_templates(), {"template_a": 1})
            tx_path = photos_root / "PB001_00000001"
            tx_path.mkdir(parents=True)
            transaction = store.start_transaction(
                plans,
                transaction_id="PB001_00000001",
                folder_path=tx_path,
                drive_slot={
                    "folder_id": "drive-folder-1",
                    "folder_url": "https://drive.google.com/drive/folders/drive-folder-1",
                    "slot_key": "slot-1",
                },
            )
            photo = store.save_raw_photo(
                transaction,
                plans[0],
                Image.new("RGB", (20, 20), "blue"),
                "capture_01.jpg",
                "capture",
            )

            class OfflineDrive:
                def upload_file(self, *args, **kwargs):
                    raise DriveApiError("network unavailable", 503)

            sync_manifest(transaction.manifest_path, OfflineDrive())
            saved = json.loads(transaction.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["upload_status"], "UPLOAD_RETRY")
            self.assertEqual(saved["upload_files"]["raw/session_001/capture_01.jpg"]["status"], "UPLOAD_RETRY")
            self.assertTrue(photo.is_file())

    def test_local_manifest_writes_preserve_background_upload_progress(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            store = TransactionStore(root / "photos", root / "data" / "booth_state.json", "PB001")
            plans = build_session_plans(get_templates(), {"template_a": 1})
            folder = root / "photos" / "PB001_00000001"
            folder.mkdir(parents=True)
            transaction = store.start_transaction(
                plans,
                transaction_id="PB001_00000001",
                folder_path=folder,
                drive_slot={
                    "folder_id": "drive-folder-1",
                    "folder_url": "https://drive.google.com/drive/folders/drive-folder-1",
                    "slot_key": "slot-1",
                },
            )
            first = store.save_raw_photo(
                transaction,
                plans[0],
                Image.new("RGB", (10, 10), "red"),
                "capture_01.jpg",
                "capture",
            )
            manifest = json.loads(transaction.manifest_path.read_text(encoding="utf-8"))
            first_record = manifest["upload_files"]["raw/session_001/capture_01.jpg"]
            first_record.update(
                {
                    "status": "VERIFIED",
                    "drive_file_id": "drive-file-1",
                    "md5_checksum": hashlib.md5(first.read_bytes()).hexdigest(),
                }
            )
            transaction.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            store.save_raw_photo(
                transaction,
                plans[0],
                Image.new("RGB", (10, 10), "green"),
                "capture_02.jpg",
                "capture",
            )
            updated = json.loads(transaction.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                updated["upload_files"]["raw/session_001/capture_01.jpg"]["status"],
                "VERIFIED",
            )
            self.assertEqual(
                updated["upload_files"]["raw/session_001/capture_02.jpg"]["status"],
                "PENDING_UPLOAD",
            )


class DriveSyncTests(unittest.TestCase):
    def test_completed_transaction_upload_records_each_verified_drive_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            photos_root = root / "photos"
            store = TransactionStore(photos_root, root / "data" / "booth_state.json", "PB001")
            plans = build_session_plans(get_templates(), {"template_a": 1})
            tx_path = photos_root / "PB001_00000001"
            tx_path.mkdir(parents=True)
            transaction = store.start_transaction(
                plans,
                transaction_id="PB001_00000001",
                folder_path=tx_path,
                drive_slot={
                    "folder_id": "drive-folder-1",
                    "folder_url": "https://drive.google.com/drive/folders/drive-folder-1",
                    "slot_key": "slot-1",
                },
            )
            raw_paths = [
                store.save_raw_photo(
                    transaction,
                    plans[0],
                    Image.new("RGB", (30, 20), (index * 40, 60, 120)),
                    f"capture_{index:02d}.jpg",
                    "capture",
                )
                for index in range(1, 4)
            ]
            output_path = tx_path / "output" / "session_001" / "template_a.png"
            output_path.parent.mkdir(parents=True)
            Image.new("RGB", (40, 40), "white").save(output_path)
            store.record_output(transaction, "session_001", raw_paths, output_path)
            store.complete_transaction(transaction)

            class FakeDrive:
                def __init__(self):
                    self.paths = []

                def upload_file(self, folder_id, transaction_id, relative_path, local_path, **kwargs):
                    self.paths.append(relative_path)
                    if kwargs.get("on_session_url"):
                        kwargs["on_session_url"]("https://upload.example/session")
                        kwargs["on_session_url"](None)
                    data = Path(local_path).read_bytes()
                    return {
                        "id": f"file-{len(self.paths)}",
                        "size": len(data),
                        "md5Checksum": hashlib.md5(data).hexdigest(),
                    }

            client = FakeDrive()
            result = sync_manifest(transaction.manifest_path, client)
            self.assertEqual(result["upload_status"], "UPLOAD_COMPLETE")
            self.assertEqual(len(client.paths), 4)
            self.assertTrue(
                all(record["status"] == "VERIFIED" for record in result["upload_files"].values())
            )
            sync_manifest(transaction.manifest_path, client)
            self.assertEqual(len(client.paths), 4)


if __name__ == "__main__":
    unittest.main()
