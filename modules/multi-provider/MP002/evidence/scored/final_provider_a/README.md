# Final Provider A State

This directory contains the final durable Provider A state captured after the MP002 scored campaign.

It preserves Provider A's local execution record and spent-authorization state after completion of both scored cases.

## Contents

- `provider_a_execution.jsonl` — Provider A's durable local execution records.
- `provider_a_spent_state.json` — Provider A's durable record of consumed authorizations.

These files were copied from Provider A after the scored requests completed and before the provider process was shut down.

## Scored result represented here

Provider A participated in both scored cases:

- **B01_CONTROL** — Provider A accepted its valid provider-issued authorization and executed.
- **D01_POLICY_DIVERGENCE** — Provider A independently permitted the request and executed even though Provider B denied the same operation under Provider B's own local policy.

The final captured state contains:

- 2 Provider A execution records.
- 2 consumed Provider A authorizations.

The D01 Provider A authorization was consumed and is present in Provider A's final spent state.

## What this evidence supports

This directory provides provider-local durable evidence that Provider A executed both scored requests and consumed the corresponding Provider A authorizations.

For D01, this state is consistent with the signed Provider A `START` and `COMPLETE` boundary events recorded by the association.

Provider A's execution does not establish or imply authority for Provider B. Each provider validates, decides, consumes, and records its own provider-scoped authorization independently.

## What this evidence does not establish

These files are Provider A's local final state. They do not by themselves establish:

- Provider B's execution or authorization state.
- A globally synchronized chronology across hosts.
- Cross-provider atomic execution.
- A requirement that all providers approve before another provider may execute.
- Crash-window, concurrent-use, or power-loss behavior for MP002.
- Physical actuation or independent hardware-witness evidence.

MP002 intentionally permits independent provider decisions. In D01, Provider A executed while Provider B denied. The test therefore demonstrates provider-local decision independence, not an all-or-nothing distributed transaction.

## Related evidence

The corresponding Provider B final state is preserved in:

`../final_provider_b/`

Signed association records for both scored cases are preserved in:

`../association.jsonl`

The scored campaign summary is preserved in:

`../SCORECARD.txt`

Integrity information for the scored evidence set is preserved in:

`../SHA256SUMS.txt`
