"""AR-06 original ticket memory, private reboot and trusted resume-permit seam."""
import json
from pathlib import Path
import tempfile
import unittest

from photobooth.booth_auth import BoothAuthenticator
from photobooth.qris_api import create_app
from photobooth.qris_kiosk_client import QrisKioskClient
from photobooth.qris_session import KioskCheckout
from photobooth.resume_authority import ResumePermit
from tests.qris_v2_fixture import Fixture,InProcessSession


class CustomerClaimSessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.fixture=Fixture(self.root);self.addCleanup(self.fixture.close)

    def reopen(self):
        self.fixture.flow.close()
        client=QrisKioskClient('http://127.0.0.1:8765','PB001','a'*48,allow_local_http=True,
            session=InProcessSession(create_app(self.fixture.backend,BoothAuthenticator({'PB001':'a'*48}))))
        flow=KioskCheckout(self.root/'visit.json',client,mode='sandbox',booth_id='PB001',endpoint=client.base_url)
        self.addCleanup(flow.close)
        return flow

    def test_original_ticket_is_memory_only_and_cannot_be_redisplayed_after_restart(self):
        self.fixture.service.begin({'template_a':1})
        ticket=self.fixture.flow.customer_ticket()
        self.assertTrue(ticket.startswith('MEONG-RECOVERY-V1:PB001:'))
        secret=ticket.split(':')[-1]
        self.assertNotIn(secret,(self.root/'visit.json').read_text())
        self.assertNotIn(secret,str(self.fixture.flow.snapshot()))
        reopened=self.reopen()
        self.assertIsNone(reopened.customer_ticket())
        self.assertTrue(reopened.customer_claim_required)

    def test_rebooted_reserved_order_cannot_prepare_without_original_customer_proof(self):
        self.fixture.service.begin({'template_a':1});self.fixture.paid();self.fixture.service.check()
        reopened=self.reopen()
        with self.assertRaises(RuntimeError):reopened.prepare_capture()
        self.assertEqual(reopened.snapshot()['phase'],'RESERVED')

    def test_original_claim_reuses_binding_and_issues_one_short_lived_restore_permit(self):
        self.fixture.service.begin({'template_a':1});ticket=self.fixture.flow.customer_ticket()
        self.fixture.paid();self.fixture.service.check();self.fixture.service.prepare()
        tx=self.fixture.flow.snapshot()['transaction_id'];self.fixture.service.started(tx)
        reopened=self.reopen();reopened.refresh()
        with self.assertRaises(RuntimeError):reopened.resume_permit()
        reopened.customer_claim(ticket)
        permit=reopened.resume_permit()
        self.assertIsInstance(permit,ResumePermit)
        self.assertEqual(reopened.resume_binding()['transaction_id'],tx)
        self.assertNotIn(ticket.split(':')[-1],(self.root/'visit.json').read_text())
        with self.assertRaises(RuntimeError):reopened.resume_permit()

    def test_wrong_ticket_never_changes_original_order_or_grant(self):
        self.fixture.service.begin({'template_a':1});ticket=self.fixture.flow.customer_ticket()
        reopened=self.reopen();before=reopened.snapshot()
        with self.assertRaises(ValueError):reopened.customer_claim(ticket.replace(':PB001:',':PB002:'))
        self.assertEqual(reopened.snapshot(),before)

    def test_pending_owner_proof_can_restore_payment_qr_but_never_media_permit(self):
        self.fixture.service.begin({'template_a':1});ticket=self.fixture.flow.customer_ticket()
        reopened=self.reopen();view=reopened.customer_claim(ticket)
        self.assertEqual(view['phase'],'WAITING')
        self.assertIsNone(view['order']['grant_id'])
        self.assertFalse(view['order']['customer_claim']['payment_verified'])
        with self.assertRaises(RuntimeError):reopened.resume_permit()

    def test_privacy_lock_fences_a_late_customer_claim_callback(self):
        from concurrent.futures import ThreadPoolExecutor
        import threading
        from unittest.mock import patch
        self.fixture.service.begin({'template_a':1});ticket=self.fixture.flow.customer_ticket()
        self.fixture.paid();self.fixture.service.check()
        reopened=self.reopen();entered,release=threading.Event(),threading.Event()
        original=reopened.client.customer_claim
        def slow(*args):
            entered.set();release.wait(3);return original(*args)
        with patch.object(reopened.client,'customer_claim',side_effect=slow),ThreadPoolExecutor(max_workers=1) as pool:
            result=pool.submit(reopened.customer_claim,ticket)
            try:
                self.assertTrue(entered.wait(1));reopened.lock_customer()
            finally:release.set()
            with self.assertRaises(RuntimeError):result.result(3)
        self.assertTrue(reopened.customer_claim_required)
        with self.assertRaises(RuntimeError):reopened.resume_permit()

    def allocated_reopen(self):
        self.fixture.service.begin({'template_a':1});ticket=self.fixture.flow.customer_ticket()
        self.fixture.paid();self.fixture.service.check();self.fixture.service.prepare()
        tx=self.fixture.flow.snapshot()['transaction_id'];self.fixture.service.started(tx)
        reopened=self.reopen();reopened.customer_claim(ticket)
        return reopened,ticket,tx

    def test_privacy_lock_revokes_already_issued_resume_permit(self):
        reopened,ticket,tx=self.allocated_reopen()
        binding=reopened.resume_binding();permit=reopened.resume_permit()
        reopened.lock_customer()
        with self.assertRaises(RuntimeError):permit.consume(binding)
        reopened.customer_claim(ticket)
        reopened.resume_permit().consume(binding)

    def test_resume_ack_reuses_original_started_binding_and_rechecks_payment(self):
        reopened,ticket,tx=self.allocated_reopen()
        with self.assertRaises(RuntimeError):reopened.confirm_resume('other_tx','capture')
        view=reopened.confirm_resume(tx,'capture')
        self.assertEqual(view['phase'],'STARTED')
        self.assertEqual(view['transaction_id'],tx)
        self.fixture.provider.rows[view['order']['order_id']].update(transaction_status='refund')
        with self.assertRaises(Exception):reopened.confirm_resume(tx,'capture')

    def test_completed_service_can_restore_result_only_without_capture_readmission(self):
        reopened,ticket,tx=self.allocated_reopen()
        oid=reopened.snapshot()['order']['order_id'];grant=reopened.snapshot()['order']['grant_id']
        self.fixture.backend.service_transition(oid,'PB001',grant,'COMPLETED',tx)
        reopened.customer_claim(ticket)
        with self.assertRaises(RuntimeError):reopened.confirm_resume(tx,'capture')
        view=reopened.confirm_resume(tx,'result')
        self.assertEqual(view['order']['service_state'],'COMPLETED')
        self.assertEqual(view['phase'],'STARTED')
