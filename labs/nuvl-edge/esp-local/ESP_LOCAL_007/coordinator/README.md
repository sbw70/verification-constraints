# ESP-LOCAL-007 Coordinator

This directory contains the coordinator used for the ESP-LOCAL-007 concurrent-requester contention test.

The coordinator does not decide whether an authority is valid and does not participate in persistent authority consumption. Its role is to arrange a controlled concurrent presentation of identical request bytes, coordinate the independent hardware witness, and record requester-level timing and responses as machine-readable evidence.

The authoritative scored run is **R003 (2026-09-23)**.

## File

- `esp_local_007_coordinator.py` — opens and arms requester connections, gates release on the endpoint's exact READY response, releases identical bytes through a Python thread barrier, controls the witness run, records per-requester timestamps and responses, and writes a JSON evidence record.

## Test role

ESP-LOCAL-007 asks whether simultaneous presentation of the same valid, provider-issued, single-use authority can enlarge that authority into more than one physical execution.

For the scored R003 run:

- endpoint: `esp32-xiao-servo-02`, `192.168.0.186:19061`
- witness: `esp32-witness-007`, `192.168.0.216:19072`
- requesters: 2
- authority: AUTH2
- `max_uses`: 1
- coordinator release send-start skew: **42.7 µs**
- requester result: **1 accepted, 1 denied**
- independent physical result: **1 servo-like burst**
- final authority state: **SPENT**

The coordinator's accepted/denied counts are requester-level network evidence only. ESP-LOCAL-007 scoring also requires endpoint execution logs, independent witness evidence, and a final persistent-state readback.

## Coordination sequence

A run proceeds in this order:

1. Select rehearsal or live request bytes.
2. In live mode, load the frozen provider request without reserializing it.
3. Decode the canonical authority bytes and independently compute the authority ID as SHA-256 over those exact bytes.
4. Query the witness and start a named witness run.
5. Open all requester TCP connections to the endpoint.
6. Require the exact unsolicited READY object from every requester connection.
7. Hold every armed requester at a shared thread barrier.
8. Release the identical request bytes from all requester threads.
9. Capture each response independently with timestamps.
10. Mark requester completion at the witness.
11. Stop the witness run and query post-run witness status.
12. Write one machine-readable coordinator evidence JSON file.

The release is aborted if a requester does not receive the exact READY object. A denial line, timeout, closed connection, or any other response is not treated as READY.

## Rehearsal mode

Rehearsal is the default mode.

~~~powershell
python .\esp_local_007_coordinator.py --run-id RH003
~~~

The rehearsal payload is deliberately malformed and is expected to be rejected before persistent authority consumption. It exercises connection setup, READY gating, barrier release, response collection, witness control, and evidence generation without presenting the real authority.

A rehearsal is not evidence that the bounded-authority property passed. It verifies the coordination path before the one-shot live presentation.

## Live mode

Live mode presents the frozen provider request:

~~~powershell
python .\esp_local_007_coordinator.py --run-id R003 --live
~~~

The default request file is:

~~~text
../provider/ESP_LOCAL_007_AUTH2_REQUEST.json
~~~

Before any live release, the coordinator:

1. loads the frozen request bytes;
2. extracts and decodes `authority_b64`;
3. computes the authority ID from the canonical authority bytes;
4. displays the decoded authority and computed ID; and
5. requires the authority ID to be typed back exactly.

A mismatch aborts before the request is sent.

Live presentation of a single-use authority is intentionally one-shot. The coordinator contains no automatic retry of a live authority presentation.

## READY gating

The endpoint's exact expected READY line is:

~~~json
{"ready":true,"test":"ESP_LOCAL_007"}
~~~

Every requester must receive that exact object before the barrier can release.

This requirement is important to the test design. Merely opening two TCP connections does not establish concurrent execution inside the endpoint. READY confirms that each connection has been accepted by the concurrent runtime and has reached the point immediately before request receipt.

If one requester fails this gate, the barrier is broken for all requester threads and no coordinated release occurs.

## Request-byte preservation

The coordinator does not parse and regenerate the frozen wire request before transmission.

The request file is loaded as bytes, checked for the expected envelope shape, and transmitted with only the terminating newline added. This preserves the exact provider-generated request representation used by the endpoint's strict parser.

Every requester in a live run receives the same `request_line` object.

## Timing evidence

For each requester, the coordinator records:

- connection start;
- connection completion;
- READY receipt;
- pre-send release timestamp;
- post-send timestamp;
- response receipt;
- raw response;
- parsed response; and
- requester error, if any.

Release timing uses `time.perf_counter_ns()`. The evidence summary reports the difference between the earliest and latest requester pre-send timestamps as `release_send_skew_ns`.

R003 recorded:

~~~text
release_send_skew_ns = 42700
~~~

This is a measured coordinator send-start skew, not a claim that the endpoint executed both code paths within exactly 42.7 µs.

## Witness coordination

Unless `--skip-witness` is supplied, the coordinator wraps requester activity in an independent witness run:

~~~text
STATUS
START <run-id> <UTC-anchor>
MARK requesters_complete
STOP <UTC-anchor>
STATUS
~~~

The witness has no authority role. For R003, the independent ESP32-S3 RMT witness observed the endpoint's servo signal electrically and recorded the physical pulse evidence separately from the coordinator.

`--skip-witness` is suitable only for endpoint-only rehearsal or diagnostics. A scored ESP-LOCAL-007 result requires the independent witness.

## R003 result

The coordinator recorded:

~~~text
requesters: 2
accepted:   1
denied:     1
errored:    0
send skew:  42700 ns
~~~

The losing requester was denied `state_invalid`. Endpoint evidence showed that it did not cross the physical execution boundary.

The coordinator result alone is not the PASS determination. The scored R003 record was completed by correlating it with:

- exactly one endpoint `PWM_COMMAND_BEGIN`;
- exactly one endpoint `PWM_COMMAND_END`;
- exactly one endpoint `ACCEPT_EXECUTED`;
- one independent servo-like witness burst;
- zero witness capture overflows, truncations, and errors; and
- final `nuvl_state` readback showing AUTH2 durably SPENT.

The witness burst contained 50 servo-valid pulses, 1999–2000 µs wide, with 20000–20001 µs periods and a duration of approximately 982 ms.

## R003 witness-summary timing artifact

R003 exposed a coordinator timing issue that does **not** change the raw physical observation.

The coordinator sent `STOP` roughly 29 ms before the witness's 100 ms quiet-gap interval had elapsed. As a result, the witness `run_end` summary finalized with `servo_like_bursts: 0` before the active burst had been closed and counted.

The subsequent raw `burst_end` event recorded:

~~~text
burst_run: R003
pulses: 50
servo_like: true
duration_us: 982013
period_out_of_range: 0
~~~

The R003 evidence therefore uses the raw `burst_end` event as the physical burst record and retains the `run_end` discrepancy as a documented measurement artifact.

A future coordinator revision should wait approximately 200 ms after requester completion before issuing witness `STOP`, allowing the witness quiet-gap classifier to close the burst before the run summary is generated. That change was **not** part of the R003 tested coordinator and must not be retroactively attributed to R003.

## Earlier runs

### R001

R001 produced one accepted requester, one endpoint execution, a denied competing requester, and a final SPENT authority. The original interrupt-driven witness did not capture the physical burst reliably enough to satisfy the independent physical criterion.

R001 is retained as `INCONCLUSIVE_WITNESS_CAPTURE`, not as an ESP-LOCAL-007 contention failure.

### R002

R002 presented the already-spent AUTH1 request to an endpoint provisioned for AUTH2. Both requesters were denied `authority_state_mismatch`, no PWM execution occurred, and the witness observed no physical execution.

R002 is retained as a negative control and setup misfire, not as the scored contention run.

## Evidence JSON

The coordinator writes:

~~~text
ESP_LOCAL_007_COORDINATOR_<RUN_ID>_<unix-time>.json
~~~

The record includes:

- test ID and run ID;
- rehearsal/live mode;
- computed authority ID for live runs;
- endpoint and witness addresses;
- witness pre-run status;
- witness START reply;
- witness STOP reply;
- witness post-run status;
- all requester timing and response records;
- accepted, denied, and error counts;
- denial reasons;
- release send skew; and
- UTC recording time.

The R003 coordinator evidence file is:

~~~text
ESP_LOCAL_007_COORDINATOR_R003_1790183932.json
~~~

Coordinator JSON is one evidence stream. It must be evaluated together with the endpoint serial log, witness evidence, and persistent-state readback.

## Relevant R003 artifacts

| Artifact | Identifier / SHA-256 |
|---|---|
| AUTH2 request | `55f4380f4f50b2c68e6b4dfd1cb6e9b405fb938a498ae680ff36a5d248fc236a` |
| AUTH2 authority ID | `066fd59f04ba90f1476ea388a84e125a349a54435552205c0aaa6d5adfa14545` |
| Concurrent runtime source | `179029cb805fa93ca593f1433454311b4640a8aca0421228c88a8cffda9cf356` |
| Concurrent runtime binary | `6266f600f1d463b0d73878374fad178cae62497dbf38854e4df92a69a44b4abf` |
| Pre-race AUTH2 UNSPENT partition | `38327e63133030933c23b8d5d816fa85729a4aeb48f3e14fc3e71ee9fb35340f` |
| Post-race AUTH2 SPENT partition | `b87b8deba8d08c602af86ff3bac7636a02f0bc8dec5a4401d162b955384d4471` |
| Witness R003 run file | `cad594e3fc18a0baa90f6a11bc789124c21241340329f83be23f50341ba10705` |

## Claim boundary

The coordinator supports a controlled test of concurrent presentation. It does not itself establish at-most-once execution.

The complete R003 evidence establishes that, on the tested ESP-IDF/NVS endpoint and witness configuration, concurrent presentation of one valid single-use provider authority resulted in at most one physical execution.

It does not establish resistance to provider private-key theft, compromised endpoint firmware, denial-of-service or availability loss, persistent-state tampering or rollback, time-based validity, or storage-stack-independent persistence behavior.
