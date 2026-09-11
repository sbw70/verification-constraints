import hashlib
import json
import secrets

authority = {
    "device_id": "esp32-xiao-servo-01",
    "context": "esp_local_003",
    "action": "move_servo",
    "nonce": secrets.token_hex(16),
    "max_uses": 1,
}

canonical = json.dumps(
    authority,
    sort_keys=True,
    separators=(",", ":"),
)

commitment = hashlib.sha256(
    canonical.encode("utf-8")
).hexdigest()

print("AUTHORITY_OBJECT")
print(json.dumps(authority, separators=(",", ":")))

print()
print("CANONICAL")
print(canonical)

print()
print("COMMITMENT")
print(commitment)
