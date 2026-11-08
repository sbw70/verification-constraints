"""MH001 provider launcher: inspect offline; run only on approved provider host."""
import argparse
import json
import os
from pathlib import Path
import sys
import deployment as d


def inspect(config):
    return dict(status='PREPARATION_ONLY_NO_PROVIDER_IMPORTED', **d.provider_plan(config))


def configure(module, config, plan):
    # This is the complete override set. No methods, keys, decisions or state content change.
    module.HOST, module.PORT = config['listen']['host'], config['listen']['port']
    module.ASSOCIATION_URL = config['observer_url']
    module.CONSUME_LEDGER_PATH = Path(plan['ledger'])
    module.SPENT_STATE_PATH = Path(plan['snapshot'])
    module.EXECUTION_LOG_PATH = Path(plan['execution'])


def start(config_path, approval):
    config = d.read(config_path)
    plan = d.provider_plan(config)
    if sys.platform != 'linux':
        raise ValueError('provider_host_Linux_required')
    if d.no_redirect(plan['root']) != d.ROOT:
        raise ValueError('launcher_must_be_installed_in_reviewed_MH001_run_root')
    d.require_approval(approval, config_path, plan['trust'])
    trust = d.public_trust(plan['trust'], config['session'])['providers'][config['provider_id']]
    source = d.no_redirect(plan['source'])
    if d.sha(source) != d.EXPECTED[config['role']]:
        raise ValueError('frozen_provider_source_hash_mismatch')
    if d.sha(d.no_redirect(plan['mint_source'])) != plan['mint_sha256']:
        raise ValueError('frozen_provider_mint_hash_mismatch')
    # All key checks occur before provider import. No fallback paths exist.
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    for suffix, field in (('issuance_public', 'issuance_key_id'), ('public', 'boundary_key_id')):
        key_path = d.no_redirect(plan['keys'][suffix])
        key = serialization.load_pem_public_key(key_path.read_bytes())
        if not isinstance(key, Ed25519PublicKey):
            raise ValueError('Ed25519_public_key_required')
        raw = key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        if 'sha256:' + d.hashlib.sha256(raw).hexdigest() != trust[field]:
            raise ValueError('provider_host_key_fingerprint_mismatch')
    for suffix in ('issuance_private', 'private'):
        key_path = d.no_redirect(plan['keys'][suffix])
        if (not key_path.is_file() or key_path.stat().st_mode & 0o077 or
                key_path.stat().st_uid != os.getuid()):
            raise ValueError('provider_private_key_missing_or_permissions_too_open')
    # Fail on uninitialized state; never call bootstrap or repair here.
    d.no_redirect(plan['ledger']).read_bytes()
    d.no_redirect(plan['snapshot']).read_bytes()
    d.no_redirect(plan['execution'])
    module = d.load_module(source, 'mh001_frozen_' + config['role'])
    configure(module, config, plan)
    module.main()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['inspect', 'run'])
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--approval', type=Path)
    args = parser.parse_args()
    if args.action == 'inspect':
        print(json.dumps(inspect(d.read(args.config)), indent=2))
    else:
        start(args.config, args.approval)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        raise SystemExit('PRECONDITION_NOT_MET: ' + str(error))
