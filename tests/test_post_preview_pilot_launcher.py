"""Safety checks for the explicitly synthetic real-camera/optional-paper pilot."""
import unittest
from pathlib import Path
import tempfile
from tools.run_post_preview_checkout_pilot import build_parser,validate_printer,validate_drive,validate_private_root


class PilotArgsTests(unittest.TestCase):
    def test_synthetic_payment_flag_is_mandatory(self):
        with self.assertRaises(SystemExit):
            build_parser().parse_args(['--private-root','new-empty-root'])
        args=build_parser().parse_args([
            '--private-root','new-empty-root','--synthetic-payment-only'])
        self.assertFalse(args.enable_real_printer)

    def test_real_printer_requires_both_explicit_optins(self):
        args=build_parser().parse_args([
            '--private-root','test','--synthetic-payment-only',
            '--enable-real-printer'])
        with self.assertRaises(ValueError):validate_printer(args,{})
        args.accept_real_paper=True
        with self.assertRaises(ValueError):validate_printer(args,{})
        validate_printer(args,{'PHOTOBOOTH_PRINTER_WINDOWS_NAME':'POS80'})

    def test_virtual_printer_requires_no_config(self):
        args=build_parser().parse_args([
            '--private-root','test','--synthetic-payment-only'])
        validate_printer(args,{})


    def test_real_drive_needs_separate_upload_consent_and_deployed_script(self):
        args=build_parser().parse_args([
            '--private-root','test','--synthetic-payment-only','--enable-real-drive'])
        with self.assertRaises(ValueError):validate_drive(args,{})
        args.accept_public_test_upload=True
        with self.assertRaises(ValueError):validate_drive(args,{})
        validate_drive(args,{
            'PHOTOBOOTH_WEB_APP_URL':'https://script.google.com/macros/s/TEST/exec',
            'PHOTOBOOTH_UPLOAD_TOKEN':'EXPLICIT_TEST_TOKEN'})
        with self.assertRaises(ValueError):
            validate_drive(args,{
                'PHOTOBOOTH_WEB_APP_URL':'https://example.org/macros/s/TEST/exec',
                'PHOTOBOOTH_UPLOAD_TOKEN':'EXPLICIT_TEST_TOKEN'})

    def test_virtual_drive_never_uses_external_credentials(self):
        args=build_parser().parse_args([
            '--private-root','test','--synthetic-payment-only'])
        validate_drive(args,{})

    def test_native_pilot_requires_explicit_live_worker_binding(self):
        import inspect
        from tools import run_post_preview_checkout_pilot as pilot
        source=inspect.getsource(pilot.main)
        self.assertIn('fixture.bind_app(self)',source)
        self.assertIn('class BoundPilotApp',source)

    def test_dedicated_private_root_never_reopens_customer_data(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            clean=root/'new-pilot'
            self.assertEqual(clean.resolve(),validate_private_root(clean,project_root=root/'repo'))
            clean.mkdir()
            self.assertEqual(clean.resolve(),validate_private_root(clean,project_root=root/'repo'))
            (clean/'drafts.sqlite3').write_bytes(b'prior paid customer')
            with self.assertRaisesRegex(ValueError,'occupied'):
                validate_private_root(clean,project_root=root/'repo')
            with self.assertRaisesRegex(ValueError,'parent directory'):
                validate_private_root(root,project_root=root/'repo')
            other=root/'OLD'/'saved'
            with self.assertRaises(ValueError):
                validate_private_root(other,project_root=root/'repo')
            link=root/'link'
            try: link.symlink_to(clean,target_is_directory=True)
            except (OSError,NotImplementedError): pass
            else:
                with self.assertRaises(ValueError):
                    validate_private_root(link,project_root=root/'repo')

    def test_pilot_does_not_accept_repository_or_home_as_data_root(self):
        import os
        with self.assertRaises(ValueError):
            validate_private_root(Path.home())
        with self.assertRaises(ValueError):
            validate_private_root(Path.cwd(),project_root=Path.cwd())
        with self.assertRaises(ValueError):
            validate_private_root(Path.cwd().parent,project_root=Path.cwd())


if __name__=='__main__':unittest.main()
