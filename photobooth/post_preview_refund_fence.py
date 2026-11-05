"""A mock full-refund intent fences original fulfillment, never money authority."""
from photobooth.post_preview_store import DraftHeld


def deny_full_mock_refund_fulfillment(ledger,group):
    if ledger.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='pp_mock_refund_intents'").fetchone():
        if ledger.db.execute("SELECT 1 FROM pp_mock_refund_intents WHERE purchase_group_id=? AND kind='FULL'",(group,)).fetchone():
            raise DraftHeld('Original fulfillment is quarantined by a mock full-refund intent')
