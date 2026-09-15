# ESP-LOCAL — Endpoint-Local Recognition and Enforcement

This directory contains the ESP-LOCAL test series for NUVL endpoint-local recognition, validation, consumption, and enforcement of provider-controlled bounded authority on ESP32-class devices.

The series progressively moves authority recognition and enforcement closer to the physical endpoint while preserving the core NUVL authority constraint:

> Authority accepted for execution must remain within provider-established bounds and must not be independently originated or enlarged by intermediary or recognition/enforcement components.

The endpoint may recognize, validate, consume, and enforce authority.

The endpoint does not become the source of authority.

## Scope

ESP-LOCAL evaluates whether bounded authority can be enforced directly on constrained edge hardware without transferring authority-generation power to the endpoint.

The series covers:

- local admissibility checks,
- externally generated one-time capability material,
- integrity-bound authority objects,
- provider-signed authority,
- endpoint-local asymmetric verification,
- persistent one-use authority state,
- replay resistance,
- reboot and power-loss persistence,
- fail-closed persistent-state handling,
- independent observation of physical command issuance,
- crash behavior around the persistence/execution boundary.

These tests are conducted on ESP32-S3 hardware using progressively stronger authority representations and enforcement mechanisms.

## Architectural Position

ESP-LOCAL is part of NUVL core testing.

Moving recognition or enforcement to the endpoint does not constitute an authority transfer.

The distinction is:

```text
LOCAL CAPABILITY != LOCAL AUTHORITY
