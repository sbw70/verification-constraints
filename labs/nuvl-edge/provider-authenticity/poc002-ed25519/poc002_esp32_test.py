import gc
import json
import socket
import time

PI_IP = "192.168.8.234"
PORT = 8089

DEVICE_ID = "esp32-field-01"
GOOD_CONTEXT = "field_led_demo"

CASES = [
    ("valid_accept", "accept", GOOD_CONTEXT, "valid", "accepted", True),
    ("valid_deny", "deny", GOOD_CONTEXT, "valid", "denied", True),
    ("signed_stale", "accept", GOOD_CONTEXT, "stale", "denied", False),
    ("tampered_after_signing", "accept", GOOD_CONTEXT, "tampered", "denied", False),
    ("unsigned", "accept", GOOD_CONTEXT, "unsigned", "denied", False),
    ("wrong_context_request", "accept", "wrong_context", "valid", "denied", True),
    ("signed_context_mismatch", "accept", GOOD_CONTEXT, "context_mismatch", "denied", False),
    ("signed_nonce_mismatch", "accept", GOOD_CONTEXT, "nonce_mismatch", "denied", False),
]


def post_case(index, action, context, mode):
    payload = {
        "device_id": DEVICE_ID,
        "context": context,
        "requested_action": action,
        "nonce": "poc002-{:02d}-{}".format(index, time.ticks_ms()),
        "test_mode": mode,
    }
    body = json.dumps(payload).encode()

    request = (
        "POST /nuvl HTTP/1.1\r\n"
        "Host: {}\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(PI_IP, len(body)).encode() + body

    s = socket.socket()
    s.settimeout(6)

    try:
        s.connect((PI_IP, PORT))
        s.send(request)

        chunks = []
        while True:
            try:
                chunk = s.recv(512)
                if not chunk:
                    break
                chunks.append(chunk)
            except OSError:
                if chunks:
                    break
                raise

        raw = b"".join(chunks)
        body_raw = raw.split(b"\r\n\r\n", 1)[1]
        return json.loads(body_raw.decode())
    finally:
        try:
            s.close()
        except Exception:
            pass


print("POC002_ED25519_PROVIDER_BOUNDARY_START")
gc.collect()
baseline_free = gc.mem_free()

passed = 0
failed = 0

for index, case in enumerate(CASES, 1):
    name, action, context, mode, expected_decision, expected_verified = case

    try:
        response = post_case(index, action, context, mode)
        actual_decision = response.get("decision")
        actual_verified = response.get("provider_verified")
        ok = (
            actual_decision == expected_decision
            and actual_verified == expected_verified
        )

        if ok:
            passed += 1
        else:
            failed += 1

        print(
            "CASE {} name={} expected={}/{} actual={}/{} reason={} result={}".format(
                index,
                name,
                expected_decision,
                expected_verified,
                actual_decision,
                actual_verified,
                response.get("reason"),
                "PASS" if ok else "FAIL",
            )
        )
    except Exception as exc:
        failed += 1
        print(
            "CASE {} name={} transport_error={} result=FAIL".format(
                index, name, repr(exc)
            )
        )

    gc.collect()
    time.sleep_ms(200)

gc.collect()
final_free = gc.mem_free()

print("POC002_ED25519_PROVIDER_BOUNDARY_SUMMARY")
print("cases=", len(CASES))
print("passed=", passed)
print("failed=", failed)
print("baseline_free=", baseline_free)
print("final_free=", final_free)
print("free_delta=", final_free - baseline_free)
print("private_key_on_endpoint=", False)
print("signature_verification_location=pi_boundary")
print("POC002_ED25519_PROVIDER_BOUNDARY_END")
