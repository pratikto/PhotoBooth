"""Verified immutable global/local snapshots; keep the last good offline copy.

Use the existing ad catalog and receipt pack renderer. Only a small atomic
pointer changes; an active visitor keeps its previous templates/media paths.
There is no cache garbage collector that could remove an in-use asset.
"""
import hashlib
import json
import logging
from pathlib import Path, PurePosixPath
import re
import shutil
from uuid import uuid4

from photobooth.advertising import AdCatalog, Advertisement, IMAGE_SUFFIXES, VIDEO_SUFFIXES
from photobooth.booth_storage import checked_path
from photobooth.catalog import get_templates, load_template_pack
from photobooth.manifest_io import write_json_atomic

NAMESPACES = ('Global_Advertisement','Global_Template','Local/Advertisement','Local/Template')
LOG = logging.getLogger(__name__)


def content_path(value):
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or '\\' in value or str(path) != value
            or any(p in {'.','..'} or p.casefold() == 'old' or p.endswith((' ','.'))
                or re.search(r'[<>:"|?*\x00-\x1f]',p)
                or re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?',p,re.I) for p in path.parts)):
        raise ValueError('Unsafe content path.')
    return path


class ContentCache:
    def __init__(self, workspace):
        self.workspace = workspace
        self.pointer = workspace.state_root/'content-current.json'
        self._pending = None
        self._manifest = None
        self.current = None  # Replaced atomically by the single background worker.

    def _file(self, version, path):
        parts=content_path(path).parts
        if parts[0].startswith('Global_') and parts[0] in NAMESPACES:
            base=self.workspace.root/'Cache'/parts[0];tail=parts[1:]
        elif len(parts)>2 and '/'.join(parts[:2]) in NAMESPACES:
            base=self.workspace.root/'Cache'/('Local_'+parts[1]);tail=parts[2:]
        else:
            raise ValueError('Unknown content source.')
        if not tail or not re.fullmatch(r'[a-f0-9]{32}',version):
            raise ValueError('Invalid content generation.')
        return checked_path(base/version/Path(*tail))

    def _validate_manifest(self, manifest):
        version=manifest.get('version');files=manifest.get('files');seen=set();total=0
        if not re.fullmatch(r'[a-f0-9]{32}',str(version)) or not isinstance(files,list) or len(files)>500:
            raise ValueError('Invalid content inventory.')
        for item in files:
            key=item['path'].casefold()
            if key in seen or not item.get('id') or type(item.get('size')) is not int or not 0<=item['size']<=2*1024**3 or not re.fullmatch(r'[a-f0-9]{32}',str(item.get('md5'))):
                raise ValueError('Invalid/duplicate content file.')
            seen.add(key);total+=item['size'];self._file(version,item['path'])
        if total>10*1024**3:
            raise ValueError('Content snapshot exceeds 10 GiB.')
        return version,files,total

    def _snapshot(self, manifest):
        version,files,_=self._validate_manifest(manifest)
        ads=AdCatalog(); extras=[];templates=list(get_templates())
        for namespace in NAMESPACES:
            source=[f for f in files if f['path'].startswith(namespace+'/')]
            playlist=next((f for f in source if f['path']==namespace+'/playlist.json'),None)
            for entry in source:
                path=self._file(version,entry['path'])
                if not path.is_file() or path.stat().st_size != entry['size']:
                    raise ValueError('Cached content is incomplete.')
                if namespace.endswith('Advertisement') and not playlist and path.suffix.lower() in IMAGE_SUFFIXES|VIDEO_SUFFIXES:
                    extras.append(Advertisement(entry['path'],path.stem,path,('idle','payment')))
            if namespace.endswith('Advertisement') and playlist:
                playlist_path=self._file(version,playlist['path'])
                payload=json.loads(playlist_path.read_text(encoding='utf-8'))
                allowed={f['path'] for f in source}
                for item in payload['ads']:
                    for field in ('file','poster'):
                        if item.get(field):
                            relative=str(content_path(item[field]))
                            if namespace+'/'+relative not in allowed:
                                raise ValueError('Playlist references an uncached asset.')
                scoped=AdCatalog(playlist_path)
                extras+=scoped.items
                if namespace.startswith('Global'):
                    ads.zone=scoped.zone;ads.timing=scoped.timing
            if namespace.endswith('Template'):
                pack=next((f for f in source if f['path']==namespace+'/layout_80mm.json'),None)
                if source and not pack:
                    raise ValueError('Templates require layout_80mm.json plus artwork/masks.')
                if pack:
                    loaded=load_template_pack(self._file(version,pack['path']).parent,
                        'global' if namespace.startswith('Global') else 'local')
                    templates=list(loaded) if namespace.startswith('Global') else templates+list(loaded)
        # Remote per-booth assets and global assets coexist; neither hides the other.
        if extras:
            ads.items=extras
        # Manually installed booth-specific media remains available offline too.
        local=self.workspace.root/'Local'/'Advertisement'
        for path in sorted(local.iterdir(),key=lambda p:p.name.casefold()) if local.is_dir() else ():
            if path.name.casefold()=='old':continue
            if path.suffix.lower() in IMAGE_SUFFIXES|VIDEO_SUFFIXES and checked_path(path).is_file():
                ads.items.append(Advertisement('booth-file/'+path.name,path.stem,path,('idle','payment')))
        pack=self.workspace.root/'Local'/'Template'/'layout_80mm.json'
        try:
            if checked_path(pack).is_file():
                templates+=list(load_template_pack(pack.parent,'booth'))
        except (OSError,ValueError,TypeError,KeyError):
            LOG.warning('Invalid manual booth template pack; retaining verified/bundled templates.')
        return {'version':version,'templates':tuple(templates),'catalog':ads}

    def load(self):
        """Called on the photo worker, never decode templates on a button tap."""
        try:
            manifest=json.loads(checked_path(self.pointer).read_text(encoding='utf-8'))
            self.current=self._snapshot(manifest)
            self._manifest=manifest
        except (OSError,ValueError,TypeError,KeyError):
            # First offline launch still uses bundled art + manual local assets.
            self.current=self._snapshot({'version':'0'*32,'files':[]})
        return self.current

    @property
    def pending(self):
        return self._pending is not None

    def sync(self, client, *, cancelled=lambda:False):
        """Yield at request/chunk boundaries, retaining staged bytes and old publication."""
        if self._pending is None:
            self._pending = self._download(client)
        try:
            while not cancelled():
                try:
                    next(self._pending)
                except StopIteration as finished:
                    self._pending = None
                    return bool(finished.value)
            return False
        except Exception:
            self._pending.close()
            self._pending = None
            raise

    def _download(self, client):
        manifest=client.asset_manifest();version,files,total=self._validate_manifest(manifest)
        yield  # A newly arrived customer takes priority over the first asset.
        if self.current and self.current['version']==version:
            return False
        if shutil.disk_usage(self.workspace.root).free < total+100*1024**2:
            raise OSError('Insufficient cache staging space.')
        for entry in files:
            target=self._file(version,entry['path']);target.parent.mkdir(parents=True,exist_ok=True)
            if target.is_file():
                with target.open('rb') as stream:
                    if target.stat().st_size == entry['size'] and hashlib.file_digest(stream,'md5').hexdigest()==entry['md5']:
                        yield
                        continue
            temporary=checked_path(target.with_name(target.name+'.'+uuid4().hex+'.part'))
            digest=hashlib.md5()
            previous = next((f for f in (self._manifest or {}).get('files', [])
                             if f['path'] == entry['path'] and f['size'] == entry['size']
                             and f['md5'] == entry['md5']), None)
            try:
                if previous:
                    source = self._file(self._manifest['version'], previous['path'])
                    if source.is_file() and source.stat().st_size == entry['size']:
                        # Copy rather than link: a corrupt/new generation cannot mutate active bytes.
                        with source.open('rb') as old, temporary.open('xb') as new:
                            while chunk := old.read(512*1024):
                                new.write(chunk); digest.update(chunk)
                                yield
                        if digest.hexdigest() == entry['md5']:
                            temporary.replace(target)
                            yield
                            continue
                        temporary.unlink()
                        digest = hashlib.md5()
                with temporary.open('xb') as stream:
                    for offset in range(0,entry['size'],512*1024):
                        chunk=client.asset_chunk(entry,offset,min(512*1024,entry['size']-offset))
                        if len(chunk)!=min(512*1024,entry['size']-offset):raise ValueError('Truncated content range.')
                        stream.write(chunk);digest.update(chunk)
                        yield
                if digest.hexdigest()!=entry['md5']:raise ValueError('Content checksum mismatch.')
                temporary.replace(target)
            finally:
                temporary.unlink(missing_ok=True)
        # A source edit during download cannot publish a mixed generation.
        if client.asset_manifest()!=manifest:return False
        snapshot=self._snapshot(manifest)  # Decode/validate all template art first.
        write_json_atomic(self.pointer,manifest)
        self.current=snapshot
        self._manifest=manifest
        return True
