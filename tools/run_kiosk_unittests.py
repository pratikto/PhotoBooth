"""Execute the complete kiosk unittest suite with reliable CI diagnostics.

Kivy may intercept/redirect sys.stderr while its window/audio providers
start. Standard unittest discovery can therefore fail GitHub Actions without
displaying any test names or tracebacks. This runner retains unittest's default
discovery and prints its final report to the real OS stdout file descriptor,
bypassing Python/Kivy logging.

No real hardware, payment provider, customer photos or production data are
accessed beyond the existing synthetic unittest suite.
"""

from __future__ import annotations

import io
import os
from pathlib import Path
import sys
import unittest


def main() -> int:
    """Run existing tests unchanged and preserve their exit status."""
    # Invoking a file from tools/ makes sys.path[0] point to tools/, not the
    # repository root. Restore the normal 'python -m unittest' import context
    # before discovery so every test can import photobooth as it does locally.
    repository_root = Path(__file__).resolve().parent.parent
    if str(repository_root) not in sys.path:
        sys.path.insert(0, str(repository_root))
    suite = unittest.defaultTestLoader.discover(
        str(repository_root / "tests"), pattern="test_*.py",
        top_level_dir=str(repository_root),
    )
    output = io.StringIO()
    result = unittest.TextTestRunner(
        stream=output, verbosity=2, buffer=False
    ).run(suite)

    # The POSIX file descriptor is not affected by Kivy's logger redirects.
    report = output.getvalue()
    if not report.endswith("\n"):
        report += "\n"
    report += (
        f"KIOSK_UNITTEST_SUMMARY: run={result.testsRun} "
        f"failures={len(result.failures)} errors={len(result.errors)} "
        f"skipped={len(result.skipped)} "
        f"success={result.wasSuccessful()}\n"
    )
    raw = report.encode("utf-8", errors="replace")
    for offset in range(0, len(raw), 4096):
        os.write(1, raw[offset:offset + 4096])

    # Keep the same output as an artifact if Actions truncates the console.
    report_path = os.environ.get("MEONG_CI_TEST_REPORT")
    if report_path:
        destination = Path(report_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(report, encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
