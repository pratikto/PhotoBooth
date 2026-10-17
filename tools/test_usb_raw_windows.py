"""One-shot RAW ESC/POS test using the installed Windows USB printer queue.

Run from the repository root:
  python -m pip install pywin32
  python tools/test_usb_raw_windows.py --printer "POS80 Printer"

The cutter command is optional because model-specific cutter support varies.
"""
import argparse
import sys
from pathlib import Path

# Support both direct script execution and python -m without installing package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from photobooth.printer import ThermalPrinter


def main():
    parser = argparse.ArgumentParser(description="Send one RAW Windows ESC/POS test job")
    parser.add_argument("--printer", required=True, help="Exact Get-Printer queue name")
    parser.add_argument("--cut", action="store_true", help="Request a full paper cut")
    args = parser.parse_args()
    data = (
        b"\x1b\x40"            # Initialize printer.
        b"\x1b\x61\x01"      # Center alignment.
        b"\x1d\x21\x11"      # Double width/height (supported ESC/POS).
        b"MEONG PHOTOBOOTH\n"
        b"\x1d\x21\x00"      # Normal size.
        b"USB RAW TEST\n"
        b"------------------------\n"
        b"Windows spooler OK\n\n\n"
    )
    if args.cut:
        data += b"\x1d\x56\x42\x00"  # Cut; optional.
    try:
        ThermalPrinter._send_windows_raw(args.printer, data)
    except Exception as error:
        print(f"RAW spooler job FAILED: {error}", file=sys.stderr)
        return 1
    print("RAW job accepted by Windows spooler. Check actual paper output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
