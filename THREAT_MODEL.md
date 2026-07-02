# Threat Model

This repository defines provider-controlled verification constraint architectures.

The common failure mode is authority migration: an intermediary, artifact, ledger, endpoint, hub, timing signal, analytics layer, domain bridge, or adaptive evaluator begins to function as a source of authorization or execution meaning outside the provider-controlled boundary.

## In Scope

These architectures constrain:

- intermediary authority drift
- artifact misuse as authorization
- cross-provider authority collapse
- cross-domain verification state leakage
- timing, replay, or freshness acquiring authorization meaning
- ledger state substituting for provider verification
- constrained endpoints assuming authorization roles
- adaptive evaluators relocating decision authority
- pre-denial downstream activation

## Out of Scope

These architectures do not, by themselves, solve:

- compromised provider signing keys
- unsafe provider token issuance
- provider-side policy errors
- provider-side authorization bugs
- transport-layer compromise
- endpoint compromise after provider admission
- general denial-of-service protection
- malicious provider execution

## Core Assumption

Execution authority remains scoped to the provider-controlled boundary.

External systems may observe, relay, store, or present artifacts only within their constrained roles. They may not independently derive, elevate, amplify, reinterpret, or substitute execution authority.

## Reference Implementation

NUVL is included as a neutral reference implementation of the intermediary constraint.

NUVL is stateless, holds no provider signing material, evaluates no provider policy, and does not become the authority that decides execution.
