"""Single-use and restart evidence for local DEMO inputs, never real receipts."""

from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
import threading
import time
import unittest

from photobooth.kiosk_v2.demo_game import DemoClaimError, DemoGameStore, GameJobs


class DemoGameTests(unittest.TestCase):
    def test_claim_is_durable_before_game_and_never_reset_by_restart_or_outcome(self):
        with TemporaryDirectory() as root:
            store = DemoGameStore(root)
            started = store.claim(' demo-sample-1 ')
            self.assertEqual(started['result'], 'started')
            with self.assertRaisesRegex(DemoClaimError, 'used'):
                DemoGameStore(root).claim('DEMO-SAMPLE-1')
            result = store.finish(started['attempt_id'], 'won', 10)
            self.assertEqual(result['result'], 'won')
            with self.assertRaisesRegex(DemoClaimError, 'used'):
                DemoGameStore(root).claim('DEMO-SAMPLE-1')

    def test_concurrent_claim_allows_exactly_one_attempt(self):
        with TemporaryDirectory() as root:
            store = DemoGameStore(root)
            def claim(_):
                try:
                    return store.claim('DEMO-RACE')['attempt_id']
                except DemoClaimError:
                    return None
            with ThreadPoolExecutor(max_workers=8) as pool:
                self.assertEqual(sum(item is not None for item in pool.map(claim, range(16))), 1)

    def test_invalid_real_or_empty_tokens_never_create_attempts(self):
        with TemporaryDirectory() as root:
            store = DemoGameStore(root)
            for token in (None, '', 'DEMO-', 'CAFE-123', 'https://partner/receipt', 'DEMO-<tag>', 'DEMO-'+'X'*65):
                with self.subTest(token=token), self.assertRaisesRegex(DemoClaimError, 'invalid'):
                    store.claim(token)

    def test_terminal_result_is_idempotent_and_cannot_be_rewritten(self):
        with TemporaryDirectory() as root:
            store = DemoGameStore(root)
            attempt = store.claim('DEMO-LOSE')['attempt_id']
            first = store.finish(attempt, 'lost', 2)
            self.assertEqual(store.finish(attempt, 'lost', 2), first)
            with self.assertRaisesRegex(DemoClaimError, 'conflicting-result'):
                store.finish(attempt, 'won', 10)
            self.assertEqual(store.get(attempt)['result'], 'lost')

    def test_false_win_and_missing_attempt_fail_closed(self):
        with TemporaryDirectory() as root:
            store = DemoGameStore(root)
            attempt = store.claim('DEMO-RESULT')['attempt_id']
            for result, score in (('won', 9), ('lost', 10), ('won', True), ('paid', 10)):
                with self.assertRaises(DemoClaimError):
                    store.finish(attempt, result, score)
            with self.assertRaises(DemoClaimError):
                store.finish('unknown', 'lost', 0)
            self.assertEqual(store.get(attempt)['result'], 'started')

    def test_abandonment_does_not_restore_a_consumed_code(self):
        with TemporaryDirectory() as root:
            store = DemoGameStore(root)
            attempt = store.claim('DEMO-EXIT')['attempt_id']
            store.finish(attempt, 'abandoned', 1)
            with self.assertRaises(DemoClaimError):
                store.claim('DEMO-EXIT')

    def test_slow_claim_never_blocks_gui_or_queues_a_second_tap_and_close_discards_callback(self):
        entered, release = threading.Event(), threading.Event()
        with TemporaryDirectory() as root:
            store = DemoGameStore(root)
            def factory():
                entered.set(); release.wait(2)
                return store
            jobs = GameJobs(factory)
            try:
                before = time.monotonic()
                self.assertTrue(jobs.submit('claim', 3, 'DEMO-WORKER'))
                self.assertLess(time.monotonic()-before, .1)
                self.assertTrue(entered.wait(1))
                self.assertFalse(jobs.submit('claim', 3, 'DEMO-SECOND'))
                self.assertIsNone(jobs.poll())
                jobs.close();release.set();jobs.wait_closed()
                self.assertIsNone(jobs.poll())
                self.assertFalse(jobs.submit('claim', 4, 'DEMO-SECOND'))
                with self.assertRaises(DemoClaimError):
                    store.claim('DEMO-WORKER')
            finally:
                release.set();jobs.close();jobs.wait_closed()

    def test_poll_returns_revision_and_storage_failures_without_inventing_a_claim(self):
        def unavailable():
            raise OSError('read-only')
        jobs = GameJobs(unavailable)
        try:
            self.assertTrue(jobs.submit('claim', 12, 'DEMO-FAIL'))
            jobs.wait_closed()
            result = jobs.poll()
            self.assertEqual((result.revision,result.action,result.error), (12,'claim','unavailable'))
            self.assertIsNone(result.value)
            self.assertFalse(jobs.busy)
        finally:
            jobs.close()


if __name__ == '__main__':
    unittest.main()
