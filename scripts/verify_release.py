#!/usr/bin/env python3
"""Verify the compact public release without loading serialized model files."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    required = [
        ROOT / "README.md",
        ROOT / "LICENSE.md",
        ROOT / "CITATION.cff",
        ROOT / "paper/wmroute_preprint.pdf",
        ROOT / "paper/source/main.tex",
        ROOT / "docs/index.html",
        ROOT / "artifacts/v107/audit/scientific_gate.json",
        ROOT / "artifacts/v106/global_primary_bootstrap.csv",
        ROOT / "artifacts/v104e/repaired_inference/global_primary_fixed_seed_state_clustered.csv",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    require(not missing, f"missing required files: {missing}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    source = (ROOT / "paper/source/main.tex").read_text(encoding="utf-8")
    require("Routing World-Model Compute from Predicted Consequences" in readme, "README title mismatch")
    require("Routing World-Model Compute from Predicted Consequences" in citation, "citation title mismatch")
    require("Routing World-Model Compute from Predicted Consequences" in source, "paper source title mismatch")
    require("TO_BE_ADDED" not in readme + citation, "unresolved public-release placeholder")

    gate = json.loads((ROOT / "artifacts/v107/audit/scientific_gate.json").read_text())
    require(gate["primary_gate_pass"], "prospective confirmation gate did not pass")
    require(abs(gate["aggregate_point"] + 0.0025493366853158186) < 1e-15, "confirmation point mismatch")
    require(gate["one_sided_95_upper"] < 0, "confirmation one-sided bound is not negative")
    require(all(value < 0 for value in gate["checkpoint_pair_points"].values()), "checkpoint-pair sign failure")

    v106 = {
        row["reference"]: float(row["cost_difference_candidate_minus_reference"])
        for row in read_csv(ROOT / "artifacts/v106/global_primary_bootstrap.csv")
    }
    require(abs(v106["Fixed Medium"] + 0.004307652735007721) < 1e-15, "initial PushT snapshot mismatch")
    require(abs(v106["Fixed Full"] + 0.002576937001531322) < 1e-15, "initial PushT Full snapshot mismatch")

    v104e = {
        row["reference"]: float(row["cost_difference_candidate_minus_reference"])
        for row in read_csv(ROOT / "artifacts/v104e/repaired_inference/global_primary_fixed_seed_state_clustered.csv")
    }
    require(abs(v104e["Fixed Medium"] + 0.0036772961183432016) < 1e-15, "PyBullet snapshot mismatch")
    require(abs(v104e["Fixed Full"] + 0.003746314265757149) < 1e-15, "PyBullet Full snapshot mismatch")

    prohibited = ("BEGIN OPENSSH PRIVATE KEY", "BEGIN RSA PRIVATE KEY")
    excluded_roots = {".git", ".venv", "__pycache__", ".pytest_cache"}

    def included(path: Path) -> bool:
        try:
            rel = path.relative_to(ROOT)
        except ValueError:
            return False
        return not any(part in excluded_roots for part in rel.parts)

    scanned = 0
    for path in ROOT.rglob("*"):
        if not included(path):
            continue
        if not path.is_file() or path.suffix.lower() in {".npz", ".joblib", ".pdf", ".png", ".gz", ".zip"}:
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        if path.stat().st_size > 2_000_000:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        scanned += 1
        for marker in prohibited:
            require(marker.lower() not in text.lower(), f"possible secret marker in {path.relative_to(ROOT)}: {marker}")

    release_files = [path for path in ROOT.rglob("*") if path.is_file() and included(path)]
    largest = max((path.stat().st_size, path) for path in release_files)
    require(largest[0] < 50 * 1024 * 1024, f"unexpectedly large file: {largest[1].relative_to(ROOT)}")

    manifest = {
        "status": "WMROUTE_PUBLIC_RELEASE_VERIFY_PASS",
        "paper_sha256": sha256(ROOT / "paper/wmroute_preprint.pdf"),
        "files": len(release_files),
        "text_files_scanned": scanned,
        "largest_file": str(largest[1].relative_to(ROOT)),
        "largest_file_bytes": largest[0],
        "prospective_confirmation_point": gate["aggregate_point"],
        "prospective_confirmation_gate": gate["primary_gate_pass"],
    }
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
