# Final Provider B State

This directory contains the final durable Provider B state captured after the MP002 scored campaign.

It preserves Provider B's local execution record and spent-authorization state after completion of both scored cases.

## Contents

- `provider_b_execution.jsonl` — Provider B's durable local execution records.
- `provider_b_spent_state.json` — Provider B's durable record of consumed authorizations.

These files were copied from Provider B after the scored requests completed and before the provider process was shut down.

## Scored result represented here

Provider B handled both scored cases differently under its own local policy:

- **B01_CONTROL** — Provider B accepted its valid provider-issued authorization and executed.
- **D01_POLICY_DIVERGENCE** — Provider B validated its provider-specific authorization, applied its local policy, and returned a signed `DENY` with reason `policy_denied` before authorization consumption or execution.

The final captured state contains:

- 1 Provider B execution record.
- 1 consumed Provider B authorization.

The D01 Provider B authorization is absent from the final spent state and no D01 execution record exists.

## What this evidence supports

This directory provides provider-local durable evidence that Provider B executed B01 but did not execute D01.

For D01, the final state is consistent with the signed Provider B `DENY policy_denied` event recorded by the association.

The D01 authorization remained unconsumed because the tested Provider B policy gate was applied before the durable spent-state update.

This demonstrates the tested ordering:

valid provider-specific authorization  
→ provider-local policy decision  
→ denial before consumption  
→ no Provider B execution

Provider A's decision did not cause Provider B to execute and did not consume Provider B's authorization.

## Important interpretation

The D01 authorization remained valid and unspent after the policy denial.

MP002 does not test what would happen if Provider B's local policy later changed and the same authorization were presented again. No claim about later acceptance, expiration, revocation, or subsequent consumption is made from this evidence.

The policy used in MP002 was deliberately simple and deterministic: Provider B denied the test context `CTX_MP002_DIVERGE`.

The claim under test is not policy sophistication. It is that Provider B retains its own execution decision and that another provider, the relay, or the association does not override that decision.

## What this evidence does not establish

These files do not by themselves establish:

- Provider A's execution or authorization state.
- A globally synchronized chronology across hosts.
- Cross-provider atomic execution.
- An all-provider approval requirement.
- Later behavior of the unconsumed D01 authorization.
- Crash-window, concurrent-use, or power-loss behavior for MP002.
- Physical actuation or independent hardware-witness evidence.

MP002 demonstrates independent provider judgment, not an all-or-nothing distributed transaction.

## Related evidence

The corresponding Provider A final state is preserved in:

`../final_provider_a/`

Signed association records for both scored cases are preserved in:

`../association.jsonl`

The scored campaign summary is preserved in:

`../SCORECARD.txt`

Integrity information for the scored evidence set is preserved in:

`../SHA256SUMS.txt`
