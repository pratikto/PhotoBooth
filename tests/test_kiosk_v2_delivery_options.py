"""Explicit hardware/storage opt-ins, without importing Kivy or opening devices."""
from contextlib import redirect_stderr, redirect_stdout
import io
import unittest

from photobooth.kiosk_v2.delivery_options import configure_delivery


class DeliveryOptionsTests(unittest.TestCase):
    def test_default_and_flags_preserve_existing_private_configuration(self):
        env={'PHOTOBOOTH_UPLOAD_TOKEN':'PRIVATE','UNRELATED':'unchanged'}
        before=dict(env);configure_delivery((),environ=env);self.assertEqual(env,before)
        configure_delivery(['--print','--drive'],environ=env)
        self.assertEqual(env['PHOTOBOOTH_V2_PRINT'],'1')
        self.assertEqual(env['PHOTOBOOTH_V2_AUTO_PRINT'],'1')
        self.assertEqual(env['PHOTOBOOTH_V2_DRIVE'],'1')
        self.assertEqual(env['PHOTOBOOTH_UPLOAD_TOKEN'],'PRIVATE')
        self.assertEqual(env['UNRELATED'],'unchanged')
    def test_manual_operator_print_remains_explicit(self):
        env={};configure_delivery(['--print','--manual-print'],environ=env)
        self.assertEqual(env['PHOTOBOOTH_V2_PRINT'],'1')
        self.assertEqual(env['PHOTOBOOTH_V2_AUTO_PRINT'],'0')
        with redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
            configure_delivery(['--manual-print'],environ={})
    def test_merchant_trial_cannot_enable_print_or_drive_or_leak_config(self):
        for flags in (['--print'],['--drive']):
            env={'PHOTOBOOTH_V2_CHECKOUT_SANDBOX':'1','PHOTOBOOTH_UPLOAD_TOKEN':'PRIVATE'}
            before=dict(env);output=io.StringIO()
            with redirect_stderr(output),self.assertRaises(SystemExit):
                configure_delivery(flags,environ=env)
            self.assertEqual(env,before);self.assertNotIn('PRIVATE',output.getvalue())
    def test_help_explains_existing_settings_without_starting_gui(self):
        env={};output=io.StringIO()
        with redirect_stdout(output),self.assertRaises(SystemExit) as result:
            configure_delivery(['--help'],environ=env)
        self.assertEqual(result.exception.code,0);self.assertEqual(env,{})
        self.assertIn('saved v1 printer settings',output.getvalue())
