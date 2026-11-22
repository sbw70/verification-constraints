# MD001 — Runtime Configuration

## Multi-Domain Stateless Verification

**Organization:** Xer0trust LLC  
**Experiment:** MD001  
**Component:** Runtime configuration  
**Scored date:** November 19, 2026  
**Configuration files:** 4

---

## 1. Overview

This directory contains the runtime configuration files for MD001 — Multi-Domain Stateless Verification.

The configurations define:

- Network listening endpoints.
- Permitted source addresses.
- Downstream forwarding destinations.
- Runtime component roles.
- Normal forwarding behavior.
- Controlled assertion modification for the negative experiment.

The configuration files support the separation between the originating domain, mechanical transport, and independent verification.

The normal operating configuration forwards signed assertions without intentionally modifying their contents.

The negative configuration introduces a controlled modification at Domain B ingress to evaluate signature-verification behavior.

These files are configuration artifacts.

They are not authorization grants, signing keys, or independent proof of successful execution.

---

## 2. Directory Contents

```text
configs/
|
|-- relay.json
|
|-- ingress.json
|
|-- ingress_N01.json
|
|-- verifier.json
|
`-- README.md
```

Each JSON file defines one runtime component configuration.

| File | Role | Mode | Purpose |
|---|---|---|---|
| `relay.json` | Relay | `pass` | Forward assertions toward Domain B |
| `ingress.json` | Ingress | `pass` | Forward assertions to the local verifier |
| `ingress_N01.json` | Ingress | `tamper` | Modify an assertion during the negative experiment |
| `verifier.json` | Verifier | `pass` | Receive assertions for local verification |

The `mode` field describes application behavior.

It does not represent authorization status.

---

# 3. Network Topology

The configured network path is:

```text
DOMAIN A
Producer
10.10.10.10
       |
       | Signed assertion
       v
MECHANICAL RELAY
30.30.30.30:18081
       |
       | Forward assertion
       v
DOMAIN B INGRESS
40.40.40.40:18443
       |
       | Local forwarding
       v
DOMAIN B VERIFIER
127.0.0.1:18444
       |
       | Signature verification
       v
VERIFICATION RESULT
```

The relay and ingress are separate runtime roles.

The verifier listens on the Domain B host's loopback interface.

The configuration therefore distinguishes external cross-domain transport from local verification.

---

# 4. relay.json — Mechanical Relay

## 4.1 Recorded Configuration

```json
{
  "role": "relay",
  "listen": {
    "host": "30.30.30.30",
    "port": 18081
  },
  "allowed_peer": null,
  "target": {
    "host": "40.40.40.40",
    "port": 18443
  },
  "mode": "pass"
}
```

## 4.2 Responsibility

The relay receives an assertion and forwards it toward Domain B ingress.

Its configured listening endpoint is:

```text
30.30.30.30:18081
```

Its downstream target is:

```text
40.40.40.40:18443
```

The relay operates in:

```text
mode = pass
```

This specifies normal forwarding rather than deliberate assertion modification.

## 4.3 Peer Restriction

The configuration contains:

```json
"allowed_peer": null
```

No application-level source-address restriction is specified by this field.

This does not establish that the relay was publicly accessible.

Actual network reachability depends on routing, firewall rules, interface configuration, and other controls outside this JSON file.

## 4.4 Authority Boundary

The relay configuration does not contain:

- A private signing key.
- An authorization policy.
- A provider execution credential.
- A durable artifact-consumption record.

The relay's configured function is transport.

It does not become the authority responsible for the assertion.

---

# 5. ingress.json — Normal Domain B Ingress

## 5.1 Recorded Configuration

```json
{
  "role": "ingress",
  "listen": {
    "host": "40.40.40.40",
    "port": 18443
  },
  "allowed_peer": "30.30.30.30",
  "target": {
    "host": "127.0.0.1",
    "port": 18444
  },
  "mode": "pass"
}
```

## 5.2 Responsibility

Domain B ingress receives the assertion from the mechanical relay.

Its listening endpoint is:

```text
40.40.40.40:18443
```

Its configured permitted peer is:

```text
30.30.30.30
```

Its downstream target is:

```text
127.0.0.1:18444
```

The downstream target is the local verifier.

## 5.3 Normal Forwarding

The configuration specifies:

```text
mode = pass
```

The application is configured to forward the assertion without deliberate mutation.

This is the normal ingress configuration associated with valid-assertion verification.

## 5.4 Peer Restriction

The configured peer restriction identifies the relay's IP address.

```text
allowed_peer = 30.30.30.30
```

This is an application-level source-address restriction.

It is not cryptographic authentication of the relay.

The source address alone does not establish that a request is authorized.

## 5.5 Verification Boundary

Ingress forwards the assertion to the local verifier.

It does not independently establish that the signed assertion is authentic.

Cryptographic verification remains the verifier's responsibility.

---

# 6. ingress_N01.json — Negative-Test Ingress

## 6.1 Recorded Configuration

```json
{
  "role": "ingress",
  "listen": {
    "host": "40.40.40.40",
    "port": 18443
  },
  "allowed_peer": "30.30.30.30",
  "target": {
    "host": "127.0.0.1",
    "port": 18444
  },
  "mode": "tamper"
}
```

## 6.2 Purpose

This configuration supports the MD001 N01 negative experiment.

The experiment evaluates whether modification of signed assertion content causes verification rejection.

The negative configuration retains the same:

- Runtime role.
- Listening endpoint.
- Permitted peer.
- Downstream target.

The distinguishing change is:

```text
mode = tamper
```

## 6.3 Configuration Difference

The normal ingress configuration contains:

```json
"mode": "pass"
```

The negative ingress configuration contains:

```json
"mode": "tamper"
```

This is the only field-value difference between the two published ingress configuration files.

The network path remains unchanged.

## 6.4 Controlled Assertion Modification

In the recorded N01 experiment, the signed assertion's outcome was modified:

```text
Original:

event.outcome = SUCCESS
```

```text
Modified:

event.outcome = FAILURE
```

The original signature was retained.

The modified assertion was then submitted to the verifier.

Because the signed content had changed, the original signature no longer matched the assertion.

## 6.5 Expected Verification Result

The expected result was:

```text
accepted = false
reason = invalid_signature
```

The scored N01 evidence recorded:

```text
HTTP 422
accepted = false
reason = invalid_signature
signature_checks = 1
```

**N01 result: PASS**

The negative configuration demonstrates a controlled experimental modification.

It is not the normal operating configuration.

## 6.6 Scope

The configuration file establishes that the ingress was configured for `tamper` mode.

The configuration alone does not establish that a mutation occurred during a particular network transaction.

That observation is supported by the N01 scored evidence, including artifact comparisons and verification records.

---

# 7. verifier.json — Domain B Verifier

## 7.1 Recorded Configuration

```json
{
  "role": "verifier",
  "listen": {
    "host": "127.0.0.1",
    "port": 18444
  },
  "allowed_peer": "127.0.0.1",
  "target": null,
  "mode": "pass"
}
```

## 7.2 Responsibility

The verifier receives assertions from Domain B ingress.

Its listening endpoint is:

```text
127.0.0.1:18444
```

Its configured permitted peer is:

```text
127.0.0.1
```

The verifier therefore listens on the local loopback interface.

## 7.3 No Downstream Target

The configuration contains:

```json
"target": null
```

The verifier is the terminal component in this configured request path.

It does not forward the assertion to another network destination.

## 7.4 Verification Function

The verifier evaluates the received assertion using the MD001 artifact-verification implementation.

The verification process includes:

1. Parsing the assertion.
2. Validating its structure.
3. Resolving the locally provisioned public key.
4. Verifying the Ed25519 signature.
5. Evaluating the local assertion criteria.
6. Returning the verification result.

The verifier's public-key trust mapping is maintained separately from this configuration file.

## 7.5 Authority Boundary

The verifier determines whether the assertion satisfies the implemented verification criteria.

It does not execute the underlying sorting operation.

It does not maintain a durable single-use authority ledger.

A successful verification result is not an execution authorization.

---

# 8. Configuration Comparison

The four configurations can be compared directly.

| Property | Relay | Normal ingress | N01 ingress | Verifier |
|---|---|---|---|---|
| Role | relay | ingress | ingress | verifier |
| Listen IP | 30.30.30.30 | 40.40.40.40 | 40.40.40.40 | 127.0.0.1 |
| Listen port | 18081 | 18443 | 18443 | 18444 |
| Allowed peer | null | 30.30.30.30 | 30.30.30.30 | 127.0.0.1 |
| Target IP | 40.40.40.40 | 127.0.0.1 | 127.0.0.1 | None |
| Target port | 18443 | 18444 | 18444 | None |
| Mode | pass | pass | tamper | pass |

The negative ingress configuration changes behavior without changing the configured network path.

This allows N01 to isolate the signed-content modification from the normal routing arrangement.

---

# 9. Relationship to Scored Experiments

## B01 — Valid Assertion

The normal configuration path is used.

```text
relay.json
    |
    v
ingress.json
    |
    v
verifier.json
```

Expected:

```text
Valid signature accepted
```

Recorded:

```text
PASS
```

Evidence:

```text
../evidence/B01_SCORED_20261119_223940/
```

## N01 — Modified Assertion

The negative ingress configuration is used.

```text
relay.json
    |
    v
ingress_N01.json
    |
    v
verifier.json
```

Expected:

```text
Modified signed assertion rejected
```

Recorded:

```text
PASS
```

Evidence:

```text
../evidence/N01_SCORED_20261119_224654/
```

## B02 — Producer-Unavailable Verification

The normal configuration path is used.

```text
relay.json
    |
    v
ingress.json
    |
    v
verifier.json
```

The previously issued valid assertion is resubmitted after Domain A is physically disconnected.

Expected:

```text
Original valid assertion accepted
```

Recorded:

```text
PASS
```

Evidence:

```text
../evidence/B02_SCORED_20261119_225126/
```

---

# 10. Security Boundaries

The configurations implement distinct responsibilities.

### Relay

Transports the assertion.

### Ingress

Receives and forwards the assertion.

### Verifier

Evaluates the assertion.

The configuration does not give the relay or ingress authority to sign assertions.

It does not transfer Domain A's private signing key to Domain B.

It does not create shared execution authority.

The negative configuration deliberately modifies an assertion to test whether the verifier detects the change.

## Limitations

These files do not independently establish:

- Firewall enforcement.
- Network isolation.
- Cryptographic authentication of transport peers.
- TLS encryption.
- Private-key custody.
- Correct deployment on a particular host.
- Successful completion of a scored experiment.
- Authorization to execute an operation.
- Replay prevention.
- Durable artifact consumption.

Those properties require separate implementation or evidence.

---

# 11. Independent Review

A reviewer can inspect the configuration files without executing the application.

Recommended procedure:

1. Open `relay.json`.
2. Confirm the relay listening endpoint and downstream target.
3. Open `ingress.json`.
4. Confirm the permitted relay address and local verifier target.
5. Open `ingress_N01.json`.
6. Compare it against `ingress.json`.
7. Confirm that the only difference is `mode`.
8. Open `verifier.json`.
9. Confirm loopback binding and absence of a downstream target.
10. Compare the configuration against the scored evidence.

The configuration files should be treated as preserved experiment inputs.

They should not be modified to describe later experiments.

New experiments requiring different behavior should use separately identified configurations.

---

# 12. Supporting Documentation

The implementation is documented in:

```text
../runtime/
```

The local validation records are preserved in:

```text
../validation/
```

The deployment preparation records are preserved in:

```text
../support/MD001_DEPLOYMENT_R1/
```

The physical-network evidence is preserved in:

```text
../evidence/
```

The main experiment overview is available at:

```text
../README.md
```

---

# 13. Conclusion

The MD001 configuration files define a fixed laboratory verification path.

The normal configuration transports signed assertions from the relay through Domain B ingress to the local verifier.

The N01 configuration changes only the ingress operating mode, introducing a controlled modification to signed assertion content.

The verifier remains responsible for cryptographic verification.

The configuration preserves the architectural distinction between transport and verification.

**The relay determines where an assertion is forwarded. The verifier determines whether the assertion satisfies the implemented verification criteria. Neither function independently authorizes execution of the underlying operation.**
