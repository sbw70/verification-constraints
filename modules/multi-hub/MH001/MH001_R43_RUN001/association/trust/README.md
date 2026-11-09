
# MH001 — Independent Observer Public Keys

## Purpose

This directory preserves the two Ed25519 public keys used by the independent observer to verify provider-signed boundary events during MH001 R4.3.

Each provider signs its own execution and denial events. The observer checks those signatures against an approved provider registry.

The observer does not issue execution authority, and the forwarding hubs do not participate in signature verification.

**Session:** `MH001_R43_RUN001`

**Key role:** Provider boundary-event signature verification

## 1. Directory Contents

```text
trust/
├── provider_a_public.pem
└── provider_b_public.pem
```

Both files contain public keys only.

| File | Signing provider |
|---|---|
| `provider_a_public.pem` | PROVIDER_A |
| `provider_b_public.pem` | PROVIDER_B |

No private signing keys are required to independently verify the historical observer evidence.

## 2. Original File Integrity

Both PEM files are included in the original 132-file scored evidence manifest.

### Provider A

File SHA-256:

`4575b0b5fe2b4b6bf90c80313c889dc44b415e9bf73af0bcbc39b8ac1e4dee6c`

### Provider B

File SHA-256:

`f6255b7402eeebb16b92917ce47e48cc03ecee003530816f2951e1f17b5d75af`

These hashes identify the complete PEM file bytes.

They are different from the public-key identifiers used inside signed events.

### Verify on Linux

From this directory:

```bash
sha256sum provider_a_public.pem
sha256sum provider_b_public.pem
```

### Verify on PowerShell

From this directory:

```powershell
Get-FileHash .\provider_a_public.pem -Algorithm SHA256
Get-FileHash .\provider_b_public.pem -Algorithm SHA256
```

The calculated hashes must match the original values above.

## 3. Provider Key Identifiers

The observer uses SHA-256 fingerprints of the raw Ed25519 public-key bytes.

The calculation is:

`key_id = "sha256:" + SHA256(raw_public_key_bytes)`

### Provider A

`sha256:43938d000689ef68e298d69c19dd2b5879efc7daf27e6af8bd099f577c91c789`

### Provider B

`sha256:9ab1cd6d33fea596624f7d2a0e93442746bee9c97ad237d338c23b4385ebb445`

These identifiers must match the approved provider registry and the key IDs inside the signed provider events.

A valid signature under the wrong provider's key does not satisfy provider identity verification.

## 4. Relationship to the Provider Registry

The observer registry is located one directory above:

`../provider_registry.json`

It contains two provider entries.

Each entry specifies:

- Provider identity.
- Expected public-key identifier.
- Relative public-key file path.

For Provider A:

```json
{
  "key_id": "sha256:43938d000689ef68e298d69c19dd2b5879efc7daf27e6af8bd099f577c91c789",
  "public_key_file": "trust/provider_a_public.pem"
}
```

For Provider B:

```json
{
  "key_id": "sha256:9ab1cd6d33fea596624f7d2a0e93442746bee9c97ad237d338c23b4385ebb445",
  "public_key_file": "trust/provider_b_public.pem"
}
```

The paths are relative to the `association/` directory.

The registry's original SHA-256 is:

`893cd6153db95ba93016c894adfd3f4c577921a3bd9c9bfc935eda9951ac76e7`

The observer also cross-checks these boundary-key identifiers against the approved trust record at:

`../../trust/provider_keys.json`

The observer must reject unknown providers, unexpected keys, and invalid signatures.

## 5. Boundary Keys Versus Issuance Keys

MH001 uses separate cryptographic key roles.

| Key role | Purpose |
|---|---|
| Issuance key | Signs provider authorization packages |
| Boundary-event key | Signs provider execution and denial events |

The two public keys in this directory are **boundary-event verification keys**.

They are not the issuance public keys used to verify the authorization packages in `authorizations/`.

The original issuance public keys are preserved separately under:

`../../../original_host_test_keys/`

That path is relative to this directory, with the original test-key directory located alongside `MH001_R43_RUN001/` under `MH001/`.

Using the wrong key role must not be treated as successful verification.

## 6. How the Observer Verifies Events

The original verification implementation is preserved at:

`../../observer_support/association_recorder.py`

Its signature-verification procedure is:

1. Read the original provider event envelope.
2. Require algorithm `Ed25519`.
3. Extract the claimed provider identity and key ID.
4. Find that provider in the approved registry.
5. Confirm the claimed key ID matches the registered key.
6. Canonicalize the signed event object.
7. Verify the Ed25519 signature.
8. Record the verification result.

The signature covers:

```text
NUVL-MP-BOUNDARY-v1| + canonical(event)
```

The prefix is included as bytes before the canonical JSON event representation.

Canonical JSON uses sorted keys, compact separators, and UTF-8 encoding.

The original observer stores the signed event envelope in the `raw_body_b64` field of each submission record.

The observer's recorded claims are not substitutes for independently checking that original envelope.

## 7. Independently Verify the Historical Signatures

The completed observer log is located at:

`../../evidence/observer.jsonl`

It contains 14 provider submissions.

The following offline Python verification checks the original provider public-key identifiers and all 14 signed event envelopes.

It requires Python 3 and the `cryptography` package.

Run from the `MH001_R43_RUN001/` root:

```python
import base64
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization

registry_path = Path("association/provider_registry.json")
registry = json.loads(registry_path.read_bytes())["providers"]

keys = {}

for provider_id, entry in registry.items():
    key_path = registry_path.parent / entry["public_key_file"]

    public_key = serialization.load_pem_public_key(
        key_path.read_bytes()
    )

    raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    actual_id = "sha256:" + hashlib.sha256(raw).hexdigest()

    assert actual_id == entry["key_id"]

    keys[provider_id] = public_key
    print("KEY PASS:", provider_id)

count = 0

with open("evidence/observer.jsonl", encoding="utf-8") as log:
    for line in log:
        record = json.loads(line)

        if record["record_type"] != "SUBMISSION":
            continue

        envelope = json.loads(
            base64.b64decode(record["raw_body_b64"])
        )

        assert envelope["alg"] == "Ed25519"

        event = envelope["event"]
        provider_id = event["provider_id"]

        assert provider_id in registry
        assert event["key_id"] == registry[provider_id]["key_id"]
        assert record["claimed_provider_id"] == provider_id

        canonical = json.dumps(
            event,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        encoded_signature = envelope["signature"]

        signature = base64.urlsafe_b64decode(
            encoded_signature + "=" * (-len(encoded_signature) % 4)
        )

        keys[provider_id].verify(
            signature,
            b"NUVL-MP-BOUNDARY-v1|" + canonical,
        )

        assert record["sig_valid"] is True
        assert record["registry_match"] is True
        assert record["verification_code"] == "ok"

        count += 1

print(f"PASS: {count}/14 provider signatures verified")
```

Expected result:

```text
KEY PASS: PROVIDER_B
KEY PASS: PROVIDER_A
PASS: 14/14 provider signatures verified
```

The two key lines may appear in either order.

This verification performs no network requests and requires no provider private keys.

It verifies the recorded provider signatures against the published original public keys.

It does not independently prove network delivery, persistent consumption, or physical execution.

## 8. Critical T03 Verification

The decisive MH001 replay events are:

| Observer record | Provider | Signed stage | Signed reason |
|---|---|---|---|
| 10 | PROVIDER_A | DENY | auth_spent |
| 11 | PROVIDER_B | DENY | auth_spent |

An independent reviewer must confirm that each signed envelope contains:

- The correct provider ID.
- Its registered boundary-key ID.
- `stage: DENY`.
- `reason_code: auth_spent`.
- The original T01 authorization identity.
- The original authorization nonce and binding.
- The matching operation identity and ledger state.

A valid signature over a different denial reason does not establish T03 PASS.

These signatures establish that the registered provider signing keys authenticated the recorded denial events.

Provider-ingress and persistent-state evidence must separately establish that the exact replay reached each provider and did not execute again.

## 9. New Experiment Requirements

For a new independent MH001 reproduction:

1. Establish independent provider-controlled signing identities.
2. Preserve the distinction between issuance keys and boundary-event keys.
3. Export each provider's boundary-event public key to the observer.
4. Calculate its raw Ed25519 public-key fingerprint.
5. Construct a new reviewed provider registry.
6. Approve the corresponding public trust identities.
7. Verify the registry before starting the observer.
8. Record newly signed events in a separate evidence session.
9. Preserve the public keys, registry, observer log, and their hashes.

The published original disposable test keys remain available for exact historical verification.

Do not replace them in the historical archive.

New live experiments should use independent signing identities and isolated provider state.

## 10. Preservation Boundary

Both PEM files are members of the original 132-file scored evidence inventory.

This README is supplemental documentation.

Do not modify or replace the original keys.

Do not regenerate their historical fingerprints.

Do not rewrite the provider registry or observer log to make a signature match.

A failed key-identity or signature check must be reported as a verification failure.

## Conclusion

The observer's two independent public keys permit offline verification of provider-signed execution and denial events.

In particular, the T03 `DENY / auth_spent` events can be authenticated without trusting the forwarding hubs or obtaining either provider's private keys.
