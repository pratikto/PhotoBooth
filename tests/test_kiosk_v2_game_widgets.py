"""P4 real-widget guards with a temporary DEMO ledger and no real devices."""

from contextlib import contextmanager
import os
from tempfile import TemporaryDirectory
import threading
import time
import unittest

os.environ.setdefault('PHOTOBOOTH_AUDIO','0')
os.environ.setdefault('PHOTOBOOTH_CAMERA','0')
os.environ.setdefault('PHOTOBOOTH_FACE_TRIGGER','0')
os.environ.setdefault('PHOTOBOOTH_PALM_TRIGGER','0')
os.environ.setdefault('PHOTOBOOTH_AD_VIDEO','0')

try:
    import kivy
except ImportError:
    HAS_KIVY = False
else:
    HAS_KIVY = True
    from kivy.base import EventLoop
    from kivy.core.window import Window
    from photobooth.kiosk_v2.app import PortraitKioskV2App
    from photobooth.kiosk_v2.demo_game import DemoClaimError, DemoGameStore, GameJobs
    from photobooth.kiosk_v2.flow import ADVERT, GAME_PLAY, GAME_RECEIPT, GAME_RESULT, TUTORIAL, TEMPLATES
    from photobooth.kiosk_v2.game_engine import TARGET_SCORE
    from photobooth.kiosk_v2.theme import ArcadeButton


@unittest.skipUnless(HAS_KIVY, 'Native widget environment required')
class GameWidgetTests(unittest.TestCase):
    @contextmanager
    def booth(self, factory=None):
        with TemporaryDirectory() as root:
            store = DemoGameStore(root)
            jobs = GameJobs(factory or (lambda:store))
            app = PortraitKioskV2App(game_jobs=jobs)
            Window.add_widget(app.build())
            try:
                yield app, store
            finally:
                app.on_stop();jobs.wait_closed();Window.remove_widget(app.stage)

    def settle(self, app):
        deadline = time.monotonic()+3
        while app._game_jobs.busy and time.monotonic()<deadline:
            app._poll_game();EventLoop.idle()
        self.assertFalse(app._game_jobs.busy)

    def claim(self, app, code='DEMO-GUI'):
        app._choose_game();app._open_game_demo()
        app._demo_code.text=code
        app._claim_game_demo();app._claim_game_demo()
        self.settle(app)
        self.assertEqual(app.navigation.page,GAME_PLAY)
        self.assertEqual(app._game_engine.status,'ready')

    def finish(self, app, won=False):
        app._game_engine.score = TARGET_SCORE if won else 2
        app._game_engine.status = 'won' if won else 'lost'
        app._game_tick(0)
        self.settle(app)
        self.assertEqual(app.navigation.page,GAME_RESULT)

    def test_win_and_loss_handoff_preserve_tutorial_cart_and_no_real_discount(self):
        from photobooth.workflow import quote_order
        for won in (False,True):
            with self.subTest(won=won),self.booth() as (app,store):
                self.claim(app)
                attempt=app._game_attempt['attempt_id']
                self.assertEqual(store.get(attempt)['result'],'started')
                self.finish(app,won)
                self.assertEqual(store.get(attempt)['result'],'won' if won else 'lost')
                buttons=[w for w in app.stage.walk() if isinstance(w,ArcadeButton)]
                self.assertFalse(any('MAIN LAGI'==w.text for w in buttons))
                old=next(w for w in buttons if w.text=='LANJUT PILIH TEMPLATE')
                old.dispatch('on_release')
                self.assertEqual(app.navigation.page,TUTORIAL)
                old.dispatch('on_release')
                self.assertEqual(app.navigation.page,TUTORIAL)
                app._complete_tutorial();app._change_copies(1)
                self.assertEqual(quote_order(app.templates,app.quantities).total_amount,10000)
                self.assertFalse(hasattr(app.navigation,'paid'))
                self.assertFalse(hasattr(app.navigation,'discount_amount'))
                app._return_ad()
                self.assertIsNone(app._game_result)
                app._choose_game();app._open_game_demo();app._demo_code.text='DEMO-GUI'
                app._claim_game_demo();self.settle(app)
                self.assertEqual(app.navigation.page,GAME_RECEIPT)
                self.assertIn('sudah dipakai',app._game_message.text)

    def test_seen_tutorial_skips_to_real_gallery_without_payment_route(self):
        with self.booth() as (app,_):
            self.claim(app)
            app.navigation.tutorial_seen=True
            self.finish(app)
            app._continue_game_photo()
            self.assertEqual(app.navigation.page,TEMPLATES)

    def test_minimize_and_resize_preserve_run_and_require_manual_resume(self):
        original=Window.size
        try:
            with self.booth() as (app,_):
                self.claim(app)
                app._flap_game()
                engine=app._game_engine
                app.on_pause();elapsed=engine.elapsed
                app._game_tick(20)
                self.assertEqual(engine.elapsed,elapsed)
                app.on_resume();app._game_tick(.01)
                self.assertEqual(engine.elapsed,elapsed)
                self.assertTrue(app._game_paused)
                app._toggle_game_pause()
                for size in ((800,1280),(452,900),(360,640)):
                    Window.size=size
                    for _ in range(4):EventLoop.idle()
                    self.assertIs(app._game_engine,engine)
                    arena=app._game_field.arena
                    bottom=arena.to_window(*arena.pos)
                    top=arena.to_window(arena.right,arena.top)
                    self.assertGreaterEqual(min(bottom),-1)
                    self.assertLessEqual(top[0],size[0]+1)
                    self.assertLessEqual(top[1],size[1]+1)
        finally:
            Window.size=original

    def test_abandonment_disposes_input_and_keeps_token_consumed(self):
        with self.booth() as (app,store):
            self.claim(app)
            field=app._game_field
            attempt=app._game_attempt['attempt_id']
            app._finish_game_demo();self.settle(app)
            self.assertTrue(field._disposed)
            self.assertEqual(store.get(attempt)['result'],'abandoned')
            with self.assertRaises(DemoClaimError):store.claim('DEMO-GUI')
            app._return_ad()
            field._flap()
            self.assertEqual(app.navigation.page,ADVERT)

    def test_stale_claim_never_navigates_a_new_visit(self):
        entered,release=threading.Event(),threading.Event()
        with TemporaryDirectory() as root:
            store=DemoGameStore(root)
            def slow():
                entered.set();release.wait(2);return store
            try:
                with self.booth(slow) as (app,_):
                    app._choose_game();app._open_game_demo();app._demo_code.text='DEMO-STALE'
                    app._claim_game_demo();self.assertTrue(entered.wait(1))
                    app._return_ad();release.set();self.settle(app)
                    self.assertEqual(app.navigation.page,ADVERT)
                    self.assertIsNone(app._game_attempt)
                    with self.assertRaises(DemoClaimError):store.claim('DEMO-STALE')
            finally:release.set()

    def test_failed_ledger_never_starts_game_or_disables_manual_photo_entry(self):
        def unavailable():raise OSError('read-only')
        with self.booth(unavailable) as (app,_):
            app._choose_game();app._open_game_demo();app._demo_code.text='DEMO-FAIL'
            app._claim_game_demo();self.settle(app)
            self.assertEqual(app.navigation.page,GAME_RECEIPT)
            self.assertIsNone(app._game_attempt)
            self.assertFalse(app._demo_start.disabled)
            app._back_game_intro();app._choose_photo()
            self.assertEqual(app.navigation.page,TUTORIAL)


if __name__=='__main__':unittest.main()
