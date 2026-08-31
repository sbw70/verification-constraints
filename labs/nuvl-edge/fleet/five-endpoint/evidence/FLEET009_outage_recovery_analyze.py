import re
import statistics
from collections import Counter, defaultdict

path = "FLEET009_OUTAGE_RECOVERY_WINDOW.log"

PHASES = {
    "PRE_OUTAGE": (77261, 77288),
    "OUTAGE": (77289, 77595),
    "RECOVERY": (77596, 77785),
}

pat = re.compile(
    r'^RESULT run_id=(\S+) device_id=(\S+) decision=(\S+) reason=(\S+) elapsed_ms=(\d+)'
)

records = []

with open(path, "r", encoding="utf-8", errors="replace") as f:
    for offset, line in enumerate(f):
        original_line = 77261 + offset
        m = pat.match(line.strip())
        if not m:
            continue

        run_id, device_id, decision, reason, elapsed_ms = m.groups()

        phase = None
        for name, (start, end) in PHASES.items():
            if start <= original_line <= end:
                phase = name
                break

        if phase is None:
            continue

        records.append({
            "line": original_line,
            "phase": phase,
            "run_id": run_id,
            "device_id": device_id,
            "decision": decision,
            "reason": reason,
            "elapsed_ms": int(elapsed_ms),
        })

print("FLEET009_OUTAGE_RECOVERY_DATASET_SUMMARY")

run_ids = [r["run_id"] for r in records]
run_id_counts = Counter(run_ids)

print("parsed_transactions=", len(records))
print("unique_run_ids=", len(run_id_counts))
print("duplicate_run_ids=", sum(1 for n in run_id_counts.values() if n > 1))

for phase in ("PRE_OUTAGE", "OUTAGE", "RECOVERY"):
    subset = [r for r in records if r["phase"] == phase]
    latencies = [r["elapsed_ms"] for r in subset]

    print()
    print("PHASE", phase)
    print("transactions=", len(subset))
    print("decisions=", dict(Counter(r["decision"] for r in subset)))
    print("reasons=", dict(Counter(r["reason"] for r in subset)))

    if latencies:
        print("latency_min_ms=", min(latencies))
        print("latency_mean_ms=", round(statistics.mean(latencies), 2))
        print("latency_median_ms=", statistics.median(latencies))
        print("latency_max_ms=", max(latencies))
        print("over_250_ms=", sum(v > 250 for v in latencies))
        print("over_1000_ms=", sum(v > 1000 for v in latencies))
        print("over_3000_ms=", sum(v > 3000 for v in latencies))

    by_device = defaultdict(list)
    for r in subset:
        by_device[r["device_id"]].append(r)

    for device_id in sorted(by_device):
        dev = by_device[device_id]
        print(
            "device",
            device_id,
            "transactions=", len(dev),
            "decisions=", dict(Counter(r["decision"] for r in dev)),
            "reasons=", dict(Counter(r["reason"] for r in dev)),
        )
