"""Summarize anonymous local playback events as CSV for a venue/advertiser.

Example: python tools/ad_report.py --events data/advertising/events.jsonl
Redirect stdout to a CSV file if needed. These are play counts and actual
displayed seconds, not counts of people, unique viewers or verified attention.
"""

import argparse
import csv
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from photobooth.advertising import summarize_events


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--events', type=Path, default=Path('data/advertising/events.jsonl'))
    args = parser.parse_args()
    columns = ['ad_id', 'placement', 'plays', 'completed', 'displayed_seconds', 'photo_entries']
    writer = csv.DictWriter(sys.stdout, fieldnames=columns)
    writer.writeheader()
    writer.writerows(summarize_events(args.events))


if __name__ == '__main__':
    main()
