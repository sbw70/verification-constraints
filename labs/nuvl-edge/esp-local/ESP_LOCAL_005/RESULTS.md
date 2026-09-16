# ESP-LOCAL-005 Results

## Test Objective

ESP-LOCAL-005 evaluated persistent endpoint-local enforcement of provider-issued, single-use bounded authority on an ESP32-S3 actuator endpoint.

The test focused on whether authority could be consumed locally before physical command issuance and remain consumed across replay, reboot, power loss, malformed persistent state, and deliberately injected crash conditions.

An independent ESP32-S3 witness monitored the actuator PWM path during execution and negative-control cases.

## Overall Result

**PASS**

The tested endpoint demonstrated at-most-once bounded authority consumption with persistent endpoint-local enforcement before the observed physical command path.

Across the completed matrix:

- one valid authority produced one permitted execution,
- replay did not produce a second execution,
- spent authority remained spent across reboot and power loss,
- missing, corrupt, and truncated persistent state did not create executable authority,
- deliberate crashes around the persistence/execution boundary did not produce unauthorized PWM,
- the independent witness observed one accepted PWM burst and no second burst on replay.

## Result Matrix

| Test | Result | Observed Behavior |
|---|---|---|
| Native Ed25519 verification | PASS | Provider-signed authority verified locally on the ESP32-S3 |
| Normal authority consumption | PASS | Valid authority progressed through verification, admissibility, persistent consumption, and physical command |
| Replay after consumption | PASS | Previously consumed authority was denied |
| Reboot persistence | PASS | Spent authority remained spent after restart |
| Full power-loss persistence | PASS | Spent authority remained spent after complete power removal |
| Extended power-loss persistence | PASS | Original spent authority remained spent after overnight power removal |
| Independent physical-command witness | PASS | One accepted execution produced one observed PWM burst |
| Replay physical-command control | PASS | Replay produced no second observed PWM burst |
| Missing persistent state | FAIL CLOSED | Missing state did not create fresh authority |
| Corrupt persistent state | FAIL CLOSED | Invalid record contents were rejected |
| Truncated persistent state | FAIL CLOSED | Wrong-length state was rejected |
| Post-consumption / pre-PWM crash | PASS | Authority remained spent after deliberate crash before physical command |
| Pre-explicit-commit crash | FAIL-SAFE | Authority recovered as spent; no PWM occurred before the crash |
| Post-crash replay | PASS | Recovered spent authority remained non-executable |

## Normal Consumption and Replay

A fresh provider-issued authority was explicitly provisioned as `UNSPENT`.

The normal runtime performed:

1. provider-signature verification,
2. semantic admissibility checks,
3. persistent-state validation,
4. confirmation that the authority was unspent,
5. persistent transition to `SPENT`,
6. fresh persistent-state readback,
7. PWM command issuance.

The accepted path completed successfully.

Subsequent evaluation of the same authority produced replay denial rather than another execution.

## Reboot Persistence

After normal authority consumption, the endpoint was restarted.

Startup recovered the authority as:

`005_STARTUP_STATE_SPENT`

A subsequent evaluation was denied as replay.

No reprovisioning was required to preserve the spent state.

## Power-Loss Persistence

The endpoint was subjected to complete power removal after authority consumption.

After power restoration, startup again recovered the authority as spent.

The original spent authority also remained spent after an extended overnight power-loss interval.

These tests demonstrated that authority consumption was not limited to runtime memory or reset-persistent state.

## Independent Physical Witness

The actuator execution path was independently monitored by a separate ESP32-S3 witness.

For the accepted Authority #3 execution, the witness recorded:

- 49 pulses,
- 960 ms observed burst duration,
- minimum observed pulse width of 1832 µs,
- maximum observed pulse width of 2001 µs.

The witness observed one execution burst.

Subsequent replay attempts produced no second burst.

This result establishes electrical PWM command issuance on the observed signal path. It does not independently establish mechanical actuator movement.

## Missing-State Test

The dedicated persistent-state partition was erased while the normal runtime remained unchanged.

Startup reported that the authority state could not be opened and entered the invalid-state path.

Observed behavior included:

`005_STARTUP_STATE_INVALID`

`005_STARTUP_FAIL_CLOSED`

No `UNSPENT` state was synthesized.

No physical command was observed by the independent witness.

**Result: FAIL CLOSED**

## Corrupt-State Test

A deliberately invalid 44-byte persistent record was written under the correct NVS partition, namespace, and key.

The record contained an invalid magic value and invalid integrity information.

The normal runtime detected the invalid record during startup validation.

Observed behavior included:

`Persistent record magic mismatch`

`Persistent authority state failed validation`

`005_STARTUP_STATE_INVALID`

`005_STARTUP_FAIL_CLOSED`

The independent witness remained idle.

**Result: FAIL CLOSED**

## Truncated-State Test

A 12-byte blob was written under the correct persistent-state partition, namespace, and key instead of the expected 44-byte record.

The normal runtime rejected the record based on its invalid size.

Observed behavior included:

`Persistent authority-state size invalid: 12`

`005_STARTUP_STATE_INVALID`

`005_STARTUP_FAIL_CLOSED`

The independent witness remained idle.

**Result: FAIL CLOSED**

## Post-Consumption / Pre-PWM Crash

A fresh provider-issued authority was used with a fault-injection runtime.

The runtime deliberately aborted after persistent consumption had been completed and freshly reread as `SPENT`, but before returning to the physical execution path.

The deliberate abort produced a software reset.

After restart, startup reported:

`005_STARTUP_STATE_SPENT`

A subsequent evaluation produced:

`005_REPLAY_DENIED_SPENT`

The independent witness remained idle throughout the crash and recovery sequence.

No PWM burst was observed.

This result demonstrates that an authority consumed before the crash did not become executable again simply because physical execution had not occurred.

**Result: PASS**

## Pre-Explicit-Commit Crash

A second fault-injection test targeted an earlier persistence window.

A fresh authority began in the `UNSPENT` state.

During evaluation, the endpoint reached:

`005_STATE_VALID_UNSPENT`

The persistent update was initiated with `nvs_set_blob()`.

The runtime then deliberately aborted before reaching the explicit `nvs_commit()` call.

Observed fault marker:

`005_FAULT_PRE_COMMIT_ABORT`

The following markers were not observed before the crash:

`005_DURABLE_SPEND_COMMIT_PASS`

`005_PWM_COMMAND_ISSUED`

After automatic reboot, startup reported:

`005_STARTUP_STATE_SPENT`

A later evaluation produced:

`005_REPLAY_DENIED_SPENT`

The independent witness remained continuously idle and observed no PWM burst.

**Result: FAIL-SAFE**

## Persistence-Boundary Finding

The pre-explicit-commit crash produced an implementation-specific finding.

The `SPENT` state survived a deliberate abort after `nvs_set_blob()` but before the explicit `nvs_commit()` call.

The explicit `nvs_commit()` call therefore was not the demonstrated persistence boundary in the tested ESP-IDF NVS path.

The observed behavior was conservative:

- authority became unavailable for future execution,
- authority was not recreated,
- no physical command occurred before the crash,
- replay after restart remained denied.

The exact lower-level persistence point inside the ESP-IDF NVS implementation was not further characterized in ESP-LOCAL-005.

## Supported Result

ESP-LOCAL-005 supports the following result:

> A provider-issued one-use authority was locally verified and persistently consumed on an ESP32-S3 endpoint before an observed physical command path. Consumption remained effective across replay, reboot, complete power loss, malformed persistent-state conditions, and tested crash windows without creating additional executable authority.

The strongest demonstrated execution property is **at-most-once bounded authority consumption**.

## Limitations

ESP-LOCAL-005 does not establish:

- exactly-once mechanical execution,
- secure boot,
- tamper-resistant persistent storage,
- hardware-backed protection of endpoint state,
- resistance to full endpoint compromise,
- resistance to provider private-key compromise,
- trusted time,
- confidentiality,
- complete characterization of ESP-IDF NVS internal persistence behavior,
- equivalent behavior on other storage implementations or MCU platforms.

The independent witness establishes observed electrical PWM issuance, not guaranteed mechanical actuator movement.
