"""Real ad/template loaders with synthetic verified chunks; no Google account."""
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock
from PIL import Image

from photobooth.booth_storage import BoothWorkspace
from photobooth.content_cache import ContentCache, content_path
from photobooth.catalog import ASSET_ROOT


def image_bytes():
    stream=io.BytesIO();Image.new('RGB',(40,60),'red').save(stream,format='PNG');return stream.getvalue()


def fixture(files):
    entries=[{'id':str(i),'path':path,'size':len(data),'md5':hashlib.md5(data).hexdigest(),'mime_type':'application/octet-stream'} for i,(path,data) in enumerate(files.items())]
    version=hashlib.md5(json.dumps(entries).encode()).hexdigest()
    client=Mock();client.asset_manifest.return_value={'ok':True,'storage_layout':2,'version':version,'files':entries}
    client.asset_chunk.side_effect=lambda descriptor,offset,length:files[descriptor['path']][offset:offset+length]
    return client


class ContentCacheTests(unittest.TestCase):
    def test_verified_global_local_copies_survive_offline_restart_and_partial_new_generation(self):
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare();cache=ContentCache(w)
            client=fixture({'Global_Advertisement/sale.png':image_bytes(),'Local/Advertisement/event.png':image_bytes()})
            self.assertTrue(cache.sync(client));pointer=cache.pointer.read_bytes();old=cache.current
            self.assertEqual(len(old['catalog'].items),2);self.assertEqual(len(old['templates']),12)
            local=ContentCache(w);local.load();self.assertEqual(local.current['version'],old['version'])
            self.assertTrue(all(ad.path.is_file() for ad in local.current['catalog'].items))
            interrupted=fixture({'Global_Advertisement/new.png':image_bytes()+b'new'})
            interrupted.asset_chunk.side_effect=OSError('offline')
            with self.assertRaises(OSError):cache.sync(interrupted)
            self.assertIs(cache.current,old);self.assertEqual(cache.pointer.read_bytes(),pointer)
            corrupt=fixture({'Global_Advertisement/new.png':image_bytes()+b'new'})
            corrupt.asset_chunk.side_effect=lambda f,o,n:b'x'*n
            with self.assertRaises(ValueError):cache.sync(corrupt)
            self.assertEqual(cache.pointer.read_bytes(),pointer)
            self.assertFalse(cache.sync(client));self.assertTrue(old['catalog'].items[0].path.exists())

    def test_original_pack_renderer_validates_cache_before_activation_and_keeps_active_paths(self):
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare();cache=ContentCache(w)
            data=json.loads((ASSET_ROOT/'layout_80mm.json').read_text());entry=data['templates'][0];data['templates']=[entry]
            files={'Global_Template/layout_80mm.json':json.dumps(data).encode(),'Global_Template/'+entry['png_file']:(ASSET_ROOT/entry['png_file']).read_bytes()}
            for frame in entry['photo_apertures']:files['Global_Template/'+frame['mask_file']]=(ASSET_ROOT/frame['mask_file']).read_bytes()
            client=fixture(files);cache.sync(client);active=cache.current['templates'][0];pointer=cache.pointer.read_bytes()
            self.assertEqual(active.template_id,'global_01')
            invalid=deepcopy(data);invalid['templates'][0]['png_file']='../outside.png'
            bad=fixture({**files,'Global_Template/layout_80mm.json':json.dumps(invalid).encode()})
            with self.assertRaises(ValueError):cache.sync(bad)
            self.assertEqual(cache.pointer.read_bytes(),pointer);self.assertTrue(active.artwork_path.is_file())
            self.assertEqual(ContentCache(w).load()['templates'][0],active)

    def test_archive_traversal_windows_collisions_and_outside_playlist_fail_before_download(self):
        for path in ('Global_Template/old/a.png','Global_Template/../a.png','Global_Advertisement/CON.mp4','/absolute','Local/Advertisement/x\\a.png'):
            with self.assertRaises(ValueError):content_path(path)
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare();cache=ContentCache(w)
            bad=fixture({'Global_Advertisement/old/skip.png':b'do not read'})
            with self.assertRaises(ValueError):cache.sync(bad)
            bad.asset_chunk.assert_not_called()
            collision=fixture({'Global_Advertisement/A.png':image_bytes(),'Global_Advertisement/a.png':image_bytes()})
            with self.assertRaises(ValueError):cache.sync(collision)
            collision.asset_chunk.assert_not_called()
            playlist=fixture({'Global_Advertisement/playlist.json':json.dumps({'ads':[{'id':'a','file':'../old/x.mp4'}]}).encode()})
            with self.assertRaises(ValueError):cache.sync(playlist)
            self.assertFalse(cache.pointer.exists())

    def test_manual_local_ads_and_scheduled_global_playlist_reuse_original_ad_catalog(self):
        with TemporaryDirectory() as folder:
            w=BoothWorkspace(folder);w.prepare()
            (w.root/'Local/Advertisement/booth.png').write_bytes(image_bytes())
            cache=ContentCache(w);cache.load();self.assertTrue(any(ad.ad_id=='booth-file/booth.png' for ad in cache.current['catalog'].items))
            playlist={'timing':{'landing_idle':120},'ads':[{'id':'sale','file':'sale.png','seconds':11,'placements':['idle']}]}
            cache.sync(fixture({'Global_Advertisement/playlist.json':json.dumps(playlist).encode(),'Global_Advertisement/sale.png':image_bytes()}))
            self.assertEqual(cache.current['catalog'].timing.landing_idle,120)
            self.assertEqual(cache.current['catalog'].items[0].seconds,11)
            self.assertEqual(cache.current['catalog'].items[0].placements,('idle',))
