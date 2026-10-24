"""Shared DEMO amount math; a preview never authorizes real payment."""

from collections.abc import Mapping
from dataclasses import dataclass
from .game_engine import TARGET_SCORE

GAME_DISCOUNT = 2500


def is_demo_winner(record):
    return bool(isinstance(record, Mapping) and record.get('result') == 'won' and
                type(record.get('score')) is int and record['score'] >= TARGET_SCORE and
                isinstance(record.get('attempt_id'), str) and record['attempt_id'])


@dataclass(frozen=True)
class DemoAmount:
    subtotal: int
    discount: int
    total: int


def demo_amount(subtotal, eligible=False):
    if type(subtotal) is not int or subtotal < 0 or type(eligible) is not bool:
        raise ValueError('Invalid DEMO quote input')
    discount = min(GAME_DISCOUNT, subtotal) if eligible else 0
    return DemoAmount(subtotal, discount, subtotal-discount)
