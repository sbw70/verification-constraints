# ESP-LOCAL-008 Provenance

This document records the lineage, tested identities, publication relationships, evidence classifications, and interpretation boundaries for ESP-LOCAL-008.

ESP-LOCAL-008 evaluates signed endpoint directionality:

> Valid provider-issued authority for one endpoint must not become executable authority at another endpoint.

The final scored matrix was executed on 2026-09-29 local time, corresponding to 2026-09-30 UTC.

ESP-LOCAL-008 retains the provider-controlled bounded-authority model established by the preceding ESP-LOCAL tests and adds an explicit signed target-binding gate before endpoint persistent-state access.

## Test Lineage

The tested authority model remains:

1. The provider originates authority.
2. The provider signs the canonical authority with Ed25519.
3. The signed `device_id` identifies the intended endpoint.
4. The endpoint verifies the provider signature.
5. The endpoint verifies semantic admissibility.
6. The endpoint verifies signed target binding.
7. The endpoint verifies local authority state.
8. The endpoint durably consumes authority.
9. The endpoint crosses the PWM command boundary.
10. The independent witness observes the electrical control signal.

ESP-LOCAL-008 separates target identity from the general semantic check and evaluates the signed target before persistent authority-state access.

The test variable is endpoint directionality.

The provider authority source is unchanged.

## Architectural Classification

ESP-LOCAL-008 is classified as:

    NUVL core
    architecture change: no

The tested property is narrower than general authorization correctness.

The supported directionality statement is:

> Provider-signed authority remained bound to its designated endpoint. Cross-target presentation was rejected before persistent authority-state access and before physical execution, while correctly targeted authority was accepted once, durably consumed, and independently observed at the physical control-signal boundary.

The physical claim is limited to the electrical PWM/control-signal boundary.

Mechanical servo-shaft displacement was not independently measured.

## Final Test Topology

Coordinator / presenter host:

    192.168.0.50

Servo #1:

    device_id:         esp32-xiao-servo-01
    hardware:          Seeed XIAO ESP32-S3
    IP:                192.168.0.81
    TCP port:          19081
    MAC:               1c:db:d4:45:11:e8
    endpoint PWM GPIO: 5

Servo #2:

    device_id:         esp32-xiao-servo-02
    hardware:          Seeed XIAO ESP32-S3
    IP:                192.168.0.186
    TCP port:          19081
    MAC:               1c:db:d4:45:10:a4
    endpoint PWM GPIO: 5

Independent witness:

    device_id:      esp32-witness-007
    hardware:       ESP32-S3
    IP:             192.168.0.216
    MAC:            44:1b:f6:ff:36:a8
    control port:   19072/UDP
    capture engine: RMT RX

Physical witness mapping:

| Witness Input | Monitored Signal |
|---|---|
| GPIO4 | Servo #2 control signal |
| GPIO5 | Servo #1 control signal |

Both endpoints used GPIO5 for their own PWM output. The witness GPIO numbers identify inputs on the separate witness device.

USB serial interfaces were bench interfaces and were not used as scored endpoint identity.

## Final Matrix

The final evidence matrix is:

| Run | Authority Scope | Target | Endpoint Result | State Result | Physical Witness |
|---|---|---|---|---|---|
| `X2_S2_DENY_001` | Servo1 | Servo2 | `target_id_mismatch` | target state unchanged | GPIO4: 0 pulses / 0 bursts |
| `Y3_S1_DENY_001` | Servo2 | Servo1 | `target_id_mismatch` | target state unchanged | GPIO5: 0 pulses / 0 bursts |
| `X3_S1_ACCEPT_001` | Servo1 | Servo1 | `accepted / executed` | authority SPENT | GPIO5: 49 pulses / 1 burst |
| `Y2_S2_ACCEPT_001` | Servo2 | Servo2 | `accepted / executed` | authority SPENT | GPIO4: 49 pulses / 1 burst |

The timestamps embedded in the presenter filenames establish the following run order. They are distinct from the later request-send and completion timestamps recorded inside each JSON file.

| Run | Filename Timestamp — UTC | Local Time — UTC−04:00 |
|---|---|---|
| `X2_S2_DENY_001` | 2026-09-30 00:50:36 | 2026-09-29 20:50:36 |
| `Y2_S2_ACCEPT_001` | 2026-09-30 01:05:12 | 2026-09-29 21:05:12 |
| `X3_S1_ACCEPT_001` | 2026-09-30 01:49:13 | 2026-09-29 21:49:13 |
| `Y3_S1_DENY_001` | 2026-09-30 02:04:04 | 2026-09-29 22:04:04 |

All final witness captures reported zero capture overflow, truncation, and error counts.

## Provider Lineage

The ESP-LOCAL-008 provider source is:

    provider/esp_local_008_provider.py

The provider creates Ed25519-signed authority with:

    context:  esp_local_008
    action:   move_servo
    max_uses: 1

Each authority also contains:

    device_id
    nonce

The signed `device_id` establishes the intended endpoint.

Canonical authority serialization uses sorted JSON keys and compact separators.

Authority identity is:

    SHA256(canonical authority bytes)

The same canonical bytes are signed with the provider Ed25519 private key.

## Provider Trust Identity

Trusted raw Ed25519 provider public key:

    48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1

Trusted provider private-key file SHA-256:

    DA0A36F274EFC6E3CE1C7643800B952B1AA2895201E5A6D6852D308729466509

The provider source resolves the signing key pair from the established ESP-LOCAL-004 provider-key location in the local test tree.

The ESP-LOCAL-008 publication does not duplicate those key files inside its own provider directory.

The frozen authority generation records preserve the provider public-key identity and private-key file hash used during generation.

## AUTH-X2 Lineage

AUTH-X2:

    device_id: esp32-xiao-servo-01
    context:   esp_local_008
    action:    move_servo
    max_uses:  1
    nonce:     c52317c297a174ece0266bc04ba74639

Canonical authority:

    {"action":"move_servo","context":"esp_local_008","device_id":"esp32-xiao-servo-01","max_uses":1,"nonce":"c52317c297a174ece0266bc04ba74639"}

Authority ID:

    0acbe0f43890299440c0f85b0b8a2c27e5cc38268a746f9bf296b765949f2710

Request SHA-256:

    B31A8826EDDC11EB00616E1CD00B3006EE6533486A7FDB0E93E17E197201AE4D

Generation-record SHA-256:

    DBE455503E4111D0046DEA8E94B59DC10EA68806A1211A8A083F7B9705431DF1

Published artifacts:

    provider/authorities/ESP_LOCAL_008_AUTH_X2_REQUEST.json
    provider/authorities/ESP_LOCAL_008_AUTH_X2.txt

Final scored use:

    signed target: Servo1
    presented to:  Servo2
    result:        target_id_mismatch

## AUTH-Y2 Lineage

AUTH-Y2:

    device_id: esp32-xiao-servo-02
    context:   esp_local_008
    action:    move_servo
    max_uses:  1
    nonce:     71886edad817176a2dca4b8a8bf70fa3

Canonical authority:

    {"action":"move_servo","context":"esp_local_008","device_id":"esp32-xiao-servo-02","max_uses":1,"nonce":"71886edad817176a2dca4b8a8bf70fa3"}

Authority ID:

    3ba6239d703d5ba203be2069f1c4c3fc89c27e63cff0b59be6977883ca654519

Request SHA-256:

    E46A3420468A54FEBAE66203131F0CA36B3B89E0E79F3BBF5CC9A4121A08A3E8

Generation-record SHA-256:

    A182D7F9712B831A7712C788EBC9C25030C0329742382C503010C2D7BC9B5E26

Published artifacts:

    provider/authorities/ESP_LOCAL_008_AUTH_Y2_REQUEST.json
    provider/authorities/ESP_LOCAL_008_AUTH_Y2.txt

Final scored use:

    signed target: Servo2
    presented to:  Servo2
    result:        accepted / executed

## AUTH-X3 Lineage

AUTH-X3:

    device_id: esp32-xiao-servo-01
    context:   esp_local_008
    action:    move_servo
    max_uses:  1
    nonce:     86062287c3d8be01446bf80ec69131bf

Canonical authority:

    {"action":"move_servo","context":"esp_local_008","device_id":"esp32-xiao-servo-01","max_uses":1,"nonce":"86062287c3d8be01446bf80ec69131bf"}

Authority ID:

    5222af8445ee67ba8712f2469c91449a841c777cb40b9395d22c9bb1f30388ef

Request SHA-256:

    809298A745EF0D8D54310E37D94D377508EDBD8A3BF9F9A22ECA09BD1D516C67

Generation-record SHA-256:

    7EEDB1855CE27BDC8784DABE0CB7FF9EAC1C38A4A23F46C0F268BE38DAD1883E

Published artifacts:

    provider/authorities/ESP_LOCAL_008_AUTH_X3_REQUEST.json
    provider/authorities/ESP_LOCAL_008_AUTH_X3.txt

Final scored use:

    signed target: Servo1
    presented to:  Servo1
    result:        accepted / executed

AUTH-X3 replaced the earlier X2 Servo1 positive run for the final independently witnessed Servo1 physical-signal criterion.

## AUTH-Y3 Lineage

AUTH-Y3:

    device_id: esp32-xiao-servo-02
    context:   esp_local_008
    action:    move_servo
    max_uses:  1
    nonce:     045c3bbf278c91bfe2605cacb5bca37d

Canonical authority:

    {"action":"move_servo","context":"esp_local_008","device_id":"esp32-xiao-servo-02","max_uses":1,"nonce":"045c3bbf278c91bfe2605cacb5bca37d"}

Authority ID:

    2c7ded33c6d5cc142c6f4ba91c04add1803fc361d00f34b9d288b3bb67f711fa

Request SHA-256:

    87607234070D39EE414CE51FE839D61A822FB1BC012C69F8FDE3D2C895052C43

Generation-record SHA-256:

    D5872E0956B327A84EE465E595BEB28BD0BE33D987DF1E2F188A510E9FE0B014

Published artifacts:

    provider/authorities/ESP_LOCAL_008_AUTH_Y3_REQUEST.json
    provider/authorities/ESP_LOCAL_008_AUTH_Y3.txt

Final scored use:

    signed target: Servo2
    presented to:  Servo1
    result:        target_id_mismatch

AUTH-Y3 replaced the earlier Y2 Servo1 wrong-target run for the final independently witnessed Servo1 zero-signal criterion.

## Endpoint Runtime Lineage

Published endpoint source:

    firmware/endpoint-runtime/project/main/ESP_LOCAL_008_ENDPOINT.c

The runtime extends the preceding endpoint enforcement path with an explicit target-binding gate.

Evaluation order:

1. Receive the request.
2. Decode the authority and signature.
3. Verify the provider Ed25519 signature.
4. Verify semantic admissibility.
5. Compare the signed target with the local endpoint identity.
6. Reject a mismatch with `target_id_mismatch`.
7. For a matching target, compute the SHA-256 authority binding.
8. Validate persistent authority state.
9. Require an exact authority-ID match.
10. Require UNSPENT state.
11. Durably consume the authority.
12. Verify SPENT through a fresh reread.
13. Issue the PWM command.

The target-binding gate precedes persistent authority-state access.

## Endpoint Build Selector Lineage

The endpoint source uses `ENDPOINT_INSTANCE` to create the two endpoint builds.

| Instance | Endpoint Identity | Endpoint PWM GPIO |
|---|---|---|
| 1 | `esp32-xiao-servo-01` | 5 |
| 2 | `esp32-xiao-servo-02` | 5 |

The publication contains one selector-based source file.

The published source snapshot selects instance 1.

The scored Servo2 build used the same implementation with instance 2 selected.

Recorded test-time source-configuration SHA-256 values:

    Servo1 / instance 1:
    873A15DB09DF51D4A8BF430DF5C11AE51CFCFC31DAEFDA7BFF4A8F27D6DCEED3

    Servo2 / instance 2:
    DECB8F04A4B7B36CC3366D7302F41E7F76B9F81217548C925CED443FA65CCA0E

These hashes identify test-time source configurations. They are not represented as hashes of two separately published source files.

## Tested Endpoint Binary Identities

Recorded Servo1 corrected runtime binary SHA-256:

    C743FBE3D03BF3267B3BDFE9BD84FFE5D31E5335875F4FFADDD39E705E7A6A7E

Recorded Servo2 corrected runtime binary SHA-256:

    8CEB6B65C08885173C007D859AEE9F134F6DC97FF2E55518A811AB9E1FC88EE0

The firmware tree publishes source and ESP-IDF project material.

These scored application binaries are identified by hash but are not included in the published firmware directory.

A later rebuild is a reproduction artifact unless its SHA-256 exactly matches the recorded tested binary.

## Endpoint GPIO Configuration

Pre-scored validation identified an incorrect Servo #2 actuator GPIO mapping. It was corrected before scored execution.

Final scored endpoint configuration:

    Servo1 endpoint PWM GPIO: 5
    Servo2 endpoint PWM GPIO: 5

No final scored result depends on the incorrect pre-score mapping.

## Persistent-State Format

ESP-LOCAL-008 uses the dedicated `nuvl_state` NVS partition.

Resolved partition parameters:

    offset: 0x110000
    size:   0x6000
    length: 24576 bytes

Namespace:

    nuvl_auth

Key:

    state

Record format:

    magic
    version
    state
    reserved
    authority_id[32]
    crc32

Record size:

    44 bytes

State values:

    UNSPENT = 1
    SPENT   = 2

The authority ID is the SHA-256 identifier of the provider-signed canonical authority.

## Provisioner Lineage

Published provisioner source:

    firmware/provisioner/project/main/ESP_LOCAL_008_PROVISIONER.c

The provisioner:

- refuses to silently overwrite existing authority state;
- writes one UNSPENT authority record;
- commits the NVS update;
- deinitializes and reinitializes the partition;
- rereads the record;
- validates structure, authority ID, CRC, and state;
- emits PASS only after durable UNSPENT verification.

Final instance definitions:

    instance 1:
      endpoint:  esp32-xiao-servo-01
      authority: AUTH-X3
      authority_id:
      5222af8445ee67ba8712f2469c91449a841c777cb40b9395d22c9bb1f30388ef

    instance 2:
      endpoint:  esp32-xiao-servo-02
      authority: AUTH-Y2
      authority_id:
      3ba6239d703d5ba203be2069f1c4c3fc89c27e63cff0b59be6977883ca654519

Recorded final X3 provisioner source-configuration SHA-256:

    1917B7CBCB872DE0C1AB9270668B2E6A26F03FCFDCE4925456BD416E6D5A9CAC

Recorded final X3 provisioner binary SHA-256:

    FF68964B8156BEAFAED632B9F6AB4738048CF66EAA07CBA8F466E21E34F29CFC

Recorded binary size:

    191600 bytes

The tested provisioner binary is identified by hash but is not included in the published firmware tree.

## Servo1 X3 State Lineage

After AUTH-X3 provisioning and restoration of the endpoint runtime, Servo1 state was captured as:

    evidence/state/SERVO1_X3_STATE_CHECK.bin

Recorded SHA-256:

    588C34697B132DF7B82E79BC6A06A2DD973938A446AEFF199726CA5F0F4BEF36

The X3 authority was UNSPENT.

After `X3_S1_ACCEPT_001`, the state was captured as:

    evidence/state/SERVO1_X3_AFTER_ACCEPT.bin

Recorded SHA-256:

    F2193B58041E1BFAFB2DB2A97463C4833AA2EAE196F84102DAB3A26DF6144873

The raw post-accept NVS image contains the earlier UNSPENT record and a later SPENT record for the same authority ID, consistent with NVS append/update behavior.

The latest valid authority record establishes the final SPENT state.

## Servo1 Y3 Wrong-Target State Lineage

Immediately before `Y3_S1_DENY_001`:

    evidence/state/SERVO1_PRE_Y3_DENY.bin

Immediately after `Y3_S1_DENY_001`:

    evidence/state/SERVO1_POST_Y3_DENY.bin

Both files have the recorded SHA-256:

    F2193B58041E1BFAFB2DB2A97463C4833AA2EAE196F84102DAB3A26DF6144873

The files are byte-identical.

The wrong-target Y3 presentation therefore did not alter Servo1's persistent authority-state partition.

## Servo2 X2 Wrong-Target State Lineage

Servo2 held AUTH-Y2 as its local authority state when the Servo1-scoped AUTH-X2 request was presented.

After `X2_S2_DENY_001`:

    evidence/state/SERVO2_Y2_AFTER_X2_S2_DENY.bin

Recorded SHA-256:

    3CF11DBE7EA19F45E6194451AB2D5B1C94627FAAD6574A9BB566D7BEFC562E76

This matched the recorded Servo2/Y2 pre-denial state.

The pre-denial comparison is recorded in the test provenance; a separately named pre-denial Servo2/Y2 image is not included in the published state directory.

The recorded comparison, endpoint target-gate trace, and subsequent Y2 acceptance support the conclusion that the wrong-target X2 request did not consume Servo2's legitimate Y2 authority.

## Servo2 Y2 Positive State Lineage

After `Y2_S2_ACCEPT_001`:

    evidence/state/SERVO2_Y2_AFTER_ACCEPT.bin

Recorded SHA-256:

    A443EE0C0DEB23DE73A4F08F3A6BE20C5231DCFF131AE4A026C1A3D4DBF1C29B

The endpoint trace records durable consumption before PWM execution.

The post-accept state differs from the recorded Y2 UNSPENT baseline.

## Coordinator / Presenter Lineage

Primary presenter source:

    coordinator/esp_local_008_presenter.py

The presenter:

- selects one frozen authority;
- selects one target endpoint;
- reads exact frozen request bytes;
- recomputes the authority ID;
- checks it against the expected frozen ID;
- requires explicit live-mode confirmation;
- controls the witness bracket;
- sends one request;
- records endpoint response and timing;
- records witness status;
- emits machine-readable JSON evidence.

Final recorded test-time presenter source SHA-256:

    7C6D164607F6FF1FC126ED577E7ACE511CC0482C6E7EFD0DB00B6E54924E67A0

This hash identifies the exact test-time presenter source, not the current publication copy.

## Publication-Tree Authority Path

Frozen authority artifacts are published under:

    provider/authorities/

The published presenter resolves its frozen request files from this directory.

During testing, the authority files were located beside the provider script, and the test-time presenter resolved them from:

    provider/

The published presenter uses the repository layout. It is a publication derivative of the test-time presenter and does not inherit the test-time source hash.

The frozen requests and recorded test results retain their own identities independently of the presenter's publication path.

## Historical X/Y Source Commentary

Several source files retain comments from the original X/Y planning stage:

    coordinator/esp_local_008_presenter.py
    provider/esp_local_008_provider.py
    firmware/endpoint-runtime/project/main/ESP_LOCAL_008_ENDPOINT.c
    firmware/provisioner/project/main/ESP_LOCAL_008_PROVISIONER.c

The executable configurations were subsequently extended to X2/Y2/X3/Y3.

The final scored matrix is defined by AUTH-X2, AUTH-Y2, AUTH-X3, AUTH-Y3, and their corresponding final evidence artifacts.

Historical comments are not the authoritative description of the final scored matrix.

## Independent Witness Lineage

Published witness implementation:

    witness/ESP_LOCAL_008_WITNESS_RMT_V1/

Primary source:

    witness/ESP_LOCAL_008_WITNESS_RMT_V1/main/witness_rmt_v1.c

The witness is an ESP-IDF RMT RX implementation derived from the independent witness used during ESP-LOCAL-007.

Witness identity:

    esp32-witness-007

The retained identity reflects device and implementation lineage.

The witness has:

    authority_role:     NONE
    authorization_role: NONE

It observes the electrical servo-control line only.

## Witness Capture Configuration

| Parameter | Value |
|---|---|
| Capture engine | RMT RX |
| Resolution | 1 MHz |
| Servo-valid pulse width | 1500–2500 us |
| Servo-valid period | 15000–25000 us |
| Burst-gap threshold | 100000 us |
| RMT receive buffer | 256 symbols |
| Capture queue depth | 4 |

Scored runs required zero capture-overflow, truncation, and error increments.

## Witness GPIO Build Lineage

The final matrix required two physical input configurations:

| Cases | Witness Input |
|---|---|
| Servo2 cases | GPIO4 |
| Servo1 cases | GPIO5 |

The published source snapshot selects:

    WITNESS_GPIO = GPIO_NUM_5

This corresponds to the final Servo1 configuration.

The GPIO4 scored cases used the same witness implementation with `WITNESS_GPIO` set to GPIO4.

Recorded scored GPIO4 witness application SHA-256:

    DE68A458A8B80FA6A27904F8DEFBAEC755C74981E2B3706AF441ED98E98183B2

Recorded GPIO5 source-configuration SHA-256:

    FE1BBA2C8B15D437FF7BFAF255A77CC3EFDE085B47F79689473C3A953832EE42

Recorded GPIO5 witness application SHA-256:

    8F90F1695650602C844404E0A5417F39F5C2B5E469EB91333EC490A7BC386BFD

The publication contains one selector state in source form while retaining hashes for the scored GPIO variants.

## Witness Storage Lineage

The witness stores evidence in a dedicated SPIFFS partition:

    label:  evidence
    offset: 0x200000
    size:   0x400000

Equivalent size:

    4 MiB

The witness creates session files, per-run files, and per-run SHA-256 sidecars.

STOP computes the SHA-256 of the completed run file and returns the digest to the presenter.

## X2_S2_DENY_001 Witness Lineage

Witness configuration:

    GPIO4

Observed:

    pulse_seq before: 0
    pulse_seq after:  0
    burst_seq before: 0
    burst_seq after:  0

Capture faults:

    overflows:   0
    truncations: 0
    errors:      0

Witness-computed run-file SHA-256:

    ffa3a7b598e55d871b1114dc77123e5e2674cafeec2ef858f89a2a595ce0b4a6

The wrong-target presentation produced no observed Servo2 control burst.

## Y2_S2_ACCEPT_001 Witness Lineage

Witness configuration:

    GPIO4

Observed:

    pulse_seq before: 0
    pulse_seq after:  49
    burst_seq before: 0
    burst_seq after:  1

Capture faults:

    overflows:   0
    truncations: 0
    errors:      0

Witness-computed run-file SHA-256:

    1756bacf8d53c0336137f78876e91a0f42a3d204441850c6c7263bf47447930b

The correctly targeted Servo2 authority produced one observed servo-like control burst.

## X3_S1_ACCEPT_001 Witness Lineage

Witness configuration:

    GPIO5

Observed:

    pulse_seq before: 0
    pulse_seq after:  49
    burst_seq before: 0
    burst_seq after:  1

Capture faults:

    overflows:   0
    truncations: 0
    errors:      0

Witness-computed run-file SHA-256:

    1b7247e7f4639556b66a3db3f14c4054229cd724dfb180107f1b7b645124021d

The correctly targeted Servo1 authority produced one observed servo-like control burst.

## Y3_S1_DENY_001 Witness Lineage

Witness configuration:

    GPIO5

Observed:

    pulse_seq before: 0
    pulse_seq after:  0
    burst_seq before: 0
    burst_seq after:  0

Capture faults:

    overflows:   0
    truncations: 0
    errors:      0

Witness-computed run-file SHA-256:

    8c1f95aa2acaec4c97cace8461892cab3c737e4651c134946a3ec9452694adeb

The wrong-target presentation produced no observed Servo1 control burst.

## Witness Partition Images

Published raw witness partition images are retained under:

    evidence/witness-images/

Post-Servo2 matrix image:

    ESP_LOCAL_008_WITNESS_AFTER_Y2_PASS.bin

Recorded SHA-256:

    BC1DC3B46758BAA7AE470F10557F638AB43584DBA191D410D978ADDC4D0935D1

Post-X3 image:

    ESP_LOCAL_008_WITNESS_AFTER_X3_PASS.bin

Recorded SHA-256:

    393FC673A41E9E99F0B7FE7994B818D04FBB551D151361B448415EF3745CECF1

Post-Y3-denial image:

    ESP_LOCAL_008_WITNESS_AFTER_Y3_DENY.bin

Recorded SHA-256:

    28AF6266B49C6C56605C91DC437D7886474AB663875A5143195FA82F7A500458

A pre-score witness evidence-partition image is also retained as:

    evidence/witness-images/ESP_LOCAL_008_WITNESS_EVIDENCE_PRE_SCORE.bin

These are raw partition images rather than reconstructed summaries.

## Final Presenter Evidence

Final machine-readable presenter records:

    evidence/final/ESP_LOCAL_008_PRESENTER_X2_S2_DENY_001_1790729436.json
    evidence/final/ESP_LOCAL_008_PRESENTER_Y2_S2_ACCEPT_001_1790730312.json
    evidence/final/ESP_LOCAL_008_PRESENTER_X3_S1_ACCEPT_001_1790732953.json
    evidence/final/ESP_LOCAL_008_PRESENTER_Y3_S1_DENY_001_1790733844.json

These records preserve:

    authority label
    authority ID
    target identity
    target address
    expected verdict
    endpoint response
    presenter scoring result
    timing
    witness pre-status
    witness START result
    witness STOP result
    witness post-status

## Final Endpoint Serial Evidence

Canonical final endpoint logs:

    evidence/final/ESP_LOCAL_008_X2_S2_DENY_001_ENDPOINT.log
    evidence/final/ESP_LOCAL_008_Y2_S2_ACCEPT_001_ENDPOINT.log
    evidence/final/ESP_LOCAL_008_X3_S1_ACCEPT_001_ENDPOINT.log
    evidence/final/ESP_LOCAL_008_Y3_S1_DENY_001_ENDPOINT.log

Wrong-target logs record:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_DENY_TARGET_ID_MISMATCH

Correct-target logs record:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_TARGET_ID_MATCH
    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

The files under `evidence/final/` are the canonical serial records for the final matrix.

## Y3_S1_DENY_001 Scoring Metadata Caveat

The `Y3_S1_DENY_001` presenter invocation supplied:

    --expect denied

The endpoint returned:

    status: denied
    reason: target_id_mismatch

The presenter scores denial expectations against the specific reason string.

The resulting JSON therefore records:

    scored_match: false

This is retained unchanged.

The endpoint behavior itself satisfied the target-binding condition.

Independent corroboration includes:

    valid signature marker
    semantic-admissibility marker
    explicit target-id mismatch
    unchanged pre/post persistent state
    zero target-line pulses
    zero target-line bursts
    zero capture faults

The runner metadata mismatch is documented separately from the DUT result.

## Superseded Y2_S1_DENY_001 Lineage

Published under:

    evidence/superseded/

Presenter artifact:

    ESP_LOCAL_008_PRESENTER_Y2_S1_DENY_001_1790729623.json

Endpoint artifact:

    ESP_LOCAL_008_Y2_S1_DENY_001_ENDPOINT.log

Observed endpoint result:

    denied
    target_id_mismatch

Presenter scoring:

    scored_match: true

The witness was configured on GPIO4 while Servo1 was physically connected to witness GPIO5.

The endpoint and persistent-state evidence are retained, but the physical zero-signal result is not used for the final Servo1 claim.

This run was superseded by:

    Y3_S1_DENY_001

## Superseded X2_S1_ACCEPT_001 Lineage

Published under:

    evidence/superseded/

Presenter artifact:

    ESP_LOCAL_008_PRESENTER_X2_S1_ACCEPT_001_1790729763.json

Endpoint artifact:

    ESP_LOCAL_008_X2_S1_ACCEPT_001_ENDPOINT.log

Observed endpoint result:

    accepted
    executed

Presenter scoring:

    scored_match: true

The endpoint log records target match, durable consumption, PWM command, and acceptance.

The witness was configured on GPIO4 while Servo1 was physically connected to witness GPIO5.

The endpoint evidence is retained, but the physical witness criterion is not satisfied by that run.

This run was superseded by:

    X3_S1_ACCEPT_001

## Y3_S1_DENY_002 Control Lineage

Published under:

    evidence/controls/

Presenter artifact:

    ESP_LOCAL_008_PRESENTER_Y3_S1_DENY_002_1790734167.json

Endpoint log placeholder:

    ESP_LOCAL_008_Y3_S1_DENY_002_ENDPOINT.log

Filename timestamp:

    2026-09-30 02:09:27 UTC
    2026-09-29 22:09:27 -04:00

Presenter result:

    expected:     target_id_mismatch
    status:       denied
    reason:       target_id_mismatch
    scored_match: true

Witness START returned:

    ok: false
    detail: run_already_active

Witness STOP digest:

    903bd1651b3ffba0854f63f3f35eed7fbbb9763c9fa670d415e3678f0510fdde

The endpoint serial log was not successfully captured. The published placeholder contains one newline and no serial evidence.

The run is retained as a runner/control artifact and is excluded from the final scored matrix.

## Evidence Chain

The final wrong-target result combines:

1. Frozen provider authority identifying the intended endpoint.
2. Presenter records identifying the endpoint actually contacted.
3. Endpoint signature-valid and semantic-admissibility markers.
4. Explicit `target_id_mismatch` rejection.
5. No progression into the successful authority-state or PWM path.
6. Persistent-state comparisons supporting non-modification.
7. Zero control-signal pulses and bursts on the correct witness line.

The final correct-target result combines:

1. Frozen provider authority identifying the intended endpoint.
2. Presenter records identifying the matching endpoint.
3. Endpoint signature-valid and semantic-admissibility markers.
4. Explicit target match.
5. Valid UNSPENT authority state.
6. Durable SPENT reread before PWM.
7. Endpoint PWM and accepted/executed markers.
8. One independent target-line control-signal burst.

## Source / Artifact Classification

| Artifact class | Classification | Purpose |
|---|---|---|
| `provider/esp_local_008_provider.py` | Provider-generation source | Creates signed target-scoped authority |
| `provider/authorities/*.txt` | Original provider-generated artifact | Human-readable frozen authority record |
| `provider/authorities/*_REQUEST.json` | Original provider-generated artifact | Exact signed request envelope |
| `coordinator/esp_local_008_presenter.py` | Publication derivative of test presenter source | One-request presentation and evidence collection using the publication directory layout |
| `firmware/endpoint-runtime/project/main/ESP_LOCAL_008_ENDPOINT.c` | Endpoint implementation | Target binding and bounded-authority enforcement |
| `firmware/provisioner/project/main/ESP_LOCAL_008_PROVISIONER.c` | Provisioner implementation | Establishes one durable UNSPENT authority |
| `firmware/**/partitions.csv` | Build material | Persistent-state partition definition |
| `firmware/**/sdkconfig` | Build material | ESP-IDF configuration |
| `firmware/endpoint-runtime/project/components/monocypher/*` | Cryptographic dependency source | Ed25519 verification support |
| `witness/ESP_LOCAL_008_WITNESS_RMT_V1/*` | Independent witness implementation | Physical control-signal observation |
| `evidence/final/*.json` | Original test-time machine-readable evidence | Presenter result and witness bracket |
| `evidence/final/*_ENDPOINT.log` | Published serial evidence | Endpoint enforcement sequence |
| `evidence/state/*.bin` | Original raw binary evidence | Endpoint persistent-state partition captures |
| `evidence/witness-images/*.bin` | Original raw binary evidence | Witness SPIFFS evidence-partition captures |
| `evidence/superseded/*` | Retained non-final evidence | Earlier runs replaced for physical witness correctness |
| `evidence/controls/*` | Retained control/debug artifacts | Non-scored runner/control condition and serial-log placeholder |
| `*.md` | Publication documentation | Test description, interpretation, and provenance |
| `SHA256SUMS.txt` | Published-file checksum manifest | Byte-level verification of listed publication files |

## Credential-Bearing Configuration

The endpoint source includes:

    local_wifi_config.h

The witness source includes:

    witness_wifi_config.h

Real lab Wi-Fi credentials are local configuration and are not part of the authority property.

Credential-bearing local configuration files are not required as scored authority evidence.

The firmware and witness READMEs describe the local configuration interfaces needed for reproduction.

A sanitized reproduction configuration has its own identity and must not be assigned the SHA-256 of an original credential-bearing file.

## Tested Binary Relationship

Recorded tested application binary hashes identify the exact bench artifacts used during scored execution.

Where the corresponding binary is not published, the hash remains an identity record for that tested artifact. It does not provide the binary itself for independent inspection.

A rebuild from the published source:

- may contain different Wi-Fi credentials;
- may contain different build metadata;
- may use a different ESP-IDF build environment;
- may produce a different binary hash.

Such a rebuild is a reproduction artifact unless it exactly matches the recorded tested binary SHA-256.

## Publication and Hash Identities

Test-time hashes and published-file hashes serve different purposes.

The test-time hashes in this document identify the recorded bench artifacts.

`SHA256SUMS.txt` is the checksum manifest for the files listed in the publication package. Its entries are evaluated against the exact published bytes.

A publication source file or rebuilt binary does not inherit a historical test-time hash merely because its intended behavior is equivalent.

Text line endings also affect byte-level hashes. Equality of text after line-ending normalization is not byte-for-byte equality.

A checksum match establishes agreement with the listed digest. It does not independently establish that the file was executed during the bench test.

## Scored Evidence Preservation

The following evidence categories are retained for the test record:

    provider frozen request artifacts
    provider authority records
    final presenter JSON records
    final endpoint serial logs
    raw endpoint state images
    raw witness evidence-partition images
    superseded-run evidence
    control-run evidence

Evidence contents must not be rewritten to change a recorded result.

Errors or limitations present in the original evidence are interpreted explicitly.

The `Y3_S1_DENY_001` presenter scoring mismatch is one such retained condition.

The `Y3_S1_DENY_002` witness-control condition and absent serial capture are another.

## Interpretation Boundaries

A valid provider signature alone does not establish correct target binding.

A TCP denial alone does not establish that denial occurred before persistent-state access.

A TCP acceptance alone does not establish durable consumption or physical execution.

A changed raw NVS partition hash alone does not establish the meaning of the state transition.

An unchanged raw partition image is strong evidence of byte-level non-modification but does not replace the endpoint execution trace.

A recorded baseline comparison is distinct from publishing both images for an independent byte-level comparison.

A witness zero-signal result is meaningful only when capture health is valid and the correct physical signal line is monitored.

A witness servo-like burst establishes an electrical control-signal observation, not guaranteed mechanical movement.

Historical source comments do not supersede final machine-readable evidence.

Superseded runs are not promoted into the final physical-witness matrix.

Control artifacts are not scored as final results.

## Known Limitations

ESP-LOCAL-008 establishes the tested signed target-binding property in the recorded two-endpoint configuration.

It does not independently establish resistance to:

    trusted provider private-key compromise
    complete endpoint firmware compromise
    rollback of persistent storage
    physical tampering with endpoint storage
    denial of service
    hostile network routing
    absence of trusted time
    arbitrary endpoint cloning

It also does not independently rerun all properties previously tested in the ESP-LOCAL series:

    replay and reboot persistence
    power-loss persistence
    malformed-state behavior
    crash-window behavior
    hostile-relay mutation
    wrong-provider-key rejection
    concurrent-requester contention

ESP-LOCAL-008 relies on its own evidence only for signed target directionality and the associated positive control paths.

## Result Provenance Boundary

The final result is supported by agreement between provider scope, presenter records, endpoint enforcement traces, persistent-state evidence, and independent physical-witness observations.

For wrong-target cases, the retained evidence supports rejection of provider-signed authority at the unintended endpoint before the PWM command boundary.

For correct-target cases, the retained evidence supports acceptance by the intended endpoint, durable consumption before execution, and one independently observed electrical control-signal burst.

The experiment does not claim provenance beyond the recorded artifacts, hashes, configuration, and evidence relationships documented in the ESP-LOCAL-008 package.
