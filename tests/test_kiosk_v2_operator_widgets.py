"""Original v1 panel inside real v2 window, with probe/file fixtures only."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import time
import unittest
from unittest.mock import Mock, patch

from kivy.base import EventLoop
from kivy.core.window import Window
from kivy.input.motionevent import MotionEvent
from photobooth.device_health import HealthCheck, HealthSnapshot
from photobooth.ui_health import HealthPanelMixin
from photobooth.ui_kivy import PhotoBoothUI
from photobooth.kiosk_v2.app import PortraitKioskV2App
from photobooth.kiosk_v2.flow import ADVERT, CAPTURE, GAME_PLAY, MOCK_CHECKOUT, SANDBOX_CHECKOUT
from photobooth.kiosk_v2.operator_health import OperatorPanel, OperatorMeongLogo
from photobooth.kiosk_v2.theme import ArcadeButton



class Pointer(MotionEvent):
    # Same native MotionEvent pattern used by the existing gallery touch tests.
    def __init__(self,x,y):
        super().__init__('operator-test',str(id(self)),(x/Window.width,y/Window.height),is_touch=True)
        self.scale_for_screen(Window.width,Window.height)
    def depack(self,args):
        self.sx,self.sy=args;self.profile=['pos'];super().depack(args)
    def move_to(self,x,y):
        self.move((x/Window.width,y/Window.height))
        self.scale_for_screen(Window.width,Window.height)

def fixture_snapshot(status='ready'):
    return HealthSnapshot('2026-10-25T05:00:00+00:00',tuple(
        HealthCheck(name,status,'Pemeriksaan terbatas, bukan sertifikasi perangkat.')
        for name in ('camera','printer','disk','network','media','heartbeat')))


class OperatorWidgetTests(unittest.TestCase):
    @contextmanager
    def booth(self,collector=None):
        with TemporaryDirectory() as root, patch.dict(os.environ,{
                'PHOTOBOOTH_AUDIO':'0','PHOTOBOOTH_AD_VIDEO':'0','PHOTOBOOTH_CAMERA':'0',
                'PHOTOBOOTH_FACE_TRIGGER':'0','PHOTOBOOTH_PALM_TRIGGER':'0',
                'PHOTOBOOTH_V2_CHECKOUT_MOCK':'0','PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'0'}),patch(
                'photobooth.kiosk_v2.operator_health.PROJECT_ROOT',Path(root)),patch(
                'photobooth.v1_health_controller.collect_health_snapshot',side_effect=collector or (lambda **_:fixture_snapshot())) as probe:
            app=PortraitKioskV2App();Window.add_widget(app.build())
            try:yield app,probe,Path(root)
            finally:
                app.on_stop();app._health_reports.wait_closed()
                Window.remove_widget(app.stage)
                # Complete already scheduled closing guards without starting hardware.
                EventLoop.idle()
    def settle(self,app,*,snapshot=True):
        deadline=time.monotonic()+4
        while time.monotonic()<deadline:
            EventLoop.idle();app._poll_operator()
            panel=app._operator_panel
            if not app._health_reports.busy and (not snapshot or (panel and panel.snapshot is not None)):return
            time.sleep(.005)
        self.fail('Operator worker did not settle')
    def test_original_panel_and_label_methods_reused_with_six_rows_and_no_selection(self):
        self.assertIs(OperatorPanel.show_health_settings,HealthPanelMixin.show_health_settings)
        self.assertIs(OperatorPanel._label,PhotoBoothUI._label)
        with self.booth() as (app,probe,_):
            page=app.navigation.page;player=app._ad_player
            app._open_operator();self.settle(app);panel=app._operator_panel
            self.assertEqual(len(panel._health_labels),6)
            self.assertIs(app._ad_player,player);self.assertEqual(app.navigation.page,page)
            self.assertTrue(panel._health_select_button.disabled)
            self.assertIsNone(panel.show_device_selection_settings())
            self.assertEqual(probe.call_count,1)
    def test_f12_opens_once_and_operator_cannot_interrupt_active_customer_pages(self):
        with self.booth() as (app,probe,_):
            for page in (CAPTURE,GAME_PLAY,MOCK_CHECKOUT,SANDBOX_CHECKOUT):
                app.navigation.page=page
                self.assertFalse(app._operator_key(Window,293));self.assertIsNone(app._operator_panel)
            app.navigation.page=ADVERT
            self.assertTrue(app._operator_key(Window,293));self.settle(app)
            panel=app._operator_panel
            self.assertTrue(app._operator_key(Window,293));self.assertIs(app._operator_panel,panel)
            self.assertFalse(app._operator_key(Window,27));self.assertEqual(probe.call_count,1)
    def test_header_short_tap_drag_right_click_do_not_open_and_hold_opens_once(self):
        with self.booth() as (app,probe,_):
            for _ in range(3):EventLoop.idle()
            brand=next(w for w in app.stage.walk() if isinstance(w,OperatorMeongLogo))
            tap=Pointer(*brand.center);brand.on_touch_down(tap);brand.on_touch_up(tap)
            self.assertIsNone(app._operator_panel)
            drag=Pointer(*brand.center);brand.on_touch_down(drag)
            drag.move_to(brand.center_x+100,brand.center_y)
            brand.on_touch_move(drag);brand.on_touch_up(drag)
            self.assertIsNone(brand._hold_event)
            right=Pointer(*brand.center);right.button='right'
            brand.on_touch_down(right);self.assertIsNone(brand._hold_event)
            hold=Pointer(*brand.center);brand.on_touch_down(hold)
            deadline=time.monotonic()+2
            while app._operator_panel is None and time.monotonic()<deadline:EventLoop.idle()
            self.assertIsNotNone(app._operator_panel);self.settle(app)
            self.assertEqual(probe.call_count,1);self.assertIsNone(brand._hold_touch)
    def test_close_reopen_during_probe_ignores_stale_result_and_never_queues_probe(self):
        entered=threading.Event();release=threading.Event()
        def collector(**_):entered.set();release.wait(3);return fixture_snapshot()
        with self.booth(collector) as (app,probe,_):
            app._open_operator();self.assertTrue(entered.wait(1));old=app._operator_panel
            old._health_refresh_button.dispatch('on_release');self.assertEqual(probe.call_count,1)
            app._close_operator();app._open_operator();fresh=app._operator_panel
            for _ in range(4):EventLoop.idle()
            self.assertIsNot(fresh,old);self.assertIsNone(fresh.snapshot)
            release.set()
            for _ in range(8):EventLoop.idle()
            self.assertIsNone(fresh.snapshot);self.assertEqual(probe.call_count,1)
            fresh._health_refresh_button.dispatch('on_release');self.settle(app)
            self.assertIsNotNone(fresh.snapshot);self.assertEqual(probe.call_count,2)
    def test_export_is_local_and_reports_do_not_certify_provider_or_include_raw_text(self):
        with self.booth() as (app,_,root):
            app._open_operator();self.settle(app);panel=app._operator_panel
            panel.export_button.dispatch('on_release');self.settle(app)
            files=list((root/'data'/'diagnostics').glob('device-health-*.json'))
            self.assertEqual(len(files),1)
            report=json.loads(files[0].read_text())
            self.assertEqual(len(report['health']['checks']),6)
            self.assertEqual(set(report['acceptance'].values()),{'NOT_RUN'})
            self.assertNotIn('Pemeriksaan terbatas',files[0].read_text())
            self.assertIn(files[0].name,panel.report_message.text)
    def test_old_export_completion_does_not_paint_new_panel_or_leave_export_disabled(self):
        with self.booth() as (app,_,root):
            app._open_operator();self.settle(app)
            entered=threading.Event();release=threading.Event()
            original=app._health_reports._factory
            store=original()
            def save(snapshot):
                entered.set();release.wait(3)
                return {'file':'retired-report.json','head':'unknown'}
            with patch.object(store,'save',side_effect=save):
                app._health_reports.store=store
                app._operator_panel.export_button.dispatch('on_release');self.assertTrue(entered.wait(1))
                app._close_operator();app._open_operator()
                fresh=app._operator_panel
                deadline=time.monotonic()+2
                while fresh.snapshot is None and time.monotonic()<deadline:EventLoop.idle()
                self.assertTrue(fresh.export_button.disabled)
                release.set();self.settle(app)
                self.assertFalse(fresh.export_button.disabled)
                self.assertNotIn('retired-report',fresh.report_message.text)

    def test_minimize_closes_modal_and_resume_does_not_reopen_or_reset_customer(self):
        with self.booth() as (app,probe,_):
            app._open_operator();self.settle(app)
            app.on_pause();self.assertIsNone(app._operator_panel)
            app.on_resume();self.assertIsNone(app._operator_panel)
            self.assertEqual(app.navigation.page,ADVERT)
            app._open_operator();self.settle(app);self.assertEqual(probe.call_count,2)
    def test_resizes_keep_original_dialog_inside_window_and_main_audio_owner(self):
        with self.booth() as (app,_,__):
            app._open_operator();self.settle(app);panel=app._operator_panel
            size=Window.size;page=app.navigation.page
            try:
                for dimensions in ((800,1280),(452,900),(360,640)):
                    Window.size=dimensions
                    for _ in range(5):EventLoop.idle()
                    self.assertLessEqual(panel._health_popup.width,Window.width)
                    self.assertLessEqual(panel._health_popup.height,Window.height)
                    self.assertEqual(app.navigation.page,page)
                    self.assertEqual(app.audio_v2.page,ADVERT)
            finally:Window.size=size
    def test_retired_modal_and_customer_releases_are_inert_but_new_single_tap_works(self):
        with self.booth() as (app,probe,_):
            start=next(w for w in app.stage.walk() if isinstance(w,ArcadeButton) and w.text=='MULAI FOTO')
            start.dispatch('on_press')
            app._open_operator();self.settle(app);old=app._operator_panel
            refresh=old._health_refresh_button
            app._close_operator()
            refresh.dispatch('on_release');start.dispatch('on_release')
            self.assertEqual(app.navigation.page,ADVERT);self.assertEqual(probe.call_count,1)
            start.dispatch('on_press');start.dispatch('on_release')
            self.assertEqual(app.navigation.page,'tutorial')
    def test_twenty_open_refresh_close_cycles_leave_no_popup_size_bindings(self):
        with self.booth() as (app,probe,_):
            baseline=len(Window.get_property_observers('size'))
            for _ in range(20):
                app._open_operator();self.settle(app);app._close_operator();EventLoop.idle()
            self.assertIsNone(app._operator_panel);self.assertEqual(probe.call_count,20)
            self.assertEqual(len(Window.get_property_observers('size')),baseline)
            self.assertEqual(app.navigation.page,ADVERT)
    def test_probe_error_keeps_unknown_status_and_disables_export_without_driver_exception(self):
        with self.booth(lambda **_:(_ for _ in ()).throw(RuntimeError('SECRET DRIVER token'))) as (app,_,__):
            app._open_operator()
            deadline=time.monotonic()+3
            while app._operator_panel._health_refresh_button.disabled and time.monotonic()<deadline:EventLoop.idle()
            panel=app._operator_panel
            self.assertIsNone(panel.snapshot);self.assertTrue(panel.export_button.disabled)
            captions=' '.join(w.text for w in panel._health_popup.walk() if hasattr(w,'text'))
            self.assertNotIn('SECRET DRIVER',captions)
            self.assertIn('BELUM DIKETAHUI',captions)
