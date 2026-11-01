"""Synthetic private-ledger tests; no paid/customer/device acceptance claims."""
from dataclasses import replace
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest

from photobooth.payment_quote import quote_checkout
from photobooth.post_preview_store import (DraftHeld, ORDER_VERSION,
                                           PostPreviewStore, quote_post_preview)


class PrivateDraftTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'private.sqlite3'
        self.store = self.open()

    def open(self):
        store = PostPreviewStore(self.path, now=lambda: 1000)
        self.addCleanup(store.close)
        return store

    def create(self, cart=None):
        return self.store.create('PB001', 'visitA', cart or {'template_a': 2})

    def test_versioned_private_cart_and_existing_prices(self):
        lease = self.create({'template_a': 2, 'template_b': 1})
        state = self.store.inspect(lease)
        self.assertEqual(ORDER_VERSION, state['version'])
        self.assertEqual(25000, state['amount'])
        self.assertEqual(2, len(state['templates']))
        self.assertEqual('OPEN', state['state'])
        self.assertEqual({'pp_schema', 'pp_drafts', 'pp_templates', 'pp_events', 'pp_checkout_intents', 'pp_ccp_credentials', 'sqlite_sequence'},
                         {r[0] for r in self.store.db.execute("SELECT name FROM sqlite_master WHERE type='table'")})

    def test_twelve_templates_have_one_lineage_each_independent_of_copies(self):
        lease = self.create({'template_'+c: 9 for c in 'abcdefghijkl'})
        state = self.store.inspect(lease)
        self.assertEqual(12, len(state['templates']))
        self.assertEqual(12, len({r['lineage_id'] for r in state['templates']}))

    def test_new_copy_cap_matches_gallery_without_changing_legacy(self):
        self.assertEqual(55000, quote_checkout({'template_a': 10}).total_amount)
        self.assertEqual(50000, quote_post_preview({'template_a': 9}).total_amount)
        for cart in ({'template_a': 10}, {'template_a': True}, {'template_a': 0},
                     {'template_z': 1}, {}, {'template_a': 1.0}):
            with self.subTest(cart=cart), self.assertRaises(ValueError):
                self.store.create('PB001', 'bad', cart)

    def test_deselect_reselect_keeps_lineage(self):
        lease = self.create({'template_a': 1, 'template_b': 2})
        before = self.store.inspect(lease)
        self.store.edit(lease, {'template_b': 1}, revision=1)
        self.store.edit(lease, {'template_a': 3}, revision=2)
        after = self.store.inspect(lease)
        self.assertEqual(3, after['revision'])
        self.assertEqual(before['templates'][0]['lineage_id'], after['templates'][0]['lineage_id'])
        self.assertEqual(2, len(after['templates']))

    def test_restart_preserves_exact_cart_and_no_create_replay(self):
        lease = self.create()
        other = self.open()
        self.assertEqual(self.store.inspect(lease), other.inspect(lease))
        with self.assertRaises(DraftHeld):
            other.create('PB001', 'visitA', {'template_a': 2})

    def test_new_visitor_cannot_replace_unresolved_owner(self):
        lease = self.create()
        self.store.lifecycle_event(lease, 'VISIT_ABANDONED')
        with self.assertRaises(DraftHeld):
            self.open().create('PB001', 'visitB', {'template_b': 1})

    def test_wrong_owner_and_stale_generation_cannot_read_or_edit(self):
        lease = self.create()
        for bad in (replace(lease, booth_id='PB002'), replace(lease, visit_id='visitB'),
                    replace(lease, generation=2), None):
            with self.subTest(bad=bad), self.assertRaises(DraftHeld):
                self.store.inspect(bad)

    def test_warning_does_not_abandon_but_other_events_fence_stale_callbacks(self):
        lease = self.create()
        self.store.lifecycle_event(lease, 'INACTIVITY_WARNING')
        self.assertEqual('ACTIVE', self.store.inspect(lease)['lifecycle'])
        self.store.lifecycle_event(lease, 'APP_SUSPENDED')
        with self.assertRaises(DraftHeld):
            self.store.edit(lease, {'template_b': 1}, revision=1)
        self.assertEqual(['DRAFT_CREATED', 'INACTIVITY_WARNING', 'APP_SUSPENDED'],
                         [r[0] for r in self.store.db.execute('SELECT event FROM pp_events')])
        row = self.store.db.execute('SELECT * FROM pp_drafts').fetchone()
        self.assertEqual(0, row['closed'])
        self.assertEqual('APP_SUSPENDED', row['lifecycle'])

    def test_compare_revision_across_two_connections(self):
        lease = self.create()
        other = self.open()
        self.store.edit(lease, {'template_b': 2}, revision=1)
        with self.assertRaises(DraftHeld):
            other.edit(lease, {'template_c': 1}, revision=1)
        self.assertEqual({'template_b': 2}, other.inspect(lease)['quantities'])

    def test_competing_creates_only_one_local_owner(self):
        other = self.open()
        gate = threading.Barrier(2)
        outcomes = []
        def create(store, visit):
            gate.wait()
            try:
                store.create('PB001', visit, {'template_a': 1})
                outcomes.append('created')
            except DraftHeld:
                outcomes.append('held')
        threads = [threading.Thread(target=create, args=(s, v))
                   for s, v in ((self.store, 'visitA'), (other, 'visitB'))]
        for t in threads: t.start()
        for t in threads: t.join(5)
        self.assertCountEqual(['created', 'held'], outcomes)

    def test_future_schema_fails_closed(self):
        self.store.db.execute('UPDATE pp_schema SET version=99')
        with self.assertRaises(DraftHeld):
            PostPreviewStore(self.path)

    def test_does_not_migrate_legacy_records(self):
        self.store.db.execute('CREATE TABLE legacy_evidence (value TEXT)')
        self.store.db.execute("INSERT INTO legacy_evidence VALUES('original-paid-grant')")
        self.create()
        self.open()
        self.assertEqual('original-paid-grant', self.store.db.execute('SELECT value FROM legacy_evidence').fetchone()[0])


if __name__ == '__main__':
    unittest.main()
