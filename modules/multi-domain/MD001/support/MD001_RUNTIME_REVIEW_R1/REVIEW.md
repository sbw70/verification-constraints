# MD001 frozen application runtime review R1

Finding: SOURCE_API_COMPATIBLE_CANDIDATES_HOST_VALIDATION_PENDING.
No physical host was contacted. No deployment, install, service start, firewall or
network change, or scored test was performed. New work is confined to this sibling
review directory. Existing application bundle, source, hashes and prior validation
are preserved. This review supersedes only the proposed runtime-install procedure
if the operator accepts the explicit runtime exception below.

## Requirement distinction and proposed exception

The frozen requirements.txt is `cryptography==49.0.0`. Neither 41.0.7 nor43.0.0
satisfies that literal dependency constraint. Therefore it is incorrect to claim the
reported installations satisfy every frozen requirement unchanged. Pip would attempt
to obtain49 if instructed to install that file. Do not change it or run pip against it.

Source inspection finds no functional API requirement unique to49. The application
can be a candidate for direct system-Python execution with no source change, venv,
ensurepip, pip, APT or additional package install. The earlier documentation treated
the desktop reproducibility pin as a demonstrated runtime minimum; that was too strict.
This review proposes an explicit, separately recorded deployment-runtime exception:
keep the immutable49 pin as historical desktop environment identity and validate only
the exact installed Linux combinations below as additional deployment profiles.
This is not a claim of full49 dependency resolution or a blanket supported version range.
Accept this exception before using the revised commands to launch services.

| Host | Reported Python | Reported distro python3-cryptography package | Required import version | Status |
|---|---|---|---|---|
| Dell |3.12.3|41.0.7-4ubuntu0.1|41.0.7|Source/API compatible candidate; not host validated|
| HP |3.12.3|41.0.7-4ubuntu0.1|41.0.7|Source/API compatible candidate; not host validated|
| Pi |3.13.5|43.0.0-3+deb13u1|43.0.0|Source/API compatible candidate; not host validated|

Distro package versions and cryptography.__version__ are different identifiers.
Capture both, plus actual executable, module paths, architecture, OS, package status
and crypto-linked OpenSSL version. A backend without working Ed25519 can fail even
when API names exist. An already installed package is not proof the selected interpreter
can import it. Check the actual system interpreter rather than an activated/partial venv.

## Source surface reviewed

All six shipped Python modules: md001.py, observe.py, runtime/artifact.py, hub.py,
routes.py and wire.py. Frozen artifact/hub/wire/routes hashes match RUNTIME_LOCK.json.
All17 bundle content hashes match the archive's APP_SHA256SUMS.txt.

| Use | API / language feature | Compatibility finding |
|---|---|---|
| Producer/keygen |Ed25519PrivateKey.generate, public_key, sign|Present in41.0.7 and43.0.0|
| Private fixture storage/loading |private_bytes(PEM, PKCS8, NoEncryption), load_pem_private_key(password=None)|Present in41.0.7 and43.0.0|
| Trust/fingerprint |public_bytes(Raw, Raw), Ed25519PublicKey.from_public_bytes|Present in41.0.7 and43.0.0|
| Verifier |verify(signature, tagged canonical bytes), InvalidSignature|Present in41.0.7 and43.0.0|
| Encoding |json.dumps sort_keys/separators/ensure_ascii/allow_nan; UTF8; Base64; hashlib SHA256|Python standard-library features available in3.12/3.13|
| Process/evidence |argparse, pathlib exclusive writes/mkdir/chmod, datetime.timezone.utc, uuid4, os|No3.14-specific feature found|
| Transport/relay |http.client, socketserver, socket, threading, HTTPStatus, ipaddress, regex, buffered IO|No3.14-specific feature found; actual network behavior still needs non-scored host validation|

No X509 parser, Rust build tooling, certificate validation, new49 algorithm, PKCS12,
TLS, newer convenience serialization API, or nonstandard crypto package is used.
The relay implementation itself is standard library, but the launcher imports the
artifact module, so Pi still needs an importable cryptography package.

Primary API references inspected:
- https://cryptography.io/en/41.0.7/hazmat/primitives/asymmetric/ed25519/
- https://cryptography.io/en/41.0.7/hazmat/primitives/asymmetric/serialization/
- https://cryptography.io/en/43.0.0/hazmat/primitives/asymmetric/ed25519/
- https://cryptography.io/en/43.0.0/changelog/

These support API availability, not certification of Ubuntu/Debian builds, OpenSSL
linkage, system package integrity, Pi hardware or actual inter-host behavior. This
review does not make a production security/support claim for all older library features.

## Actual desktop checks

Python3.12 grammar parse of all shipped Python modules passed on the desktop parser;
this is not execution under Python3.12. Desktop runtime_probe.py --profile desktop
passed18/18 on Python3.14.3/cryptography49.0.0. This checks the probe itself and generates
a common exact-byte fixture baseline. It does not validate any Linux combination.
Original adapter12 checks and observation6 checks remain as recorded, not rerun.

FIXTURE.json contains an explicitly public synthetic seed and one fixed-ID signed
artifact generated by frozen artifact.py on desktop49. It is not a scored artifact
or a deployable signing key. Every host must accept it and reproduce the identical
canonical artifact/signature bytes. This establishes tested interoperability for
the exact serialization/signature path, not general cryptographic security.

## Revised host runtime acceptance criteria

1. Verify original archive digest, all17 APP_SHA256SUMS entries and review-file hashes.
2. Use `/usr/bin/python3 -B -E -s`; record version/executable, platform/machine and
   distro package version/status. Require the exact profile above and successful
   distro-module import from /usr/lib/python3/dist-packages, with no active venv.
3. Run the separately transferred runtime_probe.py using the appropriate profile.
   It must produce PROBE_PASS_NOT_SCORED with20/20 checks on Linux; any exception
   or mismatch stops. Report requirement_pin_satisfied=false as expected under the
   explicit exception; do not label that as satisfying requirements.txt.
4. Check crypto-linked OpenSSL details in the report. Require actual Ed25519 generation,
   PKCS8 PEM load, raw public-key round trip, sign/verify, desktop fixture acceptance,
   and identical deterministic signature output. InvalidSignature must reject mutation.
5. Require unknown key, producer mismatch, malformed and noncanonical artifact rejection;
   deterministic canonical encoding; unique IDs; repeated fresh acceptance; unchanged
   trust configuration; all config parsers and frozen HTTP extraction functions working.
   The probe forbids socket creation/connect and starts no service. It writes only a
   new review evidence directory, not the application source or prior evidence.
6. After all three host probes pass and the runtime exception is accepted, use revised
   system-Python launches for non-scored application preflight. Need actual correct
   socket binds, original relay->ingress->verifier path, byte equality and responses,
   and both positive and downstream-mutated fixture behavior in a uniquely labeled
   preflight session. This remains distinct from B01/N01/B02 scored cases and must
   retain the already reported OPNsense deny export/log and approved path observations.
7. Preserve captured host reports, stdout/stderr, package inventory and module hashes
   alongside new deployment evidence. Record the accepted runtime exception with
   command/interpreter identity. No physical B01/B02/N01 PASS is conferred by probes.

runtime_probe.py verifies the actual frozen modules; it does not instantiate the
service handlers or bind/listen. Actual process startup, return routing, HTTP forwarding
and capture/reassembly are later host-preflight properties. None has been revalidated
by desktop in this review. No availability claim is made based solely on import tests.

## Updated reported deployment state

Operator reports Dell->Pi HTTP PASS, Pi->HP HTTP PASS, direct Dell->HP BLOCK logged,
and controller SSH to all three. These are accepted handoff facts; no rediscovery is
requested. They do not establish MD001 application forwarding because no application
service has launched. Dell archive/hash verification and17/17 extracted hashes passed.
Dell ensurepip failed and APT retrieval encountered DNS failure, with no upgrades
reported. Leave the possibly partial .venv untouched; never activate or invoke it.
Pi/HP transfers are still pending. No scoring has occurred. No firewall relaxation,
DNS/network change or repeat APT attempt is proposed for the system-package option.

If any exact-profile probe fails, preserve it and STOP. Do not edit the frozen source
to accommodate the failure. OFFLINE_FALLBACK.md supplies the dependency strategy if
the literal49 pin must be retained or installed runtimes prove unusable.
