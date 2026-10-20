"""Standalone mockup-matched FEAT-021 game entry point.

Use python -m photobooth.meong_fly_demo. This app is NOT integrated into the
production photobooth's welcome screen, QRIS checkout, or photo session.
"""

from .meong_fly_gui import MeongFlyStandaloneApp

# Preserve the original Demo class name for developer scripts/imports.
Demo = MeongFlyStandaloneApp


if __name__ == "__main__":
    Demo().run()
