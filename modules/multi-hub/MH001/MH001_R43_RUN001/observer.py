"""Independent MH001 evidence correlation using frozen MP005 signature/ledger checks."""
import base64
import json
from pathlib import Path
import sys
import deployment as d

sys.path.insert(0, str(d.ROOT / 'observer_support'))
import common as h
import ledger_evidence as ledger


def recorder():
    d.verify_baseline()
    return d.load_module(d.ROOT / 'observer_support/association_recorder.py', 'mh001_recorder')


def observer_plan(config):
    run = d.session(config)
    root = Path(config['run_root'])
    if not root.is_absolute() or root.name != run or root.parent.name != 'MULTI_HUB_001':
        raise ValueError('isolated_observer_run_root_required')
    if d.routes.endpoint(config['listen']) != {'host': '192.168.1.102', 'port': 9191}:
        raise ValueError('independent_observer_endpoint_required')
    return {'root': root, 'registry': root / 'association/provider_registry.json',
            'trust': root / 'trust/provider_keys.json',
            'log': root / 'evidence/observer.jsonl', 'config_path': d.ROOT / 'configs/observer.json'}


def load_registry(plan, run):
    approved = d.public_trust(plan['trust'], run)
    registry = d.read(d.no_redirect(plan['registry']))
    if set(registry) != {'providers'} or set(registry['providers']) != {'PROVIDER_A', 'PROVIDER_B'}:
        raise ValueError('exact_new_observer_registry_required')
    for role, item in registry['providers'].items():
        expected_file = 'trust/' + role.lower() + '_public.pem'
        if item != {'key_id': approved['providers'][role]['boundary_key_id'], 'public_key_file': expected_file}:
            raise ValueError('registry_key_or_path_mismatch')
        d.no_redirect(plan['root'] / 'association' / expected_file)
    return recorder().load_registry(plan['registry'])


def session_records(path, run):
    raw = Path(path).read_bytes()
    if not raw or not raw.endswith(b'\n'):
        raise ValueError('complete_observer_prehistory_required')
    rows = [json.loads(line, object_pairs_hook=d.routes.unique) for line in raw.splitlines()]
    if rows[0].get('record_type') != 'SESSION_START':
        raise ValueError('observer_SESSION_START_required')
    previous = '0' * 64
    canonical = recorder().canonical_bytes
    for seq, row in enumerate(rows, 1):
        if (row.get('session_id') != run or type(row.get('record_seq')) is not int or
                row['record_seq'] != seq or row.get('prev_record_hash') != previous or
                row.get('record_hash') != h.digest(canonical({k: v for k, v in row.items() if k != 'record_hash'}))):
            raise ValueError('observer_session_chain_invalid')
        if seq > 1 and row.get('record_type') == 'SESSION_START':
            raise ValueError('observer_session_restarted')
        if row.get('record_type') == 'SESSION_END' and seq != len(rows):
            raise ValueError('records_after_SESSION_END')
        previous = row['record_hash']
    return raw, rows


def snapshot(folder):
    return ledger.validate_saved(folder, h.validate_snapshot(folder))


def checked_history(plan, run):
    raw, rows = session_records(plan['log'], run)
    expected = {'registry_sha256': d.sha(plan['registry']),
                'recorder_sha256': d.sha(d.ROOT / 'observer_support/association_recorder.py'),
                'manifest_sha256': d.sha(plan['config_path']), 'contract_sha256': d.sha(d.ROOT / 'REVIEW.md')}
    if any(rows[0].get(key) != value for key, value in expected.items()):
        raise ValueError('observer_session_source_config_or_trust_changed')
    return raw, rows


def checkpoint(plan, run, identity, before_folder, mode):
    if mode not in ('fresh', 'replay'):
        raise ValueError('expected_fresh_or_replay')
    load_registry(plan, run)
    before = snapshot(before_folder)
    if before['authorization_id'] != identity['authorization_id']:
        raise ValueError('snapshot_authority_mismatch')
    if identity['provider_id'] not in ('PROVIDER_A', 'PROVIDER_B'):
        raise ValueError('independent_provider_identity_required')
    provider = d.provider_plan(d.read(d.ROOT / 'configs' / (identity['provider_id'].lower() + '.json')))
    if before['state_path'] != provider['snapshot'] or before['ledger_path'] != provider['ledger']:
        raise ValueError('isolated_MH001_provider_snapshot_required')
    raw, rows = checked_history(plan, run)
    if rows[-1]['record_type'] == 'SESSION_END':
        raise ValueError('observer_already_stopped')
    prior = h.correlate(plan['root'], plan['log'], {'byte_offset': 0, 'prefix_sha256': h.digest(b'')}, identity)
    if mode == 'replay' and any(row['event']['stage'] == 'DENY' for row in prior):
        raise ValueError('T03_matching_denial_already_in_prehistory')
    if mode == 'fresh' and prior:
        raise ValueError('fresh_authority_already_observed')
    return {'session': run, 'mode': mode, 'identity': identity, 'before_snapshot': before,
            'before_folder': str(Path(before_folder).resolve()),
            'trust_sha256': d.sha(plan['trust']),
            'cursor': {'byte_offset': len(raw), 'prefix_sha256': h.digest(raw)},
            'prior_envelopes': [row['raw_body_b64'] for row in prior]}


def verify_outcome(plan, checked, after_folder):
    run, identity = checked['session'], checked['identity']
    load_registry(plan, run)
    if checked['trust_sha256'] != d.sha(plan['trust']):
        raise ValueError('provider_trust_changed_since_checkpoint')
    _, rows = checked_history(plan, run)
    records = h.correlate(plan['root'], plan['log'], checked['cursor'], identity)
    events = h.validate_boundary_records(plan['root'], records, identity)
    if not records:
        raise ValueError('fresh_signed_provider_outcome_missing')
    if any(row['raw_body_b64'] in checked['prior_envelopes'] for row in records):
        raise ValueError('old_signed_envelope_reused')
    if any(type(e.get('ledger_seq')) is not int or e['ledger_seq'] < 0 for e in events):
        raise ValueError('signed_ledger_sequence_invalid')
    expected_host = d.read(d.ROOT / 'configs' / (identity['provider_id'].lower() + '.json'))['listen']['host']
    by_seq = {row['record_seq']: row for row in rows}
    if any(by_seq[row['record_seq']].get('source_addr') != expected_host for row in records):
        raise ValueError('signed_outcome_not_received_directly_from_provider')
    before, after = checked['before_snapshot'], snapshot(after_folder)
    if snapshot(checked['before_folder']) != before:
        raise ValueError('pre_send_snapshot_changed')
    if (after['authorization_id'] != identity['authorization_id'] or
            before['state_path'] != after['state_path'] or before['ledger_path'] != after['ledger_path']):
        raise ValueError('provider_snapshot_identity_or_path_changed')
    if checked['mode'] == 'replay':
        assertions = {**h.replay_assertions(before, after, events), **ledger.replay_checks(before, after, events)}
    else:
        assertions = ledger.advance_checks(before, after, events)
        assertions['authority_was_unspent'] = not before['authorization_present'] and not before['ledger_authorization_present']
    return {'status': 'VERIFIED_PROVIDER_OUTCOME' if all(assertions.values()) else 'FAIL',
            'provider_id': identity['provider_id'], 'mode': checked['mode'], 'checks': assertions,
            'records': records, 'execution_inferred_from_hub_response': False,
            'scored_case_PASS': False, 'remaining': 'Independent provider ingress and full operator/scorer evidence required'}
