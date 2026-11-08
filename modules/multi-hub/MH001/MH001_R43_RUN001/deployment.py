"""MH001 deployment checks. Imports no providers and never initializes state."""
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'frozen_R43'))
sys.path.insert(0, str(ROOT / 'frozen_R43/provider_support'))
import routes

EXPECTED = {'provider_a': '79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6',
            'provider_b': '618ec76ef5dd3bfa3ba7b1ad3941ed0516a7511b72957d7efb82ec565905b605'}
LIVE_HASHES = {'hub_a.json': 'f4e50329e17949365f7c3aef96a33853b5b0d1a33a2b851c107f1601453ec083',
               'hub_b.json': 'f6c8fa3e0e7a3368ca4bd615aafd89b1f4149ccdb2bb7b799179ef6fc5569936',
               'approved_hubs.json': '4588635b63ebc1dee6ca15b3de930726edb503cd3032a93d66bf79ba8b2c54b8'}
# Fingerprints only; no historical public or private key is installed or loaded.
FORBIDDEN_KEYS = frozenset(('sha256:f696894568a361fcaf5441bf803c761d4245268ddc4e68d7d8a05e179a9649c0',
    'sha256:e4664ee3b7bb0012fb7d8f763c9df74594d8a6bec8488d97532a5846cc04b6ff',
    'sha256:13fc04bc84273db73c38a2442117cad0874d7e5c088139d4655acdca00953fe6',
    'sha256:db764408aa319642363057d804f0c2a3d2c7dd22de86ae4a6d6549cb97f60225'))


def read(path):
    return json.loads(Path(path).read_bytes(), object_pairs_hook=routes.unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite_json')))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_baseline():
    baseline = read(ROOT / 'BASELINE.json')
    for relative, expected in baseline['files'].items():
        if sha(ROOT / relative) != expected:
            raise ValueError('frozen_dependency_changed: ' + relative)
    for name, expected in LIVE_HASHES.items():
        if sha(ROOT / 'frozen_R43/live_review_R43' / name) != expected:
            raise ValueError('live_review_hash_mismatch: ' + name)
    return routes.validate_pair(ROOT / 'frozen_R43/live_review_R43/hub_a.json',
                                ROOT / 'frozen_R43/live_review_R43/hub_b.json')


def session(config):
    if config['project'] != 'MULTI_HUB_001' or not re.fullmatch(r'MH001_R43_[A-Za-z0-9_-]+', config['session']):
        raise ValueError('MH001_session_required')
    return config['session']


def provider_plan(config):
    run = session(config)
    role = config['role']
    if role not in EXPECTED or config['provider_id'] != role.upper():
        raise ValueError('provider_identity_mismatch')
    root = PurePosixPath(config['run_root'])
    if not root.is_absolute() or root.name != run or root.parent.name != 'MULTI_HUB_001' or '..' in root.parts:
        raise ValueError('isolated_MH001_run_root_required')
    a, b = verify_baseline()
    endpoint = routes.endpoint(config['listen'])
    if endpoint != a['routes'][role.upper()]['endpoint'] and role == 'provider_a':
        raise ValueError('provider_A_route_mismatch')
    if endpoint != b['routes'][role.upper()]['endpoint']:
        raise ValueError('provider_route_mismatch')
    if config['observer_url'] != 'http://192.168.1.102:9191/boundary':
        raise ValueError('direct_observer_endpoint_required')
    source = root / 'providers' / role / (role + '.py')
    mint_name = 'mint_authorization_' + role[-1] + '.py'
    state = root / 'state' / role
    return {'root': str(root), 'source': str(source), 'source_sha256': EXPECTED[role],
            'mint_source': str(source.parent / mint_name),
            'mint_sha256': sha(ROOT / 'frozen_R43/providers' / role / mint_name),
            'keys': {suffix: str(source.parent / (role + '_' + suffix + '.pem')) for suffix in
                     ('issuance_private', 'issuance_public', 'private', 'public')},
            'ledger': str(state / (role + '_consume_ledger.jsonl')),
            'snapshot': str(state / (role + '_spent_state.json')),
            'execution': str(state / (role + '_execution.jsonl')),
            'trust': str(root / 'trust/provider_keys.json'), 'listen': endpoint,
            'observer_url': config['observer_url']}


def public_trust(path, run):
    trust = read(path)
    if trust['session'] != run or trust['status'] != 'APPROVED_PROVIDER_HOST_KEYS':
        raise ValueError('new_provider_host_trust_not_approved')
    if set(trust['providers']) != {'PROVIDER_A', 'PROVIDER_B'}:
        raise ValueError('two_independent_provider_keys_required')
    ids = [entry[k] for entry in trust['providers'].values() for k in ('issuance_key_id', 'boundary_key_id')]
    if (len(set(ids)) != 4 or any(not isinstance(k, str) or
            re.fullmatch(r'sha256:[0-9a-f]{64}', k) is None or k in FORBIDDEN_KEYS for k in ids)):
        raise ValueError('fresh_distinct_nonhistorical_key_ids_required')
    return trust


def require_approval(path, config_path, trust_path):
    if path is None:
        raise ValueError('STOP_1_operator_approval_required')
    approval = read(path)
    if approval.get('authorized') is not True or approval.get('phase') != 'LIVE_STARTUP':
        raise ValueError('STOP_1_operator_approval_required')
    config = read(config_path)
    if approval.get('session') != session(config) or approval.get('config_sha256') != sha(config_path):
        raise ValueError('approval_config_or_session_mismatch')
    if approval.get('trust_sha256') != sha(trust_path):
        raise ValueError('approved_trust_hash_required')
    required = ('deployment.py', 'provider_launcher.py', 'observer.py', 'observer_launcher.py',
                'frozen_R43/hub.py', 'frozen_R43/routes.py', 'frozen_R43/wire.py',
                'frozen_R43/requester.py', 'observer_support/common.py',
                'observer_support/association_recorder.py', 'frozen_R43/provider_support/ledger_evidence.py')
    for relative in required:
        if approval.get('source_sha256', {}).get(relative) != sha(ROOT / relative):
            raise ValueError('approval_source_hash_mismatch: ' + relative)


def no_redirect(path):
    path = Path(path)
    if path.is_symlink() or path.resolve() != path.absolute():
        raise ValueError('redirected_path_forbidden: ' + str(path))
    return path
