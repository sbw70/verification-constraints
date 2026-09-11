import base64
import json
import secrets
from pathlib import Path

from cryptography.hazmat.primitives import serialization


BASE_DIR = Path(__file__).resolve().parent

PRIVATE_KEY_PATH = (
    BASE_DIR
    / "keys"
    / "esp_local_004_private.pem"
)

PUBLIC_KEY_PATH = (
    BASE_DIR
    / "keys"
    / "esp_local_004_public.pem"
)


def canonical_authority(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


with PRIVATE_KEY_PATH.open("rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,
    )

with PUBLIC_KEY_PATH.open("rb") as f:
    public_key = serialization.load_pem_public_key(
        f.read()
    )


authority = {
    "device_id": "esp32-xiao-servo-01",
    "context": "esp_local_004",
    "action": "move_servo",
    "nonce": secrets.token_hex(16),
    "max_uses": 1,
}

canonical = canonical_authority(authority)

signature = private_key.sign(canonical)

public_raw = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw,
)


print("ESP_LOCAL_004_PROVIDER")
print()

print("AUTHORITY_OBJECT")
print(
    json.dumps(
        authority,
        separators=(",", ":"),
    )
)

print()

print("CANONICAL")
print(canonical.decode("utf-8"))

print()

print("SIGNATURE_BASE64")
print(
    base64.b64encode(signature).decode("ascii")
)

print()

print("PUBLIC_KEY_HEX")
print(public_raw.hex())

print()

print("PUBLIC_KEY_LENGTH")
print(len(public_raw))

print()

print("SIGNATURE_LENGTH")
print(len(signature))
