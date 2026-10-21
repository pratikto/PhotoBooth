"""Run the opt-in GUI v2 prototype, without changing python main.py.

Windows:
    .\.venv-kivy\Scripts\Activate.ps1
    python tools/run_portrait_v2.py

This stage cannot accept payments, operate a real cafe receipt scanner,
capture camera frames, print or issue discounts.
"""

import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Kivy reads these before opening the window. Ignore kiosk framework CLI flags.
os.environ.setdefault("KIVY_NO_ARGS", "1")

from kivy.config import Config

Config.set("graphics", "width", "800")
Config.set("graphics", "height", "1280")

from photobooth.kiosk_v2.app import PortraitKioskV2App


if __name__ == "__main__":
    print("MEONG v2 PORTRAIT PROTOTYPE - no payment, camera, printing or real game")
    PortraitKioskV2App().run()
