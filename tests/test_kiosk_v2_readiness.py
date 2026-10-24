"""Preflight preserves unknown hardware and excludes credential/customer data."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from photobooth.kiosk_v2.readiness import inventory, BRANCH, windows_display


class ReadinessTests(unittest.TestCase):
    def report(self,env):
        def git(root,*args):
            return {'branch':BRANCH,'rev-parse':'a'*40,'status':''}[args[0]]
        with patch('photobooth.kiosk_v2.readiness.git_value',side_effect=git),patch(
                'photobooth.kiosk_v2.readiness.importlib.metadata.version',return_value='1.0'):
            return inventory(Path('/tmp'),env=env,display={'resolution':None,'scaling_percent':None})
    def test_unknown_device_does_not_become_pass(self):
        report=self.report({})
        self.assertIsNone(report['device']['camera_model'])
        self.assertIsNone(report['device']['display']['resolution'])
        self.assertEqual(set(report['acceptance'].values()),{'NOT_RUN'})
        self.assertEqual(report['preflight']['status'],'READY_FOR_MANUAL_TEST')
    def test_no_env_values_are_disclosed_and_conflicting_modes_fail(self):
        report=self.report({'MIDTRANS_SERVER_KEY':'secret-key-value','MEONG_QRIS_BOOTH_TOKEN':'secret-token-value',
            'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'1','PHOTOBOOTH_V2_CHECKOUT_MOCK':'1','MEONG_QRIS_MODE':'production'})
        text=json.dumps(report)
        self.assertNotIn('secret-key-value',text);self.assertNotIn('secret-token-value',text)
        self.assertEqual(report['preflight']['status'],'NEEDS_ATTENTION')
        self.assertFalse(report['preflight']['checks']['checkout_mode_exclusive'])
        self.assertFalse(report['preflight']['checks']['gui_merchant_credentials_absent'])
    def test_invalid_camera_index_is_not_silently_changed(self):
        report=self.report({'PHOTOBOOTH_CAMERA_INDEX':'wrong'})
        self.assertIsNone(report['device']['camera_index'])
        self.assertFalse(report['preflight']['checks']['camera_index_valid'])
    def test_non_windows_does_not_invent_resolution(self):
        with patch('photobooth.kiosk_v2.readiness.platform.system',return_value='Linux'):
            self.assertIsNone(windows_display()['resolution'])
