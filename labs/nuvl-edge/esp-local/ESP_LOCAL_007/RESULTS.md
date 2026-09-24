# ESP-LOCAL-007 Results

## Result

**PASS — R003, 2026-09-23**

ESP-LOCAL-007 tested whether concurrent presentation of the same valid, provider-issued, single-use authority could result in more than one physical execution.

Two requesters presented the same AUTH2 request with `max_uses = 1`.

Observed result:

~~~text
requesters:                  2
accepted:                    1
denied:                      1
requester errors:            0
endpoint PWM executions:     1
endpoint ACCEPT_EXECUTED:    1
witness servo-like bursts:   1
final authority state:       SPENT
~~~

The bounded-authority property held under the tested concurrent contention condition.

## Claim under test

ESP-LOCAL-007 asks:

> If multiple requesters present the same valid one-use provider authority concurrently, can more than one physical command escape?

The provider model and authority semantics are unchanged from the preceding endpoint-local tests.

The new variable is concurrent dispatch.

For R003, PASS required:

1. exactly one requester accepted;
2. exactly one competing requester denied;
3. exactly one endpoint PWM command begin/end sequence;
4. exactly one endpoint `ACCEPT_EXECUTED`;
5. exactly one independently observed servo-like physical burst;
6. no witness capture overflow, truncation, or error during the scored observation; and
7. final persistent authority state `SPENT`.

R003 satisfied all seven criteria.

## Test authority

R003 used AUTH2:

~~~text
device_id: esp32-xiao-servo-02
context:   esp_local_006
action:    move_servo
max_uses:  1
nonce:     b3e5571eee07d3e37ca757b54a549a3e
~~~

Canonical authority:

~~~json
{"action":"move_servo","context":"esp_local_006","device_id":"esp32-xiao-servo-02","max_uses":1,"nonce":"b3e5571eee07d3e37ca757b54a549a3e"}
~~~

Authority ID:

~~~text
066fd59f04ba90f1476ea388a84e125a349a54435552205c0aaa6d5adfa14545
~~~

Both requesters presented the same signed request. No second authority was issued for the competing requester.

## Initial state

Before R003, the endpoint's dedicated `nuvl_state` partition was verified to contain AUTH2 in the `UNSPENT` state.

Pre-race partition SHA-256:

~~~text
38327e63133030933c23b8d5d816fa85729a4aeb48f3e14fc3e71ee9fb35340f
~~~

The concurrent runtime was then installed without replacing the provisioned authority state.

A subsequent readback confirmed AUTH2 remained `UNSPENT` before the race.

## Concurrent release

The coordinator opened two requester connections.

Both endpoint client tasks reported READY before the coordinator released either request:

~~~text
007_CLIENT_READY fd=55
007_CLIENT_READY fd=56
~~~

The endpoint then recorded both requests arriving at the contention path:

~~~text
007_CLIENT_REQUEST_RECEIVED fd=56
007_CLIENT_REQUEST_RECEIVED fd=55
~~~

The coordinator measured the requester send-start skew as:

~~~text
42700 ns
~~~

or:

~~~text
42.7 µs
~~~

This value describes coordinator send-start timing. It is not an assertion that the endpoint executed both internal paths exactly 42.7 µs apart.

## Winning requester

The winning path was file descriptor 56.

It recorded:

~~~text
006_SIGNATURE_VALID
006_SEMANTIC_ADMISSIBILITY_PASS
006_AUTHORITY_UNSPENT_PASS
006_DURABLE_SPENT_REREAD_PASS
006_PWM_COMMAND_BEGIN
006_PWM_COMMAND_END
006_ACCEPT_EXECUTED
007_CLIENT_COMPLETE fd=56 result=accepted
~~~

The physical command lasted approximately one second between PWM begin and PWM end.

The requester received:

~~~json
{"status":"accepted","reason":"executed"}
~~~

## Losing requester

The competing path was file descriptor 55.

It passed provider-signature and semantic checks:

~~~text
006_SIGNATURE_VALID
006_SEMANTIC_ADMISSIBILITY_PASS
~~~

It then encountered:

~~~text
Unable to read authority state: ESP_ERR_NVS_INVALID_HANDLE
006_DENY_STATE_INVALID
007_CLIENT_COMPLETE fd=55 result=state_invalid
~~~

The failure occurred while the winning durable-consumption path had the NVS state partition deinitialized as part of its persistence sequence.

The failure direction was conservative: the competing request was denied.

The losing path did not record:

~~~text
006_PWM_COMMAND_BEGIN
006_PWM_COMMAND_END
006_ACCEPT_EXECUTED
~~~

The requester received:

~~~json
{"status":"denied","reason":"state_invalid"}
~~~

## Endpoint execution count

The scored R003 endpoint sequence contains exactly one:

~~~text
006_PWM_COMMAND_BEGIN
~~~

exactly one:

~~~text
006_PWM_COMMAND_END
~~~

and exactly one:

~~~text
006_ACCEPT_EXECUTED
~~~

No second physical execution path appears in the endpoint evidence.

## Independent physical witness

R003 used the ESP-IDF RMT hardware witness on GPIO4 to observe the endpoint's servo signal independently.

The authoritative R003 `burst_end` event recorded:

~~~text
burst_run:             R003
pulses:                50
width_min_us:          1999
width_max_us:          2000
period_min_us:         20000
period_max_us:         20001
period_out_of_range:   0
servo_like:            true
duration_us:           982013
~~~

The witness therefore observed one clean servo-like physical pulse burst.

The observed signal is consistent with the single endpoint PWM execution.

## Witness capture health

Before the run, the coordinator recorded:

~~~text
capture_ready:        true
capture_queue_depth:  0
capture_overflows:    0
capture_truncations:  0
capture_errors:       0
~~~

No capture overflow, truncation, or error was recorded during the scored observation.

This distinguishes R003 from R001, where endpoint enforcement passed but the original witness did not capture the physical event with sufficient fidelity to satisfy the independent-witness criterion.

## Witness run-summary timing artifact

The witness run-level summary contains a known timing artifact.

`R_R003.jl` reports:

~~~text
servo_valid_pulses:  0
bursts:              0
servo_like_bursts:   0
~~~

The full witness serial record contains the completed R003 `burst_end` event showing:

~~~text
pulses:              50
servo_like:          true
burst_run:           R003
period_out_of_range: 0
~~~

The coordinator sent STOP approximately 29 ms before the witness's 100 ms quiet-gap interval had elapsed.

The run-level summary was therefore finalized before the active burst had been closed and counted by the burst classifier.

The complete burst itself was captured.

For R003, the raw `burst_end` event is the authoritative physical-burst record. The run-summary discrepancy is retained as a measurement artifact.

A future coordinator procedure should wait approximately 200 ms after requester completion before issuing STOP so the run-level summary is generated after burst closure.

That procedural change was not part of R003.

## Final persistent state

After the race, the endpoint authority state was reread and the raw `nuvl_state` partition was captured.

The final record contained AUTH2 in the:

~~~text
SPENT
~~~

state.

Post-race partition SHA-256:

~~~text
b87b8deba8d08c602af86ff3bac7636a02f0bc8dec5a4401d162b955384d4471
~~~

The state transition for the scored run was therefore:

~~~text
AUTH2 / UNSPENT
       |
       | two concurrent presentations
       |
       +---- requester A ---- DENIED
       |
       +---- requester B ---- durable consume ---- physical execution
                                                    |
                                                    v
                                             AUTH2 / SPENT
~~~

## Evidence correlation

The PASS determination is not based on the requester responses alone.

Independent evidence streams agree on the scored property:

| Evidence | Observation |
|---|---|
| Coordinator | 2 requesters released; 1 accepted; 1 denied |
| Coordinator timing | 42.7 µs send-start skew |
| Endpoint | both requests reached concurrent processing |
| Endpoint | one requester denied before PWM |
| Endpoint | exactly one PWM begin/end sequence |
| Endpoint | exactly one `ACCEPT_EXECUTED` |
| Witness | exactly one completed 50-pulse servo-like burst |
| Witness health | zero capture overflow, truncation, or error |
| Persistent state | AUTH2 `UNSPENT` before race |
| Persistent state | AUTH2 `SPENT` after race |

These observations support the scored conclusion that the tested single-use authority did not enlarge into two physical executions under the R003 contention condition.

## Prior runs

### R001 — enforcement passed, witness inconclusive

R001 used AUTH1.

Endpoint-side observations were consistent with the intended property:

~~~text
accepted requesters: 1
denied requesters:   1
PWM executions:      1
final state:         SPENT
~~~

The original MicroPython witness captured only fragments of the physical signal and did not produce a complete independently classifiable servo-like burst.

R001 is therefore retained as:

~~~text
INCONCLUSIVE_WITNESS_CAPTURE
~~~

R001 is not classified as a contention-enforcement failure.

### R002 — setup misfire / negative control

Before R003, AUTH2 had been provisioned into the endpoint but the coordinator still referenced the already-spent AUTH1 request.

Both concurrent requesters therefore presented AUTH1 against AUTH2 state.

Observed result:

~~~text
accepted:           0
denied:             2
physical execution: 0
~~~

Both were denied for authority-state mismatch.

AUTH2 remained available for the subsequent scored run.

R002 is retained as a setup misfire and negative control. It is not the scored ESP-LOCAL-007 result.

### R003 — scored PASS

R003 corrected the request selection and used the provisioned AUTH2 request.

Observed result:

~~~text
same AUTH2 presented twice concurrently
max_uses = 1

accepted = 1
denied   = 1

endpoint physical commands = 1
independent witness bursts = 1

final state = SPENT
~~~

R003 supersedes R001 as the scored ESP-LOCAL-007 result.

## What R003 establishes

For the tested ESP32-S3 / ESP-IDF / NVS endpoint and independent RMT witness configuration, R003 establishes:

> Concurrent presentation of one valid provider-issued single-use authority resulted in at most one physical execution, and the authority was durably left SPENT.

The physical execution count is corroborated independently of the endpoint's own execution log.

## What R003 does not establish

R003 does not establish:

- resistance to provider private-key theft;
- security after compromise of endpoint firmware;
- denial-of-service resistance;
- availability under contention;
- protection against deliberate persistent-state tampering;
- protection against persistent-state rollback;
- time-based authority validity or expiry;
- persistence guarantees independent of the tested ESP-IDF/NVS storage stack;
- correctness for arbitrary numbers of concurrent requesters; or
- correctness for arbitrary hardware, firmware, storage, or scheduler implementations.

The losing requester's `state_invalid` result is fail-closed for this test, but R003 does not claim that contention preserves availability.

## Final disposition

~~~text
ESP-LOCAL-007
Scored run: R003
Date:       2026-09-23
Result:     PASS
~~~

The tested bounded-authority property held under genuine two-requester contention and was corroborated at the physical execution boundary by an independent hardware witness.
