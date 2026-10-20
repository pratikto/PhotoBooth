"""QR download boundary tests: no external image or provider requests."""
import io
import unittest
from unittest.mock import patch
from PIL import Image
from photobooth.qris_images import payment_qr_image

URL = 'https://api.sandbox.midtrans.com/v2/qris/verified-transaction/qr-code'


class ImageResponse:
    def __init__(self, chunks, status=200):
        self.chunks, self.status_code, self.reads = chunks, status, 0
    def __enter__(self): return self
    def __exit__(self, *_): pass
    def iter_content(self, size):
        for chunk in self.chunks:
            self.reads += 1
            yield chunk


class QrisImageTests(unittest.TestCase):
    def test_verified_image_is_displayed_not_url_reencoded(self):
        original = Image.new('RGB', (100,100), 'white')
        original.putpixel((50,50), (0,0,0))
        stream=io.BytesIO(); original.save(stream, format='PNG')
        response=ImageResponse([stream.getvalue()])
        with patch('photobooth.qris_images.requests.get', return_value=response) as get:
            result=payment_qr_image({'mode':'sandbox','qr_url':URL})
        self.assertEqual(result.tobytes(), original.tobytes())
        self.assertFalse(get.call_args.kwargs['allow_redirects'])
        self.assertTrue(get.call_args.kwargs['stream'])

    def test_external_origin_is_rejected_before_network(self):
        with patch('photobooth.qris_images.requests.get') as get:
            with self.assertRaises(ValueError):
                payment_qr_image({'mode':'sandbox','qr_url':'https://example.test/qr'})
        get.assert_not_called()

    def test_redirect_is_rejected_before_read(self):
        response=ImageResponse([b'do not read'], status=302)
        with patch('photobooth.qris_images.requests.get', return_value=response):
            with self.assertRaises(ValueError): payment_qr_image({'mode':'sandbox','qr_url':URL})
        self.assertEqual(response.reads, 0)

    def test_stream_stops_at_byte_limit(self):
        response=ImageResponse([b'x' * 300000] * 10)
        with patch('photobooth.qris_images.requests.get', return_value=response):
            with self.assertRaises(ValueError): payment_qr_image({'mode':'sandbox','qr_url':URL})
        self.assertEqual(response.reads, 2)

    def test_extreme_dimensions_rejected(self):
        stream=io.BytesIO(); Image.new('RGB',(3000,10)).save(stream, format='PNG')
        with patch('photobooth.qris_images.requests.get', return_value=ImageResponse([stream.getvalue()])):
            with self.assertRaises(ValueError): payment_qr_image({'mode':'sandbox','qr_url':URL})
