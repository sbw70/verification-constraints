# MULTI_HUB_001 — MH001 R4.3 local build

This package implements two independent mechanical hubs, a requester adapter,
byte-identical MP005 provider preparations, and sequential offline mock tests.
Read `validation/requester_allowlist/LOCAL_VALIDATION.json` for the latest validation outcome.
The original 18-test record remains unchanged under `validation/final/`.
Nothing in this package is deployed. No lab-host contact, provider signing-key
generation, scored transaction, service change, or GitHub publication is part of
the local validation.

| Deliverable | Location |
|---|---|
| Single-threaded hub | `hub.py` |
| Opaque HTTP framing/transport | `wire.py` |
| Strict topology loader/pair validation | `routes.py` |
| Separate local configurations | `configs/hub_a.json`, `configs/hub_b.json` |
| Requester adapter (no minting/signing) | `requester.py` |
| Isolated, unchanged provider/mint source | `providers/provider_a/`, `providers/provider_b/` |
| Provider installation/key/state preparation | `PROVIDER_PREPARATION.md` |
| Byte-capturing mocks | `test_offline.py` |
| Validation runner | `validate_local.py` |
| Published source and verification | `provenance/`, `verify_provider_sources.py` |
| Source review | `SOURCE_REVIEW.md` |
| Deployment and scoring prerequisites | `OPERATOR_GATES.md` |
| Package/source/configuration hashes | `SHA256SUMS.txt` |

All new runtime hub/requester code uses only the Python standard library. The
unchanged providers retain their existing `cryptography` dependency; they are not
imported or executed in offline validation. Python 3.9+ is required for the new
code; actual Pi/Pavilion/provider Python versions must be inventoried later.

The frozen local configurations use **loopback only**, ports 18080/18081 for hubs
and 18090/18091 for mock providers. They are review artifacts, not verified live
addresses. Tests use additional temporary loopback endpoints to avoid port
conflicts. Runtime configurations are loaded once, validated together before
either hub starts, and never reloaded. The suite includes separate hub subprocesses;
each process serves one connection/request at a time.

To repeat offline validation from this directory, choose a new output directory:

```powershell
python -B validate_local.py --output validation/repeat-001
```

That runs sequential loopback mocks only, including a real 10-second timeout.
It never starts an actual MP005/MP006 provider. The initial OS-temp sandbox denial
and subsequent approved rerun are disclosed in the final validation record.

Do not use the mock test artifacts as provider authority. The tests deliberately
transport nonsense opaque authority and use no signing keys, including mock keys.
The requester CLI permits loopback by default. Remote sends require the optional
`send --approved-hubs configs/approved_hubs.json` configuration and an exact
canonical literal IP/port match. The shipped list is empty. No remote bypass exists.
It never reads hub routing configuration. Only after verified live addresses and
explicit STOP 1 approval may an operator populate and hash that separate list.
An entry has the form `{"host":"<verified-literal-IP>","port":<verified-port>}`
inside `{"approved_hubs":[...]}`; no DNS names or scoped addresses are supported.
Loopback still works without this option. The same policy applies to `submit()`. Its `prepare` action
accepts only already-issued package bytes and constructs the outer provider-bound
artifact; it does not mint authority or verify signatures on the provider's behalf.
See `SOURCE_REVIEW.md` for the explicit requester adaptation and HTTP framing limits.

Actual provider keys and persistent state remain absent from these preparations.
Do not run a provider source file on the OmniBook. Future live endpoints, provider
setup, observer configuration, ingress capture, rehearsal, and scored execution
require the gates in `OPERATOR_GATES.md`.

STOP after local validation. Await operator authorization for the next phase.
