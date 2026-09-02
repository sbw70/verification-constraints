import gc
import json
import socket
import time

PI_IP = "192.168.8.234"
PORT = 8089

DEVICE_ID = "esp32-field-01"
GOOD_CONTEXT = "field_led_demo"

MATRICES = 10

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


def post_case(matrix_no, case_no, action, context, mode):
    payload = {
        "device_id": DEVICE_ID,
        "context": context,
        "requested_action": action,
        "nonce": "poc002-repeat-m{:02d}-c{:02d}-{}".format(
            matrix_no, case_no, time.ticks_ms()
        ),
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
    s.settimeout(7)

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
        response_body = raw.split(b"\r\n\r\n", 1)[1]
        return json.loads(response_body.decode())
    finally:
        try:
            s.close()
        except Exception:
            pass


print("POC002_REPEAT_MATRIX_START")
print("matrices=", MATRICES)
print("cases_per_matrix=", len(CASES))
print("total_cases=", MATRICES * len(CASES))

gc.collect()
baseline_free = gc.mem_free()

passed = 0
failed = 0
transport_failures = 0

matrix_free_values = []
matrix_deltas = []

for matrix_no in range(1, MATRICES + 1):
    matrix_passed = 0
    matrix_failed = 0

    for case_no, case in enumerate(CASES, 1):
        name, action, context, mode, expected_decision, expected_verified = case

        try:
            response = post_case(
                matrix_no,
                case_no,
                action,
                context,
                mode,
            )

            actual_decision = response.get("decision")
            actual_verified = response.get("provider_verified")

            ok = (
                actual_decision == expected_decision
                and actual_verified == expected_verified
            )

            if ok:
                passed += 1
                matrix_passed += 1
            else:
                failed += 1
                matrix_failed += 1
                print(
                    "FAIL matrix={} case={} name={} expected={}/{} actual={}/{} reason={}".format(
                        matrix_no,
                        case_no,
                        name,
                        expected_decision,
                        expected_verified,
                        actual_decision,
                        actual_verified,
                        response.get("reason"),
                    )
                )

        except Exception as exc:
            failed += 1
            matrix_failed += 1
            transport_failures += 1
            print(
                "TRANSPORT_FAIL matrix={} case={} name={} err={}".format(
                    matrix_no,
                    case_no,
                    name,
                    repr(exc),
                )
            )

        gc.collect()
        time.sleep_ms(100)

    gc.collect()
    matrix_free = gc.mem_free()
    matrix_delta = matrix_free - baseline_free
    matrix_free_values.append(matrix_free)
    matrix_deltas.append(matrix_delta)

    print(
        "MATRIX {} passed={} failed={} free_after_gc={} delta_from_baseline={}".format(
            matrix_no,
            matrix_passed,
            matrix_failed,
            matrix_free,
            matrix_delta,
        )
    )

gc.collect()
final_free = gc.mem_free()

print("POC002_REPEAT_MATRIX_SUMMARY")
print("matrices=", MATRICES)
print("total_cases=", MATRICES * len(CASES))
print("passed=", passed)
print("failed=", failed)
print("transport_failures=", transport_failures)
print("baseline_free=", baseline_free)
print("final_free=", final_free)
print("free_delta_final_minus_baseline=", final_free - baseline_free)
print("matrix_free_min=", min(matrix_free_values))
print("matrix_free_max=", max(matrix_free_values))
print("matrix_free_range=", max(matrix_free_values) - min(matrix_free_values))
print("matrix_delta_first=", matrix_deltas[0])
print("matrix_delta_last=", matrix_deltas[-1])
print("private_key_on_endpoint=", False)
print("signature_verification_location=pi_boundary")
print("POC002_REPEAT_MATRIX_END")
