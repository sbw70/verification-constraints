# ESP-LOCAL-006 Witness

This directory contains the independent witness implementation used during ESP-LOCAL-006 physical-command verification.

## Contents

`ESP_LOCAL_006_WITNESS_GPIO4.py`

MicroPython witness used on a separate ESP32-S3 DevKit to observe the PWM command line associated with the ESP-LOCAL-006 actuator endpoint.

The witness is independent of the endpoint enforcement runtime and does not participate in authority verification, state consumption, relay operation, or execution decisions.

## Witness Topology

The tested connection was:

```text
Servo #2 / ESP-LOCAL-006 endpoint GPIO5
        ↓
independent witness GPIO4
        ↓
MicroPython pulse-width observation
```

The endpoint under test was:

```text
Identity: esp32-xiao-servo-02
Hardware: Seeed XIAO ESP32-S3
```

The independent witness ran on a separate ESP32-S3 DevKit connected through COM8.

## Witness Behavior

The witness configures GPIO4 as an input and measures positive pulse widths using MicroPython `time_pulse_us()`.

Observed positive pulse widths are emitted as:

```text
PWM_HIGH_US <width>
```

The witness performs observation only.

It does not:

- hold provider signing material,
- verify provider signatures,
- determine semantic admissibility,
- read or modify endpoint persistent authority state,
- accept or deny authority,
- issue actuator commands.

## Auth1 Observation

During the accepted Auth1 execution, the witness recorded one servo-valid PWM burst consisting of:

- 49 pulses,
- observed pulse widths from 1998 µs to 2001 µs.

Two isolated 1 µs transients were also recorded during the Auth1 witness session.

Those transients are retained in the evidence record. They did not form a PWM burst and were not consistent with the approximately 2 ms pulse widths observed during the accepted servo command.

After Auth1 had been consumed, replay produced no second servo-valid PWM burst.

## Auth2 Observation

During the wrong-provider Auth2 submission, no PWM command burst was observed.

The same canonical Auth2 authority bytes were then presented with the trusted-provider signature.

The accepted trusted-provider execution produced one servo-valid PWM burst consisting of:

- 49 pulses,
- observed pulse widths from 1999 µs to 2001 µs.

Subsequent replay of the consumed trusted Auth2 authority produced no second servo-valid PWM burst.

## What the Witness Establishes

The witness provides an observation path independent of the endpoint decision log.

For ESP-LOCAL-006, it supports correlation between endpoint acceptance and PWM command issuance, and between endpoint denial or replay denial and the absence of a second servo-valid PWM burst.

This allows cryptographic and persistent-state decisions at the endpoint to be compared with independently observed electrical command behavior.

## Scope

The witness establishes observed electrical PWM issuance on the monitored command line.

It does not independently establish:

- mechanical servo movement,
- actuator position,
- actuator health,
- exactly-once mechanical execution,
- absence of every possible electrical transient,
- authorization correctness by itself.

Authorization and authority-consumption decisions are made by the ESP-LOCAL-006 endpoint runtime, not by the witness.

## Evidence Relationship

The preserved witness transcript is stored at:

```text
../evidence/ESP_LOCAL_006_WITNESS_COM8_CURATED.txt
```

That file is explicitly identified as a curated transcript reconstructed from terminal output preserved during the live test session. It is not represented as a raw redirected serial log.

Endpoint decision evidence is stored separately at:

```text
../evidence/ESP_LOCAL_006_ENDPOINT_COM15_CURATED.txt
```

Relay transaction records are stored in:

```text
../evidence/ESP_LOCAL_006_RELAY_AUTH1.jsonl
../evidence/ESP_LOCAL_006_RELAY_AUTH2.jsonl
```

Observed test outcomes are documented in:

```text
../RESULTS.md
```

Artifact lineage is documented in:

```text
../PROVENANCE.md
```

Published artifact hashes are recorded in:

```text
../SHA256SUMS.txt
```
