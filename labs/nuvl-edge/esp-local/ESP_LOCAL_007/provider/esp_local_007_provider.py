import base64
import hashlib
import json
import secrets
from pathlib import Path

from cryptography.hazmat.primitives import serialization


TEST_ID = "ESP_LOCAL_007"
AUTHORITY_LABEL = "AUTH2"

DEVICE_ID = "esp32-xiao-servo-02"

# Intentional:
# ESP_LOCAL_007 reuses the tested ESP_LOCAL_006 endpoint runtime
# unchanged so that coordinated contention is the only new variable.
CONTEXT = "esp_local_006"

ACTION = "move_servo"
MAX_USES = 1

EXPECTED_PRIVATE_SHA256 = (
    "DA0A36F274EFC6E3CE1C7643800B952B1AA2895201E5A6D6852D308729466509"
)

EXPECTED_PUBLIC_RAW_HEX = (
    "48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1"
)


BASE_DIR = Path(__file__).resolve().parent
ESP_ROOT = BASE_DIR.parent.parent

PRIVATE_KEY_PATH = (
    ESP_ROOT
    / "ESP_LOCAL_004"
    / "provider"
    / "keys"
    / "esp_local_004_private.pem"
)

PUBLIC_KEY_PATH = (
    ESP_ROOT
    / "ESP_LOCAL_004"
    / "provider"
    / "keys"
    / "esp_local_004_public.pem"
)

REQUEST_PATH = (
    BASE_DIR
    / "ESP_LOCAL_007_AUTH2_REQUEST.json"
)

RECORD_PATH = (
    BASE_DIR
    / "ESP_LOCAL_007_AUTH2.txt"
)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            block = f.read(65536)

            if not block:
                break

            h.update(block)

    return h.hexdigest()


def canonical_authority(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


for output_path in (
    REQUEST_PATH,
    RECORD_PATH,
):
    if output_path.exists():
        raise SystemExit(
            "REFUSING TO OVERWRITE EXISTING AUTHORITY ARTIFACT: "
            + str(output_path)
        )


if not PRIVATE_KEY_PATH.exists():
    raise SystemExit(
        "TRUSTED PRIVATE KEY NOT FOUND: "
        + str(PRIVATE_KEY_PATH)
    )


if not PUBLIC_KEY_PATH.exists():
    raise SystemExit(
        "TRUSTED PUBLIC KEY NOT FOUND: "
        + str(PUBLIC_KEY_PATH)
    )


private_sha256 = sha256_file(
    PRIVATE_KEY_PATH
).upper()

if private_sha256 != EXPECTED_PRIVATE_SHA256:
    raise SystemExit(
        "TRUSTED PRIVATE KEY SHA256 MISMATCH: "
        + private_sha256
    )


with PRIVATE_KEY_PATH.open("rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,
    )


with PUBLIC_KEY_PATH.open("rb") as f:
    public_key = serialization.load_pem_public_key(
        f.read()
    )


private_public_raw = (
    private_key
    .public_key()
    .public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
)

public_raw = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw,
)


if private_public_raw != public_raw:
    raise SystemExit(
        "PRIVATE/PUBLIC KEYPAIR MISMATCH"
    )


public_raw_hex = public_raw.hex()

if public_raw_hex != EXPECTED_PUBLIC_RAW_HEX:
    raise SystemExit(
        "TRUSTED PUBLIC RAW KEY MISMATCH: "
        + public_raw_hex
    )


authority = {
    "device_id": DEVICE_ID,
    "context": CONTEXT,
    "action": ACTION,
    "nonce": secrets.token_hex(16),
    "max_uses": MAX_USES,
}


canonical = canonical_authority(
    authority
)

authority_id = sha256_bytes(
    canonical
)

signature = private_key.sign(
    canonical
)


request = {
    "authority_b64": base64.b64encode(
        canonical
    ).decode("ascii"),
    "signature_b64": base64.b64encode(
        signature
    ).decode("ascii"),
}


request_bytes = json.dumps(
    request,
    separators=(",", ":"),
).encode("utf-8")


record = "\n".join(
    [
        "ESP-LOCAL-007 AUTHORITY #2",
        "",
        "test_id=ESP_LOCAL_007",
        "endpoint_runtime=ESP_LOCAL_006",
        "runtime_reused_unchanged=true",
        "contention_variable_only=true",
        "device_id=" + DEVICE_ID,
        "context=" + CONTEXT,
        "action=" + ACTION,
        "max_uses=" + str(MAX_USES),
        "nonce=" + authority["nonce"],
        "canonical=" + canonical.decode("utf-8"),
        "authority_id_sha256=" + authority_id,
        "trusted_provider_public_raw="
        + public_raw_hex,
        "trusted_private_key_sha256="
        + private_sha256,
        "signature_b64="
        + request["signature_b64"],
        "",
    ]
).encode("utf-8")


REQUEST_PATH.write_bytes(
    request_bytes
)

RECORD_PATH.write_bytes(
    record
)


request_sha256 = sha256_bytes(
    request_bytes
)

record_sha256 = sha256_bytes(
    record
)


print("ESP_LOCAL_007_PROVIDER_GENERATED")
print()
print("TEST_ID=" + TEST_ID)
print("ENDPOINT_RUNTIME=ESP_LOCAL_006")
print("RUNTIME_REUSED_UNCHANGED=true")
print("DEVICE_ID=" + DEVICE_ID)
print("CONTEXT=" + CONTEXT)
print("ACTION=" + ACTION)
print("MAX_USES=" + str(MAX_USES))
print("NONCE=" + authority["nonce"])
print("AUTHORITY_ID_SHA256=" + authority_id)
print(
    "TRUSTED_PROVIDER_PUBLIC_RAW="
    + public_raw_hex
)
print(
    "TRUSTED_PRIVATE_KEY_SHA256="
    + private_sha256
)
print(
    "REQUEST_SHA256="
    + request_sha256
)
print(
    "RECORD_SHA256="
    + record_sha256
)
print()
print("REQUEST_FILE=" + str(REQUEST_PATH))
print("RECORD_FILE=" + str(RECORD_PATH))


