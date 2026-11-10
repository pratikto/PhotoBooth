"""Original isolation financial SQL, shared without provider or mode authority.

Caller owns the original SQLite transaction/snapshot. Classification is not
fresh provider evidence, kernel ownership, ACK, media or refund permission.
"""
from photobooth.post_preview_store import DraftHeld


def original_financial_class(db, draft):
    intent=db.execute(
        'SELECT * FROM pp_checkout_intents WHERE draft_id=?',
        (draft['draft_id'],)).fetchone()
    if intent is None:
        return 'NO_PAYMENT'
    group=intent['purchase_group_id']
    finance=db.execute(
        'SELECT * FROM pp_purchase_finance WHERE purchase_group_id=?',
        (group,)).fetchone()
    if finance is None:
        return 'NO_PAYMENT'
    if finance['review_required']:
        raise DraftHeld('Unresolved financial discrepancy requires review')
    attempts=list(db.execute(
        'SELECT * FROM pp_payment_attempts WHERE purchase_group_id=?',(group,)))
    terminals={'CANCELLED_UNPAID','EXPIRED_UNPAID','TERMINAL_UNPAID','NOT_CREATED'}
    if finance['entitlement_id'] is None:
        if any(a['payment_state'] not in terminals for a in attempts):
            raise DraftHeld('PENDING/UNKNOWN payment cannot release booth')
        return 'TERMINAL_UNPAID'
    if (not attempts or any(a['payment_state'] not in terminals|{'PAID'} for a in attempts)
            or not finance['legitimate_paid_attempt']):
        raise DraftHeld('Original PAID attempt/other attempts need reconciliation')
    original=next((a for a in attempts if a['attempt_id']==finance['legitimate_paid_attempt']),None)
    if (not original or original['payment_state']!='PAID'
            or not original['provider_ref'] or original['verified_at'] is None):
        raise DraftHeld('Original independently verified paid attempt required')
    ccp=db.execute('SELECT offered_at FROM pp_ccp_credentials WHERE purchase_group_id=?',
                              (group,)).fetchone()
    if ccp is None or ccp['offered_at'] is None:
        raise DraftHeld('Customer original claim was never genuinely offered')
    ticket=db.execute(
        'SELECT receipt_state FROM pp_ticket_presentations WHERE purchase_group_id=?',(group,)).fetchone()
    if ticket and ticket['receipt_state'] in {'SENDING','UNCERTAIN'}:
        raise DraftHeld('Original ticket physical output requires classification')
    states=[row['state'] for row in db.execute(
        'SELECT state FROM pp_paid_strip_jobs WHERE purchase_group_id=?',(group,))]
    if any(state in {'SENDING','UNCERTAIN'} for state in states):
        raise DraftHeld('Original purchased photo physical output is uncertain')
    return 'PAID_OWED'
