# ESP-LOCAL-005 Witness

This directory contains the independent witness implementation used during ESP-LOCAL-005 physical-command verification.

## Contents

`ESP_LOCAL_005_AUTH3_WITNESS_GPIO4.py`

MicroPython witness used on the independent ESP32-S3 DevKit to observe the PWM command line associated with Servo #2 during the Authority #3 test.

## Witness Topology

The tested connection was:

Servo #2 / ESP-LOCAL-005 endpoint → Witness GPIO4

The witness endpoint was independent of the ESP-LOCAL-005 execution firmware.

Its role was observation only.

## Observed Signal

During the accepted Authority #3 execution, the witness recorded one PWM burst consisting of:

- 49 pulses,
- approximately 960 ms total duration,
- pulse widths from approximately 1832 µs to 2001 µs.

The subsequent replay attempt produced no second burst.

## What the Witness Establishes

The witness provides independent evidence that the endpoint issued the expected electrical PWM command after authority acceptance.

It also provides independent evidence that replay did not produce a second observed PWM command.

The witness does not establish guaranteed mechanical servo movement.

## Relationship to ESP-LOCAL-005

The witness is external to the endpoint-local authority-enforcement path.

It does not generate, validate, consume, or modify authority.

Its only role is to observe whether the physical-command signal was issued.

## Related Material

Observed results are documented in:

`../RESULTS.md`

Artifact lineage is documented in:

`../PROVENANCE.md`

Authority #3 artifacts are stored in:

`../evidence/`

Published artifact hashes are recorded in:

`../SHA256SUMS.txt`
