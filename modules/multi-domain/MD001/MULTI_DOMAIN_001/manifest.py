"""Create once or verify a SHA-256 package manifest; never overwrite prior manifests."""
import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUDED = {"SHA256SUMS.txt", "MANIFEST_SHA256.txt"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def paths():
    return {p.relative_to(ROOT).as_posix(): p for p in ROOT.rglob("*") if p.is_file()
            and p.relative_to(ROOT).as_posix() not in EXCLUDED and "__pycache__" not in p.parts}


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = ROOT / "SHA256SUMS.txt"
    files = paths()
    if args.write:
        raw = "".join(f"{digest(p.read_bytes())}  {name}\n" for name, p in sorted(files.items())).encode()
        with manifest.open("xb") as f:
            f.write(raw)
        with (ROOT / "MANIFEST_SHA256.txt").open("x", encoding="utf-8") as f:
            f.write(digest(raw) + "  SHA256SUMS.txt\n")
    raw = manifest.read_bytes()
    expected = dict(line.split("  ", 1)[::-1] for line in raw.decode().splitlines())
    if set(expected) != set(files):
        raise RuntimeError("package file inventory changed; preserve existing manifest and create a new reviewed package")
    for name, hash_value in expected.items():
        if digest(files[name].read_bytes()) != hash_value:
            raise RuntimeError("checksum mismatch: " + name)
    if (ROOT / "MANIFEST_SHA256.txt").read_text().split()[0] != digest(raw):
        raise RuntimeError("manifest digest mismatch")
    # Validate nested run inventories too.
    for run_manifest in (ROOT / "evidence/offline").glob("*/SHA256SUMS.txt"):
        for line in run_manifest.read_text().splitlines():
            h, name = line.split("  ", 1)
            if digest((run_manifest.parent / name).read_bytes()) != h:
                raise RuntimeError("run manifest mismatch: " + str(run_manifest))
    print(f"VERIFIED {len(files)} files; package SHA-256 {digest(raw)}")


if __name__ == "__main__":
    main()
