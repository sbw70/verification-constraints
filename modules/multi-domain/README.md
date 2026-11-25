# Stateless Verification Architecture Across Multiple Domains

## Overview

Multi-Domain Stateless Verification (MDSV) defines an architecture for conveying verification material across independent technical domains without centralizing authorization authority.

A neutral intermediary performs mechanical request representation, domain routing, and artifact conveyance.

It does not evaluate authorization policy, enforce access control, or initiate provider-controlled operations.

Authorization authority remains domain-scoped. Each provider independently determines whether to initiate execution.

The architectural constraints are language-agnostic and do not depend on a particular cryptographic mechanism, transport protocol, or deployment environment.

This module contains a minimal executable reference implementation and separately documented experimental implementations.

---

## 1. Module Organization

    multi-domain/
    |
    |-- README.md
    |-- AI_ASSIST.md
    |-- MDSV.py
    |
    `-- MD001/

| Component | Purpose |
|---|---|
| [MDSV.py](MDSV.py) | Minimal executable architectural reference |
| [AI_ASSIST.md](AI_ASSIST.md) | Constraints governing AI-assisted development and modification |
| [MD001](MD001/) | Independently documented experimental implementation |

The reference implementation illustrates the architectural constraints.

Experimental directories contain implementations and evidence evaluating specific properties under defined conditions.

Individual experimental results must not be interpreted as validation of every possible implementation of the architecture.

---

## 2. Design Goals

The architecture is designed to:

- Support verification conveyance across independent technical domains.
- Preserve domain-scoped authorization authority.
- Preserve provider-controlled execution initiation.
- Prevent migration of authorization logic into intermediaries.
- Avoid requiring shared signing material across domains.
- Operate without retained authorization state at the intermediary.
- Enable independent domain evaluation using domain-selected verification logic.
- Maintain separation between verification, authorization, and execution.

The intermediary may perform mechanical routing and artifact conveyance.

It does not become the authority responsible for authorizing operations.

---

## 3. Architectural Model

    REQUESTER
        |
        v
    NEUTRAL INTERMEDIARY
        |
        | Mechanical representation
        | Domain routing
        | Artifact conveyance
        |
        +-------------+-------------+
        |             |             |
        v             v             v
    DOMAIN A      DOMAIN B      DOMAIN N
        |             |             |
        v             v             v
    LOCAL         LOCAL         LOCAL
    EVALUATION    EVALUATION    EVALUATION

Each domain maintains its own verification criteria and operational boundaries.

The intermediary does not require access to the internal authorization policies of participating domains.

Domain identifiers are routing inputs.

They do not constitute authorization, entitlement, or permission to execute an operation.

The architectural model does not require participating domains to share authorization state or adopt identical verification mechanisms.

---

## 4. Authority Boundary

### Intermediary Responsibilities

The intermediary may:

- Receive requests.
- Construct mechanical request representations.
- Select configured domain routes.
- Convey verification artifacts.
- Perform transport-related processing required by the implementation.

The intermediary must not:

- Originate provider authorization.
- Enlarge provider-granted authority.
- Substitute authorization decisions.
- Evaluate provider-specific authorization policy.
- Execute provider-controlled operations.
- Treat domain selection as entitlement.
- Introduce unauthorized cross-domain fallback.

### Provider Responsibilities

Providers remain responsible for:

- Domain-local verification.
- Authorization criteria.
- Signing-key custody.
- Execution decisions.
- Operational enforcement.
- Any required replay or consumption controls.

The intermediary does not replace these functions.

### Domain Independence

Participation in a common verification architecture does not require one domain to surrender its operational authority to another.

Verification material may cross domain boundaries without transferring the authority associated with the represented operation.

---

## 5. Verification and Authorization

Verification and authorization are distinct operations.

Verification determines whether presented material satisfies defined verification criteria.

Authorization determines whether an operation may be initiated within a provider-controlled boundary.

Successful verification does not inherently authorize execution.

Similarly, a valid signed assertion establishes authenticity and integrity relative to the applicable verification key and criteria. It does not independently establish the truth of the underlying asserted event.

Repeated verification does not inherently authorize repeated execution.

Systems requiring single-use execution authority, durable consumption, or replay prevention must enforce those properties separately.

---

## 6. Statelessness

Statelessness applies to the defined verification intermediary and its architectural responsibilities.

The intermediary does not retain authorization state that allows it to originate, extend, or reuse provider-controlled authority.

This constraint does not prohibit:

- Provider-local operational state.
- Provider-local authorization records.
- Locally provisioned verification material.
- Transport-related processing.
- Observational evidence collection.
- Independent experimental instrumentation.

Observational records must not become inputs that grant or enlarge authorization authority at the intermediary.

The presence of provider-local state does not inherently violate intermediary statelessness.

---

## 7. Non-Goals

The architecture does not:

- Provide a universal authorization decision across domains.
- Merge domain policies into a shared enforcement layer.
- Require identity propagation across domain boundaries.
- Require shared signing keys or shared policy semantics.
- Replace provider-local security controls.
- Guarantee confidentiality independently of the selected transport.
- Protect against every denial-of-service condition.
- Secure compromised provider implementations.
- Guarantee that an asserted event actually occurred.
- Establish production readiness independently of implementation-specific validation.

The architecture constrains authority location and responsibility.

Additional security properties must be established by the implementations responsible for enforcing them.

---

## 8. Minimal Reference Implementation

[MDSV.py](MDSV.py) is the original executable reference implementation.

It demonstrates domain-aware mechanical routing without centralizing authorization.

The reference is written in Python for portability and zero-dependency execution.

### Reference Architecture

    REQUESTER
        |
        v
    NEUTRAL INTERMEDIARY
        |
        | X-Domain
        | Mechanical binding
        |
        +----------+
        |          |
        v          v
    DOMAIN A    DOMAIN B
        |          |
        v          v
    LOCAL       LOCAL
    EVALUATION  EVALUATION

The intermediary derives a SHA-256 representation of the request.

It constructs a deterministic binding incorporating:

    BIND_V1
    domain
    request representation
    verification context

The binding is not an authorization decision.

Each provider independently evaluates the received artifact.

The reference implementation uses provider-specific HMAC keys within its provider functions.

Those keys are not used by the intermediary's request-processing function.

### Execution Flow

1. A requester submits an operation request.
2. The intermediary reads the requested domain.
3. The intermediary selects the configured provider route.
4. The intermediary derives a SHA-256 request representation.
5. The intermediary constructs a mechanical binding.
6. The intermediary asynchronously conveys the artifact.
7. The provider independently evaluates the artifact.
8. The provider determines whether to initiate the represented operation.
9. The intermediary returns HTTP 204 without receiving the provider's decision.

The reference demonstrates separation between mechanical routing and provider-local evaluation.

It does not implement a complete production authorization system.

### Running the Reference

From the module directory:

```bash
python3 MDSV.py
```

The demonstration starts:

| Component | Port |
|---|---:|
| Intermediary | 8080 |
| Domain A | 9090 |
| Domain B | 9091 |

The requester submits one example request to each domain.

Expected requester response:

    HTTP 204

Provider-local output includes:

    DOMAIN_A: INITIATED
    DOMAIN_B: INITIATED

These messages represent the demonstration's provider-local evaluation results.

They are not evidence of physical actuation.

### Reference Limitations

The implementation uses demonstration-only provider secrets.

It uses plaintext HTTP and does not provide production-grade authentication, confidentiality, or operational enforcement.

Its provider evaluation checks the configured domain, verification context, and deterministic binding.

It should not be treated as proof that arbitrary requesters are authorized.

The reference implementation is distinct from the separately documented experimental implementations.

---

## 9. Experimental Validation

Experimental implementations evaluate specific architectural properties under defined laboratory conditions.

Each experiment is independently identified and documented.

Experimental implementations may use different:

- Cryptographic mechanisms.
- Verification artifact formats.
- Domain configurations.
- Transport mechanisms.
- Physical or simulated environments.
- Verification criteria.
- Observation and evidence collection methods.

These implementation differences do not alter the underlying architectural constraints.

Experimental conclusions remain bounded by the conditions, observations, and limitations documented within each experiment.

### Experiment Index

| Experiment | Property Under Evaluation | Documentation |
|---|---|---|
| MD001 | Cross-domain signed assertion verification, modification detection, and producer-unavailable verification | [Experiment Overview](MD001/README.md) · [Results](MD001/RESULTS.md) · [Provenance](MD001/PROVENANCE.md) |

Each experiment directory is the authoritative location for its implementation, experimental conditions, scored results, supporting records, and documented limitations.

---

## 10. Experimental Documentation

Experimental documentation is maintained within the corresponding experiment directory.

Depending on the experiment, documentation and supporting records may include:

| Record | Purpose |
|---|---|
| `README.md` | Experiment overview, architecture, scope, and navigation |
| `RESULTS.md` | Recorded experimental observations and scored dispositions |
| `PROVENANCE.md` | Evidence origins, implementation identities, collection conditions, and limitations |
| `SHA256SUMS.txt` | Defined publication-time integrity inventory |
| Historical integrity records | Original manifests, recorded checksums, and artifact comparisons |
| Implementation files | Source code and supporting components |
| Configuration records | Runtime settings and deployment configuration |
| Validation records | Local tests, compatibility checks, and preflight observations |
| Scored evidence | Records supporting individual experimental dispositions |

The precise contents and organization are documented within each experiment.

This module-level README does not duplicate experiment-specific results or evidence inventories.

---

## 11. Evidence Integrity

Experimental evidence must remain distinguishable from subsequently generated publication documentation.

Original evidence records should be preserved without modification.

Historical integrity records and publication-time checksum inventories serve different purposes.

Historical integrity records document previously recorded file or artifact identities.

Publication-time checksums establish byte consistency against a defined publication inventory.

Publication-time checksums must not be represented as recovered collection-time checksums.

The scope of each checksum inventory, applicable exclusions, historical coverage, and unresolved limitations must be documented within the corresponding experiment.

Successful checksum verification establishes consistency with the referenced inventory.

It does not independently establish the validity of an experimental conclusion or authenticate the historical collection process.

Additional experiments must use separately identified evidence directories.

Historical evidence must not be overwritten by subsequent experimental activity.

---

## 12. Independent Review

Reviewers interested in the minimal architectural reference should begin with:

[MDSV.py](MDSV.py)

Reviewers interested in experimental validation should select an experiment from the experiment index.

The recommended review sequence is:

1. Review the experiment overview and defined architectural property.
2. Examine the experimental conditions and scored results.
3. Review the provenance and documented limitations.
4. Verify the applicable integrity inventories.
5. Examine the original scored evidence.
6. Review supporting implementation, configuration, and validation records.
7. Evaluate whether the recorded observations support the stated conclusions.

Development validation, physical preflight, and scored experimental evidence must remain distinguishable.

Unsuccessful development or validation attempts must not be represented as successful scored observations.

The experimental documentation defines which properties were evaluated and which remain outside the demonstrated scope.

---

## 13. AI-Assisted Development Constraints

The module contains:

[AI_ASSIST.md](AI_ASSIST.md)

This file defines constraints for AI-assisted development and modification.

The central restrictions include:

- Domain routing must not become authorization.
- Intermediaries must not evaluate provider policy.
- Unauthorized cross-domain fallback must not be introduced.
- Domain identifiers must not be treated as entitlement.
- Provider-controlled authority must remain within provider boundaries.
- Experimental observations must not be expanded into unsupported architectural claims.

Review this file before modifying the module.

Experimental implementations must preserve the architectural constraints applicable to the property under evaluation.

---

## 14. Licensing

This module is not released under the Apache 2.0 license applied to the repository root.

Commercial licensing terms apply.

Non-commercial research evaluation may be available upon request.

See the repository's module-specific licensing notices for applicable terms.

---

## 15. Conclusion

Multi-Domain Stateless Verification separates mechanical verification conveyance from domain-local authorization and execution.

The reference implementation illustrates this architectural separation.

Individual experimental implementations evaluate specific properties and preserve the corresponding evidence within independently documented experiment directories.

The architecture does not require a shared authorization authority across participating domains.

Its central constraint remains:

**Mechanical conveyance of verification material does not transfer authorization authority to the intermediary.**
