"""FEAT-021: physical print-outlet animation and single-receipt regressions.

Pure motion tests work without Kivy. Conditional Kivy tests cover renderer
integration when run on the owner's Windows hardware.
"""
import ast
import importlib.util
import tempfile
import unittest
from pathlib import Path

from photobooth.meong_fly_print_fx import InstantPhotoEmitter

SOURCE = Path(__file__).resolve().parents[1] / "photobooth" / "meong_fly_gui.py"


class InstantPhotoEmitterTests(unittest.TestCase):
    def test_no_paper_before_first_camera_print(self):
        emitter = InstantPhotoEmitter()
        emitter.update(.2, (180, 210), bottom=420)
        self.assertEqual(emitter.poses(), ())

    def test_attached_paper_feeds_in_place_and_follows_meong(self):
        emitter = InstantPhotoEmitter()
        for _ in range(8):
            emitter.update(.1, (155, 210), bottom=420)
        self.assertEqual(len(emitter.poses()), 1)
        first = emitter.poses()[0]
        self.assertTrue(first.attached)
        self.assertAlmostEqual(first.x + first.width / 2, 155)
        self.assertAlmostEqual(first.y, 210)
        self.assertGreater(first.reveal, 0)
        self.assertLess(first.reveal, 1)

        emitter.update(.1, (200, 240), bottom=420)
        moved = emitter.poses()[0]
        self.assertTrue(moved.attached)
        self.assertAlmostEqual(moved.x + moved.width/2, 200)
        self.assertAlmostEqual(moved.y, 240)

    def test_detachment_freezes_camera_origin_then_gravity_drops_paper(self):
        emitter = InstantPhotoEmitter()
        for _ in range(8):
            emitter.update(.1, (160, 180), bottom=480)
        for _ in range(5):
            emitter.update(.1, (190, 200), bottom=480)
        released = emitter.poses()[0]
        self.assertFalse(released.attached)
        self.assertGreater(released.y, 199)

        for _ in range(6):
            emitter.update(.1, (38, 90), bottom=480)
        falling = emitter.poses()[0]
        self.assertFalse(falling.attached)
        self.assertGreater(falling.y, released.y)
        self.assertLess(abs(falling.x - released.x), 6)
        self.assertGreater(falling.x, 160)  # camera is now far away

    def test_pause_freezes_paper_and_emission_clock(self):
        emitter = InstantPhotoEmitter()
        emitter.update(.8, (160, 230), bottom=440)
        before = (emitter.elapsed, emitter.poses())
        for _ in range(5):
            emitter.update(.1, (300, 90), bottom=440, paused=True)
        self.assertEqual((emitter.elapsed, emitter.poses()), before)

    def test_max_two_visible_without_random_screen_scattering(self):
        emitter = InstantPhotoEmitter()
        for _ in range(100):
            emitter.update(.08, (180, 160), bottom=680)
            poses = emitter.poses()
            self.assertLessEqual(len(poses), 2)
            for pose in poses:
                self.assertLess(abs(pose.x + pose.width / 2 - 180), 6)
                self.assertLess(pose.y + pose.height, 680)

    def test_do_not_emit_when_camera_slot_has_no_room(self):
        emitter = InstantPhotoEmitter()
        for _ in range(25):
            emitter.update(.08, (180, 398), bottom=420)
        self.assertEqual(emitter.poses(), ())

    def test_reset_removes_previous_scene_photographs(self):
        emitter = InstantPhotoEmitter()
        for _ in range(9):
            emitter.update(.1, (170, 210), bottom=450)
        self.assertTrue(emitter.poses())
        emitter.reset()
        self.assertEqual(emitter.poses(), ())
        self.assertEqual(emitter.elapsed, 0)
        self.assertEqual(emitter.next_print_at, emitter.INITIAL_DELAY)

    def test_negative_and_large_dt_are_clamped(self):
        emitter = InstantPhotoEmitter()
        emitter.update(-5, (180, 210), bottom=500)
        self.assertEqual(emitter.elapsed, 0)
        emitter.update(20, (180, 210), bottom=500)
        self.assertAlmostEqual(emitter.elapsed, .12)


class RenderingSourceContractTests(unittest.TestCase):
    def test_removed_old_scattered_particle_method(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        stage = next(node for node in tree.body
                     if isinstance(node, ast.ClassDef)
                     and node.name == "MeongFlyStage")
        methods = {node.name for node in stage.body
                   if isinstance(node, ast.FunctionDef)}
        self.assertNotIn("_draw_falling_photos", methods)
        self.assertIn("_paint_print_sheets", methods)
        self.assertIn("_printer_context", methods)
        self.assertIn("_advance_printer", methods)

    def test_camera_frames_do_not_bake_their_own_prints(self):
        import inspect
        from photobooth.meong_fly_visual_v3 import synth_print_frames
        source = inspect.getsource(synth_print_frames)
        self.assertNotIn("printed_photo_tile", source)
        self.assertNotIn("falling_photo_positions", source)


@unittest.skipUnless(importlib.util.find_spec("kivy"), "Kivy unavailable")
class KivyCameraPrintTests(unittest.TestCase):
    def setUp(self):
        from photobooth.meong_fly_flow import MeongFlyFlow
        from photobooth.meong_fly_receipts import DemoReceiptLedger
        from photobooth.meong_fly_gui import MeongFlyStage

        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        ledger = DemoReceiptLedger(Path(self.tmp.name) / "ledger.sqlite3")
        self.flow = MeongFlyFlow(ledger)
        self.stage = MeongFlyStage(self.flow, size=(450, 900),
                                   size_hint=(None, None))
        self.addCleanup(self.stage.dispose)

    def test_start_emits_at_fitted_camera_body(self):
        for _ in range(8):
            self.stage.update(.1)
        slot, _ = self.stage._printer_context("start")
        pose = self.stage._printer.poses()[0]
        self.assertAlmostEqual(pose.x+pose.width/2, slot[0])
        self.assertAlmostEqual(pose.y, slot[1])

    def test_pause_freezes_printer_and_scan_resets_it(self):
        self.flow.open_scan()
        self.stage.update(.02)
        self.assertEqual(self.stage._printer_screen, None)
        self.assertTrue(self.flow.claim_and_start("DEMO-PRINT-PAUSE"))
        for _ in range(8):
            self.stage.update(.1)
        self.assertEqual(self.stage._printer_screen, "game")
        self.assertTrue(self.flow.toggle_pause())
        before = (self.stage._printer.elapsed,
                  self.stage._printer.poses())
        self.stage.update(.1)
        self.assertEqual(before, (self.stage._printer.elapsed,
                                  self.stage._printer.poses()))
        self.assertFalse(self.flow.can_play)


if __name__ == "__main__":
    unittest.main()
