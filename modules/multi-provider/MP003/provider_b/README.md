# Provider B

This directory contains the Provider B runtime, the Provider B mint utility, and Provider B's laboratory keys as used in MP003.

In MP003, Provider B is the provider whose boundary is under test. None of Provider B's keys were compromised.

## Contents

| File | Role | SHA-256 |
|---|---|---|
| `provider_b.py` | Provider B runtime | `5e0ab4b79df4c97bc7bc324d63da85711728d625b82306cdce6c92592e2ee13e` |
| `mint_authorization_b.py` | legitimate Provider B authorization mint | `1b3ba1314761a5489817c660cdc4d62e65ba77deae2bfce2fdce48c228f98deb` |
| `provider_b_issuance_private.pem` | issuance signing key | `fb450986458ee062e1747471cfef731a743b6d3915b1d86bbf0f4c2e7e1e3433` |
| `provider_b_issuance_public.pem` | issuance verification key | `07ba26931a6112826f39fdc9a286562f608f394b4f8de4d26f48751855d8fe64` |
| `provider_b_private.pem` | boundary-signing key | `02e145e18080e3a2dc230d70c6de71f33fa4ff7ec7fed829f313292a845b95d7` |
| `provider_b_public.pem` | boundary verification key | `bcb4441a3ad143b5a3d646189d15ba806340c52530ba9b5ef4e19f30e0c59e47` |

All six files are byte-identical to the MP002 Provider B files. The runtime and mint hashes match the locked MP003 run manifest.

These are laboratory keys, published deliberately so the evidence can be verified. They are not used outside this test series.

## Deployment in MP003

- Host: HP laptop (`Xer0trust2`, 192.168.1.106)
- Listens on `0.0.0.0:9090`, endpoint `POST /ingest`
- Sends signed boundary events to the association recorder at `http://192.168.1.102:9191/boundary`
- Boundary key ID: `sha256:db764408aa319642363057d804f0c2a3d2c7dd22de86ae4a6d6549cb97f60225`

The scored session started with `Spent entries loaded: 0`, recorded in `../evidence/scored/operator_transcripts/provider_b_console.txt`.

## Relationship to the Provider A runtime

Apart from its provider identity, `provider_b.py` is functionally the same program as `provider_a.py`, with one addition carried over from MP002: a provider-local policy gate.

```python
POLICY_DENY_CONTEXT = "CTX_MP002_DIVERGE"
```

The gate runs at validation step 11, after authorization and context checks and before consumption. It denies only that MP002 context. No MP003 case used it, so the gate was never triggered in MP003.

The other textual differences are the startup banner (`MP002_PROVIDER_B` vs. `MP001_PROVIDER_A`), a UTF-8 byte-order mark present in `provider_a.py` but not here, and a trailing newline.

The MP001-to-MP002 source diff for this file is published with MP002 at `../../MP002/provider_b/MP001_TO_MP002_PROVIDER_B.diff`.

## How Provider B decides what counts as Provider B authority

Provider B accepts an authorization only if all of the following hold:

- `provider_id` is `PROVIDER_B` (step 6);
- the authorization ID recomputes correctly from the authorization core (step 7);
- the signature verifies under **Provider B's** issuance public key (step 8);
- request representation and context match (steps 9–10);
- the local policy permits it (step 11);
- it is unspent (step 12).

The Provider B runtime loads only Provider B's issuance public key for authorization verification. It does not load any Provider A key, so it has no path for treating a Provider A signature as Provider B authority. That is what C02 and C03 test.

## Provider B in MP003

| Case | Received | Result | Validation step |
|---|---|---|---|
| B01 | legitimate Provider B authorization | executed (`local_execution_seq` 1) | — |
| C01 | nothing | `DENY auth_missing` | 4 |
| C02 | valid Provider A authorization (compromised-key mint) | `DENY auth_provider_mismatch` | 6 |
| C03 | authorization claiming `PROVIDER_B`, signed with the compromised Provider A key | `DENY auth_bad_sig` | 8 |
| B02 | legitimate Provider B authorization | executed (`local_execution_seq` 2) | — |

Provider B's state was byte-identical from after B01 through after C03, and changed only when B02 executed. The DENYs in C02 and C03 name the refused authorization IDs, and neither ID appears in Provider B's final spent state.

## Durability and startup

Spent state and execution records are written with `fsync`, and spent state is written atomically. The runtime refuses to start if the spent-state file is missing or invalid, or if its boundary keypair does not match.

## Known implementation limitation

Boundary events are sent to the association recorder once, with a 2-second timeout and no retry or durable outbox. Every MP003 Provider B boundary event was delivered (`sent=True` in the console transcript).

## What MP003 does not test about Provider B

MP003 does not test compromise of Provider B's issuance key, Provider B's boundary key, or the Provider B host. It does not test Provider B under restart, crash, power loss, concurrent load, or denial of service.

## Related material

`../provider_a/`

`../attacker/`

`../association/`

`../evidence/scored/final_provider_b/`

