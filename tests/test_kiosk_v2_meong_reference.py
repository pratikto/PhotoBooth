"""Proof that v2 actually hosts the unchanged latest game, including pixels."""

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import Mock,patch

ROOT=Path(__file__).resolve().parents[1]
PARITY_RECORDS=[]


class ReferenceSourceTests(unittest.TestCase):
    def test_all_original_modules_art_and_tests_match_pinned_remote_head(self):
        reference=json.loads((ROOT/'docs/qa/portrait-v2-meong-reuse/upstream-reference.json').read_text())
        self.assertEqual(reference['reference_sha'],'672e3f7089bb40940e5b41644ceb656aa63aafbb')
        for item in reference['files']:
            with self.subTest(file=item['file']):
                self.assertEqual(hashlib.sha256((ROOT/item['file']).read_bytes()).hexdigest(),item['sha256'])

    def test_v2_compatibility_module_is_the_same_engine_class(self):
        from photobooth.meong_fly import MeongFly,Pipe
        from photobooth.kiosk_v2.game_engine import MeongFly as V2,Pipe as V2Pipe
        self.assertIs(V2,MeongFly)
        self.assertIs(V2Pipe,Pipe)


try:
    import kivy
except ImportError:
    HAS_KIVY=False
else:
    HAS_KIVY=True
    from kivy.base import EventLoop
    from kivy.core.window import Window
    from kivy.input.motionevent import MotionEvent
    from photobooth.meong_fly_gui import MeongFlyStage
    from photobooth.meong_fly_flow import MeongFlyFlow
    from photobooth.meong_fly_painter import ACTIONS
    from photobooth.kiosk_v2.game_scene import KioskGameStage
    from photobooth.kiosk_v2.flow import GAME_PREVIEW,GAME_RECEIPT,GAME_PLAY
    from tests import test_kiosk_v2_game_widgets as support


@unittest.skipUnless(HAS_KIVY,'Native game renderer required')
class ReferenceIntegrationTests(unittest.TestCase):
    def test_invalid_then_valid_demo_does_not_carry_old_warning_into_game(self):
        helper=support.GameWidgetTests()
        with helper.booth() as (app,_):
            app._choose_game();app._open_game_demo();app._demo_code.text='INVALID'
            app._claim_game_demo();helper.settle(app)
            self.assertTrue(app._game_error)
            app._demo_code.text='DEMO-RECOVER'
            app._claim_game_demo();helper.settle(app)
            self.assertEqual(app.navigation.page,GAME_PLAY)
            self.assertEqual(app._game_error,'')
            self.assertEqual(app._game_busy_label.text,'')

    def test_renderer_compositor_and_animation_methods_are_original_objects(self):
        for name in ('_draw_game','_paint_camera','_paint_print_sheets',
                     '_advance_printer','_camera_context','_printer_context','_draw_score'):
            with self.subTest(method=name):
                self.assertIs(getattr(KioskGameStage,name),getattr(MeongFlyStage,name))

    def test_original_camera_and_film_reflow_at_three_sizes_and_four_print_phases(self):
        from kivy.graphics import Quad
        from photobooth.kiosk_v2.game_layout import Layout
        helper=support.GameWidgetTests()
        with helper.booth() as (app,_):
            app._choose_game()
            stage=app._game_field
            stage._update_event.cancel();stage._update_event=None
            stage.size_hint=(None,None)
            baseline=MeongFlyStage(MeongFlyFlow(Mock()),size_hint=(None,None))
            baseline._update_event.cancel();baseline._update_event=None
            try:
                for size in ((800,1280),(452,900),(800,900)):
                    stage.size=baseline.size=size
                    for scene in ('start','game','won','lost'):
                        phases=(.30,.96,1.32,1.74) if scene=='start' else (.96,)
                        for phase in phases:
                            with self.subTest(size=size,scene=scene,time=phase):
                                for view in (stage,baseline):
                                    view.flow.screen=scene
                                    view.flow.game.y=300
                                    view.flow.game.score=10 if scene=='won' else 3
                                    view.flow.game.pipes=[]
                                    view._printer_screen=None
                                    view._time=0
                                    view._impact_until=-1
                                    while view._time+.00001<phase:
                                        view._time=round(view._time+.03,6)
                                        view._advance_printer(.03)
                                    view._refresh()
                                # The renderer, pose, layer pixels and emitter
                                # are still upstream, even as their layout moves.
                                self.assertEqual(stage._camera_context(scene),baseline._camera_context(scene))
                                self.assertEqual(stage._printer.poses(),baseline._printer.poses())
                                for name in stage._camera_layers:
                                    for actual,expected in zip(stage._camera_layers[name],baseline._camera_layers[name]):
                                        self.assertEqual(bytes(actual.pixels),bytes(expected.pixels))
                                actual=[i for i in stage.canvas.before.children if isinstance(i,Quad)]
                                expected=[i for i in baseline.canvas.before.children if isinstance(i,Quad)]
                                self.assertEqual(len(actual),len(expected))
                                layout=Layout(*size,scene)
                                ox,oy,scale=baseline._viewport()
                                for got,want in zip(actual,expected):
                                    self.assertEqual(tuple(got.tex_coords),tuple(want.tex_coords))
                                    self.assertEqual(bytes(got.texture.pixels),bytes(want.texture.pixels))
                                    for index in range(0,8,2):
                                        x=(want.points[index]-ox)/scale
                                        y=720-(want.points[index+1]-oy)/scale
                                        if scene=='game':
                                            x=layout.world_x(x);y+=layout.extra[1]/2
                                        else:
                                            x+=layout.extra[0]/2
                                            y+=layout.menu_offset(stage._camera_context(scene)[1])
                                        self.assertAlmostEqual(got.points[index],stage.x+x*layout.scale,delta=.01)
                                        self.assertAlmostEqual(got.points[index+1],stage.top-y*layout.scale,delta=.01)
                                PARITY_RECORDS.append({'width':size[0],'height':size[1],'scene':scene,
                                                       'time':phase,'original_camera_film':True})
            finally:
                baseline.dispose()

    def test_original_hitboxes_work_through_scaled_viewport_and_one_click_owner(self):
        class Pointer(MotionEvent):
            def depack(self,args):
                self.sx,self.sy=args;self.profile=['pos'];super().depack(args)
        original=Window.size
        try:
            for size in ((800,1280),(452,900),(360,640),(800,900)):
                with self.subTest(size=size),support.GameWidgetTests().booth() as (app,_):
                    Window.size=size;app._choose_game()
                    for _ in range(4):EventLoop.idle()
                    with patch.object(app.audio_v2,'cue') as cue:
                        stage=app._game_field
                        x,y,w,h=ACTIONS['start']['game']
                        pos,extent=stage._rect((x,y,w,h))
                        point=stage.to_window(pos[0]+min(20,extent[0]/4),pos[1]+extent[1]/2)
                        pointer=Pointer('reference-stage','start',(point[0]/Window.width,point[1]/Window.height),is_touch=True)
                        EventLoop.post_dispatch_input('begin',pointer);EventLoop.post_dispatch_input('end',pointer)
                        self.assertEqual(app.navigation.page,GAME_RECEIPT)
                        self.assertEqual(cue.call_count,1)
                        self.assertEqual(app._game_field.flow.screen,'scan')
        finally:Window.size=original

    def test_no_standalone_app_scanner_home_ledger_or_tutorial_marker(self):
        with patch('photobooth.meong_fly_gui.ReceiptScanner',side_effect=AssertionError('Scanner off')) as scanner, \
             patch('photobooth.meong_fly_gui.DemoReceiptLedger',side_effect=AssertionError('Use v2 ledger')) as ledger, \
             patch('photobooth.meong_fly_gui.MeongFlyStandaloneApp.build',side_effect=AssertionError('One App')) as standalone:
            helper=support.GameWidgetTests()
            with helper.booth() as (app,_):
                helper.claim(app)
                self.assertIsNone(app._game_field._scanner)
                helper.finish(app,True)
                app._continue_game_photo()
                self.assertEqual(app.navigation.page,'tutorial')
            scanner.assert_not_called();ledger.assert_not_called();standalone.assert_not_called()

    def test_only_original_stage_clock_steps_physics_and_retired_stage_is_inert(self):
        helper=support.GameWidgetTests()
        with helper.booth() as (app,_):
            helper.claim(app)
            stage=app._game_field
            stage._update_event.cancel();stage._update_event=None
            expected=copy.deepcopy(app._game_engine)
            with patch.object(app.camera_device,'read',return_value=None):app._devices_tick(.03)
            self.assertEqual(app._game_engine.elapsed,expected.elapsed)
            expected.step(.03);stage.update(.03)
            self.assertEqual(app._game_engine.elapsed,expected.elapsed)
            self.assertEqual(app._game_engine.y,expected.y)
            app._finish_game_demo();helper.settle(app);app._return_ad()
            before=app._view_revision
            stage._handle_action('game');stage.update(100)
            self.assertEqual(app._view_revision,before)
            self.assertIsNone(stage._update_event)


if __name__=='__main__':unittest.main()
