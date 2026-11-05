"""Original mock service restart probe; private proof/key travel only in pipes.

Windows uses real current-user DPAPI, never an injected key. Other platforms
exercise explicitly synthetic plumbing with one in-memory parent fixture key.
Only sanitized observations/digests leave the consumer process. No device I/O.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np

from photobooth.catalog import get_templates
from photobooth.credential_vault import SyntheticAeadProtector, platform_protector, VaultUnavailable
from photobooth.post_preview_ccp import OriginalCCPService
from photobooth.post_preview_claim import OriginalMockClaim
from photobooth.post_preview_isolation import OriginalMockIsolation
from photobooth.post_preview_ticket import OriginalRecoveryTicketService
from photobooth.post_preview_store import DraftHeld
from tests.post_preview_checkout_fixture import CheckoutFixture


def media_hashes(root):
    return sorted(hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*.jpg'))


def run(root, action, data):
    protected = os.name == 'nt'
    if protected:
        protector = platform_protector()
    else:
        key = base64.b64decode(data['fixture_key']) if data.get('fixture_key') else os.urandom(32)
        protector = SyntheticAeadProtector(key, fixture=True)
    fixture = CheckoutFixture(root, protector=protector, windows_protected_mock=protected)
    fixture.enable_paid_ticket()
    service = fixture.service
    if action == 'produce':
        service.prepare()
        view = service.start(get_templates(), {'template_a': 2})
        frame = np.zeros((32, 48, 3), dtype=np.uint8)
        for _ in range(3):
            view = service.capture(frame, view['capture_slot'], view['revision'], view['retake'], view['generation'])
        view = service.retake(1)
        view = service.capture(frame, view['capture_slot'], view['revision'], view['retake'], view['generation'])
        service.compose()
        view = service.next()
        view = service.freeze_checkout(view['revision'], view['amount'])
        proof = view['ccp_offer'].qr_payload
        service.ccp_visible(view['ccp_offer'])
        view = service.begin_payment()
        fixture.provider.state(view['payment']['attempts'][0]['provider_order_id'], 'settlement')
        service.check_payment('connectivity')
        offer = service.prepare_ticket()['ticket_offer']
        original = {'proof': proof, 'group': service.group, 'provider_rows': fixture.provider.rows,
                    'ticket_digest': hashlib.sha256(offer.qr_payload.encode()).hexdigest(),
                    'media_hashes': media_hashes(root), 'entitlement': service._payment['entitlement_id'],
                    'scope': 'WINDOWS_DPAPI_MOCK_SERVICE' if protected else 'SYNTHETIC_PIPE_KEY_ONLY'}
        if not protected:
            original['fixture_key'] = base64.b64encode(key).decode()
        service.retire('APP_SUSPENDED')
        isolation = OriginalMockIsolation(service.ledger, fixture.backend, fixture.jobs,
            fixture.launch_lease, printer_lane=service._receipt_lane, allow_incomplete_fixture=True)
        op = isolation.prepare('PB001')
        if data.get('checkpoint') != 'prepared':
            isolation.acknowledge('PB001', op)
        if data.get('uncertain_after_prepare'):
            with service.ledger.write():
                service.ledger.db.execute("UPDATE pp_ticket_presentations SET receipt_state='UNCERTAIN'")
        original['operation_id'] = op
        original['generation'] = service.ledger.db.execute('SELECT generation FROM pp_drafts').fetchone()[0]
        # Private fixture channel only: the parent retains simulated customer
        # proof in memory and forwards it over stdin, never argv/env/file/log.
        print(json.dumps(original), flush=True)
        os._exit(73)
    try:
        fixture.provider.rows = data['provider_rows']  # independent fake provider, not local PAID authority
        initial = service.prepare()
        if action == 'busy':
            service.ledger.create('PB001', 'visitor-B', {'template_b': 1})
        if action == 'vault-failure':
            def unavailable(*_args, **_kwargs):
                raise VaultUnavailable('Injected original OS-vault access failure')
            # Model missing OS access without bypassing immutable ciphertext
            # triggers or editing protected original credentials.
            protector.unprotect = unavailable
        ccp = OriginalCCPService(service.ledger, protector, 'MTEST', allow_synthetic=not protected)
        ticket = OriginalRecoveryTicketService(fixture.backend, protector, allow_synthetic=not protected)
        claim = OriginalMockClaim(fixture.backend, ccp, ticket, allow_incomplete_fixture=True,
                                  allow_windows_protected_mock=protected)
        before_reads = fixture.provider.reads
        result = None
        if action.startswith('preack'):
            from photobooth.kiosk_v2.recovery import LaunchLease
            foreign = LaunchLease(root/'foreign') if action == 'preack-foreign-lock' else None
            isolation = OriginalMockIsolation(service.ledger, fixture.backend, fixture.jobs,
                foreign or fixture.launch_lease, printer_lane=service._receipt_lane,
                allow_incomplete_fixture=True)
            try:
                operation = isolation.restore_prepared_after_process_exit('PB001', data['operation_id'])
                if operation != data['operation_id']:
                    raise AssertionError('Original operation identity changed')
                isolation.acknowledge('PB001', operation)
                service.reset_after_acked_isolation(operation)
            except DraftHeld:
                result = {'state':'ISOLATION_HOLD'}
            finally:
                if foreign is not None: foreign.close()
        if result is None:
            result = claim.claim(data['group'], 'PB001', data['proof'])
        observation = {'scope': data['scope'], 'boot_phase': initial['phase'],
            'operation_state':service.ledger.db.execute('SELECT state FROM pp_isolation_ops').fetchone()[0],
            'boot_private_offer': 'ticket_offer' in initial or 'ccp_offer' in initial,
            'state': result['state'], 'new_charges': fixture.provider.charges,
            'provider_reads': fixture.provider.reads-before_reads,
            'new_receipt_sends': len(fixture.receipt_sizes),
            'media_unchanged': media_hashes(root) == data['media_hashes']}
        if result['state'] == 'REACQUIRED':
            view = service.recover_original_owed(result['lease'], data['group'])
            observation.update(phase=view['phase'], entitlement_matches=view['payment']['entitlement_id']==data['entitlement'],
                               generation=result['lease'].generation, old_generation=data['generation'])
            try:
                offer = service.prepare_ticket()['ticket_offer']
            except VaultUnavailable:
                observation['state'] = 'VAULT_HOLD'
            else:
                observation['same_original_ticket'] = hashlib.sha256(offer.qr_payload.encode()).hexdigest()==data['ticket_digest']
        db = service.ledger.db
        observation.update(owed=db.execute('SELECT status FROM pp_paid_services').fetchone()[0],
            attempts=db.execute('SELECT count(*) FROM pp_payment_attempts').fetchone()[0],
            retakes=db.execute('SELECT sum(retake_consumed) FROM pp_templates').fetchone()[0],
            copies=db.execute('SELECT sum(copies) FROM pp_templates WHERE draft_id=(SELECT draft_id FROM pp_checkout_intents LIMIT 1)').fetchone()[0],
            ticket_issues=db.execute("SELECT count(*) FROM pp_events WHERE event='TICKET_CREATED'").fetchone()[0],
            receipt_state=db.execute('SELECT receipt_state FROM pp_ticket_presentations').fetchone()[0],
            original_ack=db.execute('SELECT operation_id FROM pp_isolation_ops').fetchone()[0]==data['operation_id'])
        print(json.dumps(observation))
    finally:
        fixture.close()


if __name__ == '__main__':
    run(Path(sys.argv[1]), sys.argv[2], json.loads(sys.stdin.read() or '{}'))
