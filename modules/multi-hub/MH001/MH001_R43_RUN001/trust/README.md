# MH001 — Provider Trust Records

## Purpose

This directory preserves the approved provider key identities used in the MH001 R4.3 scored experiment.

Each provider has two distinct Ed25519 signing identities:

- **Issuance key:** Signs operation authorizations.
- **Boundary-event key:** Signs execution and denial events.

The trust record identifies these keys without storing private signing material.

**Session:** `MH001_R43_RUN001`

## 1. Directory Contents

```text
trust/
├── provider_keys.json
└── provider_keys.pending.backup.json
```

| File | Purpose |
|---|---|
| `provider_keys.json` | Final approved provider signing-key identities |
| `provider_keys.pending.backup.json` | Preserved pre-approval trust record |

Both files contain the same four key identifiers.

Their approval statuses differ.

## 2. Approved Trust Record

File:

`provider_keys.json`

Recorded status:

`APPROVED_PROVIDER_HOST_KEYS`

Session:

`MH001_R43_RUN001`

The record identifies exactly two providers.

### Provider A

Issuance key ID:

`sha256:f80897de6f5693caedf5a63e9da63cfd683b3c9c6a42bbf6d40defed35ab1664`

Boundary-event key ID:

`sha256:43938d000689ef68e298d69c19dd2b5879efc7daf27e6af8bd099f577c91c789`

### Provider B

Issuance key ID:

`sha256:44a1f266d623faa86487cdc85244f7c95bb8fdb18aa1537e27a17a85fc704022`

Boundary-event key ID:

`sha256:9ab1cd6d33fea596624f7d2a0e93442746bee9c97ad237d338c23b4385ebb445`

All four identities are distinct.

Provider A's signing keys do not authorize Provider B's operations, and vice versa.

## 3. Preserved Pending Record

File:

`provider_keys.pending.backup.json`

Recorded status:

`AWAITING_OPERATOR_APPROVAL`

This file preserves the earlier trust approval state.

It contains the same provider identities and signing-key fingerprints as the final approved record.

The status difference is intentional.

The pending backup must not be used as the approved live trust file.

Do not rewrite its status to match the final record.

## 4. Original SHA-256 Values

Both original files are recorded in:

`evidence/MH001_FINAL_SHA256SUMS.txt`

### Approved Record

`provider_keys.json`

SHA-256:

`d9c304ff67316c7f91b6be5225519cdd7f899a18c972edb4bf2e2fe052a14b86`

### Pending Backup

`provider_keys.pending.backup.json`

SHA-256:

`27ad22d093891795e98df194b9f49d2a7a47f0d40e1adf5a893270ea39e80ed5`

### Verify Both Files

From this directory on Linux:

```bash
sha256sum provider_keys.json
sha256sum provider_keys.pending.backup.json
```

On Windows PowerShell:

```powershell
Get-FileHash .\provider_keys.json -Algorithm SHA256
Get-FileHash .\provider_keys.pending.backup.json -Algorithm SHA256
```

Both hashes must match the published values.

These commands do not modify either file.

## 5. How Trust Approval Is Enforced

The relevant implementation is:

`deployment.py`

Function:

`public_trust()`

The implementation requires:

1. The expected MH001 session.
2. Status `APPROVED_PROVIDER_HOST_KEYS`.
3. Exactly `PROVIDER_A` and `PROVIDER_B`.
4. An issuance and boundary-event key ID for each provider.
5. Four distinct key identifiers.
6. Correct `sha256:` fingerprint formatting.
7. No prohibited historical key identities from the frozen deployment configuration.

If these conditions are not satisfied, the trust precondition fails.

The provider launcher additionally verifies that the installed provider public keys match the approved fingerprints.

The observer independently checks its registry against the approved boundary-event key IDs.

A JSON status value by itself does not cryptographically authenticate the record. The reviewed file hash and actual public-key material are separate required checks.

## 6. Verify Trust Record Consistency

The following offline Python check verifies the published approval states and confirms that the four recorded key identities are distinct.

Run from the `MH001_R43_RUN001/` root:

```bash
python3 -B - <<'PY'
import json
from pathlib import Path

root = Path("trust")

approved = json.loads(
    (root / "provider_keys.json").read_bytes()
)

pending = json.loads(
    (root / "provider_keys.pending.backup.json").read_bytes()
)

assert approved["session"] == "MH001_R43_RUN001"
assert pending["session"] == approved["session"]

assert approved["status"] == "APPROVED_PROVIDER_HOST_KEYS"
assert pending["status"] == "AWAITING_OPERATOR_APPROVAL"

assert pending["providers"] == approved["providers"]

providers = approved["providers"]
assert set(providers) == {"PROVIDER_A", "PROVIDER_B"}

identities = []

for provider in sorted(providers):
    entry = providers[provider]

    assert set(entry) == {
        "issuance_key_id",
        "boundary_key_id"
    }

    for key_id in entry.values():
        assert key_id.startswith("sha256:")
        assert len(key_id) == 71
        int(key_id[7:], 16)
        identities.append(key_id)

    print("PASS:", provider)

assert len(set(identities)) == 4

print("PASS: four distinct key identities")
print("PASS: approved and pending records are consistent")
PY
```

This checks the records' contents. The SHA-256 manifest separately verifies their original bytes.

The test does not load private keys, start providers, or contact the network.

## 7. Relationship to the Observer Registry

The independent observer uses:

`association/provider_registry.json`

Its public keys are stored in:

`association/trust/`

That registry contains only the boundary-event key identifiers.

The corresponding approved identifiers in `provider_keys.json` must match.

The observer uses these public keys to verify signed events such as:

- START
- COMPLETE
- DENY

The observer does not use issuance private keys and cannot create provider authorization packages.

The observer's registry is documented separately under `association/`.

## 8. Relationship to Provider Issuance

The signed authorization packages are preserved in:

`authorizations/`

The original provider issuance tools are preserved at:

- `frozen_R43/providers/provider_a/mint_authorization_a.py`
- `frozen_R43/providers/provider_b/mint_authorization_b.py`

Those tools create provider-specific Ed25519 authorization signatures.

The issuance key identifies which provider originated the authority.

The boundary-event key identifies which provider signed the resulting execution or denial evidence.

These roles must remain separate during verification.

## 9. Connection to Startup Approvals

The final trust file's SHA-256 is incorporated into the recorded LIVE_STARTUP approval files.

Those files are located in:

`authorizations/`

The observer and provider launchers verify that the actual trust file matches the approved hash.

Changing the trust file after approval causes that approval check to fail.

The recorded startup approvals also bind the session, configuration, and reviewed source hashes.

**Trust approval and startup approval are not provider execution authority.**

A request still requires its own valid provider-issued authorization.

## 10. Historical Key Publication

The original disposable test keys are preserved separately under:

`../original_host_test_keys/`

That directory is a sibling of `MH001_R43_RUN001/`.

The published keys support independent reproduction and verification of the historical experiment.

They must not be substituted for the provider-controlled signing identities of a new operational deployment.

A new live experiment requires its own reviewed trust identities, configuration approval, and isolated provider state.

The historical test files and their hashes must remain unchanged.

## 11. Reproduction Requirements

For a new independent MH001 experiment:

1. Establish separate signing identities under each provider's control.
2. Generate independent issuance and boundary-event key pairs.
3. Calculate the SHA-256 fingerprints of the raw Ed25519 public keys.
4. Confirm all four identifiers are distinct.
5. Construct a new session-specific provider trust record.
6. Preserve the pending state before approval.
7. Obtain the required operator trust and startup approvals.
8. Verify installed provider public keys against the approved fingerprints.
9. Configure the independent observer with the approved boundary-event public keys.
10. Preserve the approved trust file and its SHA-256 before execution.

A new experiment must not modify the published MH001 trust records.

## 12. Preservation Boundary

Both JSON files belong to the original 132-file scored evidence inventory.

This README is supplemental documentation.

Do not alter either historical approval status.

Do not replace the original key identifiers.

Do not rewrite the approved trust file to accommodate a mismatched key.

Do not regenerate the original evidence manifest.

A trust mismatch must result in a failed precondition, not an automatic repair.

## Conclusion

MH001 preserved separate provider signing identities for authority issuance and execution evidence.

The approved trust record bound those identities to the reviewed experiment while keeping authorization decisions and signing authority under the individual providers' control.
