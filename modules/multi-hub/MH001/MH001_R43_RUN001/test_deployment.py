"""Offline deployment checks: real reviewed configs; mocked transport; fixed RFC test keys."""
import base64
import copy
import io
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

import deployment as d
import provider_launcher
import observer
import hub
import requester
import wire


class ConfigurationIntegration(unittest.TestCase):
    def setUp(self):
        self.a, self.b = d.verify_baseline()

    def test_three_reviewed_config_hashes(self):
        for name, expected in d.LIVE_HASHES.items():
            self.assertEqual(d.sha(d.ROOT / 'frozen_R43/live_review_R43' / name), expected)

    def test_static_routes_and_compatibility(self):
        self.assertEqual(self.a['routes']['PROVIDER_A']['endpoint'], {'host': '192.168.1.118', 'port': 18090})
        self.assertEqual(self.a['routes']['PROVIDER_B']['endpoint'], self.b['listen'])
        self.assertEqual(self.b['routes']['PROVIDER_B']['endpoint'], {'host': '192.168.1.107', 'port': 18091})
        self.assertEqual((self.a['timeout_seconds'], self.b['timeout_seconds']), (15, 10))

    def test_requester_actual_approved_destinations_only(self):
        approved = requester.load_approved_hubs(d.ROOT / 'frozen_R43/live_review_R43/approved_hubs.json')
        self.assertEqual(approved, frozenset((('192.168.1.100', 18080), ('192.168.1.106', 18081))))
        for endpoint in (self.a['listen'], self.b['listen']):
            self.assertEqual(requester.validate_destination(endpoint, approved), endpoint)
        for endpoint in ({'host': '192.168.1.100', 'port': 8080}, {'host': '192.168.1.107', 'port': 9090},
                         self.a['routes']['PROVIDER_A']['endpoint']):
            with self.assertRaises(ValueError):
                requester.validate_destination(endpoint, approved)

    def run_handler(self, config, packet, connect):
        handler = hub.Handler.__new__(hub.Handler)
        handler.connection = types.SimpleNamespace(settimeout=lambda timeout: None)
        handler.rfile, handler.wfile = io.BytesIO(packet), io.BytesIO()
        logs = []
        handler.server = types.SimpleNamespace(config=config, sequence=0, observe=logs.append)
        with patch.object(wire, 'connect', side_effect=connect):
            handler.handle()
        return handler.wfile.getvalue(), logs

    def packet(self, provider):
        body = b'\x00opaque provider-bound bytes\xff'
        return (b'POST /ingest?x=%2f HTTP/1.1\r\nHost: original.invalid\r\nX-MH-Destination: '
                + provider.encode() + b'\r\nX-Proof:\t opaque  \r\nContent-Length: '
                + str(len(body)).encode() + b'\r\n\r\n' + body)

    def test_actual_live_routes_preserve_bytes_without_network(self):
        class Downstream:
            def __init__(self, address, deliveries, route_b):
                self.address, self.deliveries, self.route_b = address, deliveries, route_b
            def __enter__(self): return self
            def __exit__(self, *unused): return False
            def sendall(self, packet): self.packet = packet; self.deliveries.append((self.address, packet))
            def makefile(self, unused):
                if self.route_b and self.address == self.route_b['listen']:
                    reply, _ = test.run_handler(self.route_b, self.packet, connect)
                    return io.BytesIO(reply)
                return io.BytesIO(b'HTTP/1.0 204 No Content\r\n\r\n')
        test = self
        for start in (self.a, self.b):
            for provider in ('PROVIDER_A', 'PROVIDER_B'):
                with self.subTest(hub=start['hub_id'], provider=provider):
                    deliveries = []
                    def connect(address, timeout):
                        return Downstream(address, deliveries, self.b)
                    packet = self.packet(provider)
                    reply, logs = self.run_handler(start, packet, connect)
                    terminal = self.a['routes']['PROVIDER_A']['endpoint'] if provider == 'PROVIDER_A' else self.b['routes']['PROVIDER_B']['endpoint']
                    self.assertEqual(deliveries[-1][0], terminal)
                    self.assertEqual(len(deliveries), 2 if start['hub_id'] == 'HUB_A' and provider == 'PROVIDER_B' else 1)
                    self.assertTrue(reply.startswith(b'HTTP/1.1 204'))
                    for _, delivered in deliveries:
                        self.assertEqual(delivered.split(b'\r\n\r\n')[1], packet.split(b'\r\n\r\n')[1])
                        self.assertIn(b'X-Proof:\t opaque  \r\n', delivered)
                        self.assertIn(b'X-MH-Destination: ' + provider.encode() + b'\r\n', delivered)
                    self.assertEqual(logs[-1]['transport_result'], 'response_forwarded')

    def test_failure_has_one_attempt_no_reroute(self):
        for config in (self.a, self.b):
            attempts = []
            def unavailable(endpoint, timeout):
                attempts.append(endpoint)
                raise TimeoutError('offline injected failure')
            response, _ = self.run_handler(config, self.packet('PROVIDER_B'), unavailable)
            self.assertEqual(attempts, [config['routes']['PROVIDER_B']['endpoint']])
            self.assertTrue(response.startswith(b'HTTP/1.1 504'))

    def test_provider_plans_distinct_and_direct_observer(self):
        plans = [d.provider_plan(d.read(d.ROOT / 'configs' / (role + '.json'))) for role in d.EXPECTED]
        self.assertNotEqual(plans[0]['source'], plans[1]['source'])
        self.assertNotEqual(plans[0]['ledger'], plans[1]['ledger'])
        for plan in plans:
            self.assertIn('/MULTI_HUB_001/MH001_R43_RUN001/', plan['source'])
            self.assertEqual(plan['observer_url'], 'http://192.168.1.102:9191/boundary')
            self.assertNotIn('MP005', plan['ledger'])
            self.assertNotIn('MP006', plan['ledger'])

    def test_inspection_does_not_import_provider(self):
        with patch.object(d, 'load_module', side_effect=AssertionError('provider import forbidden')):
            for role in d.EXPECTED:
                result = provider_launcher.inspect(d.read(d.ROOT / 'configs' / (role + '.json')))
                self.assertEqual(result['status'], 'PREPARATION_ONLY_NO_PROVIDER_IMPORTED')

    def test_overrides_are_configuration_only(self):
        config = d.read(d.ROOT / 'configs/provider_a.json')
        module = types.SimpleNamespace()
        sentinel = object()
        module.consume_authorization = sentinel
        provider_launcher.configure(module, config, d.provider_plan(config))
        self.assertIs(module.consume_authorization, sentinel)
        self.assertEqual(set(vars(module)), {'consume_authorization', 'HOST', 'PORT', 'ASSOCIATION_URL',
                                            'CONSUME_LEDGER_PATH', 'SPENT_STATE_PATH', 'EXECUTION_LOG_PATH'})

    def test_start_without_approval_rejects_before_import(self):
        with patch.object(provider_launcher.sys, 'platform', 'linux'), \
                patch.object(d, 'load_module', side_effect=AssertionError('provider imported')), \
                patch.object(d, 'no_redirect', return_value=d.ROOT):
            with self.assertRaisesRegex(ValueError, 'STOP_1'):
                provider_launcher.start(d.ROOT / 'configs/provider_a.json', None)

    def test_historical_run_root_rejected(self):
        config = d.read(d.ROOT / 'configs/provider_a.json')
        config['run_root'] = '/home/seth/MULTI_PROVIDER_006/MH001_R43_RUN001'
        with self.assertRaises(ValueError): d.provider_plan(config)

    def test_observer_config_is_preparation_only(self):
        config = d.read(d.ROOT / 'configs/observer.json')
        plan = observer.observer_plan(config)
        self.assertEqual(config['listen'], {'host': '192.168.1.102', 'port': 9191})
        self.assertEqual(plan['log'].name, 'observer.jsonl')


class ObserverFixtures(unittest.TestCase):
    """Public RFC 8032 vectors 1/2; fixed seed loading, never key generation."""
    SEEDS = {'PROVIDER_A': '9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60',
             'PROVIDER_B': '4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb'}
    PUBLIC = {'PROVIDER_A': 'd75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a',
              'PROVIDER_B': '3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c'}

    def setUp(self):
        temporary = d.ROOT / 'validation/temporary'
        temporary.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=temporary)
        self.root = Path(self.temp.name)
        self.root.resolve().relative_to(temporary.resolve())
        self.addCleanup(self.temp.cleanup)
        self.run = 'MH001_R43_FIXTURE'
        self.rec = observer.recorder()
        self.plan = {'root': self.root, 'registry': self.root / 'association/provider_registry.json',
                     'trust': self.root / 'trust/provider_keys.json', 'log': self.root / 'observer.jsonl',
                     'config_path': d.ROOT / 'configs/observer.json'}
        self.ids, self.signers = {}, {}
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        registry, trust = {}, {}
        for provider in self.PUBLIC:
            public = bytes.fromhex(self.PUBLIC[provider])
            kid = 'sha256:' + observer.h.digest(public)
            self.signers[provider] = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(self.SEEDS[provider]))
            key_path = self.root / 'association/trust' / (provider.lower() + '_public.pem')
            key_path.parent.mkdir(parents=True, exist_ok=True)
            der = bytes.fromhex('302a300506032b6570032100') + public
            key_path.write_bytes(b'-----BEGIN PUBLIC KEY-----\n' + base64.b64encode(der) + b'\n-----END PUBLIC KEY-----\n')
            registry[provider] = {'key_id': kid, 'public_key_file': 'trust/' + key_path.name}
            trust[provider] = {'issuance_key_id': 'sha256:' + observer.h.digest(provider.encode()), 'boundary_key_id': kid}
            self.ids[provider] = dict(provider_id=provider, authorization_id=observer.h.digest((provider + '-authority').encode()),
                                     authorization_nonce=provider + '-nonce', binding=observer.h.digest((provider + '-binding').encode()),
                                     operation_id=observer.h.digest((provider + '-operation').encode()))
        observer.h.write(self.plan['registry'], {'providers': registry})
        observer.h.write(self.plan['trust'], dict(session=self.run, status='APPROVED_PROVIDER_HOST_KEYS', providers=trust))
        self.rec.LOG_PATH = self.plan['log']
        self.rec.append_record(dict(record_type='SESSION_START', session_id=self.run,
            registry_sha256=d.sha(self.plan['registry']), recorder_sha256=d.sha(d.ROOT / 'observer_support/association_recorder.py'),
            manifest_sha256=d.sha(self.plan['config_path']), contract_sha256=d.sha(d.ROOT / 'REVIEW.md')))

    def event(self, provider, stage, seq, head, reason=None, identity=None):
        identity = dict(identity or self.ids[provider])
        e = dict(identity, version=1, stage=stage, reason_code=reason,
                 key_id='sha256:' + observer.h.digest(bytes.fromhex(self.PUBLIC[provider])),
                 boundary_value=observer.h.digest((stage + str(self.rec.RECORD_SEQ)).encode()),
                 ledger_seq=seq, ledger_head=head)
        signed = self.signers[provider].sign(b'NUVL-MP-BOUNDARY-v1|' + observer.h.canonical(e))
        return dict(alg='Ed25519', event=e, signature=base64.urlsafe_b64encode(signed).rstrip(b'=').decode())

    def append(self, package, source=None):
        provider = package['event']['provider_id']
        raw = observer.h.canonical(package)
        self.rec.append_record(dict(record_type='SUBMISSION', session_id=self.run,
            source_addr=source or {'PROVIDER_A': '192.168.1.118', 'PROVIDER_B': '192.168.1.107'}[provider],
            raw_body_b64=base64.b64encode(raw).decode()))

    def capture(self, name, provider, consumed):
        identity = self.ids[provider]
        entry = dict(version=1, provider_id=provider, ledger_seq=1,
                     authorization_id=identity['authorization_id'], authorization_nonce=identity['authorization_nonce'],
                     operation_id=identity['operation_id'], previous_entry_hash=None)
        entry['entry_hash'] = observer.h.digest(observer.ledger.TAG + observer.ledger.canonical(entry))
        rows = [entry] if consumed else []
        ledger_raw = b''.join(observer.ledger.canonical(e) + b'\n' for e in rows)
        snapshot = dict(version=1, spent={identity['authorization_id']: {'nonce': identity['authorization_nonce']}} if consumed else {},
                        ledger_seq=len(rows), ledger_head=entry['entry_hash'] if consumed else None)
        state_raw = observer.ledger.canonical(snapshot)
        execution_raw = observer.h.canonical(dict(authorization_id=identity['authorization_id'],
                           operation_id=identity['operation_id'], result='executed')) + b'\n' if consumed else b''
        folder = self.root / name
        folder.mkdir()
        for file, data in (('consume_ledger.jsonl', ledger_raw), ('spent_state.json', state_raw), ('execution.jsonl', execution_raw)):
            (folder / file).write_bytes(data)
        state_path = d.provider_plan(d.read(d.ROOT / 'configs' / (provider.lower() + '.json')))['snapshot']
        meta = dict(state_path=state_path, ledger_path=state_path.replace('_spent_state.json', '_consume_ledger.jsonl'),
                    authorization_id=identity['authorization_id'], spent_sha256=observer.h.digest(state_raw), spent_length=len(state_raw),
                    spent_count=int(consumed), authorization_present=consumed, execution_sha256=observer.h.digest(execution_raw),
                    execution_length=len(execution_raw), execution_line_count=int(consumed), matching_execution_count=int(consumed),
                    execution_log_exists=True)
        meta.update(observer.ledger.inspect(ledger_raw, provider, identity['authorization_id'], snapshot))
        observer.h.write(folder / 'snapshot.json', meta)
        return folder, entry['entry_hash']

    def test_fresh_start_complete_both_independent_providers(self):
        for provider in self.PUBLIC:
            before, _ = self.capture(provider + '-before', provider, False)
            checked = observer.checkpoint(self.plan, self.run, self.ids[provider], before, 'fresh')
            after, head = self.capture(provider + '-after', provider, True)
            for stage in ('START', 'COMPLETE'): self.append(self.event(provider, stage, 1, head))
            self.assertEqual(observer.verify_outcome(self.plan, checked, after)['status'], 'VERIFIED_PROVIDER_OUTCOME')

    def test_T03_auth_spent_required_both_providers(self):
        for provider in self.PUBLIC:
            before, head = self.capture(provider + '-before', provider, True)
            checked = observer.checkpoint(self.plan, self.run, self.ids[provider], before, 'replay')
            after, _ = self.capture(provider + '-after', provider, True)
            self.append(self.event(provider, 'DENY', 1, head, 'auth_spent'))
            self.assertEqual(observer.verify_outcome(self.plan, checked, after)['status'], 'VERIFIED_PROVIDER_OUTCOME')

    def test_wrong_denial_reason_is_not_T03_success(self):
        before, head = self.capture('before', 'PROVIDER_A', True)
        checked = observer.checkpoint(self.plan, self.run, self.ids['PROVIDER_A'], before, 'replay')
        after, _ = self.capture('after', 'PROVIDER_A', True)
        self.append(self.event('PROVIDER_A', 'DENY', 1, head, 'policy_denied'))
        self.assertEqual(observer.verify_outcome(self.plan, checked, after)['status'], 'FAIL')

    def test_previous_denial_blocks_replay_checkpoint(self):
        before, head = self.capture('before', 'PROVIDER_B', True)
        self.append(self.event('PROVIDER_B', 'DENY', 1, head, 'auth_spent'))
        with self.assertRaisesRegex(ValueError, 'already_in_prehistory'):
            observer.checkpoint(self.plan, self.run, self.ids['PROVIDER_B'], before, 'replay')

    def test_missing_signed_evidence_cannot_pass(self):
        before, _ = self.capture('before', 'PROVIDER_A', True)
        checked = observer.checkpoint(self.plan, self.run, self.ids['PROVIDER_A'], before, 'replay')
        after, _ = self.capture('after', 'PROVIDER_A', True)
        with self.assertRaisesRegex(ValueError, 'outcome_missing'):
            observer.verify_outcome(self.plan, checked, after)

    def test_signature_tampering_rejected(self):
        before, head = self.capture('before', 'PROVIDER_A', True)
        checked = observer.checkpoint(self.plan, self.run, self.ids['PROVIDER_A'], before, 'replay')
        after, _ = self.capture('after', 'PROVIDER_A', True)
        package = self.event('PROVIDER_A', 'DENY', 1, head, 'auth_spent')
        signature = bytearray(base64.urlsafe_b64decode(package['signature'] + '=='))
        signature[0] ^= 1
        package['signature'] = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
        self.append(package)
        with self.assertRaisesRegex(observer.h.HarnessError, 'signature invalid'):
            observer.verify_outcome(self.plan, checked, after)

    def test_valid_signature_wrong_ledger_head_fails(self):
        before, _ = self.capture('before', 'PROVIDER_B', True)
        checked = observer.checkpoint(self.plan, self.run, self.ids['PROVIDER_B'], before, 'replay')
        after, _ = self.capture('after', 'PROVIDER_B', True)
        self.append(self.event('PROVIDER_B', 'DENY', 99, '0' * 64, 'auth_spent'))
        self.assertEqual(observer.verify_outcome(self.plan, checked, after)['status'], 'FAIL')

    def test_hub_origin_is_not_direct_provider_evidence(self):
        before, head = self.capture('before', 'PROVIDER_A', True)
        checked = observer.checkpoint(self.plan, self.run, self.ids['PROVIDER_A'], before, 'replay')
        after, _ = self.capture('after', 'PROVIDER_A', True)
        self.append(self.event('PROVIDER_A', 'DENY', 1, head, 'auth_spent'), source='192.168.1.100')
        with self.assertRaisesRegex(ValueError, 'directly_from_provider'):
            observer.verify_outcome(self.plan, checked, after)

    def test_prehistory_truncation_detected(self):
        before, _ = self.capture('before', 'PROVIDER_A', True)
        checked = observer.checkpoint(self.plan, self.run, self.ids['PROVIDER_A'], before, 'replay')
        after, _ = self.capture('after', 'PROVIDER_A', True)
        self.plan['log'].write_bytes(b'')
        with self.assertRaisesRegex(ValueError, 'prehistory'):
            observer.verify_outcome(self.plan, checked, after)

    def test_historical_key_ids_and_unready_trust_rejected(self):
        path = self.root / 'invalid-trust.json'
        value = d.read(self.plan['trust'])
        value['providers']['PROVIDER_A']['boundary_key_id'] = next(iter(d.FORBIDDEN_KEYS))
        observer.h.write(path, value)
        with self.assertRaisesRegex(ValueError, 'nonhistorical'):
            d.public_trust(path, self.run)
        with self.assertRaises(ValueError):
            d.public_trust(d.ROOT / 'configs/provider_keys.template.json', 'MH001_R43_RUN001')

    def test_validly_signed_wrong_binding_does_not_correlate(self):
        before, head = self.capture('before', 'PROVIDER_B', True)
        checked = observer.checkpoint(self.plan, self.run, self.ids['PROVIDER_B'], before, 'replay')
        after, _ = self.capture('after', 'PROVIDER_B', True)
        identity = dict(self.ids['PROVIDER_B'], binding='wrong-but-signed')
        self.append(self.event('PROVIDER_B', 'DENY', 1, head, 'auth_spent', identity))
        with self.assertRaisesRegex(observer.h.HarnessError, 'identity mismatch'):
            observer.verify_outcome(self.plan, checked, after)

    def test_replay_new_execution_cannot_pass(self):
        before, head = self.capture('before', 'PROVIDER_A', True)
        checked = observer.checkpoint(self.plan, self.run, self.ids['PROVIDER_A'], before, 'replay')
        after, _ = self.capture('after', 'PROVIDER_A', True)
        # Change raw evidence AND coherent execution metadata, so this tests the
        # replay invariant rather than merely detecting a metadata hash mismatch.
        raw = (after / 'execution.jsonl').read_bytes() * 2
        (after / 'execution.jsonl').write_bytes(raw)
        meta = d.read(after / 'snapshot.json')
        meta.update(execution_sha256=observer.h.digest(raw), execution_length=len(raw),
                    execution_line_count=2, matching_execution_count=2)
        (after / 'snapshot.json').write_bytes(observer.h.canonical(meta))
        self.append(self.event('PROVIDER_A', 'DENY', 1, head, 'auth_spent'))
        self.assertEqual(observer.verify_outcome(self.plan, checked, after)['status'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
