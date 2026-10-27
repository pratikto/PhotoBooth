"""New schema foundation, always temporary and without a physical printer/Drive."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from PIL import Image
from photobooth.booth_storage import BoothWorkspace, checked_path
from photobooth.catalog import compose_result, get_templates
from photobooth.printer import PrinterConfig, ThermalPrinter
from photobooth.retention import purge_local_photos
from photobooth.transaction_store import TransactionStore
from photobooth.workflow import build_session_plans


class BoothStorageTests(unittest.TestCase):
    def test_remote_folders_cannot_be_reused_across_reserve_batches_or_claims(self):
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare();a,b=w.ready_slots()[:2]
            def reply(slot):
                return {**slot,'folder_id':'one-folder',
                    'folder_url':'https://drive.google.com/drive/folders/one-folder',
                    'photo_number_layout':1,'link_verified':True}
            w.remember_remote([reply(a)]);claimed=w.claim();before=w.state_path.read_bytes()
            with self.assertRaises(ValueError):w.remember_remote([reply(b)])
            self.assertEqual(w.state_path.read_bytes(),before)
            fresh=BoothWorkspace(folder)
            with self.assertRaises(ValueError):fresh.remember_binding(b['transaction_id'],b['claim_token'],reply(b))
            self.assertEqual(fresh.state_path.read_bytes(),before)
            self.assertEqual(claimed['transaction_id'],a['transaction_id'])

    def test_twenty_five_empty_direct_reserves_survive_restart_and_offline_exhaustion(self):
        with TemporaryDirectory() as folder:
            workspace = BoothWorkspace(Path(folder)/'Photobooth')
            self.assertEqual(workspace.prepare(), 25)
            self.assertEqual(len(workspace.ready_slots()), 25)
            self.assertTrue(all(not any((workspace.root/s['transaction_id']).iterdir()) for s in workspace.ready_slots()))
            claimed = [workspace.claim()['transaction_id'] for _ in range(30)]
            fresh = BoothWorkspace(Path(folder)/'Photobooth')
            self.assertEqual(fresh.prepare(), 25)
            self.assertNotIn(fresh.claim()['transaction_id'], claimed)
            self.assertEqual(len(set(claimed)), 30)
            self.assertEqual(workspace.root.name, 'PB001')

    def test_booth_roots_and_active_counter_checkpoint_stay_isolated(self):
        with TemporaryDirectory() as folder:
            root = Path(folder);seed=root/'active-counter.json'
            seed.write_text(json.dumps({'booth_id':'PB001V2','next_sequence':100}))
            before=seed.read_bytes();a=BoothWorkspace(root/'Photobooth',seed_counter=seed)
            b=BoothWorkspace(root/'Photobooth','PB002V2')
            a.prepare();b.prepare()
            self.assertEqual(a.claim()['transaction_id'],'PB001V2_00000100')
            self.assertEqual(b.claim()['transaction_id'],'PB002V2_00000001')
            self.assertEqual(seed.read_bytes(),before)

    def test_archive_paths_and_corrupt_identity_fail_before_claim(self):
        with TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):checked_path(Path(folder)/'old'/'anything')
            self.assertFalse((Path(folder)/'old').exists())
            workspace=BoothWorkspace(folder);workspace.prepare()
            state=json.loads(workspace.state_path.read_text());state['booth_id']='PB999'
            workspace.state_path.write_text(json.dumps(state))
            with self.assertRaises(ValueError):workspace.claim()

    def test_new_sessions_keep_raw_color_bw_and_retention_does_not_touch_assets_or_ready(self):
        with TemporaryDirectory() as folder:
            workspace=BoothWorkspace(folder);workspace.prepare();claim=workspace.claim()
            store=TransactionStore(workspace.root,workspace.counter_path,workspace.booth_id,layout_version=2)
            plans=build_session_plans(get_templates(),{'template_a':2,'template_b':1})
            tx=store.start_transaction(plans,transaction_id=claim['transaction_id'],folder_path=claim['staging_path'])
            printer=ThermalPrinter(PrinterConfig(print_width_dots=576))
            for plan in plans:
                raw=[store.save_raw_photo(tx,plan,Image.new('RGB',(160,100),'red'),f'photo_{i:02d}.jpg','capture') for i in range(1,4)]
                raw.append(store.save_raw_photo(tx,plan,Image.new('RGB',(160,100),'blue'),'retake.jpg','retake'))
                before=[p.read_bytes() for p in raw]
                output=store.output_path(tx,plan)
                compose_result(raw[:3],plan.template,output,tx.transaction_id,plan.session_id,mirror_photos=True)
                store.record_output(tx,plan.session_id,raw[:3],output)
                bw=store.session_path(tx,plan,'bw')/'strip.png';printer.render_image(output).save(bw)
                store.record_artifact(tx,plan.session_id,bw,kind='bw')
                self.assertEqual([p.read_bytes() for p in raw],before)
                with Image.open(bw) as image:self.assertEqual((image.mode,image.size),('1',(576,1728)))
            self.assertEqual(len(tx.manifest['sessions']),2)
            self.assertTrue((tx.folder_path/'Photo/01/raw/retake.jpg').exists())
            self.assertTrue((tx.folder_path/'Photo/02/color/strip.png').exists())
            asset=workspace.root/'Local/Advertisement/keep.txt';asset.write_text('keep')
            purge_local_photos(workspace.root,now=datetime.now(timezone.utc)+timedelta(days=16))
            self.assertFalse((tx.folder_path/'Photo').exists())
            self.assertEqual(asset.read_text(),'keep')
            self.assertTrue(tx.manifest_path.exists());self.assertEqual(len(workspace.ready_slots()),25)

    def test_saved_bw_print_reuses_original_batching_without_second_render(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'bw.png';Image.new('1',(576,1728),1).save(path)
            sender=Mock();printer=ThermalPrinter(PrinterConfig(),usb_sender=sender)
            with patch.object(printer,'raster_payload',return_value=b'raster-and-cut'),patch.object(
                    printer,'render_image',side_effect=AssertionError('double dithering')):
                result=printer.print_raster(path,copies=3)
            self.assertTrue(result.success)
            sender.assert_called_once_with(b'raster-and-cut'*3)
