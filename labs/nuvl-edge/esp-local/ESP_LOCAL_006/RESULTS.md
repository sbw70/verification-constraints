# ESP-LOCAL-006 Results

## Test Objective

ESP-LOCAL-006 evaluated whether a hostile or compromised intermediary positioned between provider-issued authority and an endpoint-local enforcement boundary could convert control of transport or request content into greater executable authority.

The tested relay could:

- receive provider-issued authority requests,
- inspect request contents,
- modify signed authority fields,
- forward requests unchanged,
- substitute independently signed request material,
- replay previously accepted requests.

The relay did not possess the trusted provider private key and did not have trusted-provider signing capability.

The endpoint remained responsible for:

- Ed25519 signature verification,
- semantic admissibility,
- binding received canonical authority to persistent authority state,
- persistent single-use enforcement,
- recording accepted authority as spent before physical command issuance,
- PWM command issuance.

An independent ESP32-S3 witness monitored the endpoint PWM line electrically.

## Overall Result

**PASS**

Within the tested configuration, intermediary control over transport and request content did not become authority to enlarge, substitute, regenerate, or replay provider-issued execution permission.

The completed matrix demonstrated that:

- mutation of signed authority fields was rejected,
- attempted enlargement of `max_uses` was rejected,
- rejected mutations did not consume the legitimate Authority #1 instance,
- an independently signed wrong-provider version of the same canonical Authority #2 bytes was rejected,
- wrong-provider rejection did not consume the legitimate Authority #2 instance,
- the trusted-provider version of those same Authority #2 bytes was accepted once,
- accepted authority was recorded as `SPENT` before PWM command issuance,
- the runtime closed and reinitialized the authority-state partition and freshly reread the same authority as `SPENT` before PWM,
- replay of consumed authority was denied,
- replay produced no second servo-valid PWM burst.

## Test Path

```text
requester / provider
        ↓
Raspberry Pi 3 hostile relay
        ↓
ESP32-S3 endpoint-local recognition
        ↓
persistent single-use authority enforcement
        ↓
servo PWM command path
        ↓
independent ESP32-S3 GPIO witness
```

Test endpoint:

```text
identity:      esp32-xiao-servo-02
hardware:      Seeed XIAO ESP32-S3
framework:     ESP-IDF v6.1
endpoint port: 19061
```

Relay:

```text
host:                     Raspberry Pi 3
listen port:              19060
provider private key:     absent
trusted signing capability: absent
```

## Result Matrix

| Case | Relay / Request Condition | Endpoint Result | Witness Result | Outcome |
|---|---|---|---|---|
| Auth1 action mutation | Changed `action` | `signature_invalid` | No servo-valid PWM burst | PASS |
| Auth1 context mutation | Changed `context` | `signature_invalid` | No servo-valid PWM burst | PASS |
| Auth1 device mutation | Changed `device_id` | `signature_invalid` | No servo-valid PWM burst | PASS |
| Auth1 max-use enlargement | Changed `max_uses` from `1` to `2` | `signature_invalid` | No servo-valid PWM burst | PASS |
| Auth1 untouched control | Byte-preserving trusted request | Accepted / executed | One 49-pulse PWM burst | PASS |
| Auth1 replay | Same consumed authority | `replay_spent` | No second servo-valid burst | PASS |
| Auth2 wrong-provider control | Same canonical authority bytes, wrong signature | `signature_invalid` | No PWM burst | PASS |
| Auth2 trusted-provider control | Same canonical authority bytes, trusted signature | Accepted / executed | One 49-pulse PWM burst | PASS |
| Auth2 trusted replay | Same consumed trusted authority | `replay_spent` | No second servo-valid burst | PASS |

## Authority #1

Authority #1 used:

```json
{
  "action": "move_servo",
  "context": "esp_local_006",
  "device_id": "esp32-xiao-servo-02",
  "max_uses": 1,
  "nonce": "99337255d93cee60019493a813c42f23"
}
```

Authority identifier:

```text
f72ade66cea3c93c2cb57944e03d69e185a061a59f83c3705a8e6977dfddc7d6
```

The relay altered one signed authority field at a time while retaining the original trusted-provider signature.

## Auth1 Action Mutation

Relay-modified field:

```text
action = move_servo_admin
```

Endpoint result:

```text
{"status":"denied","reason":"signature_invalid"}
```

No servo-valid PWM burst was observed.

## Auth1 Context Mutation

Relay-modified field:

```text
context = esp_local_006_relay_mutated
```

Endpoint result:

```text
{"status":"denied","reason":"signature_invalid"}
```

No servo-valid PWM burst was observed.

## Auth1 Device Mutation

Relay-modified field:

```text
device_id = esp32-xiao-servo-99
```

Endpoint result:

```text
{"status":"denied","reason":"signature_invalid"}
```

No servo-valid PWM burst was observed.

## Auth1 `max_uses` Enlargement

Relay-modified field:

```text
max_uses = 2
```

The completed endpoint-reaching run recorded:

```text
006_REQUEST_FROM 192.168.0.141:36666
006_DENY_SIGNATURE_INVALID
```

Endpoint result:

```text
{"status":"denied","reason":"signature_invalid"}
```

No servo-valid PWM burst was observed.

## Auth1 Mutation Non-Consumption Control

The four Auth1 mutation denials occurred before the untouched trusted positive control.

After those rejected submissions, the original trusted Authority #1 request was forwarded unchanged.

The relay recorded matching ingress and egress SHA-256 values:

```text
0bd146f428f7eb32c1958f4816cae0374b606517f147c7ec08c453afd41e5671
```

The endpoint then recorded:

```text
006_SIGNATURE_VALID
006_SEMANTIC_ADMISSIBILITY_PASS
006_AUTHORITY_UNSPENT_PASS
006_DURABLE_SPENT_REREAD_PASS
006_PWM_COMMAND_BEGIN
006_PWM_COMMAND_END
006_ACCEPT_EXECUTED
```

Requester result:

```text
{"status":"accepted","reason":"executed"}
```

This establishes that the preceding invalid mutations did not consume or poison the legitimate unused Authority #1 instance.

That result is distinct from simple mutation rejection.

A design that rejected altered authority but consumed the legitimate single-use state during rejection would expose an authority-exhaustion denial primitive.

That behavior was not observed.

## Auth1 Execution Ordering

For the accepted Authority #1 request, runtime processing followed:

```text
trusted signature valid
        ↓
semantic admissibility pass
        ↓
matching authority state present
        ↓
UNSPENT
        ↓
write SPENT
        ↓
nvs_commit
        ↓
nvs_close
        ↓
nvs_flash_deinit_partition
        ↓
nvs_flash_init_partition
        ↓
fresh state reread
        ↓
same authority-id + SPENT
        ↓
006_DURABLE_SPENT_REREAD_PASS
        ↓
PWM command begin
```

The observed execution therefore placed the spent-state verification before physical PWM command issuance.

The fresh reread occurred after closing the NVS handle and deinitializing and reinitializing the authority partition.

This is stronger than a same-handle cached read.

It does not independently establish persistence across every possible immediate power-loss point or resolve the exact physical ESP-IDF/NVS persistence boundary.

## Auth1 Independent Witness Result

The independent witness recorded one servo-valid PWM burst after the accepted Authority #1 request.

Observed:

```text
49 servo-valid pulses
pulse-width range: 1998–2001 µs
```

Two isolated `1 µs` transients were also preserved in the witness evidence.

Those transients did not form a servo-valid PWM burst and were not consistent with the approximately 2 ms command pulses observed during accepted execution.

## Auth1 Replay

The same trusted Authority #1 request was sent again after successful execution.

The endpoint recorded:

```text
006_SIGNATURE_VALID
006_SEMANTIC_ADMISSIBILITY_PASS
006_DENY_REPLAY_SPENT
```

Requester result:

```text
{"status":"denied","reason":"replay_spent"}
```

No second servo-valid PWM burst was observed.

Final Authority #1 state capture:

```text
evidence/ESP_LOCAL_006_AUTH1_SPENT_FINAL.bin
```

SHA-256:

```text
6cd54795b1a346e8c4c87a0ecd044bc64025e49ba55d2f170e9b03ff74306c9f
```

The parsed authority record identified Authority #1 as `SPENT`.

## Authority #2

Authority #2 used:

```json
{
  "action": "move_servo",
  "context": "esp_local_006",
  "device_id": "esp32-xiao-servo-02",
  "max_uses": 1,
  "nonce": "58f8f57034a9bbe30ffb099c7f9ae62c"
}
```

Authority identifier:

```text
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc
```

Trusted provider raw Ed25519 public key:

```text
48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1
```

Wrong-provider raw Ed25519 public key:

```text
4c0baa6a6df7637dbb78aec1262c142be80f66d68eac3fd91f7ee41ee003a2de
```

The wrong-provider keypair was generated independently for the negative control.

The endpoint had no configured trust relationship with that key.

## Auth2 Identical-Authority Control

The trusted-provider and wrong-provider Auth2 requests were constructed over identical canonical authority bytes.

Verification produced:

```text
authority_bytes_equal: True

authority_sha256:
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc

signatures_equal: False
```

This isolates provider-key trust from authority-content differences.

The canonical authority bytes were identical.

The signatures differed.

## Auth2 Pre-Test State

Before the wrong-provider / trusted-provider sequence, the dedicated authority-state partition was captured.

Published capture:

```text
evidence/ESP_LOCAL_006_AUTH2_UNSPENT.bin
```

SHA-256:

```text
7529911ee67a9702f2769bb5afdcaf40481bf3c8e601f0e508baa62478f4d80c
```

Parsed record:

```text
state = 01 / UNSPENT

authority_id =
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc

NVS page CRC32 = OK
```

This established the pre-test Authority #2 state as unused.

## Auth2 Wrong-Provider Result

The wrong-provider Auth2 request was forwarded unchanged through the relay.

Relay ingress and egress SHA-256:

```text
03bc27c96c99225f84a64fd74621293826f0a0561f67fbea2484b9041ba0137b
```

The endpoint recorded:

```text
006_REQUEST_FROM 192.168.0.141:38266
006_DENY_SIGNATURE_INVALID
```

Requester result:

```text
{"status":"denied","reason":"signature_invalid"}
```

No servo-valid PWM burst was observed.

## Auth2 Wrong-Provider Non-Consumption Control

After the wrong-provider denial, the trusted-provider request over the same canonical Authority #2 bytes was forwarded unchanged.

Relay ingress and egress SHA-256:

```text
13ce223290a908b855eccf05047a636cdee6de6207639dae2a3e8076a2d898a4
```

The endpoint recorded:

```text
006_SIGNATURE_VALID
006_SEMANTIC_ADMISSIBILITY_PASS
006_AUTHORITY_UNSPENT_PASS
006_DURABLE_SPENT_REREAD_PASS
006_PWM_COMMAND_BEGIN
006_PWM_COMMAND_END
006_ACCEPT_EXECUTED
```

Requester result:

```text
{"status":"accepted","reason":"executed"}
```

Because the trusted request used the same canonical authority bytes as the preceding wrong-provider request, this demonstrates that the wrong-provider rejection did not consume or poison the legitimate Authority #2 instance.

## Auth2 Independent Witness Result

The wrong-provider submission produced no servo-valid PWM burst.

The accepted trusted-provider Authority #2 execution produced:

```text
49 servo-valid pulses
pulse-width range: 1999–2001 µs
```

One servo-valid command burst was observed.

## Auth2 Replay

The accepted trusted-provider Auth2 request was sent again.

The endpoint recorded:

```text
006_SIGNATURE_VALID
006_SEMANTIC_ADMISSIBILITY_PASS
006_DENY_REPLAY_SPENT
```

Requester result:

```text
{"status":"denied","reason":"replay_spent"}
```

The relay forwarded the same trusted request bytes used during accepted execution.

No second servo-valid PWM burst was observed.

## Auth2 Final State

After trusted execution and replay testing, the authority partition was captured again.

Published capture:

```text
evidence/ESP_LOCAL_006_AUTH2_SPENT_FINAL.bin
```

SHA-256:

```text
f807bc6493e7d2f2ce33eb72a550e5f9eca2597c3dd83ee9ab0d60e721ea528c
```

Parsed record:

```text
state = 02 / SPENT

authority_id =
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc

NVS page CRC32 = OK
```

The pre-test and final partition images have different SHA-256 values.

That establishes that the complete captured images differ.

The specific `UNSPENT` to `SPENT` interpretation is supported by the parsed state records, preserved authority identifier, valid NVS CRC, endpoint decision sequence, and replay behavior.

The partition hashes alone are not treated as proof that only one field changed.

## Persistent-State Evidence Summary

Published raw captures:

```text
evidence/ESP_LOCAL_006_AUTH1_SPENT_FINAL.bin
evidence/ESP_LOCAL_006_AUTH2_UNSPENT.bin
evidence/ESP_LOCAL_006_AUTH2_SPENT_FINAL.bin
```

These are direct raw reads of the dedicated `nuvl_state` partition.

They are not reconstructed text artifacts.

The relevant partition parameters were:

```text
label:   nuvl_state
offset:  0x110000
length:  0x6000
size:    24576 bytes
```

## Runtime Spend-Before-Command Result

For accepted requests, the endpoint implementation and runtime observations establish this tested ordering:

```text
signature verification
        ↓
semantic admissibility
        ↓
authority-id binding
        ↓
persistent-state validation
        ↓
require UNSPENT
        ↓
write SPENT
        ↓
commit
        ↓
close NVS handle
        ↓
deinitialize authority partition
        ↓
reinitialize authority partition
        ↓
fresh reread
        ↓
require same authority-id + SPENT
        ↓
PWM command
```

The endpoint did not issue PWM before that sequence completed.

The runtime log marker:

```text
006_DURABLE_SPENT_REREAD_PASS
```

records successful post-commit verification after partition close, deinitialization, reinitialization, and fresh reread.

This result should not be expanded into a stronger claim that ESP-LOCAL-006 independently proved survival across every immediate power-loss boundary.

Persistence crash and power-loss behavior was characterized separately in ESP-LOCAL-005, including the unresolved exact ESP-IDF/NVS persistence boundary.

## Transport Anomaly

Initial `mutate-max-uses` attempts encountered relay timeout behavior while the Pi-to-endpoint path exhibited elevated latency.

Those attempts did not produce a completed endpoint authority-validation event.

They were not scored as authorization denials.

The case was rerun with a longer transport timeout.

The modified request then reached the endpoint and was explicitly rejected with:

```text
006_DENY_SIGNATURE_INVALID
```

Only the completed endpoint-reaching run was scored.

A transport timeout, dropped request, or delivery failure was not treated as equivalent to an endpoint authorization denial.

## Relay Evidence

Authority #1 relay evidence:

```text
evidence/ESP_LOCAL_006_RELAY_AUTH1.jsonl

records: 8

SHA-256:
ccac98462da0708a463ecc1328a5c01cd0b77f0566e1260f9e70237b0f43b659
```

The file includes scored authority transactions plus non-authority connectivity/probe records.

Empty probes are not treated as scored authority attempts.

Authority #2 relay evidence:

```text
evidence/ESP_LOCAL_006_RELAY_AUTH2.jsonl

records: 3

SHA-256:
27a63a71289a49e9b44df57acce8a065d4f1cba2a5b697e4314b4cbf2982a0da
```

## Curated Terminal Evidence

Endpoint observations are preserved in:

```text
evidence/ESP_LOCAL_006_ENDPOINT_COM15_CURATED.txt
```

Publication-stage SHA-256:

```text
17d7c4f5c1c8aff3bd5beac42116d92ed7b7c431d4bc78fac10bb12b909524ca
```

Witness observations are preserved in:

```text
evidence/ESP_LOCAL_006_WITNESS_COM8_CURATED.txt
```

Publication-stage SHA-256:

```text
5b768366307449d2c6694a15a50c271b2ccc217fa7c0aee0ba9f451ee209c378
```

Both are curated derivatives assembled from preserved interactive terminal output.

Neither is represented as an original raw redirected serial log.

## Supported Result

ESP-LOCAL-006 supports the following scoped result:

> In the tested endpoint-local enforcement architecture, an intermediary capable of observing, transporting, modifying, substituting, and replaying provider-issued authority could not independently enlarge, manufacture, substitute, regenerate, or reuse executable provider authority. Mutations to trusted-provider-signed authority were rejected, and an identical canonical authority object signed by an untrusted provider key was rejected while the trusted-provider signature over the same bytes was accepted. Rejected invalid submissions did not consume the corresponding legitimate unused authority. Accepted single-use authority was recorded as spent and successfully reread as the same spent authority after NVS handle close and authority-partition reinitialization before PWM command issuance. Subsequent replay produced no second witnessed servo-valid command burst.

## Boundaries

ESP-LOCAL-006 does not establish:

- resistance to trusted provider private-key theft,
- resistance to complete endpoint compromise,
- secure routing,
- denial-of-service resistance,
- guaranteed availability under hostile intermediary behavior,
- trusted time or expiration enforcement,
- tamper-resistant persistent storage,
- anti-rollback protection,
- persistence across every possible immediate power-loss point,
- the exact physical ESP-IDF/NVS persistence boundary,
- exactly-once mechanical actuation,
- guaranteed mechanical servo movement.

The relay was hostile with respect to transport and request content.

It did not possess trusted provider signing material.

That condition is fundamental to the test scope.

The demonstrated result is not that a hostile intermediary cannot interfere with communication.

The demonstrated result is that intermediary control over the tested request path did not become greater executable provider authority.

The separate non-consumption result is also material:

> Rejected invalid submissions did not exhaust the legitimate unused authority later accepted under the original provider-established bounds.
