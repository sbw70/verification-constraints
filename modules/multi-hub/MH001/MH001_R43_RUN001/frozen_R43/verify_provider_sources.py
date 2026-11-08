"""Read-only identity/binding gates. Never import providers or load their keys."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED = {"provider_a": "79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6",
            "provider_b": "618ec76ef5dd3bfa3ba7b1ad3941ed0516a7511b72957d7efb82ec565905b605"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify(historical_root=None):
    publication = json.loads((ROOT / "provenance/github_source_text.json").read_bytes())
    result = {"published_commit": publication["commit"], "providers": [], "support": [], "status": "PASS"}
    for source in publication["sources"]:
        role = source["role"]
        local = ROOT / "providers" / role / (role + ".py")
        published = ROOT / "provenance/published" / (role + ".py")
        raw, remote = local.read_bytes(), published.read_bytes()
        if not (sha(raw) == sha(remote) == sha(source["text"].encode("utf-8")) == EXPECTED[role]):
            raise ValueError(role + ": local/published/frozen source discrepancy; do not repair historical source")
        historical = None
        if historical_root is not None:
            historical = sha((Path(historical_root) / role / (role + ".py")).read_bytes())
            if historical != EXPECTED[role]:
                raise ValueError(role + ": historical source changed")
        tree = ast.parse(raw)
        binding = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "mechanical_binding")
        if [n.arg for n in binding.args.args] != ["request_repr", "verification_context"]:
            raise ValueError("provider_binding_gate_changed")
        if "NUVL_BIND_V1" not in raw.decode("utf-8"):
            raise ValueError("binding_tag_changed")
        # Frozen handlers inspect only Content-Length; routing/Host headers are ignored.
        handler = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "ProviderHandler")
        inspected_headers = []
        for node in ast.walk(handler):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Attribute) and node.func.value.attr == "headers"):
                inspected_headers.append(ast.literal_eval(node.args[0]))
        if inspected_headers != ["Content-Length"]:
            raise ValueError("provider_header_gate_changed")
        result["providers"].append({"role": role, "sha256": sha(raw), "bytes": len(raw),
            "historical_sha256": historical, "published_url": source["url"],
            "published_matches": True, "host_in_binding": False,
            "destination_header_ignored": True, "request_headers_inspected": inspected_headers,
            "method_path_query_in_signed_binding": False})
    support = json.loads((ROOT / "provenance/github_support_text.json").read_bytes())
    if support["commit"] != publication["commit"]:
        raise ValueError("support_commit_mismatch")
    for source in support["sources"]:
        actual = (ROOT / source["prepared_relative_path"]).read_bytes()
        if actual != source["text"].encode("utf-8"):
            raise ValueError("support_source_discrepancy: " + source["prepared_relative_path"])
        if historical_root is not None:
            if actual != (Path(historical_root) / source["historical_relative_path"]).read_bytes():
                raise ValueError("historical_support_discrepancy")
        result["support"].append({"path": source["prepared_relative_path"], "sha256": sha(actual),
                                  "published_matches": True, "published_url": source["published_url"]})
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical-root", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.historical_root), indent=2))
