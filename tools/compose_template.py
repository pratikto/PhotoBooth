"""Place three existing pictures inside an approved receipt without a camera.

Examples (run from the project root with the same venv as main.py):
    python tools/compose_template.py --list
    python tools/compose_template.py --template 02 --photos one.jpg two.jpg three.jpg --output preview.png

This calls the application's actual compositor. It is useful for trying your
own pictures or diagnosing assets without starting Kivy, payment, or Drive.
An optional --folder-url embeds a real HTTPS download destination. Omitting
it produces an explicitly local result; it does not invent a customer link.
"""

import argparse
from pathlib import Path
import sys

# Direct execution from tools/ otherwise omits the repository root from imports.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from photobooth.catalog import compose_result, get_templates


def main():
    """Validate user options, select one design, and save a full-size PNG."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="List the 12 template IDs and names.")
    parser.add_argument("--template", help="Approved number (01–12) or template_a–template_l.")
    parser.add_argument("--photos", nargs=3, type=Path, metavar="PHOTO")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--folder-url", help="Actual HTTPS folder URL; no upload is performed.")
    parser.add_argument("--transaction-id", default="PREVIEW")
    parser.add_argument("--session-id", default="session_001")
    args = parser.parse_args()
    templates = get_templates()
    if args.list:
        for template in templates:
            print(f"{template.source_id}  {template.template_id:12}  {template.name}")
        return
    if not args.template or not args.photos or not args.output:
        parser.error("Use --template, --photos (three paths), and --output, or use --list.")
    template = next((item for item in templates if args.template in
                     (item.source_id, item.template_id)), None)
    if template is None:
        parser.error("Unknown template. Run with --list to see the approved choices.")
    try:
        result = compose_result(args.photos, template, args.output,
                                args.transaction_id, args.session_id, args.folder_url)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"Saved {template.name}: {result.resolve()} (640 × 1920 px, 80 × 240 mm)")


if __name__ == "__main__":
    main()
