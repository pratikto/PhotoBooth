"""Render isolated private-preview fixtures; one fresh process per size.

This QA driver uses synthetic pixels and does not enable payment/print/Drive.
"""
import argparse
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--width', type=int, choices=(452, 800), required=True)
    parser.add_argument('--height', type=int, choices=(900, 1280), required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    os.environ['MEONG_PRIVATE_PREVIEW_SIZE'] = f'{args.width}x{args.height}'
    os.environ['MEONG_PRIVATE_PREVIEW_SCREENSHOTS'] = str(args.output_dir)
    os.environ['KIVY_NO_ARGS'] = '1'
    os.environ['PHOTOBOOTH_CAMERA'] = '0'
    os.environ['PHOTOBOOTH_AUDIO'] = '0'
    os.environ['PHOTOBOOTH_AD_VIDEO'] = '0'
    from kivy.config import Config
    Config.set('graphics', 'width', str(args.width))
    Config.set('graphics', 'height', str(args.height))
    from tests.test_post_preview_widgets import PrivateWidgetTests
    suite = unittest.TestSuite([PrivateWidgetTests(
        'test_native_capture_review_and_all_designs_preview_at_both_portrait_sizes')])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__': sys.exit(main())
