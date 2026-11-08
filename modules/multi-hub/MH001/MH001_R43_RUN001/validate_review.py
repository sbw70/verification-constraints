"""Separate offline validation. No provider/observer startup, key generation or lab contact."""
import argparse
from datetime import datetime, timezone
import io
import ipaddress
import json
from pathlib import Path
import shlex
import sys
import unittest
from unittest.mock import patch
import deployment as d


def guard(event, args):
    if event in ('socket.connect', 'socket.bind'):
        address = args[1]
        if not isinstance(address, tuple) or not ipaddress.ip_address(address[0]).is_loopback:
            raise RuntimeError('OFFLINE_GUARD_BLOCKED_NON_LOOPBACK_NETWORK')
    if event == 'exec':
        name = args[0].co_filename.replace('\\', '/')
        if name.endswith(('/provider_a.py', '/provider_b.py')):
            raise RuntimeError('OFFLINE_GUARD_BLOCKED_PROVIDER_IMPORT')
    if event == 'subprocess.Popen':
        argv = args[1]
        if isinstance(argv, str):
            argv = [part.strip('"') for part in shlex.split(argv, posix=False)]
        if (not isinstance(argv, (list, tuple)) or str(argv[0]) != sys.executable or
                not any(str(v).endswith('hub.py') for v in argv)):
            raise RuntimeError('OFFLINE_GUARD_BLOCKED_EXTERNAL_COMMAND')
        # Original subprocess tests may start only loopback configs.
        for flag in ('--hub-a', '--hub-b'):
            config = d.routes.load(argv[argv.index(flag) + 1])
            endpoints = [config['listen']] + [r['endpoint'] for r in config['routes'].values()]
            if not all(ipaddress.ip_address(e['host']).is_loopback for e in endpoints):
                raise RuntimeError('OFFLINE_GUARD_BLOCKED_REMOTE_HUB_SUBPROCESS')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.relative_to(d.ROOT / 'validation')
    output.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    d.verify_baseline()
    sys.addaudithook(guard)
    import http.server
    import ledger_evidence
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    import test_offline
    import test_requester
    import test_deployment
    groups = {}
    # Static fixture seeds can be loaded; creation of new signing keys is forbidden.
    with patch.object(Ed25519PrivateKey, 'generate', side_effect=RuntimeError('KEY_GENERATION_FORBIDDEN')), \
            patch.object(http.server, 'ThreadingHTTPServer', side_effect=RuntimeError('OBSERVER_PROVIDER_STARTUP_FORBIDDEN')), \
            patch.object(ledger_evidence, 'bootstrap', side_effect=RuntimeError('PROVIDER_STATE_INITIALIZATION_FORBIDDEN')):
        for label, modules in (('original_R43_29_tests', (test_offline, test_requester)),
                                ('new_deployment_tests', (test_deployment,))):
            suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(module) for module in modules)
            stream = io.StringIO()
            result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
            (output / (label + '.txt')).write_text(stream.getvalue(), encoding='utf-8', newline='\n')
            groups[label] = dict(tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                                 skipped=len(result.skipped), passed=result.wasSuccessful())
    d.verify_baseline()
    original = Path(d.read(d.ROOT / 'BASELINE.json')['original_workspace'])
    original_unchanged = all(d.sha(original / p.relative_to(d.ROOT / 'frozen_R43')) == d.sha(p)
                             for p in (d.ROOT / 'frozen_R43').rglob('*') if p.is_file())
    good = original_unchanged and all(group['passed'] for group in groups.values())
    report = dict(status='LOCAL_DEPLOYMENT_PACKAGE_VALIDATED_NOT_DEPLOYED' if good else 'LOCAL_DEPLOYMENT_VALIDATION_FAILED',
                  started_utc=started, completed_utc=datetime.now(timezone.utc).isoformat(), groups=groups,
                  original_workspace_unchanged=original_unchanged, keys_generated=False,
                  fixed_RFC8032_fixture_seed_loading=True, actual_provider_imports=False,
                  provider_state_initialized=False, observer_started=False, lab_hosts_contacted=False,
                  deployed=False, STOP_1='ACTIVE',
                  live_review_hashes={name: d.sha(d.ROOT / 'frozen_R43/live_review_R43' / name) for name in d.LIVE_HASHES},
                  network_policy='Only original loopback mock hubs; actual live configs exercised with in-memory transports',
                  pending=['Explicit STOP 1 approval', 'Provider-host fresh keys and approved public trust',
                           'Sanctioned new durable state on each provider', 'Actual installed hashes and isolated ports',
                           'Dell MP006 indirect autostart chain still requires live preflight',
                           'Independent provider ingress capture', 'Observer live readiness and authorized rehearsal latency'])
    (output / 'LOCAL_VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(report, indent=2))
    if not good: raise SystemExit(1)


if __name__ == '__main__':
    main()
