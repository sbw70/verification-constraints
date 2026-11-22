# MD001 — Public-Key Trust Provisioning

## Overview

This directory preserves a public-key trust configuration associated with the MD001 Multi-Domain Stateless Verification experiment.

The configuration identifies a trusted producer and its corresponding Ed25519 public verification key.

**Project:** MD001  
**Organization:** Xer0trust LLC  
**Evidence directory:** `MD001_TRUST_20261118_215250`  
**Evidence classification:** Supporting configuration evidence  
**Producer:** `DOMAIN_A`

The directory contains public verification material only.

It does not contain the corresponding private signing key.

## 1. Purpose

MD001 separates the creation of signed assertions from their independent verification.

Domain A produces an assertion and signs it using its private key.

Domain B evaluates the assertion using locally provisioned public-key trust.

The mechanical relay transports the assertion without requiring either signing authority or access to the verifier's trust configuration.

This directory preserves the public-key mapping used to identify an approved signing key.

## 2. Evidence Contents

```text
MD001_TRUST_20261118_215250/
|
|-- trust.json
|
`-- README.md
```

The original evidence consists of `trust.json`.

This README is explanatory documentation added separately.

## 3. Recorded Trust Configuration

The preserved `trust.json` contains:

```json
{
  "DOMAIN_A": {
    "sha256:ce33a41359734e4b748d162720a57ddbbf666e968cddc854aaba6f57591ad2c3": "35bc6f39ffcb6b71380e9f9d054f44ee9936d8b94b98530e6e31648ab0e6d570"
  }
}
```

### Producer Identifier

```text
DOMAIN_A
```

### Key Identifier

```text
sha256:ce33a41359734e4b748d162720a57ddbbf666e968cddc854aaba6f57591ad2c3
```

### Ed25519 Public Key

```text
35bc6f39ffcb6b71380e9f9d054f44ee9936d8b94b98530e6e31648ab0e6d570
```

The public key is represented as 32 bytes encoded in hexadecimal.

The key identifier uses a SHA-256 fingerprint representation.

## 4. Trust Resolution

The MD001 verifier uses the locally provisioned trust configuration to resolve the public key associated with a claimed producer and key identifier.

The verification process is:

```text
Received signed assertion
          |
          v
Read producer_id
          |
          v
Read key_id
          |
          v
Resolve public key
from local trust configuration
          |
          v
Verify Ed25519 signature
          |
          v
Evaluate local assertion criteria
          |
          v
Return verification result
```

The producer and key identifier contained in an assertion do not establish trust by themselves.

The verifier must resolve them against its locally provisioned trust mapping.

An unknown producer or unrecognized key identifier is not sufficient for successful verification.

## 5. Separation of Responsibilities

The intended MD001 architecture separates three functions.

### Domain A — Assertion Production

Domain A:

- Performs the local operation.
- Creates the corresponding assertion.
- Signs the assertion using its private key.

### Mechanical Relay — Transport

The relay:

- Receives the signed assertion.
- Forwards it toward the configured destination.
- Does not require the private signing key.
- Does not independently establish the assertion's authenticity.

### Domain B — Verification

Domain B:

- Maintains its public-key trust configuration.
- Resolves the producer and signing key.
- Verifies the assertion's signature.
- Evaluates the applicable local criteria.
- Returns a verification result.

The public-key mapping does not grant the relay authority to sign assertions.

## 6. Public and Private Key Distinction

The preserved configuration contains a public verification key.

Possession of this key permits signature verification.

It does not permit generation of valid Ed25519 signatures without the corresponding private key.

The private key is not present in this directory.

The absence of a private key from this directory does not independently establish that no other copies existed elsewhere in the laboratory.

That question requires separate key-custody evidence.

## 7. Independent Review

A reviewer can inspect the trust configuration without executing the application.

### Step 1 — Inspect the File

Open:

```text
trust.json
```

Confirm that the top-level producer identifier is:

```text
DOMAIN_A
```

### Step 2 — Inspect the Key Mapping

Confirm that the producer maps to a SHA-256-formatted key identifier and a hexadecimal public key.

### Step 3 — Validate the Structure

Confirm that:

- The document is valid JSON.
- The producer identifier is a string.
- The key identifier uses the expected fingerprint format.
- The public key contains 64 hexadecimal characters.
- The public key represents 32 bytes.

### Step 4 — Compare Against Verification Evidence

Compare the recorded trust mapping with the trust configuration and key identifiers preserved in the relevant MD001 verifier evidence.

The presence of a trust file does not establish that a particular verifier process loaded it.

That requires the corresponding process, configuration, or verification records.

## 8. Relationship to Scored Experiments

The trust configuration supports the MD001 assertion-verification architecture.

The scored experiments examine separate properties.

| Experiment | Verification property |
|---|---|
| B01 | Valid signed assertion accepted |
| N01 | Modified signed assertion rejected |
| B02 | Previously issued assertion verified while producer unavailable |

The scored evidence is preserved in:

```text
../../evidence/B01_SCORED_20261119_223940/

../../evidence/N01_SCORED_20261119_224654/

../../evidence/B02_SCORED_20261119_225126/
```

Those directories contain the primary experimental observations.

This directory contains supporting public-key configuration evidence.

It is not an additional scored experiment.

## 9. Scope and Limitations

The preserved `trust.json` establishes that a public-key mapping for `DOMAIN_A` was recorded.

It does not independently establish:

- When the key pair was generated.
- Which machine generated the key pair.
- Which operator provisioned the public key.
- Whether a particular verifier loaded this exact file.
- Whether the corresponding private key remained exclusively on Domain A.
- Whether the public key was transferred through an independently verified channel.
- Whether the key was rotated or revoked.
- Whether any scored experiment succeeded.
- Whether the underlying operation actually occurred.
- Whether repeated execution was prevented.

The trust configuration is a verification input.

It is not an execution authorization or a durable consumption record.

## 10. Conclusion

This directory preserves a public Ed25519 verification-key mapping for `DOMAIN_A`.

The mapping illustrates the trust-provisioning mechanism used by MD001: a receiving domain can evaluate a producer's signed assertion using locally provisioned public-key material without obtaining the producer's private signing key.

The file provides supporting configuration evidence.

The actual verification outcomes must be established from the corresponding scored experiment records.
