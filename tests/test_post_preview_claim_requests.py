"""Original claim request survives lost replies; occupancy and proof stay scoped."""
import hashlib
import sqlite3
import unittest
import uuid
from unittest.mock import patch

from photobooth.post_preview_sandbox_handoff import OriginalSandboxClaim
from photobooth.post_preview_store import DraftHeld
from tests.post_preview_handoff_fixture import ProtectedHandoffHarness


class ProtectedClaimRequestTests(unittest.TestCase):
    def fixture(self, *, release=True):
        self.h=ProtectedHandoffHarness(self)
        self.f=self.h.f
        self.request=uuid.uuid4().hex
        if release:
            op=self.h.prepare();self.h.ack(op)
        return self.h

    def call(self, request=None, proof=None, actor=None):
        self.f.clock[0]+=2
        return (actor or self.h.claim).claim_once(self.request if request is None else request,
            self.f.group,'PB001',self.h.proof if proof is None else proof)

    def test_lost_original_response_replays_same_lease_and_only_one_claim_after_reopen(self):
        h=self.fixture();first=self.call()
        reopened=OriginalSandboxClaim(h.payments,h.claim.ccp,h.claim.ticket)
        for _ in range(2):
            self.assertEqual(first,self.call(actor=reopened))
        self.assertEqual(4,first['lease'].generation)
        self.assertEqual(1,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_protected_claim_ops').fetchone()[0])
        self.assertEqual(1,self.f.ledger.db.execute("SELECT COUNT(*) FROM pp_events WHERE event='ORIGINAL_PAID_CLAIM_REACQUIRED'").fetchone()[0])
        self.assertEqual(1,self.f.remote.charges);self.assertEqual(1,len(self.f.sends))

    def test_request_is_durable_before_provider_get_and_contains_no_plaintext_proof(self):
        h=self.fixture();original=h.payments.provider.get_status;seen=[]
        def get(order):
            row=self.f.ledger.db.execute('SELECT * FROM pp_protected_claim_ops WHERE request_id=?',(self.request,)).fetchone()
            self.assertEqual('PREPARED',row['state'])
            seen.append(True)
            return original(order)
        with patch.object(h.payments.provider,'get_status',side_effect=get):self.call()
        self.assertTrue(seen)
        row=self.f.ledger.db.execute('SELECT * FROM pp_protected_claim_ops').fetchone()
        self.assertEqual(hashlib.sha256(h.proof.encode()).hexdigest(),row['proof_sha256'])
        self.assertFalse(h.proof in str(dict(row)))
        for suffix in ('','-wal'):
            path=self.f.root/('drafts.sqlite3'+suffix)
            if path.exists():self.assertFalse(h.proof.encode() in path.read_bytes(),'Raw customer proof must not persist')

    def test_busy_request_stays_prepared_and_can_retry_after_original_safe_ack(self):
        h=self.fixture(release=False)
        self.assertEqual('WAIT',self.call()['state'])
        self.assertEqual('PREPARED',self.f.ledger.db.execute('SELECT state FROM pp_protected_claim_ops').fetchone()[0])
        op=h.prepare();h.ack(op)
        self.assertEqual('REACQUIRED',self.call()['state'])
        self.assertEqual(1,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_protected_claim_ops').fetchone()[0])

    def test_record_failure_rolls_back_both_occupancy_and_original_request_result(self):
        h=self.fixture();original=h.claim._record_reacquired
        def failed(result):original(result);raise OSError('Synthetic commit failure')
        with patch.object(h.claim,'_record_reacquired',side_effect=failed),self.assertRaises(OSError):self.call()
        draft=self.f.ledger.db.execute('SELECT closed,generation FROM pp_drafts').fetchone()
        self.assertEqual((1,3),tuple(draft))
        self.assertEqual('PREPARED',self.f.ledger.db.execute('SELECT state FROM pp_protected_claim_ops').fetchone()[0])
        self.assertEqual('REACQUIRED',self.call()['state'])

    def test_same_request_cannot_be_rebound_even_to_another_valid_original_proof_role(self):
        h=self.fixture();self.call()
        with self.assertRaises(PermissionError):self.call(proof=h.ticket_proof)
        self.assertEqual(4,self.f.ledger.db.execute('SELECT generation FROM pp_drafts').fetchone()[0])

    def test_unknown_or_invalid_proof_does_not_create_a_request(self):
        h=self.fixture()
        for proof in ('MEONG:QRIS:1:fake',h.proof[:-1]+('A' if h.proof[-1]!='A' else 'B')):
            with self.assertRaises(PermissionError):self.call(proof=proof)
        with self.assertRaises(ValueError):self.call(request='invalid')
        self.assertEqual(0,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_protected_claim_ops').fetchone()[0])

    def test_provider_outage_on_replay_keeps_same_grant_and_owed_without_a_second_claim(self):
        h=self.fixture();first=self.call();self.f.remote.outage=True
        with self.assertRaises(DraftHeld):self.call()
        self.assertEqual(first['lease'].generation,self.f.ledger.db.execute('SELECT generation FROM pp_drafts').fetchone()[0])
        self.assertEqual('OWED',self.f.ledger.db.execute('SELECT status FROM pp_paid_services').fetchone()[0])

    def test_replay_cannot_resurrect_a_superseded_generation(self):
        h=self.fixture();self.call()
        # Deliberate stale-occupancy fault, not a claim of safe B admission.
        self.f.ledger.db.execute('UPDATE pp_drafts SET generation=generation+1')
        reads=self.f.remote.reads
        self.f.remote.outage=True
        result=self.call()
        self.assertEqual('WAIT',result['state']);self.assertIsNone(result['lease'])
        self.assertEqual(reads,self.f.remote.reads)
        self.assertEqual(5,self.f.ledger.db.execute('SELECT generation FROM pp_drafts').fetchone()[0])

    def test_successful_original_request_identity_and_lease_cannot_be_rewritten(self):
        h=self.fixture();self.call()
        for sql in ("UPDATE pp_protected_claim_ops SET proof_sha256='"+'0'*64+"'",
                    'UPDATE pp_protected_claim_ops SET generation=99','DELETE FROM pp_protected_claim_ops'):
            with self.assertRaises(sqlite3.IntegrityError):self.f.ledger.db.execute(sql)
        self.assertEqual(4,self.call()['lease'].generation)

    def test_owed_finance_cannot_replay_a_review_required_original_delivery(self):
        h=self.fixture();self.call()
        self.f.ledger.db.execute("UPDATE pp_paid_services SET status='REVIEW'")
        with self.assertRaises(DraftHeld):self.call()
        self.assertEqual(4,self.f.ledger.db.execute('SELECT generation FROM pp_drafts').fetchone()[0])

    def test_partial_existing_request_schema_holds_without_repair_or_occupancy_change(self):
        h=self.fixture()
        self.f.ledger.db.execute('ALTER TABLE pp_protected_claim_ops ADD COLUMN foreign_grant TEXT')
        with self.assertRaises(DraftHeld):OriginalSandboxClaim(h.payments,h.claim.ccp,h.claim.ticket)
        self.assertEqual((1,3),tuple(self.f.ledger.db.execute('SELECT closed,generation FROM pp_drafts').fetchone()))
        self.assertEqual(0,self.f.ledger.db.execute('SELECT COUNT(*) FROM pp_protected_claim_ops').fetchone()[0])


if __name__=='__main__':unittest.main()
