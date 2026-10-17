# Final Provider B State

This directory contains the final durable Provider B state captured after the MP003 scored campaign.

## Contents

- `provider_b_execution.jsonl` — Provider B's durable local execution records.
- `provider_b_spent_state.json` — Provider B's durable record of consumed authorizations.

These files were copied byte-for-byte via `scp` from Provider B (`Xer0trust2`, 192.168.1.106) after B02 completed and before the provider process was shut down. They are identical to `../B02_POST_ATTACK_B_HEALTH/_post_b/`.

| File | SHA-256 |
|---|---|
| `provider_b_execution.jsonl` | `cf422d6db5ef648816fbcad593a9d98e1a5304fccc57bec32c4b2b8532e1b4bd` |
| `provider_b_spent_state.json` | `8228e5e53d1778f53fc49b836b40a80ccbfaff5ba44ae1c5ca36de3f5e0c1dc5` |

## Scored result represented here

The final captured state contains 2 Provider B execution records and 2 consumed Provider B authorizations:

| Local seq | Case | Authorization | Origin |
|---|---|---|---|
| 1 | B01 | `92a84e45db900b5ce25807cb8d16267657a922f29ded3a11908f6ef7d8c1771b` | legitimate Provider B mint |
| 2 | B02 | `8f0e91c818c7bce6e3252244fc59fa404a808bfe4c2da4e1547aa597f75134a1` | legitimate Provider B mint |

Neither authorization presented to Provider B during the attack cases appears here:

- C02 Provider A authorization `0e2ed472…` — not present.
- C03 forged Provider B claim `11e016ab…` — not present.

Provider B's state was byte-identical after B01, C01, C02, and C03, and changed only when B02 executed.

## What this evidence supports

This is Provider B's own durable record that the only authority it consumed and acted on during MP003 was authority minted with its own issuance key.

Exposure of Provider A's issuance key did not result in any Provider B consumption or execution.

## What this evidence does not establish

These files do not by themselves establish:

- resistance to compromise of Provider B's own keys or host;
- post-restart persistence of Provider B state (not tested in MP003);
- globally synchronized chronology across hosts;
- crash-window, concurrent-use, or power-loss behavior.

## Related evidence

`../final_provider_a/`

`../association.jsonl`

`../SCORECARD.txt`

`../SHA256SUMS.txt`
