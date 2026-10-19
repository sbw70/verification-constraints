# Final Provider A State

This directory contains the final durable Provider A state captured after the MP003 scored campaign.

## Contents

- `provider_a_execution.jsonl` — Provider A's durable local execution records.
- `provider_a_spent_state.json` — Provider A's durable record of consumed authorizations.

These files were copied byte-for-byte via `scp` from Provider A (`Xer0trust-3`, 192.168.1.118) after B02 completed and before the provider process was shut down. They are identical to `../B02_POST_ATTACK_B_HEALTH/_post_a/`.

| File | SHA-256 |
|---|---|
| `provider_a_execution.jsonl` | `f5cc50251cfeaf9ae500b1272b8ea81ca08d602d3627635dfba7da48eb4bb9db` |
| `provider_a_spent_state.json` | `539ec62758281220d6025ca653fafaae59f24ad19f5ea90f3613d357f2c4bbf0` |

## Scored result represented here

The final captured state contains 3 Provider A execution records and 3 consumed Provider A authorizations:

| Local seq | Case | Authorization | Origin |
|---|---|---|---|
| 1 | B01 | `aac7988b08e14b382105470d20c9cc3b15abf50ff288cba615cb962e5d12cfc1` | legitimate Provider A mint |
| 2 | C01 | `6e3ce147b1337f74451823a78cef40011378c88e2e4103f2ffcd82845dc7de1a` | attacker copy of Provider A issuance key |
| 3 | C02 | `0e2ed472caeda2781354e5545f870f70d00910a49019e230e9d7d09edfcb1689` | attacker copy of Provider A issuance key |

Provider A received no authorization in C03 or B02 and denied both with `auth_missing`. Its state did not change after C02.

## What this evidence supports

This is Provider A's own durable record that it executed and consumed the B01, C01, and C02 authorizations, consistent with the signed Provider A `START` and `COMPLETE` events in `../association.jsonl`.

Two of the three entries were produced with the compromised issuance key. That is the intended MP003 result: Provider A cannot distinguish attacker-minted authority from legitimately minted authority, because both are signed by the same key. Provider A's authority boundary is compromised by design of the test.

## What this evidence does not establish

These files do not by themselves establish:

- Provider B's state (see `../final_provider_b/`);
- that Provider A detected or could detect the compromise;
- globally synchronized chronology across hosts;
- crash-window, concurrent-use, or power-loss behavior.

## Related evidence

`../final_provider_b/`

`../association.jsonl`

`../SCORECARD.txt`

`../SHA256SUMS.txt`
