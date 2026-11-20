"""Non-scored, no-listener runtime compatibility checks of unchanged MD001 files."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import importlib
import io
import json
from pathlib import Path
import platform
import socket
import ssl
import sys
import traceback
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PROFILES = {'dell': ('3.12.3', '41.0.7'), 'hp': ('3.12.3', '41.0.7'), 'pi': ('3.13.5', '43.0.0')}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--app', type=Path, required=True)
    p.add_argument('--profile', choices=[*PROFILES, 'desktop'], required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    app = a.app.resolve()
    a.out.mkdir(parents=True, exist_ok=False)
    report = dict(profile=a.profile, utc=datetime.now(timezone.utc).isoformat(),
                  python=sys.version, executable=sys.executable, platform=platform.platform(),
                  machine=platform.machine(), ssl_module_openssl=ssl.OPENSSL_VERSION,
                  application=str(app), checks=[], mode='NON_SCORED_NO_NETWORK_NO_SERVICE_RUNTIME_PROBE',
                  requirement_pin_satisfied=None)

    def check(name, value):
        report['checks'].append(dict(name=name, passed=bool(value)))
        if not value:
            raise AssertionError(name)
    try:
        lock = json.loads((HERE / 'APPROVED_APP_FILES.json').read_bytes())
        current = {n: sha((app / n).read_bytes()) for n in lock}
        report['application_sha256'] = current
        check('frozen_application_hashes', current == lock)
        fixture_raw = (HERE / 'FIXTURE.json').read_bytes()
        check('fixture_hash', sha(fixture_raw) == (HERE / 'FIXTURE_SHA256.txt').read_text().split()[0])
        fixture = json.loads(fixture_raw)
        import cryptography
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
        from cryptography.hazmat.backends.openssl.backend import backend
        report.update(cryptography=cryptography.__version__, cryptography_path=cryptography.__file__,
                      cryptography_openssl=backend.openssl_version_text())
        report['cryptography_init_sha256'] = sha(Path(cryptography.__file__).read_bytes())
        rust_binding = importlib.import_module('cryptography.hazmat.bindings._rust')
        binding_file = getattr(rust_binding, '__file__', None)
        report['crypto_binding_path'] = binding_file
        report['crypto_binding_sha256'] = sha(Path(binding_file).read_bytes()) if binding_file else None
        report['requirement_pin_satisfied'] = cryptography.__version__ == '49.0.0'
        if a.profile != 'desktop':
            py, crypto = PROFILES[a.profile]
            check('expected_python_and_upstream_crypto_version', platform.python_version() == py and cryptography.__version__ == crypto)
            check('system_interpreter_and_distro_module', sys.prefix == sys.base_prefix
                  and Path(cryptography.__file__).resolve().is_relative_to('/usr/lib/python3/dist-packages'))
        sys.path.insert(0, str(app / 'runtime'))
        sys.path.insert(0, str(app))
        # No bind/connect, producer send, physical fixture, or authority operation is allowed.
        with patch.object(socket, 'socket', side_effect=AssertionError('socket creation forbidden')), \
             patch.object(socket, 'create_connection', side_effect=AssertionError('connection forbidden')):
            artifact = importlib.import_module('artifact')
            adapter = importlib.import_module('md001')
            observer = importlib.import_module('observe')
            adapter.integrity()
            check('all_application_imports_and_runtime_lock', True)
            for name in ['relay', 'ingress', 'ingress_N01', 'verifier']:
                adapter.config(app / 'configs' / (name + '.json'))
            check('all_config_parsers', True)
            key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(fixture['PUBLIC_TEST_SEED_HEX']))
            pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
            loaded = serialization.load_pem_private_key(pem, password=None)
            check('pem_pkcs8_load_and_type', isinstance(loaded, Ed25519PrivateKey))
            public = loaded.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
            check('raw_public_roundtrip', Ed25519PublicKey.from_public_bytes(public).public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw) == public)
            generated = Ed25519PrivateKey.generate()
            check('ed25519_generate_sign_verify', generated.public_key().verify(generated.sign(b'local runtime probe'), b'local runtime probe') is None)
            raw = base64.b64decode(fixture['artifact_b64'], validate=True)
            check('same_canonical_artifact_and_signature_as_desktop49', artifact.produce(loaded, fixture['artifact_id']) == raw)
            trust = fixture['trust']
            check('desktop49_signature_accepted', artifact.verify(raw, trust)['accepted'])
            changed = json.loads(raw); changed['event']['outcome'] = 'FAILURE'
            rejection = artifact.verify(artifact.canonical_bytes(changed), trust)
            check('tamper_invalid_signature', rejection['reason'] == 'invalid_signature' and rejection['signature_checks'] == 1)
            unknown = json.loads(raw); unknown['event']['key_id'] = 'sha256:' + '0'*64
            check('unknown_key_rejected', artifact.verify(artifact.canonical_bytes(unknown), trust)['reason'] == 'untrusted_producer_key_binding')
            mismatch = json.loads(raw); mismatch['event']['producer_id'] = 'DOMAIN_B'
            check('producer_key_mismatch_rejected', not artifact.verify(artifact.canonical_bytes(mismatch), trust)['accepted'])
            check('malformed_rejected', all(not artifact.verify(x, trust)['accepted'] for x in [b'{', b'[]', raw+b'\n', b'{"event":{},"event":{}}']))
            before = artifact.canonical_bytes(trust)
            repeated = [artifact.verify(raw, trust) for _ in range(3)]
            check('repeat_fresh_checks_no_history_or_producer_network', all(r['accepted'] and r['signature_checks']==1 for r in repeated) and artifact.canonical_bytes(trust)==before)
            event = json.loads(raw)['event']
            check('canonical_order_independent', artifact.canonical_bytes(event) == artifact.canonical_bytes(dict(reversed(list(event.items())))))
            request = b'POST /verify HTTP/1.1\r\nHost: 127.0.0.1\r\nContent-Type: application/json\r\nX-MH-Destination: PROVIDER_B\r\nContent-Length: '+str(len(raw)).encode()+b'\r\n\r\n'+raw
            check('frozen_http_framing_and_observer', observer.extract(request)==raw)
            check('unique_ids', len({json.loads(artifact.produce(loaded))['event']['artifact_id'] for _ in range(5)})==5)
        check('application_still_unchanged', all(sha((app/n).read_bytes())==h for n,h in lock.items()))
    except Exception:
        report['error'] = traceback.format_exc()
    report['passed'] = sum(c['passed'] for c in report['checks'])
    report['failed'] = sum(not c['passed'] for c in report['checks'])
    report['status'] = 'PROBE_PASS_NOT_SCORED' if not report.get('error') and report['failed']==0 else 'PROBE_FAIL_STOP'
    raw = (json.dumps(report, indent=2)+'\n').encode()
    with (a.out/'RESULTS.json').open('xb') as f: f.write(raw)
    with (a.out/'SHA256SUMS.txt').open('x') as f: f.write(sha(raw)+'  RESULTS.json\n')
    print(raw.decode())
    return int(report['status'] != 'PROBE_PASS_NOT_SCORED')


if __name__ == '__main__':
    raise SystemExit(main())
