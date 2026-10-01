
# ESP-LOCAL-008 Provider

## Purpose

The ESP-LOCAL-008 provider creates provider-signed, endpoint-scoped, single-use authority artifacts for the signed target-binding test.

The provider defines the authority.

The endpoint does not create, enlarge, redirect, or reissue provider authority. It verifies and enforces the provider-signed object presented to it.

ESP-LOCAL-008 tests the following property:

> Valid provider-issued authority for one endpoint must not become authority for another endpoint.

The signed `device_id` is the directionality constraint exercised by the test.

## Repository Layout

The published provider tree is:

    provider/
    |-- README.md
    |-- esp_local_008_provider.py
    |
    `-- authorities/
        |-- ESP_LOCAL_008_AUTH_X2.txt
        |-- ESP_LOCAL_008_AUTH_X2_REQUEST.json
        |-- ESP_LOCAL_008_AUTH_Y2.txt
        |-- ESP_LOCAL_008_AUTH_Y2_REQUEST.json
        |-- ESP_LOCAL_008_AUTH_X3.txt
        |-- ESP_LOCAL_008_AUTH_X3_REQUEST.json
        |-- ESP_LOCAL_008_AUTH_Y3.txt
        `-- ESP_LOCAL_008_AUTH_Y3_REQUEST.json

The `.txt` files preserve the human-readable authority record.

The corresponding `_REQUEST.json` files preserve the exact signed request envelope presented to the endpoint.

## Provider Script

Primary source:

    esp_local_008_provider.py

The provider script:

- selects one target label;
- maps that label to one endpoint `device_id`;
- validates the expected provider private-key SHA-256;
- loads the provider private/public Ed25519 key pair;
- verifies that the private and public keys form the expected pair;
- verifies the expected raw provider public key;
- generates a fresh 128-bit nonce;
- constructs the authority object;
- serializes the authority canonically;
- computes the authority ID as SHA-256 of the exact canonical authority bytes;
- signs those canonical bytes with the provider private key;
- creates the transport request envelope;
- emits a human-readable authority record;
- refuses to overwrite an existing authority artifact.

Authority creation therefore occurs at the provider.

The presenter transports a frozen authority but does not mint one.

The endpoint verifies and enforces a frozen authority but does not mint one.

## Authority Schema

Each ESP-LOCAL-008 authority contains:

    device_id
    context
    action
    nonce
    max_uses

The final test used:

    context:  esp_local_008
    action:   move_servo
    max_uses: 1

The target endpoint identity is carried in the signed:

    device_id

The nonce is generated independently for each authority.

## Canonicalization

The provider canonicalizes the authority with:

    json.dumps(
        authority,
        sort_keys=True,
        separators=(",", ":"),
    )

The resulting UTF-8 bytes are the signed authority bytes.

The authority ID is:

    SHA256(canonical_authority_bytes)

The provider signature is calculated over those same canonical bytes.

No reserialization is required at the endpoint to establish the signed object received over the wire.

## Transport Envelope

The wire request contains:

    authority_b64
    signature_b64

`authority_b64` is the Base64 encoding of the exact canonical authority bytes.

`signature_b64` is the Base64 encoding of the Ed25519 provider signature over those bytes.

The frozen `_REQUEST.json` files preserve the exact request representation used by the presenter.

## Provider Trust Identity

The ESP-LOCAL-008 provider reuses the established ESP-LOCAL provider key pair.

Expected raw Ed25519 public key:

    48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1

Expected private-key SHA-256:

    DA0A36F274EFC6E3CE1C7643800B952B1AA2895201E5A6D6852D308729466509

The provider script refuses generation if the private-key file hash does not match the expected value.

It also derives the public key from the private key and requires that it exactly match the loaded public-key artifact.

Finally, the raw public key must match the expected trust-anchor value above.

The endpoint requires only the provider public trust anchor for signature verification.

## Key Location

The retained provider source resolves the signing key pair from the ESP-LOCAL-004 provider key location:

    ESP_LOCAL_004/
    `-- provider/
        `-- keys/
            |-- esp_local_004_private.pem
            `-- esp_local_004_public.pem

The ESP-LOCAL-008 provider directory does not duplicate those key files.

The key path in the source reflects the local test environment used to generate the frozen authority artifacts.

The provider key pair is unchanged from the established ESP-LOCAL trust anchor used by the preceding tests.

## Target Labels

The provider source supports:

    X
    Y
    X2
    Y2
    X3
    Y3

Target mapping:

    X   -> esp32-xiao-servo-01
    X2  -> esp32-xiao-servo-01
    X3  -> esp32-xiao-servo-01

    Y   -> esp32-xiao-servo-02
    Y2  -> esp32-xiao-servo-02
    Y3  -> esp32-xiao-servo-02

The original X/Y labels remain in the source as part of the test-development history.

The final scored matrix uses:

    X2
    Y2
    X3
    Y3

## Historical Source Comments

The provider source retains comments describing the original X/Y test plan.

Those comments predate the final scored matrix.

The final scored artifacts are:

    AUTH-X2
    AUTH-Y2
    AUTH-X3
    AUTH-Y3

The frozen records under `authorities/`, the final presenter JSON files, endpoint logs, state images, and witness evidence define the final scored test configuration.

Historical X/Y comments are retained as source provenance and are not the final result definition.

## Published Artifact Location

The frozen authority artifacts are published under:

    provider/authorities/

The retained provider script itself writes newly generated files beside:

    esp_local_008_provider.py

using names of the form:

    ESP_LOCAL_008_AUTH_<LABEL>.txt
    ESP_LOCAL_008_AUTH_<LABEL>_REQUEST.json

The scored artifacts were subsequently curated into the `authorities/` subdirectory for publication.

This relocation does not alter the frozen artifact bytes.

The coordinator publication path resolves the checked-in request artifacts from:

    provider/authorities/

## Final Frozen Authorities

### AUTH-X2

Target endpoint:

    esp32-xiao-servo-01

Nonce:

    c52317c297a174ece0266bc04ba74639

Canonical authority:

    {"action":"move_servo","context":"esp_local_008","device_id":"esp32-xiao-servo-01","max_uses":1,"nonce":"c52317c297a174ece0266bc04ba74639"}

Authority ID:

    0acbe0f43890299440c0f85b0b8a2c27e5cc38268a746f9bf296b765949f2710

Request SHA-256:

    B31A8826EDDC11EB00616E1CD00B3006EE6533486A7FDB0E93E17E197201AE4D

Authority-record SHA-256:

    DBE455503E4111D0046DEA8E94B59DC10EA68806A1211A8A083F7B9705431DF1

Final scored use:

    AUTH-X2 -> Servo #2

Expected result:

    target_id_mismatch

X2 is valid provider-signed authority for Servo1. Its presentation to Servo2 tests whether valid authority for one endpoint can be redirected to another.

### AUTH-Y2

Target endpoint:

    esp32-xiao-servo-02

Nonce:

    71886edad817176a2dca4b8a8bf70fa3

Canonical authority:

    {"action":"move_servo","context":"esp_local_008","device_id":"esp32-xiao-servo-02","max_uses":1,"nonce":"71886edad817176a2dca4b8a8bf70fa3"}

Authority ID:

    3ba6239d703d5ba203be2069f1c4c3fc89c27e63cff0b59be6977883ca654519

Request SHA-256:

    E46A3420468A54FEBAE66203131F0CA36B3B89E0E79F3BBF5CC9A4121A08A3E8

Authority-record SHA-256:

    A182D7F9712B831A7712C788EBC9C25030C0329742382C503010C2D7BC9B5E26

Final scored use:

    AUTH-Y2 -> Servo #2

Expected result:

    accepted

Y2 is the final positive authority for Servo2.

### AUTH-X3

Target endpoint:

    esp32-xiao-servo-01

Nonce:

    86062287c3d8be01446bf80ec69131bf

Canonical authority:

    {"action":"move_servo","context":"esp_local_008","device_id":"esp32-xiao-servo-01","max_uses":1,"nonce":"86062287c3d8be01446bf80ec69131bf"}

Authority ID:

    5222af8445ee67ba8712f2469c91449a841c777cb40b9395d22c9bb1f30388ef

Request SHA-256:

    809298A745EF0D8D54310E37D94D377508EDBD8A3BF9F9A22ECA09BD1D516C67

Authority-record SHA-256:

    7EEDB1855CE27BDC8784DABE0CB7FF9EAC1C38A4A23F46C0F268BE38DAD1883E

Final scored use:

    AUTH-X3 -> Servo #1

Expected result:

    accepted

X3 replaced the earlier Servo1 positive authority so the final physical signal could be captured on the correct Servo1 witness line.

### AUTH-Y3

Target endpoint:

    esp32-xiao-servo-02

Nonce:

    045c3bbf278c91bfe2605cacb5bca37d

Canonical authority:

    {"action":"move_servo","context":"esp_local_008","device_id":"esp32-xiao-servo-02","max_uses":1,"nonce":"045c3bbf278c91bfe2605cacb5bca37d"}

Authority ID:

    2c7ded33c6d5cc142c6f4ba91c04add1803fc361d00f34b9d288b3bb67f711fa

Request SHA-256:

    87607234070D39EE414CE51FE839D61A822FB1BC012C69F8FDE3D2C895052C43

Authority-record SHA-256:

    D5872E0956B327A84EE465E595BEB28BD0BE33D987DF1E2F188A510E9FE0B014

Final scored use:

    AUTH-Y3 -> Servo #1

Expected DUT result:

    target_id_mismatch

Y3 replaced the earlier Servo1 wrong-target physical-witness case so the final denial could be independently observed on the correct Servo1 signal line.

## Final Directionality Matrix

| Authority | Signed `device_id` | Presented To | Expected Endpoint Result |
|---|---|---|---|
| `AUTH-X2` | `esp32-xiao-servo-01` | Servo2 | `target_id_mismatch` |
| `AUTH-Y3` | `esp32-xiao-servo-02` | Servo1 | `target_id_mismatch` |
| `AUTH-X3` | `esp32-xiao-servo-01` | Servo1 | `accepted / executed` |
| `AUTH-Y2` | `esp32-xiao-servo-02` | Servo2 | `accepted / executed` |

The provider does not modify an authority between the wrong-target and correct-target concepts.

Directionality is established by the signed endpoint identity inside the authority itself.

## Authority Record

Each `.txt` authority record preserves:

    test_id
    enforcement_point
    target_label
    device_id
    context
    action
    max_uses
    nonce
    canonical authority bytes
    authority_id_sha256
    trusted provider public key
    trusted private-key SHA-256
    signature_b64

The record is evidence describing the generated object.

The `_REQUEST.json` file is the transport artifact actually consumed by the presenter.

## Generation Safety

The provider refuses to overwrite an existing output artifact.

If either expected output path already exists, generation exits before replacing it.

This prevents accidental mutation of an already-frozen authority under the same label.

The provider also refuses generation if:

- the expected private key is absent;
- the expected public key is absent;
- the private-key SHA-256 is wrong;
- the loaded private and public keys do not form the same pair;
- the raw public key does not match the expected provider trust anchor.

## Provider / Endpoint Separation

The provider possesses the signing capability required to create authority.

The endpoint possesses the provider public trust anchor required to verify authority.

The presenter possesses the frozen signed object required to transport authority.

These roles are distinct:

    provider
      creates and signs authority

    presenter
      transports frozen authority

    endpoint
      verifies target binding and local bounded-use state
      then enforces or denies

    witness
      independently observes the physical control-signal boundary

A transport component does not gain provider authority merely by possessing or forwarding a signed request.

## Relationship to ESP-LOCAL-008

ESP-LOCAL-008 does not change the provider trust anchor to create the directionality result.

The test changes the signed authority scope through `device_id` and introduces an explicit endpoint target-binding gate.

The relevant question is not whether an authority has a valid provider signature in isolation.

The tested question is whether a valid provider signature for endpoint X can become executable authority at endpoint Y.

The final wrong-target cases establish that it did not in the tested configuration.

## Scope

The provider artifacts establish the origin, signed contents, target identity, one-use bound, and cryptographic identity of the authorities used in ESP-LOCAL-008.

They do not independently establish endpoint enforcement.

Endpoint enforcement is established by the combined endpoint logs, persistent-state evidence, presenter records, and independent witness evidence retained elsewhere in the ESP-LOCAL-008 package.
