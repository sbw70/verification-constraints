# FLEET-016 — Crash After Durable Authority Consumption

**Date:** 2026-08-21  
**Status:** PASS  
**Classification:** Category 2 — optional persistence / actuator integration  
**Architecture change:** No

## Purpose

FLEET-016 tested a failure window in which a single-use authority is durably consumed by the enforcement boundary and the boundary process crashes before an accepted response can successfully reach the physical endpoint.

The test asked whether:

1. authority consumption is persisted before acceptance is returned;
2. a process crash after persistence can prevent the endpoint from receiving a valid accepted response;
3. the endpoint therefore refrains from entering the actuator path;
4. the consumed authority remains spent after boundary restart; and
5. replay of the exact same authority is denied after recovery.

This test extends persistent single-use authority testing into a physical actuator execution path.

## Module / Use Case

Persistent bounded authority with crash-safe consumption before physical execution.

The tested sequence was:

```text
provider-issued single-use authority
        |
        v
enforcement boundary
        |
        v
validate authority
        |
        v
persist spent state
        |
        X  process crash
        |
        |  accepted response never completes
        v
endpoint receives no admissible ACCEPT
        |
        v
no actuator command
```

After restart:

```text
persistent spent state recovered
        |
        v
exact same authority replayed
        |
        v
DENY / replay_detected
        |
        v
no actuator command
```

## Test Configuration

Primary physical endpoint:

```text
esp32-xiao-servo-01
```

Qualified XIAO servo baseline SHA-256:

```text
B34E5A910E8ED91D6E303A1532CC7D8D6DFB72D614767AF7DD93C40732375048
```

Independent actuator-command witness:

```text
ESP32-S3 GPIO5 PWM observer
```

The witness observed the actuator command line independently of the endpoint's own software-reported actuator state.

An isolated crash-test enforcement boundary and isolated persistent state were used so the experiment did not modify the normal fleet replay state.

## Firmware Preparation

The initial FLEET-016 XIAO test image contained an unintended UTF-8 BOM and failed to execute under MicroPython.

The broken image was preserved.

SHA-256:

```text
A2D930E01CEABB43050DEA3FD3036C1C982FCA58812C7BAF8B6F4B368F43C5FE
```

Only the BOM was removed.

The repaired FLEET-016 image SHA-256 was:

```text
670585C33E36CC9ADAD25AF506609F5220789CDAEA8941FBF2548231CD318894
```

A live readback from the endpoint matched the repaired image.

The firmware repair did not change the intended test logic.

## Pre-Test Fail-Closed Control

Before the crash test boundary was made available, the XIAO endpoint attempted normal operation against the unavailable test path.

Observed endpoint state:

```text
decision=unavailable
actuator_attempted=False
actuator_command_completed=False
```

This confirmed that absence of an admissible response did not cause local physical execution.

## Crash Transaction

Final crash transaction:

```text
esp32-xiao-servo-01-345012-40
```

Artifact ID:

```text
03233823a3b533017c200616
```

Exact request nonce:

```text
esp32-xiao-servo-01-esp32-xiao-servo-01-345012-40-345015807
```

The crash-test boundary was configured to terminate after durable replay-state consumption and before completing the accepted response.

Observed sequence:

```text
22:48:18.903703  authority package persisted
22:48:18.918447  spent state persisted
22:48:18.922305  crash triggered
```

The process was intentionally terminated in the targeted post-persistence / pre-acceptance window.

## Endpoint Result

The endpoint did not receive a valid HTTP response from the boundary.

Observed result:

```text
decision=unavailable
reason=ValueError('invalid_http_response',)
elapsed_ms=84
```

The endpoint therefore did not enter its accepted actuator path.

## Independent Witness During Crash

The independent GPIO5 PWM witness remained IDLE across the crash transaction.

Representative witness observations:

```text
22:48:16.460  state=IDLE
22:48:21.488  state=IDLE
```

Observed PWM command bursts during the crash window:

```text
0
```

Result:

**PASS**

The authority had already been durably consumed, but failure before completion of the accepted response did not produce an observed actuator command.

## Boundary Restart

The crash-test boundary was restarted using the persisted replay state.

Recovered state:

```text
spent_count=1
```

The same cached authority artifact was recovered.

This demonstrated that the authority consumption survived the intentional process termination.

## Exact Replay After Restart

The exact previously consumed authority was presented again after restart.

Observed result:

```text
decision=denied
reason=replay_detected
provider_contacted_for_spend=false
```

The denial was made from recovered persistent replay state.

No new provider spend decision was required.

## Independent Witness During Replay

The witness remained IDLE across the preserved replay attempt.

Representative observations surrounding the replay:

```text
23:02:09.685  state=IDLE
23:02:10.442  replay transaction window
23:02:14.706  state=IDLE
```

Observed PWM command bursts:

```text
0
```

Result:

**PASS**

The authority remained consumed after restart, its exact replay was denied, and no actuator command was independently observed.

## Evidence

Retained evidence SHA-256 values:

```text
79ff022cad9790d80e859b54dae539595fbf335c1d9eaf153d951c79ed9061cd  FLEET016_authority_package.json
3b366399f96cce7c1225acd6716ebbb7c64cfc719610585d7db13c8bb9932c31  FLEET016_BRIDGE_FINAL.log
3c9c3d0f75315f745f2b28cad649757ad906c6687d3c07d444c84c85135c5dd4  FLEET016_CRASH_ENDPOINT_RESULT.txt
d0372dbd51f3ac7f75c9e3aa325923ed4f549b630a4a7427385ac58a54be3f48  FLEET016_CRASH_WITNESS.log
3a7b12cb31d6ad8bd2b82251ac58c906fb6163ae0f4dc308780aaf292582d593  FLEET016_EXACT_REPLAY_RESPONSE.txt
b78458d7280603c701376591e2e40c01f4272dec5a9259e817eb729056603d8b  FLEET016_FIRMWARE_HASHES.txt
415e4c84cc2e6a3ce9104be03c045921c8cb663476bd539e33aa64cf4e22728a  FLEET016_RESTART_AFTER_CRASH.log
f5e2bc29dbc2906fe6b5e413e338ca5d5c42c282ee483fbf3758e904c1cbe12a  FLEET016_spent_state.json
f771b3a850ed2c2be172199a4501c234a1bc0dcffc1f2eb818f87cecd588f0b5  FLEET016_WITNESS_CRITICAL_WINDOWS.txt
```

## Restoration

After FLEET-016, the XIAO actuator endpoint was restored to its qualified fleet baseline.

```text
B34E5A910E8ED91D6E303A1532CC7D8D6DFB72D614767AF7DD93C40732375048
```

The temporary independent witness endpoint was also restored to the normal ESP32 autonomous fleet baseline.

```text
BE3103D0958AAB49EF325982C02A43CCD702544764526448B9CD77C8F684D954
```

Normal accepted operation was confirmed after restoration.

## Result

**FLEET-016: PASS**

Observed sequence:

```text
single-use authority
        |
        v
validated
        |
        v
spent state durably persisted
        |
        X
boundary process terminated before accepted response completed
        |
        v
endpoint result = unavailable
        |
        v
actuator path not entered
        |
        v
0 independently witnessed PWM bursts

boundary restart
        |
        v
spent_count=1 recovered
        |
        v
exact authority replay
        |
        v
DENY / replay_detected
        |
        v
0 independently witnessed PWM bursts
```

## Supported Claim

> When the tested enforcement boundary durably consumed a single-use authority and then crashed before completing the accepted response, the endpoint did not receive an admissible acceptance and did not produce an independently observed actuator command. After boundary restart, the persisted consumption was recovered and exact replay of the same authority was denied without an actuator command.

## What This Test Establishes

FLEET-016 demonstrates the tested ordering:

```text
durable authority consumption
before
successful delivery of acceptance
before
physical actuator execution
```

For the tested crash window, process failure did not reopen the consumed authority and did not cause the endpoint to execute locally without a completed admissible response.

## Not Established

FLEET-016 does **not** establish:

- universal exactly-once physical execution;
- exactly-once mechanical motion;
- recovery from every possible crash point;
- filesystem or storage durability under every hardware failure;
- distributed consensus;
- multi-boundary coordination;
- atomicity between persistent authority state and arbitrary external physical effects; or
- guaranteed eventual execution after an authority has been consumed but its accepted response is lost.

The test specifically covers the measured crash window after durable authority consumption and before successful completion of the accepted response.

## Publication Boundary

The public repository may contain:

- this test description;
- endpoint result evidence;
- independent witness evidence;
- restart/recovery evidence;
- exact replay response evidence;
- firmware hashes;
- the generated authority package;
- the generated spent-state document; and
- SHA-256 values for the retained evidence.

The crash-test enforcement implementation source is retained separately and is not required to reproduce the evidentiary result presented here.

Actual credentials or private key material should not be committed to the public repository.
