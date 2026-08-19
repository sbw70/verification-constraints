import re
import statistics
from collections import Counter

path = "/home/seth/FLEET006_AUTONOMOUS_WINDOW.log"

pat = re.compile(
    r'^RESULT run_id=(\S+) device_id=(\S+) '
    r'decision=(\S+) reason=(\S+) elapsed_ms=(\d+)'
)

rows = []

with open(path, "r", errors="replace") as f:
    for line in f:
        m = pat.match(line.strip())
        if m:
            run_id, device_id, decision, reason, elapsed = m.groups()
            rows.append(
                {
                    "run_id": run_id,
                    "device_id": device_id,
                    "decision": decision,
                    "reason": reason,
                    "elapsed_ms": int(elapsed),
                }
            )

print("FLEET006_DATASET_SUMMARY")
print("parsed_transactions=", len(rows))
print("unique_run_ids=", len({r["run_id"] for r in rows}))
print(
    "duplicate_run_ids=",
    len(rows) - len({r["run_id"] for r in rows}),
)
print()

for device_id in sorted({r["device_id"] for r in rows}):
    d = [r for r in rows if r["device_id"] == device_id]
    lat = [r["elapsed_ms"] for r in d]

    decisions = Counter(r["decision"] for r in d)
    reasons = Counter(r["reason"] for r in d)

    print("DEVICE", device_id)
    print(" transactions=", len(d))
    print(" decisions=", dict(decisions))
    print(" reasons=", dict(reasons))
    print(" latency_min_ms=", min(lat))
    print(
        " latency_mean_ms=",
        round(statistics.mean(lat), 2),
    )
    print(" latency_median_ms=", statistics.median(lat))
    print(" latency_max_ms=", max(lat))
    print(" over_250_ms=", sum(x > 250 for x in lat))
    print(" over_1000_ms=", sum(x > 1000 for x in lat))
    print(" over_3000_ms=", sum(x > 3000 for x in lat))
    print()

all_lat = [r["elapsed_ms"] for r in rows]

print("FLEET_TOTAL")
print("transactions=", len(rows))
print(
    "accepted=",
    sum(r["decision"] == "accepted" for r in rows),
)
print(
    "denied=",
    sum(r["decision"] == "denied" for r in rows),
)
print(
    "other_decisions=",
    sum(
        r["decision"] not in ("accepted", "denied")
        for r in rows
    ),
)
print("latency_min_ms=", min(all_lat))
print(
    "latency_mean_ms=",
    round(statistics.mean(all_lat), 2),
)
print("latency_median_ms=", statistics.median(all_lat))
print("latency_max_ms=", max(all_lat))
print("over_250_ms=", sum(x > 250 for x in all_lat))
print("over_1000_ms=", sum(x > 1000 for x in all_lat))
print("over_3000_ms=", sum(x > 3000 for x in all_lat))
