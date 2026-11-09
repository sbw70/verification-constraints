
# MH001 — Independent Provider Event Association

## Purpose

This directory contains the provider registry and public signing keys used by the independent MH001 observer.

The observer receives signed execution and denial events directly from Provider A and Provider B. It verifies their identities and signatures, records the results, and supports subsequent correlation with provider consumption and execution evidence.

**Session:** `MH001_R43_RUN001`

**Role:** Independent event verification and evidence association

The observer does not authorize operations, forward execution requests, or control provider state.

## 1. Directory Contents

```text
association/
├── provider_registry.json
└── trust/
    ├── provider_a_public.pem
    ├── provider_b_public.pem
    └── README.md
```

| Artifact | Purpose |
|---|---|
| `provider_registry.json` | Maps each provider to its approved boundary-event signing key |
| `trust/provider_a_public.pem` | Verifies Provider A boundary events |
| `trust/provider_b_public.pem` | Verifies Provider B boundary events |

The `trust/README.md` documents the original key fingerprints and individual signature-verification procedure.

## 2. Registered Provider Identities

The registry contains exactly two provider identities.

### PROVIDER_A

Public key:

`trust/provider_a_public.pem`

Registered key ID:

`sha256:43938d000689ef68e298d69c19dd2b5879efc7daf27e6af8bd099f577c91c789`

### PROVIDER_B

Public key:

`trust/provider_b_public.pem`

Registered key ID:

`sha256:9ab1cd6d33fea596624f7d2a0e93442746bee9c97ad237d338c23b4385ebb445`

Both key IDs are calculated from the raw Ed25519 public-key bytes, not from the PEM file bytes.

The registry does not contain private keys.

## 3. Relationship to Approved Provider Trust

The scored-run root contains:

`trust/provider_keys.json`

This separate trust record identifies the approved provider-host keys, including distinct issuance and boundary-event signing identities.

Its recorded status is:

`APPROVED_PROVIDER_HOST_KEYS`

The observer's `load_registry()` function requires:

1. The correct session identity.
2. Approved provider-host trust.
3. Exactly `PROVIDER_A` and `PROVIDER_B`.
4. Each registry key ID matching the corresponding approved boundary key ID.
5. The expected public-key path for each provider.
6. Valid Ed25519 public-key material with matching raw-key fingerprints.

A registry mismatch is a startup precondition failure.

The observer must not substitute an unknown provider, unexpected key, or alternate trust directory.

The registry is not an independent source of execution authority.

## 4. Registry and Key Integrity

The original SHA-256 values are:

| File | SHA-256 |
|---|---|
| `provider_registry.json` | `893cd6153db95ba93016c894adfd3f4c577921a3bd9c9bfc935eda9951ac76e7` |
| `trust/provider_a_public.pem` | `4575b0b5fe2b4b6bf90c80313c889dc44b415e9bf73af0bcbc39b8ac1e4dee6c` |
| `trust/provider_b_public.pem` | `f6255b7402eeebb16b92917ce47e48cc03ecee003530816f2951e1f17b5d75af` |

All three original files are included in:

`evidence/MH001_FINAL_SHA256SUMS.txt`

The manifest paths are relative to the `MH001_R43_RUN001/` root.

### Verify All Three Files

From the scored-run root on Linux:

```bash
grep '  association/' evidence/MH001_FINAL_SHA256SUMS.txt | sha256sum -c -
```

Expected: three successful checks.

This verifies file integrity, not provider signatures.

## 5. Independently Check Registry Trust

The following offline check validates the registry against the approved provider trust and the actual public-key fingerprints.

It requires Python 3 and `cryptography`.

Run from `MH001_R43_RUN001/`:

```bash
python3 -B - <<'PY'
import json
import hashlib
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

registry_path = Path("association/provider_registry.json")
registry = json.loads(registry_path.read_bytes())
trust = json.loads(Path("trust/provider_keys.json").read_bytes())

assert trust["session"] == "MH001_R43_RUN001"
assert trust["status"] == "APPROVED_PROVIDER_HOST_KEYS"
assert set(registry) == {"providers"}

expected = {"PROVIDER_A", "PROVIDER_B"}

assert set(registry["providers"]) == expected
assert set(trust["providers"]) == expected

for role in sorted(expected):
    entry = registry["providers"][role]

    relative = f"trust/{role.lower()}_public.pem"

    assert entry["public_key_file"] == relative

    key_path = registry_path.parent / relative
    public_key = serialization.load_pem_public_key(
        key_path.read_bytes()
    )

    assert isinstance(public_key, Ed25519PublicKey)

    raw = public_key.public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw
    )

    key_id = "sha256:" + hashlib.sha256(raw).hexdigest()

    assert entry["key_id"] == key_id
    assert trust["providers"][role]["boundary_key_id"] == key_id

    print("PASS:", role)

print("PASS: registry and approved boundary-key identities match")
PY
```

Expected result:

```text
PASS: PROVIDER_A
PASS: PROVIDER_B
PASS: registry and approved boundary-key identities match
```

This command does not contact the network or alter the historical evidence.

It establishes key identity consistency. Verification of individual signed provider events is documented in `trust/README.md`.

## 6. Independent Observer Operation

The observer implementation is preserved at the scored-run root:

- `observer.py`
- `observer_launcher.py`
- `observer_support/association_recorder.py`
- `observer_support/common.py`

The observer ran on the HP OmniBook at:

`192.168.1.102:9191`

The providers submitted their signed boundary events directly to the observer endpoint:

`/boundary`

The events did not travel through Hub A or Hub B.

This provides a separate evidence path from the execution-request forwarding path.

### Event Verification

For an incoming signed event, the observer:

1. Identifies the claimed provider.
2. Finds its registered public key.
3. Checks the claimed signing-key ID.
4. Verifies the Ed25519 signature.
5. Records the original signed envelope.
6. Records the verification result.
7. Appends the result to its hash-linked observer log.

An unknown provider, incorrect key ID, or invalid signature must not be treated as an authenticated provider event.

The observer records received events; it does not decide whether the provider should execute.

## 7. Recorded Evidence

The successful observer session is preserved at:

`evidence/observer.jsonl`

The original record contains:

- One SESSION_START.
- Fourteen provider event submissions.
- One SESSION_END.

The SESSION_START includes the registry SHA-256:

`893cd6153db95ba93016c894adfd3f4c577921a3bd9c9bfc935eda9951ac76e7`

This matches the original registry file.

All 14 provider submissions recorded valid signatures, matching registry identities, and successful verification codes.

An independent reviewer should reverify the signatures using the original envelopes and public keys rather than relying exclusively on those recorded flags.

## 8. Association Across Providers

The observer associates evidence from two independent provider domains.

It does not merge their execution authority.

Each provider retains its own:

- Authorization issuance keys.
- Boundary-event signing keys.
- Consumption ledger.
- Spent-authority state.
- Execution history.
- Authorization decisions.

Provider A does not need to trust Provider B's authorization or signing keys.

Provider B does not need to wait for Provider A's execution decision.

The observer can record and correlate their separate outcomes without becoming a shared authorization authority.

This distinction is central to MH001's architecture.

## 9. Critical T03 Evidence

During T03, the original consumed T01 requests were replayed through Hub B.

The independent observer recorded:

| Record sequence | Provider | Signed outcome |
|---|---|---|
| 10 | PROVIDER_A | DENY / auth_spent |
| 11 | PROVIDER_B | DENY / auth_spent |

Each denial was authenticated against the corresponding provider's registered boundary-event public key.

The signed events identify their original T01 authorizations.

Neither provider recorded an additional consumption or execution for the replay.

The observer proves the provenance of the signed decisions. Provider-ingress captures and provider-local state independently establish delivery and consumption behavior.

## 10. Reproduction Requirements

For a new, separately authorized experiment:

1. Establish independent provider-controlled issuance and boundary-signing identities.
2. Export each provider's boundary-event public key.
3. Calculate its raw Ed25519 public-key fingerprint.
4. Create a registry containing exactly the reviewed provider identities.
5. Match those identities against the approved provider-host trust.
6. Verify the registry and keys before starting the observer.
7. Establish a dedicated observer endpoint and exclusive evidence log.
8. Record signed provider events directly from the providers.
9. Verify each provider signature independently.
10. Preserve the completed observer session and its original file hashes.
11. Correlate the signed outcomes with independent provider-ingress and persistent-state evidence.

A new experiment must use a separate registry, trust state, and evidence session.

The original public keys remain published for exact historical verification.

Do not substitute historical key identities into a new operational trust domain.

## 11. Preservation Boundary

The original registry and two public-key files belong to the 132-file scored evidence inventory.

This README and the trust-directory README are supplemental documentation.

Do not change the original registry, replace public keys, or regenerate historical fingerprints.

Do not rewrite observer records to match altered trust.

A failed registry or signature check must remain a reported verification failure.

## Conclusion

The MH001 association directory provides an independently verifiable mapping between two providers and their signed execution decisions.

**The observer can verify and associate provider outcomes without receiving authority to originate, enlarge, reuse, or redirect either provider's authorization.**
