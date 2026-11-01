"""Original PAID folder reservation identity: no replay, no pool leakage."""
from pathlib import Path
import tempfile
import unittest

from photobooth.booth_storage import BoothWorkspace


class OriginalPaidDriveReservationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.workspace=BoothWorkspace(self.root,'PB001V2S2')
        self.workspace.prepare()

    def test_exact_original_claim_and_restart_return_same_reserved_folder(self):
        original=self.workspace.ready_slots()[0]
        first=self.workspace.claim_exact(original['transaction_id'],original['claim_token'])
        self.assertEqual(original['transaction_id'],first['transaction_id'])
        self.assertTrue(Path(first['staging_path']).is_dir())
        self.assertEqual(25,len(self.workspace.ready_slots()))
        restarted=BoothWorkspace(self.root,'PB001V2S2')
        again=restarted.claim_exact(original['transaction_id'],original['claim_token'])
        self.assertEqual(first,again)
        self.assertEqual(25,len(restarted.ready_slots()))
        self.assertNotIn(original['transaction_id'],
                         {s['transaction_id'] for s in restarted.ready_slots()})

    def test_other_claim_token_and_foreign_booth_identity_are_rejected(self):
        original=self.workspace.ready_slots()[0]
        with self.assertRaises(ValueError):
            self.workspace.claim_exact(original['transaction_id'],'f'*32)
        with self.assertRaises(ValueError):
            self.workspace.claim_exact('PB002V2S2_00000001',original['claim_token'])
        self.assertEqual(25,len(self.workspace.ready_slots()))

    def test_cannot_skip_reserve_queue_head_or_claim_nonempty_slot(self):
        original, later=self.workspace.ready_slots()[:2]
        with self.assertRaises(ValueError):
            self.workspace.claim_exact(later['transaction_id'],later['claim_token'])
        path=self.workspace.root/original['transaction_id']
        (path/'foreign.jpg').write_bytes(b'OTHER')
        with self.assertRaises(ValueError):
            self.workspace.claim_exact(original['transaction_id'],original['claim_token'])
        self.assertEqual(25,len(self.workspace.ready_slots()))

    def test_missing_previously_claimed_path_fails_closed(self):
        original=self.workspace.ready_slots()[0]
        self.workspace.claim_exact(original['transaction_id'],original['claim_token'])
        (self.workspace.root/original['transaction_id']).rmdir()
        with self.assertRaises(ValueError):
            self.workspace.claim_exact(original['transaction_id'],original['claim_token'])
        self.assertEqual(25,len(self.workspace.ready_slots()))


if __name__=='__main__': unittest.main()
