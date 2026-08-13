# ACT-001 — Accept/Deny Physical Actuation Binding

## Status

**PASS**

ACT-001 validated the single-endpoint physical execution boundary using one Seeed XIAO ESP32-S3 and one MG90S-class servo.

The test series exercised five conditions:

1. accepted / provider-admissible
2. unauthorized
3. stale/replay/malformed rejection class
4. external boundary unavailable
5. boundary restoration and accepted-path recovery

Across the tested paths, accepted decisions entered the actuator path and produced observable physical movement. Non-accepted outcomes did not invoke the actuator and produced no observed movement.

---

## Test Configuration

Endpoint:

`esp32-xiao-servo-01`

Hardware:

* Seeed XIAO ESP32-S3
* MG90S-class servo
* Servo signal: D4 / GPIO5
* Servo power: XIAO 5V/VBUS
* MicroPython v1.28.0

Observed IP during qualification:

`192.168.0.81`

Latency budget:

`250 ms`

External path:

`coordinator → XIAO request → NUVL boundary → returned decision → actuator gate → servo`

Servo reset or initial positioning was treated as out-of-band test preparation and was not part of the authorization path.

---

## Qualified Firmware

Original tested source:

`esp32_xiao_servo_nuvl_archer.py`

Size:

`9,790 bytes`

SHA-256:

`C29AD7BB8362BD532C62A87CE5D8BE3ED30C25E4543FF52A2CC98992E493AD84`

The firmware was hash-verified after installation on the XIAO.

The tested execution rule was:

```text id="2x30zi"
accepted → actuator attempt
all other outcomes → no actuator call
```

The firmware reported:

* `actuator_attempted`
* `actuator_command_completed`
* `actuator_error`

---

# 1. Accepted Path

## Expected

The external NUVL path returns:

`accepted / provider_admissible`

PASS requires:

```text id="4gkq26"
actuator_attempted=True
actuator_command_completed=True
actuator_error=None
physical movement observed
```

## Run 1

Run ID:

`18ca4956db80a0f8`

Observed:

* endpoint identity correct
* IP binding correct
* decision: `accepted`
* reason: `provider_admissible`
* arrival: `ON_TIME`
* latency: `37 ms`
* `actuator_attempted=True`
* `actuator_command_completed=True`
* `actuator_error=None`
* physical servo movement observed

Result:

**PASS**

## Run 2

Run ID:

`18ca4960aa45fa38`

Observed:

* endpoint identity correct
* IP binding correct
* decision: `accepted`
* reason: `provider_admissible`
* arrival: `ON_TIME`
* latency: `33 ms`
* `actuator_attempted=True`
* `actuator_command_completed=True`
* `actuator_error=None`
* physical servo movement observed

Video evidence was captured for this run.

Result:

**PASS**

## Accepted-path result

**PASS x2**

Both consecutive accepted decisions produced the expected software actuator state and observable physical movement.

---

# 2. Unauthorized Path

## Expected

The external NUVL path returns:

`denied / unauthorized_request`

PASS requires:

```text id="24ywzv"
actuator_attempted=False
actuator_command_completed=False
actuator_error=None
physical movement not observed
```

## Result

Run ID:

`18ca4a45df7242d0`

Observed:

* endpoint identity correct
* IP binding correct
* decision: `denied`
* reason: `unauthorized_request`
* arrival: `ON_TIME`
* latency: `37 ms`
* `actuator_attempted=False`
* `actuator_command_completed=False`
* `actuator_error=None`
* no physical servo movement observed

Result:

**PASS**

The unauthorized decision did not enter the actuator path.

---

# 3. Stale/Replay/Malformed Rejection Class

## Expected

The returned result is:

`denied / stale_replay_malformed`

PASS requires no actuator invocation and no physical movement.

## Result

Run ID:

`18ca4b57c9fe064c`

Observed:

* endpoint identity correct
* IP binding correct
* decision: `denied`
* reason: `stale_replay_malformed`
* arrival: `ON_TIME`
* latency: `33 ms`
* `actuator_attempted=False`
* `actuator_command_completed=False`
* `actuator_error=None`
* no physical movement observed

Result:

**PASS**

This demonstrates that the tested `stale_replay_malformed` rejection class remained outside the physical actuator path.

It is not an independent persistent replay-state test.

---

# 4. External Boundary Unavailable

## Test Condition

The normal NUVL boundary was deliberately stopped.

Original boundary PID:

`1909`

Port 8089 was confirmed unavailable before the actuator test:

```text id="bc54e8"
curl: (7) Failed to connect to 127.0.0.1 port 8089
```

The XIAO remained powered and running.

The requested coordinator mode remained:

`accept`

This tested whether loss of the external authorization boundary could result in fallback physical execution.

## Result

Run ID:

`18ca4c18d61aa52c`

Observed:

* endpoint identity correct
* IP binding correct
* requested mode: `accept`
* decision: `unavailable`
* reason: `OSError(104,)`
* arrival: `ON_TIME`
* latency: `12 ms`
* `actuator_attempted=False`
* `actuator_command_completed=False`
* `actuator_error=None`
* no physical servo movement observed

Result:

**PASS**

In the tested path, boundary loss did not produce fallback actuation.

---

# 5. Boundary Restoration and Physical Recovery

## Restoration

The external boundary was restarted.

New PID:

`2730624`

Restart evidence:

`/home/seth/nuvl_local_hardened_latency_restart_20260809_210707.log`

Health check after restart:

`ok`

The XIAO endpoint was **not reset** between the outage and recovery tests.

---

## Recovery Run 1

Run ID:

`18ca4ce38d4a0470`

Observed:

* decision: `accepted`
* reason: `provider_admissible`
* latency: `33 ms`
* `actuator_attempted=True`
* `actuator_command_completed=True`
* `actuator_error=None`
* physical movement observed

Result:

**PASS**

## Recovery Run 2

Run ID:

`18ca4cea378ad3dc`

Observed:

* decision: `accepted`
* reason: `provider_admissible`
* latency: `35 ms`
* `actuator_attempted=True`
* `actuator_command_completed=True`
* `actuator_error=None`
* physical movement observed

Video evidence was captured for this run.

Result:

**PASS**

## Recovery result

**PASS x2**

Following restoration of the external boundary, the same endpoint returned to accepted physical actuation without an endpoint reset.

---

# Result Matrix

| Condition                    | Decision / reason               | Actuator invoked | Physical movement | Result |
| ---------------------------- | ------------------------------- | ---------------- | ----------------- | ------ |
| Accept run 1                 | accepted / provider_admissible  | Yes              | Yes               | PASS   |
| Accept run 2                 | accepted / provider_admissible  | Yes              | Yes               | PASS   |
| Unauthorized                 | denied / unauthorized_request   | No               | No                | PASS   |
| Stale/replay/malformed class | denied / stale_replay_malformed | No               | No                | PASS   |
| Boundary unavailable         | unavailable / `OSError(104,)`   | No               | No                | PASS   |
| Recovery run 1               | accepted / provider_admissible  | Yes              | Yes               | PASS   |
| Recovery run 2               | accepted / provider_admissible  | Yes              | Yes               | PASS   |

Total ACT-001 executions:

**7**

PASS:

**7/7**

---

# Source Launchers

## Accept

Original source:

`run_xiao_servo_accept_archer.py`

SHA-256:

`BBAB6EA69E6B6C13B0CD7B6BC25FB52A6D0EFCC075652F0920B765956DAF2C3E`

The same qualified accept launcher was reused for the post-outage recovery runs.

---

## Unauthorized

Original source:

`run_xiao_servo_deny_archer.py`

Size:

`4,374 bytes`

SHA-256:

`CED31874869DDD8C2B646746EB6660D29006901C60CBD3EEEFAB1F2804B7429C`

---

## Stale/Replay/Malformed Class

Original source:

`run_xiao_servo_stale_archer.py`

Size:

`4,393 bytes`

SHA-256:

`0ECE21790A1604E2527889544669893CAFCD262A2862AC1199A092F09E654891`

---

## Boundary Outage

Original source:

`run_xiao_servo_outage_archer.py`

Size:

`4,410 bytes`

SHA-256:

`23CB242CECA50A4F756AF75A6625351FDC3C441C11E5DB58CF840B1A1FA179E8`

---

# Runtime Evidence

## Initial accepted runs

`xiao_servo_accept_20260809_201357.log`

Size:

`1,418 bytes`

SHA-256:

`405FA73A7E28299E179DF3B088AD6E231EF1B872FE739C11AF47DB201C423BDD`

Result:

**PASS**

---

`xiao_servo_accept_20260809_201430.log`

Size:

`1,418 bytes`

SHA-256:

`F4E4C90B5EF692E90B4F70BF294E702E95D03912B7604224CC46E85F29236B66`

Result:

**PASS**

Physical movement observed.

Video captured for this run.

---

## Unauthorized

`xiao_servo_deny_20260809_203008.log`

Size:

`1,408 bytes`

SHA-256:

`3462120D00B6C11FC01369D2E794E04FEEDEAE7833C3271C21DC62A1A63CF1AB`

Result:

**PASS**

Physical observation:

No movement.

---

## Stale/Replay/Malformed Class

`xiao_servo_stale_20260809_204955.log`

Size:

`1,418 bytes`

SHA-256:

`A2E6378EADFAD2C6E16B1F39B8A93D3DD628D4FF136BDABE1292D1C778651E06`

Result:

**PASS**

Physical observation:

No movement.

---

## Boundary Outage

`xiao_servo_outage_20260809_210412.log`

Size:

`1,416 bytes`

SHA-256:

`A19EF11ED67B970DA59306EF42495B8FB899DE5926A550553E249A08D41A7875`

Result:

**PASS**

Physical observation:

No movement.

---

## Post-Outage Recovery

`xiao_servo_recovery_20260809_211901.log`

Size:

`1,418 bytes`

SHA-256:

`6D26FDB5EEC3650C3BC9D677B4B5417F221BDA6FE87A081967B42631203884EC`

Result:

**PASS**

Physical movement observed.

---

`xiao_servo_recovery_20260809_211920.log`

Size:

`1,418 bytes`

SHA-256:

`D26864C92EDFE8F7FD4CA7BA18002B063C9FE4E47E77A418D647AC585AFB268F`

Result:

**PASS**

Physical movement observed.

Video captured for this run.

---

# Video Evidence

Initial accepted-path video:

`20260809_201436.mp4`

Size:

`15,432,149 bytes`

SHA-256:

`6411495A5406474B50C3AEBCA078C9596E2BCB906078EEA3CA90CFE5EE1C6EF1`

The test notes also record video evidence for the denied path and the second post-outage recovery run.

Where those video files are published or independently manifested, their exact filenames and hashes should be taken from the preserved local evidence rather than reconstructed here.

---

# Pi-Side Recovery Evidence

Boundary restart log:

`/home/seth/nuvl_local_hardened_latency_restart_20260809_210707.log`

Size:

`2,577 bytes`

SHA-256:

`91919D51D407F5A4C5333858471E925E1B501AFEEEB7E60601B3A56192C978A0`

Boundary health after restart:

`ok`

Subsequent physical recovery:

**PASS x2**

No XIAO reset was performed.

---

# Evidence Manifest

ACT-001 manifest:

`act001_manifest_20260809_212704.txt`

Original path:

`C:\Users\holiw\esp32-main\act001_manifest_20260809_212704.txt`

Size:

`1,449 bytes`

SHA-256:

`39FB7C16B173DC0E231917C3D53667800027D083DB41B4459478381755CA1DF3`

The manifest closes the local ACT-001 evidence set.

---

# Supported Conclusion

ACT-001 supports the following bounded conclusion:

> In the tested single-endpoint path, externally determined admissibility controlled access to a physical servo actuator. Accepted decisions produced observable physical movement; unauthorized, stale/replay/malformed-class, and boundary-unavailable outcomes produced no actuator invocation and no observed movement. After boundary restoration, accepted physical actuation resumed without resetting the endpoint.

The outage portion additionally supports:

> In the tested path, loss of the external authorization boundary did not produce fallback physical actuation.

---

# Claim Boundary

ACT-001 does not demonstrate:

* exactly-once physical execution
* sensor-confirmed mechanical position
* persistent single-use physical authority
* actuator replay prevention across restart or power loss
* crash-safe actuator execution
* concurrent physical effectors
* endpoint-enforced execution deadlines
* total request-to-mechanical-completion latency
* independent endpoint authorization

The `stale_replay_malformed` result demonstrates non-actuation for that returned rejection class. It is not itself a persistent replay-state test.

Reported `elapsed_ms` values measure the NUVL request/authorization portion of the tested path and exclude the approximately one-second servo hold.

`actuator_command_completed=True` indicates completion of the software actuator routine without a reported error. Physical observation provides separate evidence that movement occurred; no independent position sensor was used.

All conclusions apply **in the tested path and configuration**.

