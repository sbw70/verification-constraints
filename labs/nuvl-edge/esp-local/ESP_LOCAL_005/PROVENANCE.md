# ESP-LOCAL-005 Provenance

## Purpose

This document records the origin, lineage, and relationship of the artifacts published for ESP-LOCAL-005.

It is intended to distinguish:

- original tested source,
- generated authority-specific variants,
- compiled binaries,
- independent witness material,
- provider key material,
- fault-injection artifacts,
- preserved persistent-state captures.

Observed behavior is documented in `RESULTS.md`.

Artifact integrity is documented in `SHA256SUMS.txt`.

## Test Lineage

ESP-LOCAL-005 extends the endpoint-local provider-signed authority model established in ESP-LOCAL-004.

ESP-LOCAL-004 established endpoint-local Ed25519 verification of provider-issued authority.

ESP-LOCAL-005 retained that provider-controlled authority model and added persistent endpoint-local authority consumption before physical command issuance.

The provider signing key used for ESP-LOCAL-005 was reused from the ESP-LOCAL-004 test environment.

No new provider signing identity was created specifically for ESP-LOCAL-005.

## Provider Key Lineage

The ESP-LOCAL-005 authority objects were signed using the Ed25519 test key originally used for ESP-LOCAL-004.

Original local source files:

```text
C:\Users\holiw\esp32-main\ESP_LOCAL_004\provider\keys\esp_local_004_private.pem
C:\Users\holiw\esp32-main\ESP_LOCAL_004\provider\keys\esp_local_004_public.pem
```

The corresponding raw Ed25519 public key was:

```text
48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1
```

The original private-key file SHA-256 was:

```text
DA0A36F274EFC6E3CE1C7643800B952B1AA2895201E5A6D6852D308729466509
```

The original public PEM SHA-256 was:

```text
B9B33C65DDA94C39D8E48A2C563F18A24B6B9B460280184F81882BFA5C97C7ED
```

For the ESP-LOCAL-005 publication tree, the same test-key material may be published under reproduction-oriented names:

```text
provider/TEST_ONLY_private.pem
provider/TEST_ONLY_public.pem
```

Renaming does not alter the underlying key bytes.

The keys are test material used to reproduce the authority-generation process. They do not protect an operational deployment.

## Cryptographic Implementation Lineage

The native ESP32-S3 verification path used Monocypher 4.0.3 for Ed25519 verification.

The tested Monocypher source files had the following SHA-256 values:

```text
monocypher.c
F1F838CDD483BDEBE0DF0FF5C5ED60535E496F769C6A2F933AC4C0B114207123

monocypher.h
FCAF6ED771358BB4F40FBA016F6518AE86EC02B1B877D2CC35AD92D3A26FD7B3

monocypher-ed25519.c
CE0D2F8E32CA8F66398BA5B3456CC74327C3EFF14E7B950CE7D57BE9025CC453

monocypher-ed25519.h
3A3035181F991A158D0E1C7567258F0BAE8BA0F1F23C5512B4A1DB1B3C9730CE
```

Before the persistent-authority runtime was exercised, a standalone native Ed25519 verification gate was built and tested.

Published artifacts:

```text
evidence/ESP_LOCAL_005_ED25519_GATE.c
evidence/ESP_LOCAL_005_ED25519_GATE.bin
```

Original tested source SHA-256:

```text
2CC65C5051FC492221C66CD7196FBE9101FD69FAB459FDDA6CEE015D3416C1FB
```

Original tested binary SHA-256:

```text
3CE6AC79B22BF53DEB18BDF43518E87D39652DCAC309615AA24A806F12770027
```

## Base Persistent-Authority Implementation

The original ESP-LOCAL-005 persistent-authority implementation consisted of an explicit provisioner and a normal runtime.

Published source:

```text
firmware/ESP_LOCAL_005_PROVISIONER.c
firmware/ESP_LOCAL_005_RUNTIME.c
```

The original provisioner source SHA-256 was:

```text
802278B9FBB7265268E9396F6E586A9B2EC9ADFA6F667FA1929C45835D9F2EE2
```

The original runtime source SHA-256 was:

```text
8937B71FFB91ED38B45CB4B8D9C6B29C43BF98A018B74969AB3F39F8B73E12B7
```

The preserved original runtime binary is published as:

```text
evidence/ESP_LOCAL_005_RUNTIME.bin
```

Original runtime binary SHA-256:

```text
9C24BC0DAB9B741E3FD99FF524E86CEEA3B3F26F983A250DDA08913498AEE93F
```

The original authority associated with this implementation was legitimately consumed during testing.

Its preserved persistent-state partition is published as:

```text
evidence/ESP_LOCAL_005_ORIGINAL_SPENT_NUVL_STATE.bin
```

SHA-256:

```text
A24F7B46C3F75860417935918FB510E852601086F5F0D3D599C23333DF926DB8
```

## Authority-Specific Variants

Fresh provider-issued authorities were generated as testing progressed.

Each authority-specific runtime retained the same authority model while replacing the frozen authority material with newly generated provider-signed material.

Previously consumed authorities were not reset and reused as fresh authorities.

### Authority #2

Published artifacts include:

```text
evidence/ESP_LOCAL_005_AUTH2.txt
evidence/ESP_LOCAL_005_AUTH2_PROVISIONER.c
evidence/ESP_LOCAL_005_AUTH2_PROVISIONER.bin
evidence/ESP_LOCAL_005_AUTH2_RUNTIME.c
evidence/ESP_LOCAL_005_AUTH2_RUNTIME.bin
evidence/ESP_LOCAL_005_AUTH2_SPENT_NUVL_STATE.bin
```

Authority #2 identifier:

```text
b93f1e0520e5334202fd48cc403f65a601ba3edb5f1538905d6237eb5fdff601
```

Known original artifact hashes include:

```text
ESP_LOCAL_005_AUTH2_PROVISIONER.c
D6E75688485DC0AAB965691F2018D5629A2BC39DA37C5E716FAE3034354B6EB2

ESP_LOCAL_005_AUTH2_RUNTIME.c
3074603FBFC34AD66C11BD15E1F775211FE40753193C0CD766C69E6DF2011143

ESP_LOCAL_005_AUTH2.txt
3289427DEA2E9C8452E56C0D88AFEE375F09A63309DADF34FE46D31E0E6A4AB6

ESP_LOCAL_005_AUTH2_RUNTIME.bin
6394375047CA0F325956B94FE85A3039A91C8238141E02FFC38CC6CCFE4C530C

ESP_LOCAL_005_AUTH2_SPENT_NUVL_STATE.bin
7AFC8DD95308A001BB8E936F7DC62967359A34DCAD02CE9DC953E299FED9B051
```

### Authority #3

Authority #3 was generated to pair an accepted execution with an independent physical-command witness.

Published artifacts include:

```text
evidence/ESP_LOCAL_005_AUTH3.txt
evidence/ESP_LOCAL_005_AUTH3_PROVISIONER.c
evidence/ESP_LOCAL_005_AUTH3_PROVISIONER.bin
evidence/ESP_LOCAL_005_AUTH3_RUNTIME.c
evidence/ESP_LOCAL_005_AUTH3_RUNTIME.bin
evidence/ESP_LOCAL_005_AUTH3_SPENT_NUVL_STATE.bin
witness/ESP_LOCAL_005_AUTH3_WITNESS_GPIO4.py
```

Authority #3 identifier:

```text
82accbc8b1099249dbf8c0cd438bee5be1d9f77533e5481889dff918a3e69c8d
```

Known original artifact hashes:

```text
ESP_LOCAL_005_AUTH3_PROVISIONER.c
62D9DE781CF6B9001D45C5BA4AB7B65269D48490AF81C006BC3B9E179AD0CB64

ESP_LOCAL_005_AUTH3_PROVISIONER.bin
2E061F72EFA99ADA86026EF1AC98177558870ABE301F59B6D0338C755B413064

ESP_LOCAL_005_AUTH3_RUNTIME.c
648B8CB0D02BC177DA1AC9E72CD12C77841BB4C806B393CB70043969BEEDE981

ESP_LOCAL_005_AUTH3_RUNTIME.bin
8FB830E957BF328EBC480A711A72B7FA7EC03C10A80387B183A6E7ED0AE52855

ESP_LOCAL_005_AUTH3.txt
5BFA1F79BD022652098685D1768724D8025EC2DB65297DCDB9D7B54571657F91

ESP_LOCAL_005_AUTH3_SPENT_NUVL_STATE.bin
1F5055E80405B9A23C15A7438F31DF8A2078DCEA96AA2839D89C0D711DA04130

ESP_LOCAL_005_AUTH3_WITNESS_GPIO4.py
5A142014A1E9C30CFADA77859462A9BB7C0500E0FEF00C8A73A3B2634DF83690
```

### Authority #4

Authority #4 was generated for the deliberate post-consumption / pre-PWM crash case.

Published artifacts include:

```text
evidence/ESP_LOCAL_005_AUTH4.txt
firmware/ESP_LOCAL_005_AUTH4_PROVISIONER.c
firmware/ESP_LOCAL_005_AUTH4_POSTCOMMIT_CRASH_RUNTIME.c
evidence/ESP_LOCAL_005_AUTH4_PROVISIONER.bin
evidence/ESP_LOCAL_005_AUTH4_POSTCOMMIT_CRASH_RUNTIME.bin
evidence/ESP_LOCAL_005_AUTH4_POSTCOMMIT_SPENT_NUVL_STATE.bin
```

Authority #4 identifier:

```text
8da20bacde390ef6fbf278dc84490529faaad24109f9ef53741bfb5f8ef0e86f
```

Known original artifact hashes:

```text
ESP_LOCAL_005_AUTH4_PROVISIONER.c
7507DCB8BC43728B1E3C0B636E900B181582EC55801C51303111938106408C5D

ESP_LOCAL_005_AUTH4_POSTCOMMIT_CRASH_RUNTIME.c
BB48479D81AF09A21ABD531A35B9D7C328B9510D7D25B528050FAEE01FA80549

ESP_LOCAL_005_AUTH4.txt
9FDB177373013C917EECE34AA82563127FF54C0D383A74C442050C103894CEE8

ESP_LOCAL_005_AUTH4_POSTCOMMIT_SPENT_NUVL_STATE.bin
B1A4A2A085901D9510EF491843C79989226B603CDA4763EBC5DA836F65327CAD
```

### Authority #5

Authority #5 was generated for the deliberate crash after the persistent state write and before the explicit `nvs_commit()` call.

Published artifacts include:

```text
evidence/ESP_LOCAL_005_AUTH5.txt
firmware/ESP_LOCAL_005_AUTH5_PROVISIONER.c
firmware/ESP_LOCAL_005_AUTH5_PRECOMMIT_CRASH_RUNTIME.c
evidence/ESP_LOCAL_005_AUTH5_PROVISIONER.bin
evidence/ESP_LOCAL_005_AUTH5_PRECOMMIT_CRASH_RUNTIME.bin
evidence/ESP_LOCAL_005_AUTH5_PRECOMMIT_RESULT_NUVL_STATE.bin
```

Authority #5 identifier:

```text
b0726ba4fd440577313bc91c966f20e384fa1daaa75b0a3e21b688d6039500b3
```

Known original artifact hashes:

```text
ESP_LOCAL_005_AUTH5_PROVISIONER.c
5E9A7F125BE5FCFDEFCE5FCE2E71377874F00471EED88EE7A832972EF6C8B766

ESP_LOCAL_005_AUTH5_PRECOMMIT_CRASH_RUNTIME.c
536ACCEF9E9B73892A2C28541D87AAC09E8176FB7162EB46D9275AAE627BF2DB

ESP_LOCAL_005_AUTH5.txt
55ED3AAC7373E3DE5A4B24E99111870D9730455482058E5522352B49CACAA442

ESP_LOCAL_005_AUTH5_PROVISIONER.bin
0B7BC67FC8E0C5C92941502767B7A20DF07CB3498AEA45D52F5D65453CB2A539

ESP_LOCAL_005_AUTH5_PRECOMMIT_CRASH_RUNTIME.bin
CC41356233BD3BD3D231AEA4346819D04FE2AC8E95EF3866292A6799D37374BF

ESP_LOCAL_005_AUTH5_PRECOMMIT_RESULT_NUVL_STATE.bin
99E1116DA54331EF368B795E9E4CCBDD3ABD4E9346EB4A602FAD25D18087FA2A
```

## Persistent-State Fault Artifacts

Separate fault-injection programs were used to create invalid persistent-state conditions without changing the normal runtime's startup-validation behavior.

### Corrupt-State Injector

Published artifacts:

```text
firmware/ESP_LOCAL_005_CORRUPT_STATE_INJECTOR.c
evidence/ESP_LOCAL_005_CORRUPT_STATE_INJECTOR.bin
evidence/ESP_LOCAL_005_CORRUPT_STATE_NUVL_STATE.bin
```

Known original hashes:

```text
ESP_LOCAL_005_CORRUPT_STATE_INJECTOR.c
6A68241BF2A8DC62841F4429D7A393281232C9FA6D6654404B76219B8D121640

ESP_LOCAL_005_CORRUPT_STATE_INJECTOR.bin
B48F2154289824602794D054638282FDECD2746F7744DA58C0753344890FBBA7

ESP_LOCAL_005_CORRUPT_STATE_NUVL_STATE.bin
3FA43D78B625CED71E2A48880E16630A2CB1E7D7CFECB4C029455E7B7D1E3835
```

### Truncated-State Injector

Published artifacts:

```text
firmware/ESP_LOCAL_005_TRUNCATED_STATE_INJECTOR.c
evidence/ESP_LOCAL_005_TRUNCATED_STATE_INJECTOR.bin
evidence/ESP_LOCAL_005_TRUNCATED_STATE_NUVL_STATE.bin
```

Known original hashes:

```text
ESP_LOCAL_005_TRUNCATED_STATE_INJECTOR.c
88062D4ED5D1D4D72F4BB82F30F237B824F97F0889D2E1824DBC2DF583A8DA67

ESP_LOCAL_005_TRUNCATED_STATE_INJECTOR.bin
CB2615793213E20573D81E2038A2B790053F3E1AF47223098642CBE323613174

ESP_LOCAL_005_TRUNCATED_STATE_NUVL_STATE.bin
4F50D0514690580218CCED282FA11CDE3D9720A8F372B8F2A35DBE6E132E102D
```

## Independent Witness Lineage

The independent witness was a separate ESP32-S3 DevKit running MicroPython.

The witness used for Servo #2 monitored GPIO4.

Published witness implementation:

```text
witness/ESP_LOCAL_005_AUTH3_WITNESS_GPIO4.py
```

The witness script was run temporarily and did not replace the witness board's stored reference firmware.

SHA-256:

```text
5A142014A1E9C30CFADA77859462A9BB7C0500E0FEF00C8A73A3B2634DF83690
```

The physical mapping established during testing was:

```text
Servo #1 / COM3  -> Witness GPIO5
Servo #2 / COM15 -> Witness GPIO4
```

ESP-LOCAL-005 used the Servo #2 / GPIO4 path.

## Persistent-State Capture Lineage

The preserved `NUVL_STATE` images are direct raw reads of the dedicated ESP32-S3 persistent-state partition.

Partition parameters:

```text
label:  nuvl_state
offset: 0x110000
length: 0x6000
size:   24576 bytes
```

Published captures:

```text
ESP_LOCAL_005_ORIGINAL_SPENT_NUVL_STATE.bin
ESP_LOCAL_005_AUTH2_SPENT_NUVL_STATE.bin
ESP_LOCAL_005_AUTH3_SPENT_NUVL_STATE.bin
ESP_LOCAL_005_CORRUPT_STATE_NUVL_STATE.bin
ESP_LOCAL_005_TRUNCATED_STATE_NUVL_STATE.bin
ESP_LOCAL_005_AUTH4_POSTCOMMIT_SPENT_NUVL_STATE.bin
ESP_LOCAL_005_AUTH5_PRECOMMIT_RESULT_NUVL_STATE.bin
```

These files are binary partition images and are not text transcripts.

They should be compared and verified as raw binary artifacts.

## Source, Binary, and State Relationships

The publication separates several artifact classes:

| Artifact class | Purpose |
|---|---|
| `.c` | Tested firmware, provisioner, gate, or fault-injection source |
| `.py` | Independent witness implementation |
| `.txt` | Frozen authority metadata |
| application `.bin` | Compiled ESP32-S3 application image |
| state `.bin` | Raw persistent-state partition capture |
| `.pem` | Test provider signing material |

Compiled binaries are retained separately from source because they represent the executable artifacts actually flashed during the test series.

Persistent-state images are retained separately because they preserve the storage state observed after specific test conditions.

## Publication Relationship

The published ESP-LOCAL-005 package is intended to preserve the tested artifacts rather than replace them with simplified reference implementations.

Where an artifact is published byte-for-byte from the tested local copy, `SHA256SUMS.txt` provides the verification hash for the published file.

Authority-specific files remain distinct because each contains different provider-issued authority material and represents a different test state.

Previously spent authority objects are retained as historical test artifacts and are not treated as fresh authorities for reproduction of later cases.

## Reproduction

Reproduction should preserve the distinction between:

- provider authority generation,
- explicit endpoint provisioning,
- normal endpoint runtime,
- fault-injection runtime,
- independent witness,
- persistent-state capture.

The individual source and metadata files identify the authority material used for each test case.

`RESULTS.md` records the observed outcomes.

`SHA256SUMS.txt` provides the integrity manifest for the published artifact set.
