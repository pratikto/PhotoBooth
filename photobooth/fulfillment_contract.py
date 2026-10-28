"""Frozen server quote and exact template-byte identity; no customer media."""
import hashlib

from photobooth.catalog import get_templates, PRICE_PER_SESSION, PRICE_PER_PRINT_COPY
from photobooth.payment_quote import quote_checkout


def frozen_contract(quantities):
    quote = quote_checkout(quantities)
    templates = []
    for template in get_templates():
        if template.template_id not in quantities:
            continue
        templates.append({'template_id': template.template_id, 'name': template.name,
            'source_id': template.source_id, 'copies': quantities[template.template_id],
            'artwork_sha256': hashlib.sha256(template.artwork_path.read_bytes()).hexdigest(),
            'qr_box': list(template.qr_box),
            'apertures': [{'box': list(a.box), 'shape': a.shape,
                           'mask_sha256': hashlib.sha256(a.mask_path.read_bytes()).hexdigest()}
                          for a in template.apertures]})
    return {'version': 1, 'currency': 'IDR', 'amount': quote.total_amount,
            'session_fee': PRICE_PER_SESSION, 'per_copy_fee': PRICE_PER_PRINT_COPY,
            'session_count': quote.session_count, 'print_copy_count': quote.print_copy_count,
            'quantities': dict(quantities), 'templates': templates}
