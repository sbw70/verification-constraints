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
```

A local component may determine whether provider-established authority remains admissible.

It may not independently create broader authority, increase permitted use, substitute a different authorized action, or regenerate consumed authority.

## Test Progression

### ESP-LOCAL-001

Initial endpoint-local bounded recognition.

Demonstrated that a XIAO ESP32-S3 could evaluate local constraints before actuator execution.

Primary purpose:

- move recognition from an external boundary to the endpoint,
- preserve provider-defined action, device, and context constraints,
- include negative cases such as unauthorized identity or context.

Status:

```text
PASS
```

### ESP-LOCAL-002

Externally generated one-time capability with endpoint-local recognition.

The endpoint stored only a SHA-256 commitment associated with the capability and enforced runtime single-use behavior.

Primary purpose:

- separate capability generation from local recognition,
- demonstrate one-time local consumption,
- prevent runtime reuse.

Status:

```text
PASS
```

### ESP-LOCAL-003

Integrity-bound complete authority object.

Extended the authority representation so the complete object rather than an isolated bearer value was bound to the integrity check.

Primary purpose:

- prevent modification of authority fields without detection,
- bind action, context, device, use bounds, and related authority material together.

Status:

```text
PASS
```

### ESP-LOCAL-004

Provider-signed complete authority with endpoint-local asymmetric verification.

The provider retained the Ed25519 private key.

The ESP32 endpoint held only provider verification material and locally verified the signed authority object before permitting execution.

Primary purpose:

- demonstrate provider-originated signed authority,
- prevent the endpoint from minting equivalent provider authority,
- deny altered or improperly signed authority,
- preserve local recognition without provider private-key transfer.

Status:

```text
PASS
```

### ESP-LOCAL-005

Persistent endpoint-local one-use authority consumption.

ESP-LOCAL-005 extended provider-signed authority with durable endpoint-local spent-state enforcement before physical command issuance.

Primary purpose:

- consume authority before execution,
- preserve spent state across reboot,
- preserve spent state across full power loss,
- deny replay after restart,
- fail closed on missing, corrupt, and truncated state,
- independently witness physical PWM issuance,
- test deliberate crash windows around persistent consumption and execution.

Observed substantive results:

```text
normal durable spend                  PASS
replay denial                         PASS
reboot persistence                    PASS
full power-loss persistence           PASS
independent physical-command witness  PASS
no-second-command replay              PASS
missing state                         FAIL CLOSED
corrupt state                         FAIL CLOSED
truncated state                       FAIL CLOSED
post-consumption/pre-PWM crash        PASS
pre-explicit-commit crash             FAIL-SAFE
```

ESP-LOCAL-005 also exposed an implementation-specific persistence finding.

The tested ESP-IDF NVS path preserved the `SPENT` state across a deliberate abort after `nvs_set_blob()` but before the explicit `nvs_commit()` call.

Accordingly, the explicit `nvs_commit()` call was not the demonstrated persistence boundary in that test.

The resulting behavior remained conservative:

```text
availability may be lost
authority is not recreated
physical execution does not precede persistent consumption
```

Status:

```text
PASS
```

## Independent Physical Witness

Later ESP-LOCAL testing used a separate ESP32-S3 witness to observe the actuator PWM path independently of the enforcing endpoint.

For ESP-LOCAL-005, the witness observed one accepted PWM burst and no second burst on replay.

This establishes electrical command issuance on the observed signal path.

It does not independently prove mechanical motion.

## Authority Model

Across the series, authority became progressively more explicit and externally controlled.

The general model is:

```text
provider establishes authority
        ↓
authority object reaches endpoint
        ↓
endpoint verifies authenticity/integrity
        ↓
endpoint checks local admissibility
        ↓
endpoint checks remaining authority
        ↓
endpoint consumes bounded authority
        ↓
physical command may execute
```

Transport or recognition components are not permitted to enlarge the provider-established authority.

## Fail-Closed Rule

ESP-LOCAL follows the same NUVL availability-versus-authority rule used elsewhere in the test program:

```text
uncertainty must not manufacture authority
```

Examples include:

- missing state,
- malformed state,
- invalid signatures,
- mismatched identity,
- mismatched context,
- altered action,
- exhausted use bounds,
- replayed authority,
- incomplete recovery state.

A conventional availability-first fallback is not accepted where it would silently recreate or enlarge authority.

## Hardware Used

The ESP-LOCAL series has used:

- Seeed XIAO ESP32-S3 actuator endpoints,
- ESP32-S3 DevKitC-class witness hardware,
- servo actuator output,
- Raspberry Pi and external-provider systems where applicable,
- ESP-IDF and MicroPython implementations depending on test stage.

Exact hardware, firmware, serial-port mappings, and test-specific configuration are documented within each test directory.

## Directory Structure

```text
esp-local/
├── README.md
├── ESP_LOCAL_001/
├── ESP_LOCAL_002/
├── ESP_LOCAL_003/
├── ESP_LOCAL_004/
└── ESP_LOCAL_005/
```

Individual test directories may contain:

```text
README.md
RESULTS.md
PROVENANCE.md
SHA256SUMS.txt
firmware/
provider/
witness/
evidence/
```

The exact structure varies where a test did not require a particular component.

## Evidence Policy

The ESP-LOCAL directories are evidence-oriented test records.

Where available, publication includes:

- exact tested source,
- compiled test binaries,
- provider test material,
- independent witness code,
- raw persistent-state captures,
- test metadata,
- failure-injection variants,
- SHA-256 manifests,
- explicit limitations.

Exact tested bytes retain their tested hashes.

Modified or sanitized publication copies receive new hashes.

Test-only cryptographic material may be published when useful for reproduction.

Operational credentials are not publication material.

## What ESP-LOCAL Demonstrates

Taken together, ESP-LOCAL demonstrates progressively stronger forms of endpoint-local enforcement while keeping provider authority externally bounded.

The strongest demonstrated result through ESP-LOCAL-005 is:

> A constrained endpoint can locally verify provider-issued bounded authority, enforce one-use semantics, durably consume that authority before an observed physical command path, preserve consumed state across reboot and power loss, and fail closed or conservatively under tested malformed-state and crash conditions without independently creating new executable authority.

## What ESP-LOCAL Does Not Demonstrate

The completed series through ESP-LOCAL-005 does not by itself establish:

- secure boot,
- hardware-backed private-key protection,
- tamper-resistant persistent storage,
- resistance to full endpoint compromise,
- resistance to provider-key compromise,
- confidentiality,
- trusted time,
- general Byzantine fault tolerance,
- guaranteed mechanical execution,
- exactly-once physical execution,
- production certification,
- behavior across all MCU, flash, or NVS implementations.

Those remain separate claims and require separate evidence.

## Relationship to NUVL

ESP-LOCAL is not a separate authority architecture.

It is a placement and enforcement series within NUVL.

The central question is not whether the endpoint can make decisions independently.

The question is whether enforcement can move to the endpoint while authority remains bounded by the provider.

The test series to date supports that separation.
