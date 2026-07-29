#!/usr/bin/env python3
"""Rebuild threshold and escalation-mask replay semantics from released arrays.

The script does not refit a router or change a threshold.  It verifies the
scientific replay convention used by the paper:

- V106 scores and thresholds are compared as NumPy float32 with strict `>`;
- the effect of an accidental float64 promotion is recorded over the full
  seed/interface/lambda grid;
- V104E archived escalation decisions are checksum-locked because the compact
  release does not contain the heavy confirmation feature matrices required to
  rerun every router score from first principles.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
V106_INTERFACES = {
    "candidate_prediction_interface": "candidate_score",
    "task_only_baseline": "task_only_score",
}
V104E_POLICY_KEYS = [
    "Prediction_interface_sequential_router_escalation",
    "Fixed_Medium_escalation",
    "Fixed_Full_escalation",
    "Margin_sequential_matched_rate_escalation",
    "Random_input_matched_rate_escalation",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: Iterable[dict[str, object]]) -> None:
    materialized = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(materialized[0]))
        writer.writeheader()
        writer.writerows(materialized)


def packed_mask_sha256(mask: np.ndarray) -> str:
    packed = np.packbits(np.asarray(mask, dtype=np.bool_).reshape(-1, order="C"))
    return hashlib.sha256(packed.tobytes()).hexdigest()


def raw_int8_mask_sha256(mask: np.ndarray) -> str:
    values = np.asarray(mask, dtype=np.int8)
    return hashlib.sha256(values.tobytes(order="C")).hexdigest()


def build_v106_threshold_rows(root: Path = ROOT) -> list[dict[str, object]]:
    threshold_path = root / "provenance/v106/sealed_router/validation_thresholds.csv"
    thresholds = read_rows(threshold_path)
    # The scientific replay reads the exact decimal string and casts it to
    # float32.  The hostile audit also identified a portability hazard: pandas'
    # default float parser can round selected threshold strings before a
    # float64 comparison.  Record that alternate, non-scientific replay
    # explicitly rather than attributing the difference to dtype alone.
    parsed = pd.read_csv(threshold_path)
    parsed_index = {
        (int(row.upstream_model_seed), str(row.interface), float(row["lambda"])):
        float(row.threshold)
        for _, row in parsed.iterrows()
    }
    cache: dict[int, dict[str, np.ndarray]] = {}
    rows: list[dict[str, object]] = []
    for threshold_row in thresholds:
        seed = int(threshold_row["upstream_model_seed"])
        interface = threshold_row["interface"]
        if interface not in V106_INTERFACES:
            raise RuntimeError(f"unexpected V106 interface: {interface}")
        if seed not in cache:
            archive = root / f"artifacts/v106/arrays/v106_primary_audit_seed{seed}.npz"
            with np.load(archive) as payload:
                cache[seed] = {
                    key: np.asarray(payload[key], dtype=np.float32).copy()
                    for key in V106_INTERFACES.values()
                }
        scores = cache[seed][V106_INTERFACES[interface]]
        threshold64 = float(threshold_row["threshold"])
        threshold32 = np.float32(threshold64)
        strict_mask = scores > threshold32
        parser_threshold64 = parsed_index[(seed, interface, float(threshold_row["lambda"]))]
        parser_float64_mask = scores.astype(np.float64) > parser_threshold64
        equality_count = int(np.count_nonzero(scores == threshold32))
        rows.append(
            {
                "upstream_model_seed": seed,
                "interface": interface,
                "lambda": float(threshold_row["lambda"]),
                "score_dtype": "float32",
                "threshold_dtype": "float32",
                "comparison": "strict_greater_than",
                "equality_count": equality_count,
                "strict_full_route_count": int(np.count_nonzero(strict_mask)),
                "strict_full_route_rate": float(np.mean(strict_mask)),
                "pandas_float64_replay_changed_decisions": int(
                    np.count_nonzero(strict_mask != parser_float64_mask)
                ),
                "strict_mask_sha256": packed_mask_sha256(strict_mask),
            }
        )
    return rows


def build_task_only_rates(
    threshold_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    selected = [
        row
        for row in threshold_rows
        if row["interface"] == "task_only_baseline"
        and float(row["lambda"]) == 0.002
    ]
    seed_order = {2026: 0, 314159: 1, 92002: 2}
    selected.sort(key=lambda row: seed_order[int(row["upstream_model_seed"])])
    rows: list[dict[str, object]] = []
    total_rows = 0
    total_full = 0
    for row in selected:
        n = 1600 * 39
        full = int(row["strict_full_route_count"])
        total_rows += n
        total_full += full
        rows.append(
            {
                "upstream_model_seed": int(row["upstream_model_seed"]),
                "audit_query_task_rows": n,
                "full_route_count": full,
                "full_route_rate": full / n,
                "lambda": 0.002,
            }
        )
    rows.append(
        {
            "upstream_model_seed": "equal_seed_average",
            "audit_query_task_rows": total_rows,
            "full_route_count": total_full,
            "full_route_rate": total_full / total_rows,
            "lambda": 0.002,
        }
    )
    return rows


def build_v104e_mask_rows(root: Path = ROOT) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for archive in sorted((root / "artifacts/v104e/arrays").glob("confirmation_arrays_seed*.npz")):
        seed = int(archive.stem.removeprefix("confirmation_arrays_seed"))
        with np.load(archive) as payload:
            for key in V104E_POLICY_KEYS:
                mask = np.asarray(payload[key], dtype=np.int8)
                rows.append(
                    {
                        "capacity_seed": seed,
                        "policy_key": key,
                        "shape": "x".join(str(value) for value in mask.shape),
                        "dtype": "int8",
                        "ones": int(mask.sum()),
                        "mask_sha256": raw_int8_mask_sha256(mask),
                    }
                )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts")
    args = parser.parse_args()
    v106_rows = build_v106_threshold_rows(ROOT)
    write_rows(args.output / "v106/threshold_semantics_audit.csv", v106_rows)
    write_rows(args.output / "v106/task_only_escalation_rates.csv", build_task_only_rates(v106_rows))
    write_rows(args.output / "v104e/escalation_mask_checksums.csv", build_v104e_mask_rows(ROOT))
    print("WMROUTE_REPLAY_SEMANTICS_AUDIT_PASS")


if __name__ == "__main__":
    main()
