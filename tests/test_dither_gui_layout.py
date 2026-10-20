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

    def test_threshold_hidden_without_disabling_saved_preset(self):
        # The GUI renders only Floyd/Bayer/Dizzy, never a Threshold lane.
        self.assertIn('VISIBLE_MODES = ("floyd-steinberg", "bayer", "dizzy")',
                      self.source)
        self.assertIn('for idx, mode in enumerate(VISIBLE_MODES):', self.source)
        self.assertNotIn('("threshold", "Threshold", 0, 255)', self.source)
        self.assertIn('for mode in LAB_DITHER_MODES:', self.source)
        self.assertIn('for mode in VISIBLE_MODES:', self.source)
        self.assertIn('for m in LAB_DITHER_MODES}', self.source)

    def test_batch_and_export_only_visible_three(self):
        self.assertIn('Export 3 PNG', self.source)
        self.assertIn('Print All (3 jobs)', self.source)
        self.assertIn('self._start_print(VISIBLE_MODES)', self.source)
        self.assertIn('for mode in VISIBLE_MODES:', self.source)
        self.assertNotIn('Print All (4 jobs)', self.source)
        self.assertNotIn('Export 4 PNG', self.source)
        self.assertIn('meong-dither-lab-v4.json', self.source)

    def test_enhanced_floyd_is_in_floyd_panel_not_top_toolbar(self):
        # Both toggles live after their respective preview metadata.
        self.assertIn('panel, text="Enhanced Floyd (experimental)"', self.source)
        self.assertIn('panel, text="Enhanced Dizzy (experimental)"', self.source)
        self.assertNotIn(
            'ttk.Checkbutton(bar, text="Enhanced Floyd (experimental)"',
            self.source,
        )
        self.assertIn('command=self.toggle_enhanced,', self.source)
        self.assertIn('command=self.toggle_enhanced_dizzy,', self.source)

    def test_bounded_previews(self):
        self.assertIn('preview_holder = ttk.Frame(panel, height=286)', self.source)
        self.assertIn('preview_holder.pack_propagate(False)', self.source)
        self.assertIn('preview.thumbnail((370, 268)', self.source)


if __name__ == "__main__":
    unittest.main()
