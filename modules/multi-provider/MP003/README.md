# MP003 — Compromised Provider Blast Radius

MP003 extends the physically distributed multi-provider series established in MP001 and MP002.

The test asks:

**If an attacker holds one provider's real authorization-issuance private key, does that give the attacker execution authority at a different provider?**

The scored result was:

**PASS**

Provider A's real issuance private key was treated as stolen.

The attacker used it to mint authority that Provider A accepted and executed. Once a provider's issuance key is compromised, that provider's authority is compromised.

That compromise did not extend to Provider B.

Valid Provider A authority presented to Provider B was refused.

An authorization relabeled as Provider B, but signed with Provider A's key, was refused.

Provider B's legitimate authority still worked afterward.

The relay did not convert Provider A authority into Provider B authority.

The association did not authorize anything.

---

## Architecture

The tested path was:

    Requester
        |
        v
    NUVL relay
       / \
      v   v
     A     B
      \   /
       v v
    Association

### Provider A

Provider A controls Provider A authorization issuance and validation, spent state, execution, and boundary evidence.

In MP003, Provider A's **issuance private key** is in attacker hands. Provider A's boundary-signing key is not.

### Provider B

Provider B independently controls Provider B authorization issuance and validation, spent state, execution, and boundary evidence.

None of Provider B's keys were compromised.

### NUVL relay

The relay transports the request and each provider's authorization header to the corresponding provider.

It does not decode, verify, mint, or enlarge provider authority. It holds no provider keys.

### Association

The association verifies and preserves signed provider boundary evidence.

It holds only provider boundary public keys. It does not authorize execution, override provider decisions, or compute a cross-provider result.

---

## Relationship to MP001 and MP002

MP001 showed the multi-provider roles could be split across independent hosts while retaining provider-specific authority and state.

MP002 showed those providers could reach independent decisions for the same operation.

MP003 changes no code. Every runtime, mint utility, key, the relay, and the association are byte-identical to MP002.

The only new material is attacker-side, in `attacker/`:

- a byte-identical copy of Provider A's issuance private key;
- `mint_compromised_a.py` — Provider A's legitimate mint, pointed at the attacker's key copy;
- `mint_forged_b_with_a_key.py` — the same, with `PROVIDER_ID = "PROVIDER_B"`.

Each attacker utility differs from its source by one line.

---

## Scored campaign

Scored session:

`MP003_SCORED_20261015_R2`

| Case | A header | B header | Provider A | Provider B | Result |
|---|---|---|---|---|---|
| B01 | legitimate | legitimate | `START → EXECUTED → COMPLETE` | `START → EXECUTED → COMPLETE` | **PASS** |
| C01 | compromised-key A auth | absent | `START → EXECUTED → COMPLETE` | `DENY auth_missing` | **PASS** |
| C02 | compromised-key A auth | same A auth | `START → EXECUTED → COMPLETE` | `DENY auth_provider_mismatch` | **PASS** |
| C03 | absent | `PROVIDER_B` claim signed with A key | `DENY auth_missing` | `DENY auth_bad_sig` | **PASS** |
| B02 | absent | legitimate | `DENY auth_missing` | `START → EXECUTED → COMPLETE` | **PASS** |

### B01 — control

Both providers executed their own legitimate authorization.

### C01 — the stolen key is real

Provider A accepted and executed an authorization minted with the attacker's copy of its key. This proves the compromise is genuine. It is the precondition for C02 and C03, not a containment result.

### C02 — Provider A authority at Provider B

The same attacker-minted Provider A authorization was sent to both providers. Provider A executed it. Provider B refused it on scope: it is addressed to `PROVIDER_A`, so it is not Provider B authority, whatever its signature.

### C03 — relabeling as Provider B

The attacker wrote `PROVIDER_B` into a fresh authorization and signed it with Provider A's key. It passed Provider B's identity and authorization-ID checks and failed signature verification under Provider B's issuance key. Offline checking confirms the signature is valid under Provider A's key and invalid under Provider B's.

### B02 — Provider B still works

After C01–C03, Provider B accepted and executed a fresh legitimate authorization. Provider B's execution sequence went directly from 1 (B01) to 2 (B02).

For C02 and C03, Provider B's non-consumption and non-execution were confirmed from Provider B's own state files, not inferred from its signed `DENY`.

One earlier B01 send failed because of a harness file-naming error (association records 2–3, both providers `DENY auth_malformed`). It is retained, not scored, and is not a property failure.

---

## Final scored state

### Provider A

    executions = 3
    spent authorizations = 3

B01, C01, C02. Two of the three were minted with the compromised key.

### Provider B

    executions = 2
    spent authorizations = 2

B01, B02. Both were minted with Provider B's own key.

Neither the C02 authorization nor the C03 forgery appears in Provider B's state.

---

## What MP003 demonstrates

The property under test:

**the consequence of compromise stays with the authority that was actually compromised.**

Provider A and Provider B use different issuance keys, so a Provider A key is not expected to produce a Provider B signature. MP003 checks whether anything in the tested path converts one provider's authority into the other's anyway. It found nothing that did:

- the relay forwarded attacker authorization to Provider B unchanged and holds no keys;
- the association recorded each provider's own signed statements and authorizes nothing;
- Provider B evaluates authority only against its own issuance key;
- provider identity is bound into the signed authorization, so relabeling requires a signature the attacker cannot make.

There is no shared trust root, intermediary verification step, or aggregation point in the tested path through which Provider A authority could be accepted as Provider B authority.

---

## Evidence

### `evidence/scored/`

The MP003 result: five case directories with exact requests, authorization packages, relay send records, and per-case provider state; final provider state; the hash-chained association log; the scorecard; operator transcripts; and `SHA256SUMS.txt`.

### `evidence/retained_partial/`

The first scored attempt, preserved unchanged. One legitimate B01 ran. Provider state was then misclassified and reset, so the campaign was restarted as R2. No compromised-key case ran.

### `evidence/pre_run_state/`

Pre-test provider state from the first attempt.

### `evidence/preflight/`

Dry-run mints from both attacker utilities. Never sent.

---

## Integrity

Final association record hash:

`4c3282924708f504323bbd2cb1188bd0f2071e54a66b5bdb928e344abaa0a906`

SHA-256 of the scored `association.jsonl`:

`50af864099a7eb91970866a664005caa24042224d2b69525e0e9610c53eb642a`

Locked contract SHA-256:

`ac368500126f3314faa7f5193a07bbb78061c10e1931606778b6414702b9579b`

Locked run-manifest SHA-256:

`85ac48ff64f7b94d078ceb0638240980d30013a78cf3d850964abbd895eb7368`

`evidence/scored/SHA256SUMS.txt` covers the scored evidence tree (67 files). Verify with:

    cd evidence/scored
    sha256sum -c SHA256SUMS.txt

Implementation and attacker-material hashes are fixed in `configs/MP003_RUN_MANIFEST.json`.

---

## Repository layout

    MP003/
    ├── README.md
    ├── RESULTS.md
    ├── PROVENANCE.md
    ├── configs/
    ├── intermediary/
    ├── provider_a/
    ├── provider_b/
    ├── association/
    ├── attacker/
    ├── operator/
    └── evidence/
        ├── scored/
        ├── retained_partial/
        ├── pre_run_state/
        └── preflight/

### `configs/`

Locked contract and run manifest.

### `intermediary/`

NUVL multi-provider relay.

### `provider_a/`

Provider A runtime, mint utility, and laboratory keys, including the issuance key treated as compromised.

### `provider_b/`

Provider B runtime, mint utility, and laboratory keys.

### `association/`

Association recorder, provider registry, and boundary trust anchors.

### `attacker/`

The attacker's copy of Provider A's issuance key and the two attacker mint utilities.

### `operator/`

Operator notes, including retained misfires and corrections, and the pre-run baseline.

### `evidence/`

Scored, retained, pre-run, and preflight evidence.

Every folder has its own README.

---

## Laboratory keys

The provider and attacker directories include the private and public keys used for these laboratory tests. They are published intentionally so the test can be inspected and reproduced. They are laboratory-only credentials, not production keys.

Publishing them after the test does not change which components held or exercised which keys during the scored campaign.

---

## What MP003 does not establish

MP003 does not establish:

- that a compromised Provider A remains trustworthy;
- compromise of Provider A's boundary-signing key;
- compromise of any Provider B key;
- compromise of a provider host, the relay host, or the association host;
- detection, revocation, rotation, or recovery of a compromised key;
- denial-of-service resistance;
- crash-window, concurrent-use, power-loss, or restart behavior;
- cross-provider atomicity;
- globally synchronized chronology across hosts;
- implementation diversity between providers;
- physical actuation or independent hardware-witness evidence;
- independent association re-verification as part of the scored run.

Those properties require separate tests.

---

## Result summary

MP001 demonstrated physically separate provider authority domains.

MP002 showed the providers could disagree.

MP003 adds a harder condition:

**one provider is compromised.**

The attacker had Provider A's real issuance key.

Provider A was compromised, and executed attacker-minted authority.

Provider B was not. Provider A authority was refused at Provider B, directly and when relabeled, and Provider B's own authority kept working.

The relay remained transport.

The association remained evidence.

Provider authority remained provider-scoped.

That is the MP003 result.

Next: **MP004** — independent offline re-verification of the recorded provider evidence.
