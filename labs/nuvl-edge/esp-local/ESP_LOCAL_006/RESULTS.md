# ESP-LOCAL-006 Results

## Test Objective

ESP-LOCAL-006 evaluated whether a hostile or compromised intermediary positioned between the requester/provider side and an endpoint-local enforcement boundary could convert transport or content-control capability into greater executable authority.

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
- persistent single-use state enforcement,
- recording accepted authority as spent,
- physical PWM command issuance.

An independent ESP32-S3 witness monitored the endpoint PWM line electrically.

## Overall Result

**PASS**

Within the tested configuration, intermediary control over transport and request content did not become authority to enlarge, substitute, regenerate, or replay provider-issued execution permission.

The completed matrix demonstrated:

- mutation of signed authority fields was rejected,
- attempted enlargement of `max_uses` was rejected,
- rejected mutations did not consume the legitimate authority,
- an independently signed wrong-provider version of the same canonical authority bytes was rejected,
- wrong-provider rejection did not consume the legitimate authority,
- the trusted-provider version of those same authority bytes was accepted once,
- accepted authority was recorded as spent before PWM command issuance,
- replay of consumed authority was denied,
- replay produced no second servo-valid PWM burst.

## Test Path

```text
requester / provider
        ↓
Raspberry Pi 3 hostile relay
        ↓
ESP32-S3 endpoint-local enforcement
        ↓
servo PWM command path
        ↓
independent ESP32-S3 GPIO witness
```

Test endpoint:

```text
identity: esp32-xiao-servo-02
hardware: Seeed XIAO ESP32-S3
endpoint port: 19061
```

Relay:

```text
host: Raspberry Pi 3
listen port: 19060
provider private key: absent
trusted signing capability: absent
```

## Result Matrix

| Case | Relay Action | Endpoint Result | Witness Result | Outcome |
|---|---|---|---|---|
| Auth1 action mutation | Changed `action` | `signature_invalid` | No servo-valid PWM burst | PASS |
| Auth1 context mutation | Changed `context` | `signature_invalid` | No servo-valid PWM burst | PASS |
| Auth1 device mutation | Changed `device_id` | `signature_invalid` | No servo-valid PWM burst | PASS |
| Auth1 max-use enlargement | Changed `max_uses` from `1` to `2` | `signature_invalid` | No servo-valid PWM burst | PASS |
| Auth1 untouched control | Byte-preserving pass-through | Accepted / executed | One 49-pulse PWM burst | PASS |
| Auth1 replay | Same consumed authority | `replay_spent` | No second servo-valid burst | PASS |
| Auth2 wrong-provider control | Byte-preserving pass-through | `signature_invalid` | No PWM burst | PASS |
| Auth2 trusted-provider control | Byte-preserving pass-through | Accepted / executed | One 49-pulse PWM burst | PASS |
| Auth2 trusted replay | Same consumed authority | `replay_spent` | No second servo-valid burst | PASS |

## Authority #1 Mutation Matrix

Authority #1 used the bounded semantics:

```json
{
  "action": "move_servo",
  "context": "esp_local_006",
  "device_id": "esp32-xiao-servo-02",
  "max_uses": 1,
  "nonce": "99337255d93cee60019493a813c42f23"
}
```

Authority #1 identifier:

```text
f72ade66cea3c93c2cb57944e03d69e185a061a59f83c3705a8e6977dfddc7d6
```

The relay altered one signed authority field at a time while retaining the original trusted-provider signature.

### Action Mutation

The relay changed:

```text
action = move_servo_admin
```

The endpoint returned:

```text
{"status":"denied","reason":"signature_invalid"}
```

### Context Mutation

The relay changed:

```text
context = esp_local_006_relay_mutated
```

The endpoint returned:

```text
{"status":"denied","reason":"signature_invalid"}
```

### Device Mutation

The relay changed:

```text
device_id = esp32-xiao-servo-99
```

The endpoint returned:

```text
{"status":"denied","reason":"signature_invalid"}
```

### `max_uses` Enlargement

The relay changed:

```text
max_uses = 2
```

The endpoint returned:

```text
{"status":"denied","reason":"signature_invalid"}
```

The completed endpoint run recorded:

```text
006_REQUEST_FROM 192.168.0.141:36666
006_DENY_SIGNATURE_INVALID
```

## Mutation Non-Consumption Control

The four Auth1 mutation denials occurred before the untouched positive control.

After those rejected mutations, the same original Authority #1 request was forwarded unchanged through the relay.

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

The requester received:

```text
{"status":"accepted","reason":"executed"}
```

This sequence demonstrates that the rejected mutation attempts did not consume or poison the legitimate Authority #1 instance.

That property is distinct from simple mutation rejection.

A system that rejected altered authority but consumed the legitimate single-use state during rejection would still expose an authority-exhaustion denial primitive.

That behavior was not observed.

## Auth1 Independent Witness Result

The independent witness recorded one servo-valid PWM burst after the untouched Authority #1 acceptance.

Observed:

```text
49 servo-valid pulses
pulse-width range: 1998-2001 µs
```

Two isolated `1 µs` transients were also observed during the Auth1 witness session.

Those transients were retained in the evidence record.

They did not form a PWM burst and were not consistent with the approximately 2 ms command pulses observed during accepted execution.

## Auth1 Replay

The same trusted Authority #1 request was sent again after successful execution.

The endpoint recorded:

```text
006_SIGNATURE_VALID
006_SEMANTIC_ADMISSIBILITY_PASS
006_DENY_REPLAY_SPENT
```

The requester received:

```text
{"status":"denied","reason":"replay_spent"}
```

No second servo-valid PWM burst was observed.

## Authority #2 Wrong-Provider Control

Authority #2 used the same bounded semantics with a fresh nonce:

```json
{
  "action": "move_servo",
  "context": "esp_local_006",
  "device_id": "esp32-xiao-servo-02",
  "max_uses": 1,
  "nonce": "58f8f57034a9bbe30ffb099c7f9ae62c"
}
```

Authority #2 identifier:

```text
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc
```

Trusted provider raw Ed25519 public key:

```text
48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1
```

Independent wrong-provider raw Ed25519 public key:

```text
4c0baa6a6df7637dbb78aec1262c142be80f66d68eac3fd91f7ee41ee003a2de
```

The wrong-provider keypair was generated independently for the negative control and was not configured as trusted at the endpoint.

## Identical-Authority Control

The wrong-provider and trusted-provider Auth2 requests were constructed over identical canonical authority bytes.

Artifact verification produced:

```text
authority_bytes_equal: True

authority_sha256:
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc

signatures_equal: False
```

This removes authority-content differences as an explanation for the differing endpoint decisions.

Only the provider signature differed.

## Wrong-Provider Result

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

The requester received:

```text
{"status":"denied","reason":"signature_invalid"}
```

No PWM burst was observed by the independent witness.

## Trusted-Provider Control After Wrong-Provider Denial

The trusted-provider request over the same canonical Authority #2 bytes was then forwarded unchanged.

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

The requester received:

```text
{"status":"accepted","reason":"executed"}
```

This demonstrates that rejection of the wrong-provider signature did not consume the legitimate Authority #2 instance.

## Auth2 Independent Witness Result

The accepted trusted-provider Auth2 execution produced one independently observed PWM burst.

Observed:

```text
49 servo-valid pulses
pulse-width range: 1999-2001 µs
```

No PWM burst was observed for the preceding wrong-provider submission.

## Auth2 Replay

The trusted-provider Auth2 request was sent again after successful execution.

The endpoint recorded:

```text
006_SIGNATURE_VALID
006_SEMANTIC_ADMISSIBILITY_PASS
006_DENY_REPLAY_SPENT
```

The requester received:

```text
{"status":"denied","reason":"replay_spent"}
```

The relay forwarded the same trusted request bytes used during the accepted execution.

No second servo-valid PWM burst was observed.

## Persistent-State Evidence

Authority #2 was captured from the dedicated `nuvl_state` partition before the wrong-provider / trusted-provider sequence.

The parsed record showed:

```text
state = 01 / UNSPENT

authority_id =
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc

NVS page CRC32 = OK
```

Pre-test partition SHA-256:

```text
7529911ee67a9702f2769bb5afdcaf40481bf3c8e601f0e508baa62478f4d80c
```

After trusted execution and replay testing, the partition was captured again.

The parsed record showed:

```text
state = 02 / SPENT

authority_id =
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc

NVS page CRC32 = OK
```

Post-test partition SHA-256:

```text
f807bc6493e7d2f2ce33eb72a550e5f9eca2597c3dd83ee9ab0d60e721ea528c
```

The differing partition hashes establish that the two captured partition images differ.

They do not, by themselves, prove that only the spent-state field changed.

The specific observed authority-state transition is established by the parsed state records, preserved authority identifier, valid NVS CRC, endpoint decision sequence, and replay result.

## Execution Ordering

For accepted requests, the endpoint log showed the following sequence:

```text
signature valid
        ↓
semantic admissibility pass
        ↓
authority unspent
        ↓
spent-state reread pass
        ↓
PWM command begin
        ↓
PWM command end
        ↓
accept executed
```

ESP-LOCAL-006 therefore observed the authority as spent before physical PWM command issuance.

Persistence characteristics underlying that spent-state behavior were evaluated separately in ESP-LOCAL-005.

ESP-LOCAL-006 does not extend the persistence claim beyond the limits documented there, including the unresolved exact ESP-IDF/NVS persistence boundary around `nvs_set_blob()` and explicit `nvs_commit()`.

## Transport Anomaly

Initial `mutate-max-uses` attempts encountered relay timeout behavior while the Pi-to-endpoint path exhibited elevated latency.

Those attempts did not produce a corresponding completed endpoint authority-validation event.

They were therefore not scored as authorization PASS results.

The case was rerun with a longer transport timeout.

The mutated request then reached the endpoint and was explicitly rejected with:

```text
006_DENY_SIGNATURE_INVALID
```

Only that completed endpoint-validation run was counted as the scored result.

A transport timeout, lack of response, or failure to deliver a request was not treated as equivalent to an endpoint authorization denial.

## Relay Evidence

Auth1 relay evidence:

```text
ESP_LOCAL_006_RELAY_AUTH1.jsonl

records: 8
SHA-256:
ccac98462da0708a463ecc1328a5c01cd0b77f0566e1260f9e70237b0f43b659
```

Auth2 relay evidence:

```text
ESP_LOCAL_006_RELAY_AUTH2.jsonl

records: 3
SHA-256:
27a63a71289a49e9b44df57acce8a065d4f1cba2a5b697e4314b4cbf2982a0da
```

## Supported Result

ESP-LOCAL-006 supports the following scoped result:

> In the tested endpoint-local enforcement architecture, an intermediary capable of observing, transporting, modifying, substituting, and replaying provider-issued authority could not independently enlarge or manufacture executable authority. Mutations to trusted-provider-signed authority were rejected, and an identical authority object signed by an untrusted provider key was rejected while the trusted-provider signature over the same canonical authority bytes was accepted. Rejected mutations and wrong-provider submissions did not consume the corresponding legitimate authority. Accepted single-use authority was observed as spent before physical PWM command issuance, and subsequent replay produced no second witnessed command burst.

## Boundaries

ESP-LOCAL-006 does not establish:

- resistance to trusted provider private-key theft,
- resistance to complete endpoint compromise,
- secure routing,
- denial-of-service resistance,
- availability under hostile intermediary behavior,
- trusted time or expiration enforcement,
- tamper-resistant persistent storage,
- anti-rollback protection,
- exactly-once mechanical actuation,
- guaranteed mechanical servo movement.

The relay was hostile with respect to transport and request content.

It did not possess trusted provider signing material.

That condition is fundamental to the scope of the test.

The demonstrated property is not that a hostile intermediary cannot interfere with communication.

The demonstrated property is that intermediary control over the tested request path did not become greater provider authority.
