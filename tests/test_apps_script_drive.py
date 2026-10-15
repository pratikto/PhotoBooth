# PhotoBooth source file
# Offline tests for Apps Script client configuration, request format, and error handling.

import base64
import hashlib
from pathlib import Path
import tempfile
import os
import sys
import types
import unittest
from unittest.mock import patch

from photobooth.drive_storage import AppsScriptDriveClient, DriveApiError


class FakeResponse:
    # Provide the small part of requests.Response used by the client, without making a real network
    # request.
    status_code = 200

    def __init__(self, payload):
        # Store a test JSON payload that json() will return.
        self.payload = payload

    def json(self):
        # Return the saved payload in the same way as the requests library response.
        return self.payload


class FakeSession:
    # Replace HTTP networking with a responder function so tests can inspect the exact Apps Script
    # request body.
    def __init__(self, responder):
        # Keep the callback that will produce the fake response for each POST.
        self.responder = responder
        self.calls = []

    def post(self, url, **kwargs):
        # Forward the URL and request keyword arguments to the test responder.
        self.calls.append((url, kwargs))
        return FakeResponse(self.responder(kwargs["json"]))


class AppsScriptDriveClientTests(unittest.TestCase):
    # Verify configuration loading, request payloads, upload checksums, and retry behavior without
    # contacting Google.
    def test_existing_ignored_local_settings_are_read(self):
        # Confirm the client reads the pre-existing ignored local_settings.py names instead of
        # requiring new OAuth credentials.
        local_settings = types.ModuleType("photobooth.local_settings")
        local_settings.WEB_APP_URL = "https://script.google.com/macros/s/existing/exec"
        local_settings.UPLOAD_TOKEN = "existing-token"
        with patch.dict(os.environ, {
            "PHOTOBOOTH_WEB_APP_URL": "",
            "PHOTOBOOTH_UPLOAD_TOKEN": "",
        }), patch.dict(sys.modules, {"photobooth.local_settings": local_settings}):
            client = AppsScriptDriveClient.from_configuration()
        self.assertIsNotNone(client)
        self.assertEqual(client.web_app_url, local_settings.WEB_APP_URL)
        self.assertEqual(client.upload_token, local_settings.UPLOAD_TOKEN)

    def test_existing_web_app_config_supports_pool_assignment_and_idempotent_upload_api(self):
        # Exercise pool preparation, slot assignment, and file upload against a fake Web App,
        # including token, Base64, size, and MD5 fields.
        payloads = []
        photo_bytes = b"photo data"
        checksum = hashlib.md5(photo_bytes).hexdigest()

        def respond(body):
            # Return realistic fake JSON for each Apps Script action and fail the test on an
            # unexpected request.
            payloads.append(body)
            if body["action"] == "ensure_folder_pool":
                return {
                    "ok": True,
                    "slots": [{
                        "folder_id": "folder-1",
                        "folder_url": "https://drive.google.com/drive/folders/folder-1",
                        "slot_key": "PB001_00000001",
                        "status": "READY",
                        "folder_name": "PB001_00000001",
                        "transaction_id": "PB001_00000001",
                        "verified": True,
                    }],
                }
            if body["action"] == "upload_file":
                return {
                    "ok": True,
                    "file": {
                        "id": "file-1",
                        "size_bytes": len(photo_bytes),
                        "md5_checksum": checksum,
                    },
                }
            return {"ok": True}

        session = FakeSession(respond)
        client = AppsScriptDriveClient(
            "https://script.google.com/macros/s/test/exec",
            "private-test-token",
            session=session,
        )

        slots = client.ensure_folder_pool("PB001", 25)
        self.assertEqual(slots[0].transaction_id, "PB001_00000001")
        client.assign_slot("folder-1", "PB001_00000001", "PB001", "PB001_00000001")

        with tempfile.TemporaryDirectory() as directory:
            photo = Path(directory) / "capture_01.jpg"
            photo.write_bytes(photo_bytes)
            uploaded = client.upload_file(
                "folder-1",
                "PB001_00000001",
                "raw/session_001/capture_01.jpg",
                photo,
            )

        self.assertEqual(uploaded["id"], "file-1")
        self.assertEqual(uploaded["md5Checksum"], checksum)
        self.assertEqual(payloads[0]["token"], "private-test-token")
        self.assertEqual(payloads[0]["target_ready"], 25)
        self.assertEqual(base64.b64decode(payloads[-1]["image_base64"]), photo_bytes)
        self.assertEqual(payloads[-1]["relative_path"], "raw/session_001/capture_01.jpg")

    def test_web_app_errors_preserve_retry_classification(self):
        # Check that temporary Web App failures remain retryable while permanent client errors can be
        # surfaced for staff attention.
        client = AppsScriptDriveClient(
            "https://script.google.com/macros/s/test/exec",
            "token",
            session=FakeSession(lambda _body: {
                "ok": False,
                "code": 503,
                "error": "Temporarily unavailable.",
            }),
        )
        with self.assertRaises(DriveApiError) as caught:
            client.ensure_folder_pool("PB001", 25)
        self.assertTrue(caught.exception.transient)


if __name__ == "__main__":
    unittest.main()
