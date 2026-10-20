"""BUG-010 layout regression guards without requiring a Tk display."""
import ast
from pathlib import Path
import unittest


class ScrollLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        src = Path(__file__).resolve().parents[1] / "tools" / "dither_compare_gui.py"
        cls.source = src.read_text(encoding="utf-8")
        ast.parse(cls.source, filename=str(src))

    def test_independent_scroll_and_wheel(self):
        for marker in ('self.scroll_canvases[mode] = canvas',
                       'canvas.yview_scroll(amount, "units")',
                       'command=canvas.yview', '"<MouseWheel>"'):
            self.assertIn(marker, self.source)

    def test_print_buttons_outside_scroll_region(self):
        self.assertIn('sliders_host = ttk.Frame(panel)', self.source)
        self.assertIn('actions = ttk.Frame(panel)', self.source)
        self.assertIn('actions.pack(side="bottom"', self.source)

    def test_bounded_previews(self):
        self.assertIn('preview_holder = ttk.Frame(panel, height=286)', self.source)
        self.assertIn('preview_holder.pack_propagate(False)', self.source)
        self.assertIn('preview.thumbnail((270, 268)', self.source)


if __name__ == "__main__":
    unittest.main()
