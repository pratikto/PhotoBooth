"""Persist selected thermal printer settings without changing environment variables."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import tempfile

from photobooth.printer import PrinterConfig, DITHER_MODES


def load_printer_config(path):
    """Load validated operator settings, falling back to environment defaults."""
    base = PrinterConfig.from_environment()
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return base
        allowed = {"lan_host", "lan_port", "wifi_host", "wifi_port",
                   "windows_printer_name", "print_width_dots", "dither_mode"}
        values = {**asdict(base), **{k: data[k] for k in allowed if k in data}}
        if values["dither_mode"] not in DITHER_MODES:
            return base
        for key in ("lan_port", "wifi_port"):
            if type(values[key]) is not int or not 1 <= values[key] <= 65535:
                return base
        if type(values["print_width_dots"]) is not int or values["print_width_dots"] not in (384, 576):
            return base
        for key in ("lan_host", "wifi_host", "windows_printer_name"):
            if not isinstance(values[key], str) or len(values[key]) > 255:
                return base
        return PrinterConfig(**values)
    except (OSError, ValueError, TypeError):
        return base


def save_printer_config(path, config):
    """Atomically save selected fields; never store network passwords."""
    path = Path(path)
    keys = ("lan_host", "lan_port", "wifi_host", "wifi_port",
            "windows_printer_name", "print_width_dots", "dither_mode")
    data = {key: getattr(config, key) for key in keys}
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                         delete=False) as out:
            temp = Path(out.name)
            json.dump(data, out, indent=2)
            out.write("\n")
        os.replace(temp, path)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
