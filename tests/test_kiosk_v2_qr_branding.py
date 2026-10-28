"""Offline pixel checks: a center logo cannot alter a provider's QR payload."""
import io
import sys
import unittest
from unittest.mock import patch

import cv2
import numpy as np
from PIL import Image
import qrcode

from photobooth.kiosk_v2.qr_branding import branded_sandbox_qr_image, with_meong_logo
from photobooth.qr_code import create_qr_image
from tests.test_qris_images import ImageResponse, URL


PAYLOAD = 'MEONG OFFLINE HTTP FIXTURE - NOT PAYABLE'
DENSE_PAYLOAD = 'MEONG TEST ONLY - NOT PAYABLE | ' + '0123456789' * 16


class SandboxQrBrandingTests(unittest.TestCase):
    def decoded(self, image):
        return cv2.QRCodeDetector().detectAndDecode(np.asarray(image.convert('RGB')))[0]

    def test_centered_meong_art_and_exact_payload_at_full_and_compact_sizes(self):
        for payload in (PAYLOAD, DENSE_PAYLOAD,
                        'MEONG TEST ONLY - NOT PAYABLE | ' + '0123456789' * 28):
            with self.subTest(characters=len(payload)):
                original = create_qr_image(payload, with_logo=False)
                before = original.tobytes()
                branded = with_meong_logo(original)
                self.assertEqual(original.tobytes(), before)
                self.assertEqual(self.decoded(original), payload)
                pixels = np.asarray(branded)
                color = (pixels[:, :, 0] != pixels[:, :, 1]) | (pixels[:, :, 1] != pixels[:, :, 2])
                ys, xs = np.where(color)
                self.assertGreater(len(xs), 0, 'The full approved Meong insert must be visible')
                self.assertTrue(np.all((xs > branded.width * .3) & (xs < branded.width * .7)))
                self.assertTrue(np.all((ys > branded.height * .35) & (ys < branded.height * .65)))
                for size in (branded.width, 180, 260):
                    displayed = branded.resize((size, size), Image.Resampling.NEAREST)
                    self.assertEqual(self.decoded(displayed), payload)

    def test_downloaded_payload_is_branded_instead_of_encoding_its_image_url(self):
        original = create_qr_image(PAYLOAD, with_logo=False)
        stream = io.BytesIO()
        original.save(stream, format='PNG')
        with patch('photobooth.qris_images.requests.get',
                   return_value=ImageResponse([stream.getvalue()])) as request:
            branded = branded_sandbox_qr_image({'mode': 'sandbox', 'qr_url': URL})
        self.assertEqual(self.decoded(branded), PAYLOAD)
        self.assertNotEqual(self.decoded(branded), URL)
        request.assert_called_once()
        self.assertFalse(request.call_args.kwargs['allow_redirects'])

    def test_unreadable_original_is_retained_without_creating_a_substitute(self):
        original = Image.new('RGB', (100, 100), 'white')
        with patch('photobooth.qr_code.create_qr_image') as render:
            self.assertIs(with_meong_logo(original), original)
        render.assert_not_called()

    def test_significant_whitespace_is_not_trimmed_or_reencoded(self):
        payload = ' ' + PAYLOAD + ' '
        original = qrcode.make(payload).convert('RGB')
        self.assertEqual(self.decoded(original), payload)
        with patch('photobooth.qr_code.create_qr_image') as render:
            self.assertIs(with_meong_logo(original), original)
        render.assert_not_called()

    def test_asset_or_renderer_failure_retains_original_pixels(self):
        original = create_qr_image(PAYLOAD, with_logo=False)
        before = original.tobytes()
        for error in (FileNotFoundError('fixture artwork absent'), ValueError('fixture unreadable')):
            with self.subTest(error=type(error).__name__), \
                 patch('photobooth.qr_code.create_qr_image', side_effect=error):
                self.assertIs(with_meong_logo(original), original)
                self.assertEqual(original.tobytes(), before)

    def test_wrong_or_unreadable_rendered_payload_retains_original(self):
        original = create_qr_image(PAYLOAD, with_logo=False)
        wrong = create_qr_image('OTHER NONPAYABLE FIXTURE', with_logo=False)
        for candidate in (wrong, Image.new('RGB', original.size, 'white')):
            with patch('photobooth.qr_code.create_qr_image', return_value=candidate):
                self.assertIs(with_meong_logo(original), original)

    def test_optional_decoder_unavailable_keeps_original(self):
        original = create_qr_image(PAYLOAD, with_logo=False)
        with patch.dict(sys.modules, {'cv2': None}):
            self.assertIs(with_meong_logo(original), original)

    def test_mock_marker_stays_plain_and_is_not_admitted_to_sandbox_branding(self):
        order = {'mode': 'mock', 'qr_payload': 'MEONG MOCK ONLY - NOT QRIS - fixture'}
        with patch('photobooth.kiosk_v2.qr_branding.with_meong_logo') as brand:
            original = branded_sandbox_qr_image(order)
        brand.assert_not_called()
        self.assertEqual(self.decoded(original), order['qr_payload'])

    def test_download_failure_remains_an_image_failure_not_a_fake_qr(self):
        with patch('photobooth.kiosk_v2.qr_branding.payment_qr_image', side_effect=TimeoutError):
            with self.assertRaises(TimeoutError):
                branded_sandbox_qr_image({'mode': 'sandbox', 'qr_url': URL})


if __name__ == '__main__':
    unittest.main()
