"""Read-only preflight for the supervised post-preview Windows pilot.

No payments, cameras, printer bytes, Drive API calls, directory creation or
secret values are read or emitted by this utility.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "feature/post-preview-qris-checkout"
REQUIRED_FILES = (
    "tools/run_post_preview_checkout_pilot.py",
    "requirements.txt",
    "requirements-post-preview.txt",
    "requirements-qris.txt",
    "docs/qa/portrait-v2-sandbox/PP07-SUPERVISED-WINDOWS-UAT.md",
)
# These are required for the real-camera synthetic Kivy + HTTP checkout fixture.
# A successful check is about installed modules, not device/provider readiness.
IMPORTS = (
    "kivy", "PIL", "numpy", "requests", "cryptography",
    "fastapi", "httpx", "pydantic", "qrcode", "cv2", "ffpyplayer",
)
CONFLICTING_PROFILES = (
    "PHOTOBOOTH_V2_CHECKOUT_SANDBOX", "PHOTOBOOTH_V2_CHECKOUT_MOCK",
    "PHOTOBOOTH_V2_PRINT", "PHOTOBOOTH_V2_DRIVE",
)


def inspect(root: Path = ROOT, check_imports: bool = True, *, environment=None) -> dict:
    environment = os.environ if environment is None else environment
    checks = []
    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "BLOCKED", "detail": detail})

    record("Python", sys.version_info >= (3, 11),
           f"{sys.version_info.major}.{sys.version_info.minor} (minimum 3.11)")
    try:
        git = subprocess.run(
            ["git", "-C", str(root), "branch", "--show-current"],
            capture_output=True, text=True, timeout=8, check=False,
        )
        branch = git.stdout.strip() if git.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        branch = ""
    record("Authorized branch", branch == EXPECTED_BRANCH,
           branch or "Git branch could not be read")
    # Report only flag names, never secret or credential values.
    conflicting = [flag for flag in CONFLICTING_PROFILES if environment.get(flag) == "1"]
    record("Isolated synthetic launch profile", not conflicting,
           "legacy modes disabled" if not conflicting
           else "disable " + ", ".join(conflicting))
    for path in REQUIRED_FILES:
        record(f"File: {path}", (root / path).is_file(),
               "present" if (root / path).is_file() else "missing")
    if check_imports:
        for name in IMPORTS:
            try:
                found = importlib.util.find_spec(name) is not None
            except (ImportError, ValueError, AttributeError):
                found = False
            record(f"Dependency: {name}", found,
                   "available" if found else "missing in active interpreter")
    return {
        "status": "READY_FOR_SUPERVISED_SYNTHETIC_PILOT"
        if all(check["status"] == "PASS" for check in checks) else "BLOCKED",
        "checks": checks,
        "limits": [
            "Preflight does not launch camera, printer, Midtrans or Drive.",
            "READY does not prove functioning hardware, cloud access, payment or customer acceptance.",
            "Use a new dedicated empty private root for each supervised trial.",
            "Actual Midtrans, refunds and production remain disabled.",
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print redacted JSON summary")
    parser.add_argument("--skip-imports", action="store_true",
                        help="Only check source files, Python and branch")
    args = parser.parse_args(argv)
    result = inspect(check_imports=not args.skip_imports)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for check in result["checks"]:
            print(f'{check["status"]:7} {check["name"]}: {check["detail"]}')
        print(f'RESULT: {result["status"]}')
        print("No external operations or device tests were performed.")
    return 0 if result["status"] == "READY_FOR_SUPERVISED_SYNTHETIC_PILOT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
