"""Read-only source inventory and byte-preserving reference snapshot."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent


def main():
    sources = {
        "MH001_R43": (BASE / "MH001_DEPLOYMENT_REVIEW_R43", [
            "BASELINE.json", "HASHES.json", "frozen_R43/hub.py", "frozen_R43/wire.py",
            "frozen_R43/routes.py", "frozen_R43/SHA256SUMS.txt", "frozen_R43/CONFIGURATION_FREEZE.json",
            "frozen_R43/SOURCE_REVIEW.md", "frozen_R43/README.md"]),
        "MP005": (BASE / "MP005-reference/modules/multi-provider/MP005", [
            "provider_a/provider_a.py", "provider_a/mint_authorization_a.py", "requirements.txt",
            "configs/MP005_SOURCE_MANIFEST.json", "configs/MP005_LOCK_SHA256SUMS.txt",
            "harness/ledger_evidence.py", "harness/common.py", "README.md"]),
        "MP004": (BASE / "MP005-reference/modules/multi-provider/MP004", [
            "verifier/verify_mp004.py", "PROVENANCE.md", "README.md", "SHA256SUMS.txt"]),
        "MP006": (BASE / "MULTI_PROVIDER_006", ["mp006.py", "README.md", "SOURCE_REVIEW.md", "SHA256SUMS.txt"]),
        "ESP_LOCAL_008": (BASE / "MP005-reference/labs/nuvl-edge/esp-local/ESP_LOCAL_008", [
            "README.md", "PROVENANCE.md", "RESULTS.md", "SHA256SUMS.txt", "witness/README.md",
            "coordinator/esp_local_008_presenter.py", "provider/esp_local_008_provider.py",
            "firmware/endpoint-runtime/project/main/ESP_LOCAL_008_ENDPOINT.c",
            "witness/ESP_LOCAL_008_WITNESS_RMT_V1/main/witness_rmt_v1.c"])}
    rows = []
    for component, (source, files) in sources.items():
        for relative in files:
            original = source / relative
            # Flatten frozen_R43 only for the importable mechanical forwarder.
            target_rel = relative.removeprefix("frozen_R43/") if component == "MH001_R43" else relative
            target = ROOT / "reference" / component / target_rel
            target.parent.mkdir(parents=True, exist_ok=True)
            raw = original.read_bytes()
            if target.exists() and target.read_bytes() != raw:
                raise RuntimeError("refusing to overwrite different reference: " + str(target))
            if not target.exists():
                shutil.copyfile(original, target)
            rows.append(dict(component=component, source_path=str(original.resolve()),
                             copy_path=target.relative_to(ROOT).as_posix(), bytes=len(raw),
                             sha256=hashlib.sha256(raw).hexdigest()))
    baseline = json.loads((BASE / "MH001_DEPLOYMENT_REVIEW_R43/BASELINE.json").read_bytes())
    for row in rows:
        if row["component"] == "MH001_R43":
            rel = Path(row["source_path"]).relative_to(BASE / "MH001_DEPLOYMENT_REVIEW_R43").as_posix()
            expected = baseline["files"].get(rel)
            row["existing_baseline_sha256"] = expected
            if expected and expected != row["sha256"]:
                raise RuntimeError("MH001 baseline mismatch")
    # Verify exact canonical function source reuse; never import the stateful provider.
    def function(path):
        text = path.read_text(encoding="utf-8")
        node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == "canonical_bytes")
        return ast.get_source_segment(text, node)
    assert function(ROOT / "src/artifact.py") == function(sources["MP005"][0] / "provider_a/provider_a.py")
    commit = subprocess.check_output(["git", "-C", str(BASE / "MP005-reference"), "rev-parse", "HEAD"], text=True).strip()
    report = dict(reference_checkout_commit=commit, parent_revision="UNBORN_HEAD; content hashes identify local source",
                  mh001_revision=baseline["revision"], canonical_function_exact_match=True, files=rows)
    (ROOT / "reference/SOURCE_INVENTORY.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Inventoried {len(rows)} files; MH001 baseline and exact canonical function checked")


if __name__ == "__main__":
    main()
