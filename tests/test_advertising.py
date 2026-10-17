"""Offline playlist schedules, exposure accounting and deliberate face holds."""

from datetime import datetime
import json
from pathlib import Path
import tempfile
import unittest
from zoneinfo import ZoneInfo

from PIL import Image

from photobooth.advertising import AdCatalog, AdEventLog, KioskTiming, summarize_events


class AdvertisingTests(unittest.TestCase):
    def test_placements_dates_overnight_hours_and_missing_media_are_filtered(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            Image.new('RGB', (16, 16), 'blue').save(root / 'poster.png')
            config = root / 'ads.json'
            config.write_text(json.dumps({'timezone': 'Asia/Jakarta', 'ads': [
                {'id': 'night', 'file': 'poster.png', 'placements': ['idle'],
                 'start': '2026-10-17T00:00:00', 'end': '2026-10-19T00:00:00',
                 'hours': ['22:00', '06:00']},
                {'id': 'payment', 'file': 'poster.png', 'placements': ['payment']},
                {'id': 'disabled', 'file': 'poster.png', 'enabled': False},
                {'id': 'missing', 'file': 'missing.mp4'},
                {'id': 'bad-time', 'file': 'poster.png', 'hours': ['bad', 'bad']},
            ]}))
            catalog = AdCatalog(config)
            zone = ZoneInfo('Asia/Jakarta')
            at = lambda day, hour: datetime(2026, 10, day, hour, tzinfo=zone)
            self.assertEqual([x.ad_id for x in catalog.available('idle', at(17, 23))], ['night'])
            self.assertEqual([x.ad_id for x in catalog.available('idle', at(18, 5))], ['night'])
            self.assertFalse(catalog.available('idle', at(18, 6)))
            self.assertFalse(catalog.available('idle', at(19, 0)))
            self.assertEqual([x.ad_id for x in catalog.available('payment', at(18, 12))], ['payment'])

    def test_corrupt_configuration_and_nonfinite_timers_have_safe_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'broken.json'
            path.write_text('{interrupted')
            self.assertEqual(AdCatalog(path).available('idle'), [])
        timing = KioskTiming.from_config({'face_hold': float('nan'), 'landing_idle': float('inf')})
        self.assertEqual((timing.face_hold, timing.landing_idle, timing.offer_timeout), (5, 180, 15))

    def test_report_counts_actual_partial_and_completed_runs_without_faces(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'events.jsonl'
            log = AdEventLog(path)
            log.write('playback', ad_id='a', placement='idle', seconds=3.5, completed=False)
            log.write('playback', ad_id='a', placement='idle', seconds=20, completed=True)
            log.write('photo_entry', ad_id='a', placement='idle', source='face_prompt')
            with path.open('a') as output:
                output.write('{interrupted\n')
            self.assertEqual(summarize_events(path), [
                {'ad_id': 'a', 'placement': 'idle', 'plays': 2, 'completed': 1,
                 'displayed_seconds': 23.5, 'photo_entries': 1}])
            self.assertNotIn('face_id', path.read_text())

    def test_duplicate_identifiers_do_not_merge_distinct_creatives_in_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            Image.new('RGB', (8, 8)).save(root / 'poster.png')
            config = root / 'ads.json'
            config.write_text(json.dumps({'ads': [
                {'id': 'same', 'file': 'poster.png'},
                {'id': 'same', 'file': 'poster.png'},
            ]}))
            self.assertEqual(len(AdCatalog(config).items), 1)

    def test_nonfinite_and_nonplayback_events_do_not_pollute_report_totals(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'events.jsonl'
            path.write_text('\n'.join(json.dumps(row) for row in [
                {'event': 'playback', 'ad_id': 'bad', 'seconds': float('nan')},
                {'event': 'playback', 'ad_id': 'bad', 'seconds': float('inf')},
                {'event': 'diagnostic', 'ad_id': 'other'},
                {'event': 'playback', 'ad_id': 'good', 'seconds': 2},
            ]))
            self.assertEqual(summarize_events(path), [
                {'ad_id': 'good', 'placement': 'idle', 'plays': 1, 'completed': 0,
                 'displayed_seconds': 2.0, 'photo_entries': 0}])
