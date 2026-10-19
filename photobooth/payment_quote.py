"""FEAT-020 server-side order quotation rules, independent of the kiosk UI.

This pure module validates the complete customer order before any future
payment-provider request. The server must never trust a client-supplied total.
No payment gateway or credential is configured here.
"""

from dataclasses import dataclass
from collections.abc import Mapping
import re

from photobooth.catalog import PRICE_PER_SESSION, PRICE_PER_PRINT_COPY

_TEMPLATE_PATTERN = re.compile(r"template_[a-l]\\Z")


@dataclass(frozen=True)
class CheckoutQuote:
    session_count: int
    print_copy_count: int
    total_amount: int


def quote_checkout(quantities: Mapping[str, int]) -> CheckoutQuote:
    """Validate a bounded order and independently calculate its exact price."""
    if not isinstance(quantities, Mapping) or not quantities:
        raise ValueError("At least one template is required")
    if len(quantities) > 12:
        raise ValueError("Too many templates")
    copies = 0
    for template_id, count in quantities.items():
        if not isinstance(template_id, str) or not _TEMPLATE_PATTERN.fullmatch(template_id):
            raise ValueError("Unknown template ID")
        if type(count) is not int or count < 1 or count > 10:
            raise ValueError("Print copies must be an integer from 1 to 10")
        copies += count
    sessions = len(quantities)
    return CheckoutQuote(
        session_count=sessions,
        print_copy_count=copies,
        total_amount=sessions * PRICE_PER_SESSION + copies * PRICE_PER_PRINT_COPY,
    )
