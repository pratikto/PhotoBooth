"""Safety checks for the explicitly synthetic real-camera/optional-paper pilot."""
import unittest
from tools.run_post_preview_checkout_pilot import build_parser,validate_printer


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


if __name__=='__main__':unittest.main()
