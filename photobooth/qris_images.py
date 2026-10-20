"""Bounded QR image decoding; never turn a provider URL into a payment QR."""
import io
import requests
from PIL import Image
from photobooth.qris_evidence import sandbox_qr_url


def payment_qr_image(order):
    if order['mode'] == 'mock':
        from photobooth.qr_code import create_qr_image
        payload = order.get('qr_payload', '')
        if not payload.startswith('MEONG MOCK ONLY - NOT QRIS - '):
            raise ValueError('Invalid mock QR marker')
        return create_qr_image(payload, with_logo=False)
    url = sandbox_qr_url(order['qr_url'])
    with requests.get(url, timeout=6, allow_redirects=False, stream=True) as response:
        if response.status_code != 200:
            raise ValueError('Sandbox QR image unavailable')
        content = bytearray()
        for chunk in response.iter_content(4096):
            if len(content) + len(chunk) > 512 * 1024:
                raise ValueError('Sandbox QR image too large')
            content.extend(chunk)
    with Image.open(io.BytesIO(content)) as image:
        if image.width > 2048 or image.height > 2048 or image.width < 21 or image.height < 21:
            raise ValueError('Unexpected QR image dimensions')
        return image.convert('RGB')
