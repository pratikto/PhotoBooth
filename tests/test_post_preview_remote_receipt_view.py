"""Native clock/NEXT stay responsive during original backend receipt transport."""
import threading
import unittest
from unittest.mock import patch
from kivy.base import EventLoop
from kivy.core.window import Window
from photobooth.kiosk_v2.post_preview_remote_ticket import RemoteRecoveryTicketSession
from photobooth.post_preview_client import PostPreviewClient
from photobooth.post_preview_proof_client import PostPreviewRecoveryClient
from tests import test_post_preview_remote_receipt as fixtures
from tests.test_post_preview_api import TOKEN,HEADERS

class RemoteReceiptViewTests(unittest.TestCase):
    def test_original_blocked_receipt_does_not_delay_timeout_or_next_at_both_sizes(self):
        for size in ((800,1280),(452,900)):
            for action in ('timeout','next'):
                with self.subTest(size=size,action=action):
                    fixture=fixtures.RemoteReceiptTests();fixture.setUp()
                    self.addCleanup(fixture.doCleanups)
                    fixture.entered,fixture.release=threading.Event(),threading.Event()
                    payments=PostPreviewClient('https://example.invalid','PB001',TOKEN,expected_mode='mock')
                    self.addCleanup(payments.close)
                    def transport(method,path,*,payload):
                        response=fixture.http.request(method,path,json=payload,headers=HEADERS)
                        if response.status_code!=200:raise RuntimeError('fixture held')
                        return response.json()
                    patcher=patch.object(payments._transport,'_call',side_effect=transport)
                    patcher.start();self.addCleanup(patcher.stop)
                    tick=[100.]
                    session=RemoteRecoveryTicketSession(PostPreviewRecoveryClient(payments),
                        fixture.fixture.group,fixture.fixture.lease,monotonic=lambda:tick[0])
                    self.addCleanup(session.hide_private)
                    session.prepare();Window.size=size;card=session.create_card();Window.add_widget(card)
                    self.addCleanup(lambda:Window.remove_widget(card) if card.parent else None)
                    card._ready_at=0
                    for _ in range(6):EventLoop.idle()
                    card._rendered(0);session.acknowledge_visible()
                    errors=[]
                    def send():
                        try:session.send_receipt_once()
                        except Exception as error:errors.append(type(error).__name__)
                    worker=threading.Thread(target=send);worker.start()
                    try:
                        self.assertTrue(fixture.entered.wait(2))
                        self.assertEqual('SENDING',fixture.fixture.row()['receipt_state'])
                        if action=='timeout':
                            tick[0]=130.;self.assertEqual(0,session.poll())
                        else:self.assertTrue(session.finish(next_pressed=True))
                        self.assertIsNone(card.qr_image.texture);self.assertEqual('',card.code.text)
                        self.assertTrue(worker.is_alive());self.assertFalse(session.window.active)
                    finally:fixture.release.set();worker.join(5)
                    self.assertEqual([],errors);self.assertEqual('SUBMITTED',session.receipt['receipt_state'])
                    self.assertFalse(session.receipt['physical_paper_verified'])
                    session.dismiss();self.assertEqual('DISMISSED',fixture.fixture.row()['screen_state'])
                    self.assertEqual(1,len(fixture.sent));self.doCleanups()
