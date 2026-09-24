# ESP-LOCAL-007 Provider Artifacts

This directory contains the provider-side material used to create the fresh single-use authority used for the final ESP-LOCAL-007 contention test.

The provider's role is limited to originating and signing authority. It does not coordinate requesters, maintain endpoint consumption state, observe physical execution, or decide which concurrent requester succeeds.

## Directory contents

~~~text
provider/
├── README.md
├── esp_local_007_provider.py
├── ESP_LOCAL_007_AUTH2.txt
├── ESP_LOCAL_007_AUTH2_REQUEST.json
├── esp_local_004_private.pem
└── esp_local_004_public.pem
~~~

## `esp_local_007_provider.py`

`esp_local_007_provider.py` generates a fresh provider-signed authority for ESP-LOCAL-007.

The generated authority is constrained to:

~~~text
device_id = esp32-xiao-servo-02
context   = esp_local_006
action    = move_servo
max_uses  = 1
~~~

A fresh 16-byte random nonce is generated with `secrets.token_hex(16)`.

The authority object is canonicalized as compact JSON with lexicographically sorted keys:

~~~python
json.dumps(
    obj,
    sort_keys=True,
    separators=(",", ":"),
)
~~~

The SHA-256 digest of those exact canonical bytes becomes the authority ID.

The same canonical bytes are signed with the trusted Ed25519 provider private key.

The resulting request contains only:

~~~json
{
  "authority_b64": "<base64 canonical authority>",
  "signature_b64": "<base64 Ed25519 signature>"
}
~~~

## Provider key validation

Before generating an authority, the provider script verifies the expected test key material.

Expected private-key file SHA-256:

~~~text
DA0A36F274EFC6E3CE1C7643800B952B1AA2895201E5A6D6852D308729466509
~~~

Expected raw Ed25519 public key:

~~~text
48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1
~~~

The script also derives the public key from the private key and requires it to match the loaded public key.

Generation stops if:

- the expected private key is absent;
- the expected public key is absent;
- the private-key file hash differs from the expected hash;
- the private and public keys do not form the expected pair; or
- the raw public key differs from the expected trust anchor.

The checked-in PEM files are test material retained with the ESP-LOCAL-007 reproduction artifacts.

## Output protection

The generator refuses to overwrite either output artifact if it already exists:

~~~text
ESP_LOCAL_007_AUTH2_REQUEST.json
ESP_LOCAL_007_AUTH2.txt
~~~

This prevents an existing authority record from being silently replaced by a newly generated nonce, authority ID, signature, and request.

A new generation therefore requires deliberate handling of the existing artifacts.

## AUTH2

The checked-in AUTH2 instance is the authority used for the final ESP-LOCAL-007 contention run.

Its canonical authority is:

~~~json
{"action":"move_servo","context":"esp_local_006","device_id":"esp32-xiao-servo-02","max_uses":1,"nonce":"b3e5571eee07d3e37ca757b54a549a3e"}
~~~

Fields:

~~~text
device_id = esp32-xiao-servo-02
context   = esp_local_006
action    = move_servo
max_uses  = 1
nonce     = b3e5571eee07d3e37ca757b54a549a3e
~~~

Authority ID:

~~~text
066fd59f04ba90f1476ea388a84e125a349a54435552205c0aaa6d5adfa14545
~~~

Provider signature:

~~~text
oD/gud28uD5tCy2yRURfVEsejixcJ4FClJ2222fhaJNGKuDf4/6e2/sjpxTbNyay7PbujCweZD9b62uvO/0MAA==
~~~

Trusted raw provider public key:

~~~text
48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1
~~~

## `ESP_LOCAL_007_AUTH2_REQUEST.json`

This is the exact request artifact presented concurrently by the ESP-LOCAL-007 requesters.

It contains the base64-encoded canonical authority and its base64-encoded Ed25519 signature.

Decoded `authority_b64`:

~~~json
{"action":"move_servo","context":"esp_local_006","device_id":"esp32-xiao-servo-02","max_uses":1,"nonce":"b3e5571eee07d3e37ca757b54a549a3e"}
~~~

SHA-256 of the checked-in request bytes:

~~~text
55f4380f4f50b2c68e6b4dfd1cb6e9b405fb938a498ae680ff36a5d248fc236a
~~~

Both concurrent requesters in the scored R003 run presented these same request bytes. No second authority was generated for the second requester.

That distinction is central to the test: the contention was over one provider-issued authority with `max_uses=1`, not two independently valid authorities.

## `ESP_LOCAL_007_AUTH2.txt`

This is the human-readable generation record associated with AUTH2.

It records:

- test ID;
- endpoint-runtime lineage;
- device ID;
- context;
- action;
- `max_uses`;
- nonce;
- exact canonical authority;
- authority ID;
- trusted provider public key;
- trusted private-key file hash; and
- generated signature.

SHA-256 of the checked-in AUTH2 record:

~~~text
867740e115664e4031b1a9be2f97c06e074d8c0133aa9213719912b06501b651
~~~

The record is provenance material. The actual requester input is `ESP_LOCAL_007_AUTH2_REQUEST.json`.

## Why the context remains `esp_local_006`

AUTH2 deliberately contains:

~~~text
context = esp_local_006
~~~

This is not an ESP-LOCAL-007 labeling error.

ESP-LOCAL-007 was constructed to retain the previously tested authority semantics while introducing concurrent requester dispatch as the new test variable. The provider generator therefore preserves the existing authority context rather than defining a new authority semantic solely for the contention test.

The ESP-LOCAL-007 concurrent runtime is authority-agnostic with respect to AUTH1 versus AUTH2. AUTH2 is bound to the endpoint through the provisioned persistent authority state, not through an AUTH2-specific runtime build.

## Relationship to endpoint provisioning

Provider generation and endpoint provisioning are separate operations.

The provider creates:

~~~text
canonical authority
        |
        +--> SHA-256 --> authority ID
        |
        +--> Ed25519 signature
        |
        +--> requester artifact
~~~

The corresponding authority ID is then provisioned into the endpoint's dedicated persistent authority state as `UNSPENT`.

For AUTH2:

~~~text
066fd59f04ba90f1476ea388a84e125a349a54435552205c0aaa6d5adfa14545
~~~

The endpoint provisioner does not create or enlarge that authority. It records the provider-derived authority ID and its local consumption state.

During the contention test, the provider is not consulted to choose a winning requester. Both requesters present the same already-issued authority to the endpoint.

## Reproduction

The generator requires Python with the `cryptography` package.

Its source configuration expects the original ESP-LOCAL-004 test keypair under:

~~~text
ESP_LOCAL_004/provider/keys/
~~~

and verifies that material against the pinned private-key hash and raw public key before signing.

The copies of the PEM files in this directory preserve the test key material alongside the ESP-LOCAL-007 artifacts, but the checked-in generator's configured paths remain the ESP-LOCAL-004 provider key paths.

Running the generator produces a **new** authority because the nonce is random. A newly generated authority will therefore have a different:

- nonce;
- canonical authority;
- authority ID;
- signature;
- request hash; and
- record hash.

The checked-in AUTH2 files preserve the exact authority used for the scored run and should not be regenerated when verifying that historical evidence.

## Authority boundary

The provider private key is the capability to originate provider-signed authority.

The endpoint receives verification material and a provisioned authority identifier; it does not require the provider private key to verify and enforce the request.

The coordinator transports the provider-issued request but does not modify its signed authority.

The independent witness observes physical execution but does not participate in authority issuance or verification.

ESP-LOCAL-007 therefore tests contention over an already bounded provider-issued authority without transferring authority origination to the coordinator, witness, or endpoint.
