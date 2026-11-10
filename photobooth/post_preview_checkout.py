"""Private all-design approval and the immutable CREATE_PREPARED boundary.

No payment or customer-credential service is enabled here. Readiness is a typed
observation supplied only by trusted adapters; it never reserves a Drive folder.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import uuid

from photobooth.booth_storage import checked_path
from photobooth.capture_journal import CaptureRecoveryRequired, publish_output, validate_image
from photobooth.catalog import compose_result
from photobooth.kiosk_v2.photo_recovery import _publish_staged
from photobooth.manifest_io import manifest_lock
from photobooth.post_preview_store import DraftHeld, DraftLease, ORDER_VERSION, quote_post_preview
from photobooth.transaction_store import LocalTransaction, TransactionStore


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class ChargeReadiness:
    camera: bool = False
    disk: bool = False
    artwork: bool = False
    printer_route: bool = False
    payment_transport: bool = False
    drive_authenticated: bool = False
    drive_sharing: bool = False
    unclaimed_ready_capacity: int = 0

    def require(self):
        signals = (self.camera, self.disk, self.artwork, self.printer_route,
                   self.payment_transport, self.drive_authenticated, self.drive_sharing)
        if (not all(type(v) is bool and v for v in signals)
                or type(self.unclaimed_ready_capacity) is not int
                or self.unclaimed_ready_capacity < 1):
            raise DraftHeld('Charge readiness is not independently established')


class _PrivatePreviewStore(TransactionStore):
    def __init__(self, original, preview_key):
        super().__init__(original.photos_root, original.state_path, original.booth_id,
                         layout_version=2, capture_protocol=1)
        self.preview_key = preview_key

    def output_path(self, transaction, session):
        return checked_path(transaction.folder_path/'previews'/(self.preview_key+'.png'))


class PrivateDraftCheckout:
    def __init__(self, photos):
        self.photos = photos
        self.ledger = photos.ledger

    def verify_frozen(self, group, templates):
        """Recheck original frozen media/artwork without restore or allocation.

        File/hash I/O runs outside the SQL transaction. Original ownership is
        rechecked afterward; a concurrent privacy retirement cannot pass charge
        admission with a stale camera/media generation.
        """
        from photobooth.post_preview_readiness import ReadinessScope
        with self.ledger.write():
            intent = self.ledger.db.execute('''SELECT i.*,d.booth_id,d.visit_id,d.generation
                FROM pp_checkout_intents i JOIN pp_drafts d ON d.draft_id=i.draft_id
                WHERE i.purchase_group_id=?''', (group,)).fetchone()
            if not intent:
                raise DraftHeld('Original frozen purchase required')
            lease = DraftLease(intent['draft_id'], intent['booth_id'], intent['visit_id'], intent['generation'])
            self.ledger._owned(lease, revision=intent['revision'])
            selected = [dict(r) for r in self.ledger.db.execute('''SELECT * FROM pp_templates
                WHERE draft_id=? AND selected=1 ORDER BY template_id''', (lease.draft_id,))]
            contract = json.loads(intent['contract_json'])
            if (digest(contract) != intent['contract_sha256'] or contract.get('version') != ORDER_VERSION
                    or contract.get('booth_id') != lease.booth_id or contract.get('draft_id') != lease.draft_id
                    or contract.get('revision') != intent['revision'] or contract.get('currency') != 'IDR'
                    or {r['template_id']: r['copies'] for r in selected} != contract.get('quantities')
                    or quote_post_preview(contract['quantities']).total_amount != contract.get('amount')
                    or len(contract.get('designs', [])) != len(selected)):
                raise DraftHeld('Frozen purchase, quote or selection changed')
        available = {t.template_id: t for t in templates}
        for row, design in zip(selected, contract['designs']):
            template = available.get(row['template_id'])
            if (template is None or not row['approved'] or design.get('template_id') != row['template_id']
                    or design.get('copies') != row['copies'] or design.get('lineage_id') != row['lineage_id']
                    or design.get('retake_consumed') != bool(row['retake_consumed'])
                    or design.get('retake_slot') != row['retake_slot']):
                raise DraftHeld('Frozen template lineage or copy obligation changed')
            checked_path(template.artwork_path)
            for aperture in template.apertures:
                checked_path(aperture.mask_path)
            store, tx, plan = self.photos._open(lease, template, row, repair=False)
            session = self.photos._session(tx, plan)
            if not session.ready_for_review or row['retake_consumed'] and not session.retake_used:
                raise DraftHeld('Original final three-photo selection required')
            raw = {p['path']: p for p in tx.manifest['sessions'][0]['raw_photos']}
            binding = {'version': ORDER_VERSION, 'lineage_id': row['lineage_id'],
                       'artwork': tx.manifest['frozen_order']['templates'][0],
                       'photos': [{'path': p.relative_to(tx.folder_path).as_posix(),
                                   'sha256': raw[p.relative_to(tx.folder_path).as_posix()]['sha256']}
                                  for p in session.final_photo_paths]}
            if binding != design.get('binding') or digest(binding) != design.get('preview_key'):
                raise DraftHeld('Original approved media or artwork changed')
            output = checked_path(tx.folder_path/'previews'/(digest(binding)+'.png'))
            validate_image(output, design.get('preview_sha256'), image_format='PNG', expected_size=(640, 1920))
        with self.ledger.write():
            self.ledger._owned(lease, revision=intent['revision'])
        return ReadinessScope(group, lease.booth_id, intent['contract_sha256'], lease.generation)

    def _preview(self, lease, template, row):
        store, tx, plan = self.photos._open(lease, template, row)
        session = self.photos._session(tx, plan)
        if not session.ready_for_review or (row['retake_consumed'] and not session.retake_used):
            raise DraftHeld('All three final saved photos and selected retake required')
        sources = []
        raw = {p['path']: p for p in tx.manifest['sessions'][0]['raw_photos']}
        for path in session.final_photo_paths:
            relative = path.relative_to(tx.folder_path).as_posix()
            sources.append({'path': relative, 'sha256': raw[relative]['sha256']})
        binding = {'version': ORDER_VERSION, 'lineage_id': row['lineage_id'],
                   'artwork': tx.manifest['frozen_order']['templates'][0], 'photos': sources}
        preview_key = digest(binding)
        preview_store = _PrivatePreviewStore(store, preview_key)
        path = checked_path(tx.folder_path/'previews'/(preview_key+'.json'))
        with manifest_lock(path):
            if path.exists():
                if path.stat().st_size > 2*1024*1024:
                    raise CaptureRecoveryRequired('Preview intent is oversized')
                data = json.loads(path.read_text(encoding='utf-8'))
                if data.get('preview_binding') != binding:
                    raise CaptureRecoveryRequired('Private preview inputs changed')
            else:
                # Separate preview journal: revisiting review never overwrites a
                # prior rendered preview or completes the capture transaction.
                data = {'transaction_id': tx.transaction_id, 'preview_binding': binding,
                        'sessions': [json.loads(json.dumps(tx.manifest['sessions'][0]))],
                        'upload_files': {}, 'status': 'PRIVATE_PREVIEW'}
                preview_tx = LocalTransaction(tx.transaction_id, tx.folder_path, path, data)
                preview_store._write_manifest(preview_tx)
            preview_tx = LocalTransaction(tx.transaction_id, tx.folder_path, path, data)
            output = preview_store.output_path(preview_tx, plan)
            intent = data.get('output_intents', {}).get(plan.session_id)
            expected = [s['path'] for s in sources]
            if intent:
                operation = intent.get('operation_id')
                if not isinstance(operation, str) or len(operation) != 32 or any(c not in '0123456789abcdef' for c in operation):
                    raise CaptureRecoveryRequired('Preview operation identity changed')
                temporary = output.with_name('.'+output.stem+'.'+operation+'.tmp.png')
                if (intent.get('path') != output.relative_to(tx.folder_path).as_posix()
                        or intent.get('temporary_path') != temporary.relative_to(tx.folder_path).as_posix()
                        or intent.get('final_photos') != expected):
                    raise CaptureRecoveryRequired('Preview output/inputs redirected')
                if intent.get('state') == 'STAGED':
                    _publish_staged(tx.folder_path, intent, 'PNG', repair=True)
                    preview_store.record_output(preview_tx, plan.session_id, session.final_photo_paths, output)
                elif intent.get('state') != 'COMMITTED':
                    raise CaptureRecoveryRequired('Unproven preview write requires review')
            else:
                def render(target):
                    compose_result(session.final_photo_paths, template, target, tx.transaction_id,
                                   plan.session_id, folder_url=None, mirror_photos=True,
                                   download_pending=True)
                publish_output(preview_store, preview_tx, plan, session.final_photo_paths, render)
                preview_store.record_output(preview_tx, plan.session_id, session.final_photo_paths, output)
            intent = preview_tx.manifest['output_intents'][plan.session_id]
            validate_image(output, intent.get('sha256'), image_format='PNG', expected_size=(640, 1920))
            return {'binding': binding, 'preview_key': preview_key,
                    'preview_sha256': intent['sha256'], 'preview_path': output}

    def preview(self, lease, template, *, revision):
        with self.ledger.write():
            row = self.photos._selected(lease, template, revision=revision)
            return self._preview(lease, template, row)

    def approve(self, lease, template, *, revision):
        with self.ledger.write():
            row = self.photos._selected(lease, template, revision=revision)
            result = self._preview(lease, template, row)
            if not row['approved']:
                self.ledger.db.execute('UPDATE pp_templates SET approved=1 WHERE draft_id=? AND template_id=?',
                                       (lease.draft_id, template.template_id))
                self.photos._changed(lease, 'PREVIEW_APPROVED')
            return result

    def _freeze_contract(self, lease, templates, revision, expected_amount):
        available = {t.template_id: t for t in templates}
        selected = self.ledger.db.execute('SELECT * FROM pp_templates WHERE draft_id=? AND selected=1 ORDER BY template_id',
                                           (lease.draft_id,)).fetchall()
        quantities = {r['template_id']: r['copies'] for r in selected}
        quote = quote_post_preview(quantities)
        if type(expected_amount) is not int or expected_amount != quote.total_amount:
            raise DraftHeld('Original server-side quote mismatch')
        designs = []
        for row in selected:
            if not row['approved'] or row['template_id'] not in available:
                raise DraftHeld('Every selected design must be approved')
            result = self._preview(lease, available[row['template_id']], row)
            designs.append({'template_id': row['template_id'], 'copies': row['copies'],
                'lineage_id': row['lineage_id'], 'retake_consumed': bool(row['retake_consumed']),
                'retake_slot': row['retake_slot'], 'binding': result['binding'],
                'preview_key': result['preview_key'], 'preview_sha256': result['preview_sha256']})
        contract = {'version': ORDER_VERSION, 'draft_id': lease.draft_id,
                    'booth_id': lease.booth_id, 'revision': revision, 'currency': 'IDR',
                    'amount': quote.total_amount, 'quantities': quantities, 'designs': designs}
        return contract

    def freeze_scope(self, lease, templates, *, revision, expected_amount):
        """Inspect the exact original approved candidate without creating a group.

        Existing frozen intents are revalidated, never reconstructed/reset. This
        scope carries no payment/media authority and no filesystem paths.
        """
        from photobooth.post_preview_readiness import FreezeScope
        with self.ledger.write():
            self.ledger._owned(lease, revision=revision)
            existing=self.ledger.db.execute('SELECT * FROM pp_checkout_intents WHERE draft_id=?',
                                            (lease.draft_id,)).fetchone()
            if existing:
                existing=dict(existing)
            else:
                self.ledger._owned(lease, editable=True)
                contract=self._freeze_contract(lease,templates,revision,expected_amount)
        if existing:
            self.verify_frozen(existing['purchase_group_id'],templates)
            contract=json.loads(existing['contract_json'])
            if type(expected_amount) is not int or contract['amount']!=expected_amount:
                raise DraftHeld('Original immutable quote mismatch')
        scope=FreezeScope(lease.draft_id,lease.booth_id,lease.visit_id,lease.generation,
                          revision,contract['amount'],digest(contract))
        with self.ledger.write():
            self.ledger._owned(lease,revision=revision)
        return scope

    def freeze(self, lease, templates, *, revision, readiness, expected_amount,
               expected_contract_sha256=None):
        if not isinstance(readiness, ChargeReadiness):
            raise DraftHeld('Trusted typed readiness observation required')
        readiness.require()
        with self.ledger.write():
            self.ledger._owned(lease, revision=revision)
            existing = self.ledger.db.execute('SELECT * FROM pp_checkout_intents WHERE draft_id=?',
                                              (lease.draft_id,)).fetchone()
            if existing:
                result = dict(existing)
                if type(expected_amount) is not int or json.loads(result['contract_json'])['amount'] != expected_amount:
                    raise DraftHeld('Original immutable quote mismatch')
                if expected_contract_sha256 is not None and result['contract_sha256']!=expected_contract_sha256:
                    raise DraftHeld('Original immutable freeze candidate changed')
                return result
            self.ledger._owned(lease, editable=True)
            contract = self._freeze_contract(lease, templates, revision, expected_amount)
            if expected_contract_sha256 is not None and digest(contract)!=expected_contract_sha256:
                raise DraftHeld('Original approved freeze candidate changed')
            group = uuid.uuid4().hex
            self.ledger.db.execute('''INSERT INTO pp_checkout_intents
                VALUES(?,?,?,?,?,'CREATE_PREPARED',?)''',
                (group, lease.draft_id, revision, canonical(contract), digest(contract), self.ledger.now()))
            self.ledger.db.execute("UPDATE pp_drafts SET state='CREATE_PREPARED',updated_at=? WHERE draft_id=?",
                                   (self.ledger.now(), lease.draft_id))
            self.ledger._event(lease.draft_id, 'CREATE_PREPARED')
            return dict(self.ledger.db.execute('SELECT * FROM pp_checkout_intents WHERE draft_id=?',
                                               (lease.draft_id,)).fetchone())
