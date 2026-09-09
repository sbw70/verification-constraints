import hashlib
import json
import secrets

DEVICE_ID = "esp32-xiao-servo-01"
CONTEXT = "esp_local_002"
ACTION = "move_servo"


def sha256_hex(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


capability = secrets.token_hex(32)
commitment = sha256_hex(capability)

request = {
    "device_id": DEVICE_ID,
    "context": CONTEXT,
    "action": ACTION,
    "capability": capability,
}

print("ESP_LOCAL_002_PROVIDER")
print()
print("CAPABILITY:")
print(capability)
print()
print("COMMITMENT_FOR_ENDPOINT:")
print(commitment)
print()
print("VALID_REQUEST:")
print(json.dumps(request, separators=(",", ":")))
