"""Persistent printer configuration tests without hardware."""
import tempfile
import unittest
from pathlib import Path
from photobooth.printer import PrinterConfig
from photobooth.printer_settings import load_printer_config, save_printer_config


class PrinterSettingsTests(unittest.TestCase):
    def test_roundtrip_saved_config(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "printer.json"
            config = PrinterConfig(windows_printer_name="POS80 Printer(2)",
                                   print_width_dots=576, dither_mode="bayer")
            save_printer_config(path, config)
            loaded = load_printer_config(path)
            self.assertEqual(loaded.windows_printer_name, "POS80 Printer(2)")
            self.assertEqual(loaded.dither_mode, "bayer")
            self.assertEqual(loaded.print_width_dots, 576)

    def test_invalid_json_falls_back_to_default(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "printer.json"
            path.write_text('{"lan_port": -1}', encoding="utf-8")
            self.assertEqual(load_printer_config(path).lan_port, 9100)
            path.write_text("oops", encoding="utf-8")
            self.assertIsInstance(load_printer_config(path), PrinterConfig)


if __name__ == "__main__":
    unittest.main()
