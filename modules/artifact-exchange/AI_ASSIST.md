# AI/ML Agent Constraints — Artifact Exchange + Execution Boundary Signaling

COPYRIGHT 2026 SETH BRIAN WELLS. ALL RIGHTS RESERVED.

READ THIS ENTIRE DOCUMENT BEFORE WRITING, MODIFYING, DEBUGGING, REFACTORING, TESTING, OR "IMPROVING" ANY CODE IN THIS DIRECTORY.

DO NOT SKIP SECTIONS.

DO NOT SUMMARIZE.

DO NOT PARAPHRASE AND MOVE ON.

THIS DIRECTORY IMPLEMENTS A PROVIDER-CONTROLLED VERIFICATION ARTIFACT EXCHANGE ARCHITECTURE WITH EXECUTION BOUNDARY SIGNALING.

THE CORE RULE IS SIMPLE:

INTERMEDIARIES CONVEY ARTIFACTS.

PROVIDERS DECIDE WHETHER EXECUTION OCCURS.

PROVIDERS GENERATE EXECUTION BOUNDARY SIGNALS.

IF YOU MOVE AUTHORIZATION, EXECUTION DECISIONING, ARTIFACT INTERPRETATION, OR BOUNDARY GENERATION INTO AN INTERMEDIARY, YOU HAVE DESTROYED THE ARCHITECTURE.

A PASSING TEST SUITE WITH A VIOLATED AUTHORITY BOUNDARY IS A FAILING SYSTEM.

---

# SECTION 1: WHAT THIS SYSTEM IS

This directory implements a framework for provider-controlled exchange of verification artifacts with execution boundary signaling.

The system separates:

1. Artifact conveyance
2. Provider-side evaluation
3. Execution initiation
4. Execution boundary signaling

These are NOT the same thing.

A verification artifact may be conveyed through one or more intermediaries.

The intermediary may route, forward, wrap, relay, transport, or deliver the artifact.

The intermediary does NOT interpret the artifact.

The intermediary does NOT decide whether the artifact is sufficient.

The intermediary does NOT authorize execution.

The intermediary does NOT generate execution boundary signals.

The provider-controlled system is the authority.

Only the provider-controlled system evaluates verification artifacts.

Only the provider-controlled system determines whether execution is initiated.

Only the provider-controlled system generates execution boundary signals representing lifecycle stages of execution.

## THIS SEPARATION IS THE PRODUCT.

If you collapse artifact conveyance into authorization, you broke it.

If you make the intermediary "smart," you broke it.

If you let a boundary signal originate outside the provider-controlled environment, you broke it.

---

# SECTION 2: ABSOLUTE PROHIBITIONS

## AN INTERMEDIARY MUST NEVER:

### INTERPRET VERIFICATION ARTIFACTS

A verification artifact is opaque to the intermediary.

The intermediary does not parse it for meaning.

The intermediary does not validate it for sufficiency.

The intermediary does not infer authorization from it.

The intermediary does not inspect fields to determine whether an operation should proceed.

The intermediary does not decide that an artifact is "good enough."

The intermediary conveys.

That is all.

---

### EXERCISE AUTHORIZATION AUTHORITY

The intermediary must never authorize execution.

Not directly.

Not indirectly.

Not by returning "approved."

Not by choosing a provider action.

Not by allowing downstream execution because a local check passed.

Not by treating successful artifact formation as authorization.

Artifact presence is NOT authorization.

Artifact format validity is NOT authorization.

Artifact delivery is NOT authorization.

Only provider-side execution initiation constitutes authorization.

---

### GENERATE EXECUTION BOUNDARY SIGNALS

Execution boundary signals represent provider-defined lifecycle stages.

Examples may include:

- initiation
- progression
- suspension
- completion
- termination

The intermediary does not generate these signals.

The intermediary does not simulate these signals.

The intermediary does not precompute these signals.

The intermediary does not issue placeholder boundary values.

The intermediary does not "confirm" execution boundaries.

Execution boundary signaling is provider-controlled.

---

### TREAT ARTIFACT EXCHANGE AS IDENTITY PROPAGATION

This system is not an identity propagation framework.

Do not convert verification artifacts into identity assertions.

Do not require global identity propagation across intermediaries.

Do not add user identity inspection to the intermediary.

Do not require every hop to understand who the requester is.

Do not turn the intermediary into an identity-aware authorization service.

The artifact is not identity.

The artifact is not permission.

The artifact is input to provider-side evaluation.

---

### RETURN PROVIDER-INTERNAL EVALUATION LOGIC

Provider-side evaluation logic remains provider-controlled.

The provider does not disclose:

- internal policy logic
- model logic
- rules
- scoring criteria
- compliance logic
- execution semantics
- boundary-generation rationale
- rejection reasons, unless explicitly designed outside this core path

Do not add debug output that exposes provider internals.

Do not add logs that leak provider evaluation semantics.

Do not add API responses that explain provider decisioning.

---

### REPAIR FAILED ARTIFACTS

If an artifact fails provider-side evaluation, the system is working.

Do not "repair" by:

- asking the provider for missing data
- modifying the artifact
- adding default fields
- replaying a prior successful artifact
- weakening validation
- substituting a new artifact
- retrying with guessed values
- exposing rejection details to the intermediary

Failure is not a bug when the provider refuses initiation.

Failure is the boundary doing its job.

---

### CACHE AUTHORIZATION SEMANTICS

An intermediary may have ordinary transport, routing, or operational state.

That does NOT allow it to retain authorization semantics.

The intermediary must not cache:

- provider authorization outcomes
- prior successful artifacts as proof of future permission
- provider boundary signals as reusable authority
- evaluation results
- request allow/deny decisions
- lifecycle conclusions

Operational state is permitted only if it does not become authorization state.

---

### TURN DOWNSTREAM OBSERVATION INTO CONTROL AUTHORITY

Execution boundary signals may be externally observable or consumable by downstream systems.

That does NOT mean downstream systems gain provider authority.

A downstream observer may record, verify, or consume a boundary signal.

A downstream observer must not become the authority that decides whether provider execution occurred.

Boundary signals are evidence of provider-defined lifecycle stages.

They are not transferable authorization authority.

---

# SECTION 3: THE PROVIDER

## THE PROVIDER-CONTROLLED SYSTEM IS THE AUTHORITY

The provider evaluates verification artifacts using provider-selected logic.

Provider-selected logic may include:

- rules
- models
- internal policy
- context
- state
- compliance checks
- risk evaluation
- execution constraints
- provider-defined mechanisms

The specific evaluation logic is not dictated by this repository unless explicitly implemented in a provider module.

The architecture requires only this:

## PROVIDER AUTHORITY REMAINS INSIDE THE PROVIDER-CONTROLLED SYSTEM.

---

## THE PROVIDER MAY INITIATE OR NOT INITIATE EXECUTION

Authorization is realized by provider-side initiation of execution.

If execution is initiated, authorization occurred.

If execution is not initiated, authorization did not occur.

Do not add a separate intermediary approval layer.

Do not treat artifact delivery as approval.

Do not treat local validation as approval.

Do not treat successful routing as approval.

The provider decides by initiating or not initiating execution.

---

## THE PROVIDER GENERATES EXECUTION BOUNDARY SIGNALS

When execution is authorized and initiated, the provider may generate one or more execution boundary signals.

Boundary signals may correspond to:

- start
- intermediate progress
- completion
- failure
- suspension
- termination
- other provider-defined lifecycle stages

Boundary signals may be cryptographically derived, linked, signed, anchored, recorded, or otherwise associated with the authorized operation.

But those mechanisms are provider-selected.

Do not force a specific cryptographic primitive unless the implementation explicitly requires it.

Do not hard-code a ledger.

Do not hard-code zero-knowledge proofs.

Do not hard-code a trusted execution environment.

Do not hard-code a specific identity provider.

The framework is mechanism-neutral.

---

## THE PROVIDER MUST NOT OUTSOURCE BOUNDARY DETERMINATION

The provider may expose boundary signals.

The provider may allow boundary signals to be recorded.

The provider may allow downstream systems to consume them.

But the provider must not delegate boundary determination to:

- the intermediary
- a broker
- a gateway
- a shared policy layer
- a logging system
- a downstream verifier
- an external compliance engine

External systems may observe.

They do not decide.

---

# SECTION 4: VERIFICATION ARTIFACTS

A verification artifact is associated with an operation request.

It may be derived from, bound to, or otherwise associated with request information, provider-controlled elements, contextual data, or other implementation-specific material.

The architecture does not require one artifact format.

The architecture does not require one token standard.

The architecture does not require one cryptographic method.

The architecture requires that artifact evaluation authority remains provider-controlled.

---

## A VERIFICATION ARTIFACT IS NOT:

- authorization
- identity
- provider approval
- an execution boundary
- a substitute for provider evaluation
- proof that execution occurred
- proof that execution must occur
- proof that the intermediary may decide

A verification artifact is material conveyed for provider-side evaluation.

---

## DO NOT "IMPROVE" ARTIFACTS BY ADDING INTERMEDIARY AUTHORITY

Do not add:

- intermediary approval signatures
- intermediary policy conclusions
- intermediary trust scores
- intermediary allow/deny flags
- intermediary-generated boundary fields
- intermediary-generated execution claims
- intermediary interpretation metadata

These additions contaminate the artifact exchange.

The intermediary may package or convey.

It may not decide.

---

# SECTION 5: EXECUTION BOUNDARY SIGNALS

Execution boundary signals are provider-generated representations of execution lifecycle stages.

They may indicate that a provider-defined boundary was reached.

Examples:

```text
STARTED
IN_PROGRESS
COMPLETED
SUSPENDED
TERMINATED
FAILED
```

The exact labels are implementation-specific.

The authority is not.

Boundary signals must originate under provider control.

---

## EXECUTION BOUNDARY SIGNALS ARE NOT:

- intermediary acknowledgments
- transport receipts
- gateway approvals
- identity tokens
- reusable permissions
- authorization grants
- global policy decisions

They are provider-controlled lifecycle signals.

---

## BOUNDARY SIGNALS MUST NOT BE FABRICATED

Never emit a boundary signal because:

- the artifact looked valid
- the intermediary forwarded successfully
- a request reached the provider endpoint
- a queue accepted a message
- a timeout did not occur
- a test expected a signal
- a UI needs a status

A boundary signal is emitted only when the provider-controlled logic determines that the corresponding lifecycle boundary exists.

No boundary, no signal.

---

## BOUNDARY SIGNALS MUST NOT EXPOSE PROVIDER INTERNALS

A boundary signal may identify a lifecycle stage.

It must not reveal provider-internal logic unless explicitly intended.

Do not include:

- raw policy rules
- private evaluation rationale
- sensitive execution state
- model weights
- compliance internals
- provider secrets
- signing keys
- internal scoring details
- sensitive operational metadata

Boundary signaling should make execution lifecycle externally observable without disclosing provider internals.

---

# SECTION 6: INTERMEDIARY ROLE

The intermediary is a conveyance component.

It may:

- receive an operation request
- convey a verification artifact
- route to a provider-controlled system
- preserve transport integrity
- maintain non-authoritative operational state
- perform ordinary network handling

It must not:

- interpret verification semantics
- determine authorization
- initiate provider execution
- generate execution boundary signals
- infer provider outcomes
- expose provider decision logic
- convert transport success into authorization
- convert delivery failure into provider rejection

## THE INTERMEDIARY IS NOT THE AUTHORITY.

---

# SECTION 7: TEST PHILOSOPHY

Tests must prove authority separation.

A correct test suite must verify that:

- an intermediary cannot authorize execution
- an intermediary cannot generate valid provider boundary signals
- an intermediary cannot infer provider outcomes from artifact contents
- malformed artifacts do not get repaired by the intermediary
- valid-looking artifacts still require provider-side evaluation
- boundary signals appear only when provider-side lifecycle events occur
- downstream observation does not become downstream control

A passing test suite that violates any of these principles is a failing test suite.

---

## CANONICAL FAILURE CASES

The following should fail or produce no provider initiation unless provider logic explicitly authorizes:

- malformed artifact
- missing artifact
- altered artifact
- stale artifact
- artifact associated with wrong request
- artifact associated with wrong context
- forged boundary signal
- intermediary-generated boundary signal
- replayed artifact, if replay protection is implemented
- expired artifact, if expiry is implemented

Do not weaken the tests.

Do not weaken the attacker.

Fix the implementation.

---

# SECTION 8: HOW TO KNOW YOU MADE A MISTAKE

You violated the architecture if any of the following are true:

- the intermediary can approve execution
- the intermediary can deny execution semantically
- the intermediary parses artifacts to determine sufficiency
- the intermediary treats artifact presence as authorization
- the intermediary emits execution boundary signals
- boundary signals are generated before provider-side initiation
- provider internals are exposed to make debugging easier
- downstream consumers gain authority over provider execution
- the system requires identity propagation across every intermediary
- the system requires a shared policy layer to determine provider execution
- tests pass only because intermediary logic was made smarter
- tests pass only because provider authority was weakened
- logs reveal provider decision logic
- provider rejection is "fixed" by the intermediary

If any of the above become true:

## REVERT YOUR CHANGE.

The system was cleaner before you modified it.

---

# SECTION 9: COMMON AI AGENT FAILURE MODES

AI assistants frequently attempt to make distributed systems "better" by adding intelligence.

In this architecture, that instinct is dangerous.

Do not add:

- helpful retries
- semantic validation in the intermediary
- policy reconciliation in the gateway
- local allow/deny caching
- shared authorization state
- provider decision mirroring
- transparent fallback authorization
- inferred execution status
- fake boundary signals for UX convenience
- detailed rejection explanations routed through the intermediary

These are not improvements.

They are authority leaks.

---

# SECTION 10: OPTIONAL MECHANISMS

The framework may be implemented with many different technical mechanisms.

Optional mechanisms may include:

- digital signatures
- HMAC
- public-key verification
- append-only logs
- hash chaining
- Merkle structures
- trusted execution environments
- zero-knowledge proofs
- hardware security modules
- secure enclaves
- provider-controlled audit stores

None of these are mandatory unless the specific implementation says so.

Do not add optional mechanisms merely because they are fashionable.

Do not turn an optional embodiment into a required architecture.

The invariant is authority placement, not tool selection.

---

# SECTION 11: RELATIONSHIP TO NUVL CORE

This repository may be related to NUVL, but it is not a license to collapse all layers into one component.

NUVL-style constraints may require a neutral intermediary to hold nothing, know nothing, decide nothing, and learn nothing.

Artifact Exchange focuses on provider-controlled evaluation of verification artifacts and provider-generated execution boundary signaling.

Both architectures preserve the same central principle:

## AUTHORITY DOES NOT MOVE DOWNSTREAM INTO THE INTERMEDIARY.

Do not merge layers unless the architecture expressly requires it.

Do not import provider-side logic into an intermediary.

Do not move execution boundary generation outside provider control.

---

# SECTION 12: FOR THE AGENT THAT WANTS TO HELP

You may feel compelled to:

- add a gateway policy evaluator
- inspect artifacts for safety
- normalize artifact formats
- generate placeholder boundary signals
- expose provider rejection reasons
- cache successful artifacts
- retry failed provider evaluations
- infer execution status from network behavior
- add identity propagation
- require a central policy engine
- make tests pass by sharing provider secrets

Every one of these instincts is wrong unless explicitly authorized by the architecture.

The intermediary is not incomplete.

The provider is not missing a helper.

The boundary signal is not a UI status message.

The artifact is not a permission slip.

The provider-controlled boundary is the security model.

# DO NOT ADD AUTHORITY TO THE INTERMEDIARY.

# DO NOT GENERATE BOUNDARY SIGNALS OUTSIDE THE PROVIDER.

# DO NOT TURN OBSERVATION INTO CONTROL.

---

# SECTION 13: SUMMARY

THE INTERMEDIARY CONVEYS ARTIFACTS.

THE PROVIDER EVALUATES ARTIFACTS.

THE PROVIDER INITIATES OR DOES NOT INITIATE EXECUTION.

THE PROVIDER GENERATES EXECUTION BOUNDARY SIGNALS.

DOWNSTREAM SYSTEMS MAY OBSERVE SIGNALS WITHOUT RECEIVING AUTHORITY.

ARTIFACT EXCHANGE IS NOT AUTHORIZATION.

BOUNDARY SIGNALING IS NOT INTERMEDIARY CONTROL.

IF YOU MOVE DECISION AUTHORITY OUT OF THE PROVIDER, THE SECURITY MODEL IS VOID.

---

This document MUST be read by any AI agent, code assistant, automated tooling system, or language model before modifying files in this directory.

Violating these constraints renders the security model void regardless of whether tests pass.
