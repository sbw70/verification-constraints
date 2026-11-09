
# MH001 — Authorization and Startup Approval Records

## Purpose

This directory preserves two distinct classes of records from the MH001 R4.3 experiment:

1. **Provider-issued authorizations** permitting specific provider operations.
2. **Operator startup approvals** permitting reviewed laboratory components to start.

These are separate authority domains.

An operator's permission to run the experiment cannot authorize a provider operation. A provider-issued execution authorization cannot approve deployment or bypass an operator STOP gate.

**Session:** `MH001_R43_RUN001`

## 1. Directory Contents

```text
authorizations/
├── observer_LIVE_STARTUP_PENDING.json
├── observer_LIVE_STARTUP_APPROVED.json
├── provider_a_LIVE_STARTUP_PENDING.json
├── provider_a_LIVE_STARTUP_APPROVED.json
├── provider_b_LIVE_STARTUP_PENDING.json
├── provider_b_LIVE_STARTUP_APPROVED.json
├── rehearsal_provider_a.json
├── rehearsal_provider_b.json
├── t01_provider_a.json
├── t01_provider_b.json
├── t04_provider_a.json
└── t04_provider_b.json
```

There are **12 original JSON files**.

The first six document startup approval state. The remaining six contain provider-signed operation authorizations.

All 12 belong to the original 132-file scored evidence inventory.

## 2. Operator Startup Approvals

Three components have paired pending and approved startup records:

| Component | Pending file | Approved file |
|---|---|---|
| Observer | `observer_LIVE_STARTUP_PENDING.json` | `observer_LIVE_STARTUP_APPROVED.json` |
| Provider A | `provider_a_LIVE_STARTUP_PENDING.json` | `provider_a_LIVE_STARTUP_APPROVED.json` |
| Provider B | `provider_b_LIVE_STARTUP_PENDING.json` | `provider_b_LIVE_STARTUP_APPROVED.json` |

Each record contains:

- `authorized`
- `session`
- `phase`
- `config_sha256`
- `trust_sha256`
- `source_sha256`

The pending records contain:

`"authorized": false`

The approved records contain:

`"authorized": true`

All six specify:

`"phase": "LIVE_STARTUP"`

The pending records preserve the original pre-approval state. They are not active approvals.

### Approved Configuration Identities

| Component | Approved configuration SHA-256 |
|---|---|
| Observer | `4960e35cfde9a1bd43cddb615030e0ef83b478c717c59049f59616e3d367735a` |
| Provider A | `4f89bc9f0f29e39393ecab26c6001b7d6d6f6b1aaaca614da71e82c6d0ddb58b` |
| Provider B | `661754ab55105b4fa154b77b8cc16a5da52809269140d185115fab00888ebfcf` |

All six records identify the same reviewed trust file hash:

`d9c304ff67316c7f91b6be5225519cdd7f899a18c972edb4bf2e2fe052a14b86`

The approved records also contain the expected hashes of 11 reviewed source files.

## 3. How Startup Approval Is Enforced

The relevant implementation is:

`deployment.py`

Function:

`require_approval()`

The provider and observer launchers call this function before starting their respective live components.

The approval check requires:

1. An approval file was supplied.
2. `authorized` is exactly `true`.
3. `phase` is `LIVE_STARTUP`.
4. The session matches the configuration.
5. The configuration file's SHA-256 matches.
6. The approved trust file's SHA-256 matches.
7. Every required source-file hash matches the approved value.

A discrepancy causes the startup precondition check to fail.

The startup approval files are **hash-bound operator records, not Ed25519-signed provider authorizations**.

Their presence alone does not establish that every laboratory preflight or procedural STOP gate was completed.

In particular, these records do not replace the separately required approval before terminating Hub A during T02.

See:

`frozen_R43/OPERATOR_GATES.md`

## 4. Provider-Issued Operation Authorizations

Six files contain the original Ed25519-signed authorization packages.

| Phase | Provider A | Provider B |
|---|---|---|
| Rehearsal | `rehearsal_provider_a.json` | `rehearsal_provider_b.json` |
| T01 | `t01_provider_a.json` | `t01_provider_b.json` |
| T04 | `t04_provider_a.json` | `t04_provider_b.json` |

Each JSON package contains:

```json
{
  "alg": "Ed25519",
  "authorization": {
    "authorization_id": "...",
    "nonce": "...",
    "provider_id": "...",
    "request_repr": "...",
    "verification_context": "...",
    "version": 1
  },
  "signature": "..."
}
```

The signature covers the canonical authorization object with the frozen domain-separation prefix.

The authorization fields bind the package to a specific issuing provider, operation representation, verification context, and nonce.

The requester receives an already-issued package. It does not generate the signature.

## 5. Original Authorization Identities

### Rehearsal

Provider A:

`1aa113f64ee7c2ed3e4441cce7a31dfd74beb9f28f063c212f5343666978440d`

Provider B:

`60d0f8f5192def2595b611225371815c088fc024d27c26e4103dd89e226e99e4`

Both rehearsal authorizations were accepted and consumed once.

### T01

Provider A:

`a92b2daf4e88cbb066ef5ce47431b8ca09144055d3b8e60c3a1c185303f1c3ea`

Provider B:

`041315d147341d225acd07d925abcae408864bb52def806709b6b9def5e52b4a`

Both T01 authorizations were accepted and consumed once.

### T03

**No new authorization package was issued for T03.**

The original T01 requests, including their original authorization packages, were replayed unchanged through Hub B.

Both providers returned independently signed:

`DENY / auth_spent`

Creating new authorization packages for T03 would invalidate the exact-replay test.

### T04

Provider A:

`295e8d3288b7923daf7c5beaf0cb6433e8dff8eb9b47c6c56bc3822bcb1276ea`

Provider B:

`1d5777cc2f3dedba9a88d435b4d764ac749c77d6aea9f76e177d32e0fcea8226`

Both T04 authorizations were separately issued and accepted once.

Neither provider reset its earlier spent-authority history.

## 6. Original Package Integrity

| Package | SHA-256 |
|---|---|
| Rehearsal A | `56b51ed287d598840f300d09057328b03dea3011dc24fceccd4de65d5c9af5ee` |
| Rehearsal B | `41bedc437c6a09830bd0313bde539f6dac0206385185e5052de8b2b1151d83ec` |
| T01 A | `cc19d4bf04579a2038af9fac9dadc581525903e89c52cce0c7bb32e61960e272` |
| T01 B | `6133239a3c2b997cf29dc531c0672a582fdca0b5aae0fa04adc853a` |
| T04 A | `2da52f8aa6ce03d926138d4300b9f2addb0caab95f7e8c3285c87ba1ec7d4f39` |
| T04 B | `81a729d885073b2bbce214aa5bbbcf71effe5d8289ff8442db4bf1a132a59fed` |

The manifest also records these six startup approval-file hashes:

| Startup record | SHA-256 |
|---|---|
| Observer approved | `2eddac6c2b04bd05160357e0b46b5ce41606e5c033e8ffe7ff40963ae8440496` |
| Observer pending | `f1861ded393b7185208dbac1f7e6f4af0b0eeebc406be89f50e6b40e66098fc4` |
| Provider A approved | `efac91cd83a9673532a3909ac666702b77143843cb544998487cc4a099f03e91` |
| Provider A pending | `dea2c2c2546f699c886f67cbc65a41aadf42288a93d0f30d64c617fa14198015` |
| Provider B approved | `ebadf5accb0a16aab4d1e2991099f5b3eed9680acf119ce962578c8325db34e8` |
| Provider B pending | `4a27b3c831361b299fae59e7ba4b4b1de88ec5dff50cc4961755c4bcaa65f544` |

All values originate from:

`evidence/MH001_FINAL_SHA256SUMS.txt`

### Verify All 12 Files

From the `MH001_R43_RUN001/` root on Linux:

```bash
grep '  authorizations/' evidence/MH001_FINAL_SHA256SUMS.txt | sha256sum -c -
```

Expected: 12 successful checks.

This verifies file integrity. It does not independently verify Ed25519 signatures.

## 7. Verify the Provider Signatures

The frozen issuance tools define:

Authorization ID:

`SHA256(b"NUVL-MP-AUTH-ID-v1|" + canonical(core))`

Authorization signature:

`Ed25519.sign(b"NUVL-MP-AUTH-v1|" + canonical(authorization))`

Canonical JSON uses:

- Sorted object keys.
- Compact separators.
- UTF-8 encoding.
- No unnecessary ASCII escaping.

The original issuance source is preserved in:

- `frozen_R43/providers/provider_a/mint_authorization_a.py`
- `frozen_R43/providers/provider_b/mint_authorization_b.py`

The corresponding original public issuance keys are preserved in the sibling directory:

- `../original_host_test_keys/provider_a/provider_a_issuance_public.pem`
- `../original_host_test_keys/provider_b/provider_b_issuance_public.pem`

The following offline verification checks all six historical packages. It requires Python 3 and the `cryptography` library.

Run from the scored-run root:

```bash
python3 -B - <<'PY'
import base64
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization

def canonical(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")

count = 0

for phase in ("rehearsal", "t01", "t04"):
    for provider in ("a", "b"):
        role = "provider_" + provider

        package_path = Path(
            f"authorizations/{phase}_{role}.json"
        )

        public_path = Path(
            f"../original_host_test_keys/{role}/"
            f"{role}_issuance_public.pem"
        )

        package = json.loads(package_path.read_bytes())
        authorization = package["authorization"]

        assert package["alg"] == "Ed25519"
        assert authorization["provider_id"] == role.upper()

        core = {
            k: v for k, v in authorization.items()
            if k != "authorization_id"
        }

        expected_id = hashlib.sha256(
            b"NUVL-MP-AUTH-ID-v1|" + canonical(core)
        ).hexdigest()

        assert authorization["authorization_id"] == expected_id

        encoded = package["signature"]
        signature = base64.urlsafe_b64decode(
            encoded + "=" * (-len(encoded) % 4)
        )

        public_key = serialization.load_pem_public_key(
            public_path.read_bytes()
        )

        public_key.verify(
            signature,
            b"NUVL-MP-AUTH-v1|" + canonical(authorization)
        )

        print("PASS:", package_path)
        count += 1

print(f"PASS: {count}/6 authorization packages")
PY
```

Expected: six successful signature and authorization-ID checks.

This uses the published original test public keys and does not access private keys, issue new authority, or contact a provider.

A signature's validity establishes authenticity relative to its signing key. It does not establish that the authorization is still unspent.

Spent-state enforcement is independently verified through provider evidence.

## 8. Issuance Keys Versus Boundary-Event Keys

Each provider used two distinct Ed25519 key roles.

**Issuance key:** Signs operation authorizations stored in this directory.

**Boundary-event key:** Signs provider execution and denial events sent independently to the observer.

The observer's public-key registry is located at:

`association/provider_registry.json`

Its public keys are intended to verify provider event submissions, not the issuance packages documented here.

Do not use an event-signing public key as a substitute for an issuance public key.

The original disposable test keys are preserved for exact reproducibility. They are not production signing credentials.

## 9. Reproducing Authorization Issuance

For a new, separately authorized laboratory experiment:

1. Establish new, isolated provider-controlled signing identities.
2. Prepare the operation input for the appropriate provider.
3. Run that provider's original minting implementation in its approved provider-controlled environment.
4. Preserve the issued authorization package.
5. Record its package SHA-256 and authorization ID.
6. Transfer only the issued package and permitted operation materials to the requester.
7. Construct the HTTP request with the frozen requester implementation.
8. Submit the request through the approved route.
9. Verify the provider's independent signed decision and durable consumption history.

New issuance normally creates different nonces, authorization IDs, and signatures.

For T03, **do not mint new authority**. Replay the preserved T01 requests.

For T04, issue genuinely new authority while preserving the existing consumption state.

Operator startup approvals for a new experiment must separately bind to that experiment's reviewed source, configuration, trust, and session identities.

The historical approval files do not grant permission for another deployment.

## 10. Preservation Boundary

The original twelve files belong to the 132-file scored evidence inventory.

This README is supplemental documentation.

Do not modify the historical authorization packages, replace their signatures, change their nonces, or update the startup approval records.

Do not create a T03 authorization package to fill an apparent directory gap.

Do not merge the meanings of operator approval and provider execution authorization.

## Conclusion

The MH001 records demonstrate two independent authority boundaries:

- The operator controls whether reviewed laboratory components may start.
- Each provider controls whether its specific operation authorization may execute.

The requester and forwarding hubs hold neither authority.
