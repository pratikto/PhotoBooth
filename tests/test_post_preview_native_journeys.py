"""Native headless Kivy journeys: screens, UI actions and original billing.

Distinct from backend J01-J20. All charges, paper and Drive URLs are synthetic;
the actual paid output screen must remain a protected OWED liability.
"""
import time
import unittest

from kivy.base import EventLoop
from kivy.core.window import Window

from tests import test_post_preview_checkout_widgets as checkout_helpers


class NativeCustomerJourneyMatrixTests(unittest.TestCase):
    booth = checkout_helpers.PrivateCheckoutWidgetTests.booth
    settle = checkout_helpers.PrivateCheckoutWidgetTests.settle
    click = checkout_helpers.PrivateCheckoutWidgetTests.click
    shot = checkout_helpers.PrivateCheckoutWidgetTests.shot
    start = checkout_helpers.PrivateCheckoutWidgetTests.start
    final = checkout_helpers.PrivateCheckoutWidgetTests.final
    proof = checkout_helpers.PrivateCheckoutWidgetTests.proof
    paid_ticket_screen = checkout_helpers.PrivateCheckoutWidgetTests.paid_ticket_screen

    def await_phase(self, app, phase, timeout=15):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and app._photo_view.get('phase') != phase:
            app._poll_photos()
            EventLoop.idle()
            time.sleep(.01)
        self.assertEqual(phase, app._photo_view.get('phase'), app._photo_error)

    def test_n21_native_three_designs_full_gallery_to_paid_ticket_and_2_1_3_print(self):
        with self.booth(paid_delivery=True) as (app, fixture):
            Window.size = (452, 900)
            app._choose_photo()
            app._complete_tutorial()
            app.quantities.update(template_a=2, template_b=1, template_c=3)
            app._enter_photo_test()
            self.settle(app)
            app._admit_photo_test()
            self.settle(app)
            for _ in range(3):
                for _ in range(3):
                    self.shot(app)
                app._photo_submit('compose')
                self.settle(app)
                app._photo_submit('next')
                self.settle(app)
            self.assertEqual('final_preview', app._photo_view['phase'])
            self.assertEqual(3, len(app._photo_view['designs']))
            self.assertEqual(9, len(list(fixture.service.root.rglob('*.jpg'))))
            self.click(app, 'LANJUT CHECKOUT SIMULASI')
            self.settle(app)
            self.await_phase(app, 'checkout_ready')
            self.assertEqual(0, fixture.provider.charges)
            self.click(app, 'SUDAH SIMPAN BUKTI • LANJUT SIMULASI')
            self.settle(app)
            self.assertEqual('payment_pending', app._photo_view['phase'])
            self.assertEqual(1, fixture.provider.charges)
            order = app._photo_view['payment']['attempts'][0]['provider_order_id']
            fixture.provider.state(order, 'settlement')
            self.click(app, 'PERIKSA STATUS')
            self.await_phase(app, 'ticket_offer')
            self.assertIsNotNone(app._ticket_card)
            app._ticket_card._ready_at = 0
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline and app._photo_view.get('phase') != 'ticket_visible':
                EventLoop.idle()
                if app._ticket_card is not None:
                    app._ticket_card._rendered(0)
                app._poll_photos()
                time.sleep(.01)
            self.assertEqual('ticket_visible', app._photo_view['phase'])
            self.assertTrue(app._ticket_window.active)
            self.click(app, 'LANJUT • SIMPAN TIKET')
            self.await_phase(app, 'paid_delivery')
            self.assertEqual(1, len(fixture.receipt_sizes))
            self.assertTrue(any(
                isinstance(getattr(w, 'text', None), str)
                and 'BUKAN LINK DOWNLOAD' in w.text
                for w in app.stage.walk()))
            states = app._photo_view['delivery']['print_states']
            self.assertEqual({'template_a': 'PREPARED', 'template_b': 'PREPARED',
                              'template_c': 'PREPARED'}, states)
            for expected in (1, 2, 3):
                self.click(app, 'CETAK FOTO YANG SUDAH DIBAYAR')
                self.settle(app)
                self.assertEqual(expected, len(fixture.paid_print_sends))
            self.assertEqual([2, 1, 3],
                             [copies for _path, copies in fixture.paid_print_sends])
            self.assertTrue(app._photo_view['delivery']['print_all_submitted'])
            self.assertEqual('OWED', fixture.service.ledger.db.execute(
                'SELECT status FROM pp_paid_services').fetchone()[0])
            self.assertFalse(app._photo_view['delivery']['physical_paper_verified'])
            self.assertEqual(1, fixture.provider.charges)

    def test_n22_native_paid_drive_offline_then_original_paid_retry_without_recharge(self):
        with self.booth(paid_delivery=True) as (app, fixture):
            Window.size = (452, 900)
            self.paid_ticket_screen(app, fixture)
            original = fixture.drive.bind_transaction
            def offline(_manifest):
                raise OSError('synthetic Drive offline after PAID')
            fixture.drive.bind_transaction = offline
            self.click(app, 'LANJUT • SIMPAN TIKET')
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                app._poll_photos()
                EventLoop.idle()
                if not app._photo_jobs.busy and app._photo_error:
                    break
                time.sleep(.01)
            self.assertTrue(app._photo_error)
            self.assertEqual('paid_hold', app._photo_view.get('phase'))
            self.assertEqual([], fixture.paid_print_sends)
            reserved = fixture.service.ledger.db.execute(
                'SELECT transaction_id FROM pp_paid_services').fetchone()[0]
            self.assertIsNotNone(reserved)
            fixture.drive.bind_transaction = original
            self.click(app, 'COBA SIAPKAN DELIVERY')
            self.await_phase(app, 'paid_delivery')
            self.assertEqual(reserved, app._photo_view['delivery']['transaction_id'])
            self.assertEqual(1, fixture.provider.charges)
            self.assertEqual(1, len(fixture.receipt_sizes))
            self.assertEqual('OWED', app._photo_view['delivery']['service_status'])
            self.click(app, 'CETAK FOTO YANG SUDAH DIBAYAR')
            self.settle(app)
            self.assertEqual(1, len(fixture.paid_print_sends))
            self.assertFalse(app._photo_view['delivery']['physical_paper_verified'])

    def test_n23_paid_A_locked_then_B_active_cannot_open_claim_popup_or_show_A(self):
        with self.booth(paid_ticket=True, unattended=True) as (app, fixture):
            Window.size = (452, 900)
            self.proof(app)
            proof = app._photo_view['ccp_offer'].qr_payload
            self.click(app, 'SUDAH SIMPAN BUKTI • LANJUT SIMULASI')
            self.settle(app)
            order = app._photo_view['payment']['attempts'][0]['provider_order_id']
            fixture.provider.state(order, 'settlement')
            self.click(app, 'PERIKSA STATUS')
            self.await_phase(app, 'ticket_offer')
            old = fixture.service.lease
            app._sandbox_lock_customer()
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                app._poll_photos()
                EventLoop.idle()
                if (app.navigation.page == 'advert' and not app._photo_jobs.busy
                        and fixture.service._hidden.is_set()):
                    break
                time.sleep(.01)
            self.assertEqual('advert', app.navigation.page)
            self.start_B(app)
            b = fixture.service.lease
            self.assertNotEqual(old.draft_id, b.draft_id)
            self.shot(app)
            self.assertEqual(b.draft_id, fixture.service.lease.draft_id)
            self.assertEqual('capture', app._photo_view['phase'])
            # Recovery input belongs exclusively to protected Ads, not a
            # takeover tool while B owns the kiosk and camera.
            app._pilot_open_claim()
            app._pilot_submit_claim(proof)
            self.assertIsNone(app._pilot_popup)
            self.assertEqual(b.draft_id, fixture.service.lease.draft_id)
            self.assertEqual('capture', app._photo_view['phase'])
            self.assertFalse(any(
                isinstance(getattr(w, 'text', None), str)
                and (proof in w.text or 'MEONG:RECOVERY:' in w.text)
                for w in app.stage.walk()))
            self.assertEqual('OWED', fixture.service.ledger.db.execute(
                'SELECT status FROM pp_paid_services').fetchone()[0])
            self.assertEqual(1, fixture.provider.charges)

    def start_B(self, app):
        app._choose_photo()
        app._complete_tutorial()
        app.quantities.update(template_a=2, template_b=1)
        app._enter_photo_test()
        self.settle(app)
        app._admit_photo_test()
        self.settle(app)


if __name__ == '__main__':
    unittest.main()
