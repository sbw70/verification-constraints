"""MP006 R01 orchestration; frozen MP005 implements all security checks."""
import argparse
import base64
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
REF = ROOT / 'reference' / 'MP005'
sys.path.insert(0, str(REF / 'harness'))
import common as h
import ledger_evidence as ledger

FILES = ('provider_a_consume_ledger.jsonl', 'provider_a_spent_state.json',
         'provider_a_execution.jsonl')


def configuration():
    c = h.read(ROOT / 'configs/MP006_R01.json')
    if not re.fullmatch(r'MP006_[A-Za-z0-9_-]+', c['session']):
        raise h.PreconditionError('Invalid MP006 session label')
    return c


def paths(c):
    return (ROOT / 'state' / c['session'] / 'provider_a',
            ROOT / 'evidence' / c['session'] / 'R01')


def verify(c):
    h.verify_sources(REF)
    h.verify_harness(REF)
    if h.digest((REF / 'provider_a/provider_a.py').read_bytes()) != c['provider_sha256']:
        raise h.PreconditionError('Frozen Provider A hash mismatch')


def permission(c, action, authorization):
    if not authorization:
        raise h.PreconditionError('Explicit MP006 operator authorization required')
    a = h.read(authorization)
    if (c['status'] != 'REVIEWED_FOR_OPERATOR_RUN' or
            not all(c[k] for k in ('addresses_verified', 'autostart_reviewed_disabled',
                                   'operator_preflight_complete')) or
            a.get('authorized') is not True or a.get('session') != c['session'] or
            action not in a.get('allowed_actions', []) or
            a.get('config_sha256') != h.digest((ROOT / 'configs/MP006_R01.json').read_bytes())):
        raise h.PreconditionError('Unreviewed configuration or action not authorized')


def boot_id():
    h.require_linux()
    return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


def stopped(c):
    """No source imports; also catches historical MP005 provider processes."""
    h.require_linux()
    listeners = subprocess.run(['ss', '-H', '-ltn'], check=True, capture_output=True,
                               text=True).stdout.splitlines()
    if any(len(line.split()) > 3 and
           line.split()[3].rsplit(':', 1)[-1] == str(c['provider_port']) for line in listeners):
        raise h.PreconditionError('Provider port already listening')
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit() or int(entry.name) == os.getpid():
            continue
        try:
            args = (entry / 'cmdline').read_bytes().split(b'\0')
        except FileNotFoundError:
            continue
        if any(b'provider_a.py' in arg for arg in args) or (
                b'--provider' in args and b'provider_a' in args) or (
                b'_serve' in args and any(b'mp006.py' in arg for arg in args)):
            raise h.PreconditionError('Provider process already present')


def raw_capture(state, out):
    """Copy every present byte BEFORE parsing state, verifying code, or checking processes."""
    out.mkdir(parents=True, exist_ok=False)
    records = []
    for name in FILES:
        source = state / name
        item = {'source': str(source), 'name': name}
        try:
            data = source.read_bytes()
        except FileNotFoundError:
            item['present'] = False
        else:
            h.raw_write(out / name, data)
            item.update(present=True, length=len(data), sha256=h.digest(data))
        records.append(item)
    h.write(out / 'raw_capture.json', {'captured_utc': h.utc(), 'files': records})
    h.inventory(out)


def snapshot(state, case, label, aid, pid):
    process = h.process_identity(pid, REF / 'provider_a/provider_a.py', state / FILES[1],
                                 ROOT / 'mp006.py', 'provider_a')
    out = case / label
    h.state_snapshot(state / FILES[1], state / FILES[2], aid, out)
    h.write(out / 'process.json', process)


def saved(case, label):
    return ledger.validate_saved(case / label, h.validate_snapshot(case / label))


def recovery_checks(before, after, expected):
    return {'same_host': before['hostname'] == after['hostname'],
            'changed_boot_id': bool(before['boot_id']) and bool(after['boot_id']) and
                               before['boot_id'] != after['boot_id'],
            'same_runtime': before['runtime_path'] == after['runtime_path'],
            'same_source_hash': before['runtime_sha256'] == after['runtime_sha256'] == expected,
            'same_state_path': before['state_path'] == after['state_path'],
            'same_command': before['command_line'] == after['command_line'],
            'same_cwd': before['cwd'] == after['cwd']}


def boundaries(case, name, log):
    folder = 'fresh' if name == 'fresh' else 'original'
    identity = h.read(case / folder / 'identity.json')
    out = case / ('send_' + name)
    records = (h.correlate(REF, log, h.read(out / 'cursor.json'), identity)
               if name == 'replay' else h.read(out / 'boundary_records.json'))
    return h.validate_boundary_records(REF, records, identity)


def replay_safety(case, log):
    try:
        before, after = saved(case, 'before_replay'), saved(case, 'after_replay')
        events = boundaries(case, 'replay', log)
        checks = {**h.replay_assertions(before, after, events),
                  **ledger.replay_checks(before, after, events)}
        return 'REPLAY_REJECTED_WITHOUT_ADDITIONAL_CONSUMPTION_OR_EXECUTION' if all(checks.values()) else 'REPLAY_SAFETY_NOT_ESTABLISHED'
    except Exception:
        return 'REPLAY_SAFETY_NOT_EVALUABLE'


def send_checks(c, case):
    checks = {}
    for kind in ('consume', 'replay', 'fresh'):
        identity, request, header = h.preserved_request(case / ('fresh' if kind == 'fresh' else 'original'))
        sent = h.read(case / ('send_' + kind) / 'send.json')
        checks[kind + '_preserved_bytes'] = (
            sent['identity'] == identity and sent['url'] == c['relay_url'] and
            base64.b64decode(sent['request_b64'], validate=True) == request and
            sent['headers']['X-Provider-A-Authorization'] == header and
            sent['headers']['X-Verification-Context'] == identity['context'])
    return checks


def score(c, case, log):
    pre, consumed, before, after, fresh_pre, fresh_after = [saved(case, label) for label in
        ('pre_consume', 'consumed', 'before_replay', 'after_replay', 'before_fresh', 'after_fresh')]
    initial_events, replay_events, fresh_events = [boundaries(case, name, log)
                                                for name in ('consume', 'replay', 'fresh')]
    original_id = h.read(case / 'original/identity.json')['authorization_id']
    fresh_id = h.read(case / 'fresh/identity.json')['authorization_id']
    initial = ledger.advance_checks(pre, consumed, initial_events)
    initial['fresh_genesis'] = pre['ledger_entry_count'] == pre['execution_line_count'] == 0
    initial['original_identity'] = pre['authorization_id'] == consumed['authorization_id'] == original_id
    initial['original_executed_once'] = consumed['matching_execution_count'] == 1
    replay = {**h.replay_assertions(before, after, replay_events),
              **ledger.replay_checks(before, after, replay_events)}
    fresh = ledger.advance_checks(fresh_pre, fresh_after, fresh_events)
    fresh['separate_authority'] = original_id != fresh_id
    fresh['fresh_identity'] = fresh_pre['authorization_id'] == fresh_after['authorization_id'] == fresh_id
    fresh['previously_unspent'] = not fresh_pre['authorization_present'] and not fresh_pre['ledger_authorization_present']
    continuity = {key: consumed[key] == before[key] for key in
                  ('ledger_sha256', 'spent_sha256', 'execution_sha256', 'state_path')}
    continuity['fresh_follows_replay'] = all(after[k] == fresh_pre[k] for k in
                                            ('ledger_sha256', 'spent_sha256', 'execution_sha256'))
    old = h.read(case / 'consumed/process.json')
    new = h.read(case / 'before_replay/process.json')
    recovery = recovery_checks(old, new, c['provider_sha256'])
    for labels, expected in ((('pre_consume', 'consumed'), old),
            (('before_replay', 'after_replay', 'before_fresh', 'after_fresh'), new)):
        for label in labels:
            process = h.read(case / label / 'process.json')
            recovery[label + '_same_process'] = all(process[k] == expected[k] for k in
                ('hostname', 'boot_id', 'pid', 'start_ticks', 'runtime_path', 'runtime_sha256',
                 'state_path', 'command_line', 'cwd', 'executable'))
            recovery[label + '_same_state'] = saved(case, label)['state_path'] == expected['state_path']
    raw = case / 'recovered_before_start'
    capture = h.read(raw / 'raw_capture.json')
    for item in capture['files']:
        if item.get('present'):
            data = (raw / item['name']).read_bytes()
            if h.digest(data) != item['sha256'] or len(data) != item['length']:
                raise h.HarnessError('Recovered raw evidence changed')
    continuity['raw_history_preserved'] = all(
        (raw / name).read_bytes() == (case / 'consumed' / copied).read_bytes()
        for name, copied in zip(FILES, ('consume_ledger.jsonl', 'spent_state.json', 'execution.jsonl')))
    capture_check = h.read(case / 'recovery_capture_check.json')
    recovery['captured_before_start'] = capture_check['provider_stopped'] is True
    recovery['capture_boot_matches'] = capture_check['boot_id'] == new['boot_id']
    operator = h.read(case / 'power_procedure.json')
    procedure = {k: operator.get(k) is True for k in
                 ('physical_disconnect', 'power_loss_approved', 'idle_confirmed', 'initial_evidence_preserved_on_omnibook',
                  'recovered_raw_preserved_on_omnibook')}
    procedure['documented_interval'] = all(isinstance(operator.get(k), str) and operator[k].strip()
                                         for k in ('disconnected_utc', 'reconnected_utc', 'operator'))
    witness = [json.loads(line) for line in (case / 'reachability.jsonl').read_text(encoding='utf-8-sig').splitlines()]
    stages = 0
    for row in witness:
        if row['target'] != c['provider_host'] or not row.get('utc'):
            raise h.HarnessError('Witness target/timestamp missing or mismatched')
        if stages == 0 and row['status'] == 'Success': stages = 1
        elif stages == 1 and row['status'] in ('TimedOut', 'DestinationHostUnreachable',
                                               'DestinationNetworkUnreachable'): stages = 2
        elif stages == 2 and row['status'] == 'Success': stages = 3
    procedure['reachable_unreachable_reachable'] = stages == 3
    sends = send_checks(c, case)
    groups = dict(initial=initial, recovery=recovery, continuity=continuity,
                  replay=replay, fresh=fresh, procedure=procedure, sends=sends)
    if not all(sends.values()): status = 'HARNESS_ERROR'
    elif not all(initial.values()) or not all(recovery.values()): status = 'PRECONDITION_NOT_MET'
    elif not all(replay.values()) or not all(continuity.values()) or not all(fresh.values()): status = 'FAIL'
    elif not all(procedure.values()): status = 'INCOMPLETE'
    else: status = 'PASS'
    return {'status': status,
            'safety_result': 'REPLAY_REJECTED_WITHOUT_ADDITIONAL_CONSUMPTION_OR_EXECUTION'
                             if all(replay.values()) else 'REPLAY_SAFETY_NOT_ESTABLISHED',
            'checks': groups, 'timestamp_comparisons_scored': False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action', choices=['inspect', 'initialize', 'prepare', 'capture', 'send',
        'checkpoint', 'recover-capture', 'validate-recovered', 'launch', '_serve', 'marker', 'score'])
    ap.add_argument('--authorization', type=Path)
    ap.add_argument('--pid', type=int)
    ap.add_argument('--label', choices=['pre_consume', 'consumed', 'before_replay',
                                      'after_replay', 'before_fresh', 'after_fresh'])
    ap.add_argument('--kind', choices=['consume', 'replay', 'fresh'], default='consume')
    ap.add_argument('--log', type=Path)
    ap.add_argument('--tag', choices=['initial', 'recovered'], default='initial')
    ap.add_argument('--provider', choices=['provider_a'])
    ap.add_argument('--state-dir', type=Path)
    a = ap.parse_args()
    c = configuration()
    state, case = paths(c)
    if a.action == '_serve' and (a.provider != 'provider_a' or a.state_dir != state):
        raise h.PreconditionError('Detached child state/provider mismatch')
    if a.action == 'recover-capture':
        # Preserve raw bytes even if subsequent configuration/identity checks fail.
        h.require_linux()
        raw_capture(state, case / 'recovered_before_start')
        stopped(c)
        h.write(case / 'recovery_capture_check.json',
                {'boot_id': boot_id(), 'provider_stopped': True, 'utc': h.utc()})
    verify(c)
    if a.action == 'inspect':
        print(json.dumps({'status': 'LOCAL_INSPECTION_ONLY', 'session': c['session'],
                          'state': str(state), 'evidence': str(case), 'config': c}, indent=2))
        return
    if a.action == 'recover-capture': return
    if a.action == 'validate-recovered':
        raw = case / 'recovered_before_start'
        ledger_raw = (raw / FILES[0]).read_bytes()
        snapshot_raw = (raw / FILES[1]).read_bytes()
        original_id = h.read(case / 'original/identity.json')['authorization_id']
        result = ledger.inspect(ledger_raw, 'PROVIDER_A', original_id,
                                json.loads(snapshot_raw, object_pairs_hook=ledger.unique))
        unchanged = all((raw / name).read_bytes() == (case / 'consumed' / copied).read_bytes()
                        for name, copied in zip(FILES, ('consume_ledger.jsonl', 'spent_state.json', 'execution.jsonl')))
        if not result['snapshot_matches_ledger'] or not unchanged:
            raise h.PreconditionError('Recovered state differs; preserve and review without repair')
        h.write(case / 'recovered_validation.json', {'status': 'PASS', 'ledger': result})
        return
    if a.action == 'marker':
        print('MP006-R01 — PROVIDER A\nUTC: ' + h.utc() + '\nBOOT_ID: ' + boot_id() +
              '\nSTATUS: ' + ('RECOVERED' if a.tag == 'recovered' else 'READY FOR POWER LOSS'))
        return
    if a.action == 'score':
        if not a.log: raise h.PreconditionError('Continuous association log required')
        try:
            result = score(c, case, a.log)
        except FileNotFoundError as ex:
            result = {'status': 'INCOMPLETE', 'error': str(ex), 'safety_result': replay_safety(case, a.log)}
        except Exception as ex:
            result = {'status': 'HARNESS_ERROR', 'error': str(ex), 'safety_result': replay_safety(case, a.log)}
        h.write(case / 'case_results.json', result)
        h.inventory(case)
        print(json.dumps(result, indent=2))
        if result['status'] != 'PASS': sys.exit(2)
        return
    permission(c, a.action, a.authorization)
    if a.action in ('initialize', 'launch', '_serve', 'capture'):
        h.require_linux()
        if ROOT != Path(c['linux_root']): raise h.PreconditionError('Unexpected Linux root')
    if a.action == 'initialize':
        stopped(c)
        state.mkdir(parents=True, exist_ok=False)
        ledger.bootstrap(state, 'provider_a')
    elif a.action == 'prepare':
        folder = 'fresh' if a.kind == 'fresh' else 'original'
        h.prepare_authority(REF, 'provider_a', case / folder,
                            'MP006_R01_' + folder.upper(), c['session'])
    elif a.action == 'capture':
        if not a.pid or not a.label: raise h.PreconditionError('PID and label required')
        identity = h.read(case / ('fresh' if 'fresh' in a.label else 'original') / 'identity.json')
        snapshot(state, case, a.label, identity['authorization_id'], a.pid)
    elif a.action == 'send':
        if not a.log: raise h.PreconditionError('Continuous association log required')
        before_label = dict(consume='pre_consume', replay='before_replay', fresh='before_fresh')[a.kind]
        before = saved(case, before_label)
        folder = case / ('fresh' if a.kind == 'fresh' else 'original')
        identity = h.read(folder / 'identity.json')
        if before['authorization_id'] != identity['authorization_id']:
            raise h.PreconditionError('Wrong pre-send authority snapshot')
        expected_state = str(PurePosixPath(c['linux_root']) / 'state' / c['session'] / 'provider_a' / FILES[1])
        if before['state_path'] != expected_state:
            raise h.PreconditionError('Pre-send snapshot belongs to another state directory')
        if a.kind == 'replay':
            old = h.read(case / 'consumed/process.json')
            new = h.read(case / 'before_replay/process.json')
            if not all(recovery_checks(old, new, c['provider_sha256']).values()):
                raise h.PreconditionError('Changed-boot recovery not established')
            h.read(case / 'operator_checkpoint.json')
            h.read(case / 'recovery_capture_check.json')
        if a.kind == 'fresh':
            replay = boundaries(case, 'replay', a.log)
            if not all(ledger.replay_checks(saved(case, 'before_replay'), saved(case, 'after_replay'), replay).values()):
                raise h.PreconditionError('Replay safety not established')
        out = case / ('send_' + a.kind)
        out.mkdir()
        cursor = h.log_cursor(a.log)
        h.write(out / 'cursor.json', cursor)
        h.send_preserved(folder, c['relay_url'], out)
        records = h.wait_events(REF, a.log, cursor, identity,
                               ['DENY'] if a.kind == 'replay' else ['START', 'COMPLETE'])
        h.write(out / 'boundary_records.json', records)
    elif a.action == 'checkpoint':
        if not a.log: raise h.PreconditionError('Continuous association log required')
        if not all(ledger.advance_checks(saved(case, 'pre_consume'), saved(case, 'consumed'),
                                        boundaries(case, 'consume', a.log)).values()):
            raise h.PreconditionError('Consumption/execution not proven')
        h.write(case / 'operator_checkpoint.json', {'status': 'AWAITING_EXPLICIT_POWER_APPROVAL',
                'utc': h.utc(), 'boot_id': h.read(case / 'consumed/process.json')['boot_id']})
    elif a.action == 'launch':
        stopped(c)
        if a.tag == 'recovered':
            captured = h.read(case / 'recovery_capture_check.json')
            if captured['boot_id'] != boot_id(): raise h.PreconditionError('Capture is from another boot')
            if h.read(case / 'recovered_validation.json')['status'] != 'PASS':
                raise h.PreconditionError('Review preserved recovery state before startup')
        runtime = case / 'runtime'
        runtime.mkdir(parents=True, exist_ok=True)
        with (runtime / (a.tag + '.log')).open('xb') as log:
            command = ['nohup', sys.executable, '-u', '-B', str(ROOT / 'mp006.py'), '_serve',
                       '--authorization', str(a.authorization.resolve()),
                       '--provider', 'provider_a', '--state-dir', str(state)]
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True, cwd='/home/seth')
        h.write(runtime / (a.tag + '.pid.json'), {'pid': process.pid, 'command': command})
        print('Detached PID recorded; verify actual listener, process identity and log before continuing.')
    elif a.action == '_serve':
        # Only deployment constants change. No provider functions are replaced.
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        spec = importlib.util.spec_from_file_location('mp006_frozen_provider_a', REF / 'provider_a/provider_a.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.HOST = '0.0.0.0'
        module.PORT = c['provider_port']
        module.ASSOCIATION_URL = c['association_url']
        module.CONSUME_LEDGER_PATH, module.SPENT_STATE_PATH, module.EXECUTION_LOG_PATH = [state / n for n in FILES]
        module.main()


if __name__ == '__main__':
    try:
        main()
    except (h.PreconditionError, h.HarnessError, OSError, ValueError, KeyError) as ex:
        print(json.dumps({'status': 'PRECONDITION_NOT_MET' if isinstance(ex, h.PreconditionError)
                          else 'HARNESS_ERROR', 'error': str(ex)}), file=sys.stderr)
        sys.exit(2)
