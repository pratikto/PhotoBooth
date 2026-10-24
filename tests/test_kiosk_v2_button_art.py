"""Original button pixels, native fitting and unchanged touch/disabled controls."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image,ImageDraw,ImageChops
from photobooth import meong_fly_painter as painter
from photobooth.meong_fly_polish import arcade_button
from photobooth.kiosk_v2.button_art import material_pixels


class ButtonArtTests(unittest.TestCase):
    def test_material_pixels_reuse_complete_original_meong_button(self):
        for variant,kind in (('primary','pink'),('secondary','cyan'),('tertiary','dark')):
            expected=Image.new('RGBA',(291,61))
            arcade_button(ImageDraw.Draw(expected),(0,0,290,55),'',kind,painter)
            self.assertEqual(material_pixels(variant).tobytes(),expected.tobytes())



try:
    import kivy
except ImportError:
    HAS_KIVY=False
else:
    HAS_KIVY=True
    from kivy.base import EventLoop
    from kivy.core.window import Window
    from kivy.uix.floatlayout import FloatLayout
    from photobooth.kiosk_v2.theme import ArcadeButton,MUTED,rgba


@unittest.skipUnless(HAS_KIVY,'Native controls required')
class NativeButtonArtTests(unittest.TestCase):
    def test_native_nine_slice_matches_original_pixels_at_reference_size(self):
        host=FloatLayout();Window.add_widget(host)
        try:
            for variant in ('primary','secondary','tertiary'):
                b=ArcadeButton('',variant=variant,height=61,size_hint=(None,None),width=291,pos=(0,0))
                host.add_widget(b)
                for _ in range(3):EventLoop.idle()
                with tempfile.TemporaryDirectory() as directory:
                    path=str(Path(directory)/'button.png');b.export_to_png(path)
                    with Image.open(path) as actual:
                        expected=material_pixels(variant)
                        self.assertIsNone(ImageChops.difference(actual.convert('RGB'),expected.convert('RGB')).getbbox())
                        self.assertEqual(actual.convert('RGBA').getchannel('A').tobytes(),expected.getchannel('A').tobytes())
                host.remove_widget(b)
        finally:Window.remove_widget(host)

    def test_compact_native_caption_bounds_disabled_contrast_and_full_text(self):
        for text,width,height,font in (('SEBELUMNYA',108,48,12),('PEMBAYARAN (BELUM TERHUBUNG)',159,48,10),
                                       ('SELESAI / KEMBALI IKLAN',150,48,11),('MULAI FOTO',398,62,22)):
            b=ArcadeButton(text,height=height,size_hint=(None,None),width=width)
            b.font_size=font;b.texture_update()
            self.assertLessEqual(b.texture_size[0],width-24+.01)
            self.assertLessEqual(b.texture_size[1],height-18+.01)
            self.assertIs(b.texture,b._label.texture)
            self.assertEqual(tuple(b.texture_size),tuple(b.texture.size))
            self.assertEqual(b._label.text,text)
            original=b.text;b.disabled=True;b.texture_update()
            self.assertEqual(b.text,original);self.assertTrue(b.disabled)
            self.assertEqual(tuple(b.disabled_color),rgba(MUTED))
            self.assertEqual(tuple(b._label.options['color']),rgba(MUTED))

    def test_position_and_pressed_state_reuse_cached_original_material_and_caption(self):
        b=ArcadeButton('MULAI FOTO',width=398);b.texture_update()
        original=b.texture
        with patch('photobooth.kiosk_v2.button_art.arcade_button',side_effect=AssertionError('Repeated material raster')):
            for index in range(20):
                b.pos=(index,index);b.state='down' if index%2 else 'normal'
                self.assertIs(b.texture,original)

    def test_native_font_keeps_arrows_on_one_line_without_bitmap_scaling(self):
        for text in ('SEBELUMNYA','BERIKUTNYA'):
            b=ArcadeButton(text,width=108,height=48,size_hint=(None,None))
            b.font_size=12;b.texture_update()
            self.assertEqual(b._label.text,text)
            self.assertLessEqual(b.texture_size[1],18)
            self.assertIs(b.texture,b._label.texture)
            self.assertEqual(tuple(b.texture_size),tuple(b.texture.size))

    def test_native_font_preserves_punctuation_and_has_no_caption_icon(self):
        from kivy.graphics import Rectangle
        text='SELESAI • KEMBALI IKLAN'
        b=ArcadeButton(text,width=398);b.texture_update()
        self.assertEqual(b.font_size,18)
        self.assertEqual(b._label.text,text)
        self.assertIs(b.texture,b._label.texture)
        # Only the nine original frame slices; the caption is the standard
        # native Button canvas. No embedded icon or caption bitmap overlay.
        self.assertEqual(sum(isinstance(item,Rectangle) for item in b.canvas.before.children),9)
