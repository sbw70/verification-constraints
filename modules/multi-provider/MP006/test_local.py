"""Offline checks only: no providers, sockets, minting or Linux operations."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import mp006 as m
from test_hardening import entry


class LocalChecks(unittest.TestCase):
    def test_frozen_dependencies(self):
        m.verify(m.configuration())

    def test_build_is_not_live_authorization(self):
        with self.assertRaises(m.h.PreconditionError):
            m.permission(m.configuration(), 'launch', None)

    def test_raw_capture_keeps_invalid_bytes_and_absence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state = root / 'state'
            state.mkdir()
            (state / m.FILES[0]).write_bytes(b'partial ledger')
            (state / m.FILES[1]).write_bytes(b'\xffnot JSON')
            out = root / 'capture'
            m.raw_capture(state, out)
            self.assertEqual((out / m.FILES[1]).read_bytes(), b'\xffnot JSON')
            self.assertFalse(m.h.read(out / 'raw_capture.json')['files'][2]['present'])
            self.assertTrue((out / 'SHA256SUMS.txt').is_file())
            with self.assertRaises(FileExistsError):
                m.raw_capture(state, out)

    def test_boot_checks_do_not_compare_ticks_or_time(self):
        before = dict(hostname='dell', boot_id='old', runtime_path='/provider.py',
                      runtime_sha256='frozen', state_path='/state', command_line=['same'], cwd='/home/seth',
                      start_ticks=90000, pid=1)
        after = dict(before, boot_id='new', start_ticks=1, pid=1)
        self.assertTrue(all(m.recovery_checks(before, after, 'frozen').values()))
        self.assertFalse(m.recovery_checks(before, before, 'frozen')['changed_boot_id'])
        after['runtime_sha256'] = 'changed'
        self.assertFalse(m.recovery_checks(before, after, 'frozen')['same_source_hash'])

    def test_consume_does_not_include_later_replay_deny(self):
        with patch.object(m.h, 'read', side_effect=[{}, ['saved-consume']]), \
             patch.object(m.h, 'correlate') as correlate, \
             patch.object(m.h, 'validate_boundary_records', return_value=['verified']) as validate:
            self.assertEqual(m.boundaries(Path('case'), 'consume', Path('log')), ['verified'])
            correlate.assert_not_called()
            self.assertEqual(validate.call_args.args[1], ['saved-consume'])

    def test_replay_rechecks_continuous_log(self):
        with patch.object(m.h, 'read', side_effect=[{}, {}]), \
             patch.object(m.h, 'correlate', return_value=['late-events']) as correlate, \
             patch.object(m.h, 'validate_boundary_records', return_value=[]) as validate:
            m.boundaries(Path('case'), 'replay', Path('log'))
            correlate.assert_called_once()
            self.assertEqual(validate.call_args.args[1], ['late-events'])

    def test_full_score_with_saved_ledger_fixtures(self):
        # Fixture generation reuses MP005's offline entry builder; no provider runs.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state = root / 'state'
            state.mkdir()
            case = root / 'case'
            case.mkdir()
            one = entry('PROVIDER_A', aid='original')
            two = entry('PROVIDER_A', 2, one['entry_hash'], 'fresh')

            def fixture(label, rows, aid):
                raw = b''.join(m.ledger.canonical(row) + b'\n' for row in rows)
                doc = dict(version=1, spent={r['authorization_id']: {'nonce': r['authorization_nonce']} for r in rows},
                           ledger_seq=len(rows), ledger_head=rows[-1]['entry_hash'] if rows else None)
                (state / m.FILES[0]).write_bytes(raw)
                (state / m.FILES[1]).write_bytes(m.ledger.canonical(doc))
                (state / m.FILES[2]).write_bytes(b''.join(m.ledger.canonical({'authorization_id': r['authorization_id']}) + b'\n' for r in rows))
                m.h.state_snapshot(state / m.FILES[1], state / m.FILES[2], aid, case / label)

            for label, rows, aid in [('pre_consume', [], 'original'), ('consumed', [one], 'original'),
                    ('before_replay', [one], 'original'), ('after_replay', [one], 'original'),
                    ('before_fresh', [one], 'fresh'), ('after_fresh', [one, two], 'fresh')]:
                fixture(label, rows, aid)
            fixture('raw_source', [one], 'original')
            m.raw_capture(state, case / 'recovered_before_start')
            process = dict(hostname='dell', boot_id='old', runtime_path='/provider.py',
                           runtime_sha256='frozen', state_path=str(state / m.FILES[1]), command_line=['same'], cwd='/home/seth',
                           pid=123, start_ticks=100, executable='/python3')
            for label in ('pre_consume', 'consumed'):
                m.h.write(case / label / 'process.json', process)
            for label in ('before_replay', 'after_replay', 'before_fresh', 'after_fresh'):
                m.h.write(case / label / 'process.json', dict(process, boot_id='new'))
            m.h.write(case / 'recovery_capture_check.json', {'boot_id': 'new', 'provider_stopped': True})
            for name in ('original', 'fresh'):
                m.h.write(case / name / 'identity.json', {'authorization_id': name})
            m.h.write(case / 'power_procedure.json', dict(operator='offline fixture', disconnected_utc='later date',
                reconnected_utc='earlier clock value', physical_disconnect=True, power_loss_approved=True,
                idle_confirmed=True, initial_evidence_preserved_on_omnibook=True, recovered_raw_preserved_on_omnibook=True))
            witness = case / 'reachability.jsonl'
            witness.write_text('\n'.join(m.json.dumps(dict(target='127.0.0.1', utc='fixture', status=s))
                                        for s in ('Success', 'TimedOut', 'Success')), encoding='utf-8')

            def events(unused, kind, log):
                row = two if kind == 'fresh' else one
                return [dict(stage=stage, reason_code='auth_spent' if stage == 'DENY' else None,
                             ledger_seq=row['ledger_seq'], ledger_head=row['entry_hash'],
                             authorization_id=row['authorization_id'], authorization_nonce=row['authorization_nonce'],
                             operation_id=row['operation_id']) for stage in (['DENY'] if kind == 'replay' else ['START', 'COMPLETE'])]

            c = {'provider_sha256': 'frozen', 'provider_host': '127.0.0.1'}
            with patch.object(m, 'boundaries', side_effect=events), patch.object(m, 'send_checks', return_value={'fixture': True}):
                self.assertEqual(m.score(c, case, Path('unused'))['status'], 'PASS')
                changed = case / 'after_fresh/process.json'
                changed.write_text(m.json.dumps(dict(process, boot_id='unrelated-boot')))
                self.assertEqual(m.score(c, case, Path('unused'))['status'], 'PRECONDITION_NOT_MET')
                changed.write_text(m.json.dumps(dict(process, boot_id='new')))
                witness.write_text(m.json.dumps(dict(target='127.0.0.1', utc='fixture', status='Success')))
                result = m.score(c, case, Path('unused'))
                self.assertEqual(result['status'], 'INCOMPLETE')
                self.assertTrue(result['safety_result'].startswith('REPLAY_REJECTED'))
                (case / 'after_fresh/snapshot.json').unlink()
                self.assertTrue(m.replay_safety(case, Path('unused')).startswith('REPLAY_REJECTED'))

    def test_recorded_send_must_match_preserved_bytes(self):
        identity = {'context': 'signed-context'}
        send = dict(identity=identity, url='relay', request_b64='eA==',
                    headers={'X-Provider-A-Authorization': 'exact-header',
                             'X-Verification-Context': 'signed-context'})
        with patch.object(m.h, 'preserved_request', return_value=(identity, b'x', 'exact-header')), \
             patch.object(m.h, 'read', return_value=send):
            self.assertTrue(all(m.send_checks({'relay_url': 'relay'}, Path('case')).values()))
            send['headers']['X-Provider-A-Authorization'] = 'changed-header'
            self.assertFalse(any(m.send_checks({'relay_url': 'relay'}, Path('case')).values()))


if __name__ == '__main__':
    unittest.main()
