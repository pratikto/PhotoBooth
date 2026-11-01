"""No active-photo hard deadline; phase-specific warning and expiry observations."""
from dataclasses import replace
import unittest
from photobooth.kiosk_v2.post_preview_idle import PrivateInactivityPolicy


class PrivateInactivityTests(unittest.TestCase):
    def test_each_phase_warns_before_its_own_configured_expiry(self):
        policy = PrivateInactivityPolicy()
        for phase, limit in (('templates', 90), ('confirm', 90), ('capture', 120),
                             ('review', 120), ('result', 120), ('final_preview', 120)):
            with self.subTest(phase=phase):
                self.assertEqual('NONE', policy.decision(phase, limit-16))
                self.assertEqual('WARNING', policy.decision(phase, limit-15))
                self.assertEqual('EXPIRED', policy.decision(phase, limit))

    def test_legitimate_countdown_and_slow_worker_have_no_hard_visit_cutoff(self):
        policy = PrivateInactivityPolicy()
        for phase in ('capture', 'review', 'result', 'final_preview'):
            self.assertEqual('ACTIVE_WORK', policy.decision(phase, 100000, worker_busy=True))
            self.assertEqual('ACTIVE_WORK', policy.decision(phase, 100000, countdown_active=True))

    def test_pilot_values_are_configurable_without_touching_financial_state(self):
        policy = replace(PrivateInactivityPolicy(), gallery_seconds=180)
        self.assertEqual('NONE', policy.decision('templates', 120))
        self.assertEqual('EXPIRED', policy.decision('review', 120))
        self.assertEqual('NONE', policy.decision('payment_unknown', 100000))

    def test_invalid_or_nonfinite_policy_clock_is_rejected(self):
        for value in (True, float('inf'), float('nan'), '120'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                PrivateInactivityPolicy().decision('capture', value)
        with self.assertRaises(ValueError): replace(PrivateInactivityPolicy(), warning_seconds=120)


if __name__ == '__main__': unittest.main()
