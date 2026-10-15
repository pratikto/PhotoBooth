# PhotoBooth source file
# Unit tests for session planning, retake limits, transaction manifests, and photo composition.

import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from photobooth.catalog import compose_result, get_templates
from photobooth.transaction_store import TransactionStore
from photobooth.workflow import PhotoSession, build_session_plans


class WorkflowTests(unittest.TestCase):
    # Test session planning and the one-retake-per-session business rule.
    def test_quantities_create_independent_ordered_sessions(self):
        # Verify template quantities expand into separate sessions in the same order as the picker.
        templates = get_templates()
        plans = build_session_plans(
            templates,
            {
                "template_a": 2,
                "template_b": 1,
            },
        )

        self.assertEqual(
            [plan.session_id for plan in plans],
            ["session_001", "session_002", "session_003"],
        )
        self.assertEqual(
            [plan.template.template_id for plan in plans],
            ["template_a", "template_a", "template_b"],
        )
        self.assertEqual(plans[0].template_session_count, 2)
        self.assertEqual(plans[1].template_session_number, 2)
        self.assertEqual(plans[2].template_session_count, 1)

    def test_retake_quota_is_one_per_session_and_replaces_selected_photo(self):
        # Verify each template session has its own retake quota and a retake replaces only the
        # selected output photo.
        plans = build_session_plans(get_templates(), {"template_a": 2})
        first = PhotoSession(plans[0])
        second = PhotoSession(plans[1])
        originals = [Path(f"capture_{index}.jpg") for index in range(1, 4)]

        for path in originals:
            first.add_initial_photo(path)
        self.assertFalse(first.can_retake)
        first.select_photo(1)
        self.assertTrue(first.can_retake)
        replacement = Path("retake_01.jpg")
        first.apply_retake(replacement)

        self.assertTrue(first.retake_used)
        self.assertFalse(first.can_retake)
        self.assertEqual(
            first.final_photo_paths,
            [originals[0], replacement, originals[2]],
        )
        first.select_photo(2)
        self.assertEqual(
            first.final_photo_paths,
            [originals[0], replacement, originals[2]],
        )
        self.assertEqual(first.raw_photo_paths, originals + [replacement])

        for path in originals:
            second.add_initial_photo(path)
        second.select_photo(0)
        self.assertTrue(second.can_retake)


class TransactionStoreTests(unittest.TestCase):
    # Test durable transaction IDs, manifest records, and digital-photo composition using temporary
    # directories.
    def setUp(self):
        # Create an isolated temporary photo root and a transaction store for each test.
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.photos_root = root / "photos"
        self.state_path = root / "data" / "booth_state.json"
        self.store = TransactionStore(self.photos_root, self.state_path, "PB001")
        self.plans = build_session_plans(get_templates(), {"template_a": 1})

    def tearDown(self):
        # Remove the temporary files created by this test case.
        self.temp_dir.cleanup()

    def test_booth_id_rejects_path_separators(self):
        # Ensure booth IDs cannot inject path separators into local transaction folder names.
        with self.assertRaises(ValueError):
            TransactionStore(self.photos_root, self.state_path, "../PB001")

    def test_transaction_counter_persists_and_does_not_reuse_ids(self):
        # Verify the transaction sequence persists across store instances and never returns an ID
        # twice.
        first = self.store.start_transaction(self.plans)
        restarted_store = TransactionStore(
            self.photos_root,
            self.state_path,
            "PB001",
        )
        second = restarted_store.start_transaction(self.plans)

        self.assertEqual(first.transaction_id, "PB001_00000001")
        self.assertEqual(second.transaction_id, "PB001_00000002")
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["next_sequence"], 3)

    def test_preallocated_drive_ids_advance_the_local_counter(self):
        # Ensure a Drive-preallocated transaction ID advances the local counter beyond that number.
        self.store.advance_counter_past("PB001_00000025")
        self.assertEqual(self.store.reserve_transaction_id(), "PB001_00000026")

    def test_manifest_tracks_raw_retake_and_composed_output(self):
        # Check the manifest preserves original captures, the selected retake, and the final photo
        # output separately.
        transaction = self.store.start_transaction(self.plans)
        plan = self.plans[0]
        session_folder = transaction.folder_path / "raw" / plan.session_id
        session_folder.mkdir(parents=True)
        initial_paths = []
        for index in range(1, 4):
            path = self.store.save_raw_photo(
                transaction,
                plan,
                Image.new("RGB", (40, 30), (index * 40, 20, 20)),
                f"capture_{index:02d}.jpg",
                "capture",
            )
            initial_paths.append(path)

        retake_path = self.store.save_raw_photo(
            transaction,
            plan,
            Image.new("RGB", (40, 30), (0, 120, 160)),
            "retake_01.jpg",
            "retake",
        )
        self.store.record_retake(transaction, plan.session_id, initial_paths[1])

        output_path = transaction.folder_path / "output" / plan.session_id / "result.png"
        output_path.parent.mkdir(parents=True)
        Image.new("RGB", (60, 90), "white").save(output_path)
        self.store.record_output(
            transaction,
            plan.session_id,
            [initial_paths[0], retake_path, initial_paths[2]],
            output_path,
        )
        self.store.complete_transaction(transaction)

        saved = json.loads(transaction.manifest_path.read_text(encoding="utf-8"))
        record = saved["sessions"][0]
        self.assertEqual(saved["status"], "COMPLETED")
        self.assertEqual(len(record["raw_photos"]), 4)
        self.assertTrue(record["retake_used"])
        self.assertEqual(record["selected_photo"], "raw/session_001/capture_02.jpg")
        self.assertEqual(len(record["final_photos"]), 3)
        self.assertEqual(record["final_photos"][1], "raw/session_001/retake_01.jpg")
        self.assertEqual(record["output_path"], "output/session_001/result.png")

    def test_composition_writes_a_three_photo_digital_strip(self):
        # Build a sample result image and verify its output file and dimensions are saved.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            photo_paths = []
            for index in range(3):
                path = root / f"photo_{index + 1}.jpg"
                Image.new("RGB", (160, 100), (20, 80 + index * 30, 150)).save(path)
                photo_paths.append(path)

            output_path = compose_result(
                photo_paths,
                get_templates()[0],
                root / "output" / "strip.png",
                "PB001_00000001",
                "session_001",
            )

            self.assertTrue(output_path.is_file())
            with Image.open(output_path) as output:
                self.assertEqual(output.size, (1800, 1000))

    def test_composition_rejects_an_incomplete_session(self):
        # Ensure the image composer refuses to produce a result until all three photos are available.
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                compose_result(
                    [Path("one.jpg"), Path("two.jpg")],
                    get_templates()[0],
                    Path(directory) / "strip.png",
                    "PB001_00000001",
                    "session_001",
                )


if __name__ == "__main__":
    unittest.main()


class EmbeddedFolderQRTests(unittest.TestCase):
    """Each saved template must carry a decodable folder QR outside photo areas."""

    def test_all_templates_embed_the_same_folder_destination(self):
        import cv2
        import numpy as np
        url = 'https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz123456'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            photo = root / 'raw.png'
            Image.new('RGB', (640, 480), '#aabbbc').save(photo)
            for template in get_templates():
                with self.subTest(template=template.template_id):
                    path = compose_result([photo] * 3, template,
                                          root / f'{template.template_id}.png',
                                          'PB001_00000001', 'session_001', folder_url=url)
                    result = cv2.imread(str(path))
                    self.assertEqual(result.shape[:2], (1000, 1800))
                    decoded, points, _ = cv2.QRCodeDetector().detectAndDecode(result)
                    self.assertEqual(decoded, url)
                    self.assertGreater(float(points[:, :, 1].min()), 735)
