"""Hash and protocol-lineage verification."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return value


def verify_sealed_protocol(path: str | Path, expected_sha256: str) -> None:
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise RuntimeError(
            f"protocol hash mismatch for {path}: expected {expected_sha256}, got {actual}"
        )


def verify_frozen_sources(repo_root: str | Path) -> list[str]:
    """Verify every exact publication source against the archival manifest."""

    root = Path(repo_root)
    manifest = root / "artifacts" / "frozen_source_sha256.csv"
    verified: list[str] = []
    with manifest.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            experiment = row["experiment"]
            folder = "v104e_pybullet" if experiment == "V104E" else "v106_pusht"
            path = root / "experiments" / folder / "frozen_source" / row["path"]
            actual = sha256_file(path)
            if actual != row["expected_sha256"] or row["status"] != "OK":
                raise RuntimeError(f"frozen-source verification failed for {path}")
            verified.append(str(path.relative_to(root)))
    return verified
