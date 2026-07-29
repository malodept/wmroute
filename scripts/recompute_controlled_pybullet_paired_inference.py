#!/usr/bin/env python3
"""Recompute V104E inference while preserving crossed physical-state pairing.

This repair leaves the frozen V104E point estimates untouched. It provides:
1. a fixed-seed, state-clustered primary bootstrap (matching the declared
   estimand conditional on the three frozen upstream seeds); and
2. a crossed seed/state sensitivity bootstrap in which the same sampled
   physical-state IDs are used for every sampled seed within each bank.

The originally executed bootstrap is retained separately for provenance but is
not used for repaired paper-facing intervals.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable

import numpy as np

CANDIDATE = "Prediction-interface sequential router_cost"
REFERENCES = [
    "Fixed Medium_cost",
    "Fixed Full_cost",
    "Margin sequential matched-rate_cost",
    "Random input matched-rate_cost",
]
DISPLAY = {name: name.removesuffix("_cost") for name in REFERENCES}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: Iterable[dict[str, object]]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_crossed_array(path: Path) -> tuple[np.ndarray, list[str], list[int]]:
    rows = read_rows(path)
    banks = list(dict.fromkeys(row["bank"] for row in rows))
    seeds = sorted({int(row["capacity_seed"]) for row in rows})
    state_ids_by_bank: dict[str, list[int]] = {}
    for bank in banks:
        ids = sorted({int(row["local_state_id"]) for row in rows if row["bank"] == bank})
        state_ids_by_bank[bank] = ids
    sizes = {len(ids) for ids in state_ids_by_bank.values()}
    if len(sizes) != 1:
        raise RuntimeError(f"unequal bank sizes: {sorted(sizes)}")
    n_states = sizes.pop()
    expected_ids = list(range(n_states))
    for bank, ids in state_ids_by_bank.items():
        if ids != expected_ids:
            raise RuntimeError(f"non-contiguous state IDs in {bank}")

    index = {
        (row["bank"], int(row["capacity_seed"]), int(row["local_state_id"])): row
        for row in rows
    }
    if len(index) != len(rows):
        raise RuntimeError("duplicate bank/seed/state rows")
    expected = len(banks) * len(seeds) * n_states
    if len(rows) != expected:
        raise RuntimeError(f"expected {expected} crossed rows, found {len(rows)}")

    values = np.empty((len(banks), len(seeds), n_states, len(REFERENCES)))
    for b, bank in enumerate(banks):
        for r, seed in enumerate(seeds):
            for i in range(n_states):
                row = index[(bank, seed, i)]
                candidate = float(row[CANDIDATE])
                for k, reference in enumerate(REFERENCES):
                    values[b, r, i, k] = candidate - float(row[reference])
    if not np.isfinite(values).all():
        raise RuntimeError("non-finite V104E differences")
    return values, banks, seeds


def sample_counts(indices: np.ndarray, n_categories: int) -> np.ndarray:
    """Convert integer bootstrap indices into per-replicate frequency counts."""
    offsets = np.arange(indices.shape[0], dtype=np.int64)[:, None] * n_categories
    encoded = (indices + offsets).reshape(-1)
    return np.bincount(
        encoded,
        minlength=indices.shape[0] * n_categories,
    ).reshape(indices.shape[0], n_categories).astype(np.float64, copy=False)


def fixed_seed_state_bootstrap(
    values: np.ndarray,
    *,
    repeats: int,
    seed: int,
    chunk_size: int = 128,
) -> np.ndarray:
    """Average frozen seed effects per state, then resample states within bank."""
    state_effect = values.mean(axis=1)  # [bank, state, comparison]
    n_banks, n_states, n_comparisons = state_effect.shape
    rng = np.random.default_rng(seed)
    draws = np.empty((repeats, n_comparisons), dtype=np.float64)
    for start in range(0, repeats, chunk_size):
        end = min(start + chunk_size, repeats)
        chunk = end - start
        bank_means = np.empty((chunk, n_banks, n_comparisons), dtype=np.float64)
        for bank in range(n_banks):
            indices = rng.integers(0, n_states, size=(chunk, n_states))
            counts = sample_counts(indices, n_states)
            bank_means[:, bank] = (counts @ state_effect[bank]) / n_states
        draws[start:end] = bank_means.mean(axis=1)
    return draws


def crossed_seed_state_bootstrap(
    values: np.ndarray,
    *,
    repeats: int,
    seed: int,
    chunk_size: int = 64,
) -> np.ndarray:
    """Resample seeds and states while preserving the state pairing across seeds."""
    n_banks, n_seeds, n_states, n_comparisons = values.shape
    rng = np.random.default_rng(seed)
    draws = np.empty((repeats, n_comparisons), dtype=np.float64)
    for start in range(0, repeats, chunk_size):
        end = min(start + chunk_size, repeats)
        chunk = end - start
        sampled_seeds = rng.integers(0, n_seeds, size=(chunk, n_seeds))
        seed_counts = sample_counts(sampled_seeds, n_seeds)
        bank_means = np.empty((chunk, n_banks, n_comparisons), dtype=np.float64)
        for bank in range(n_banks):
            sampled_states = rng.integers(0, n_states, size=(chunk, n_states))
            state_counts = sample_counts(sampled_states, n_states)
            bank_means[:, bank] = np.einsum(
                "rs,ri,sik->rk",
                seed_counts,
                state_counts,
                values[bank],
                optimize=True,
            ) / (n_seeds * n_states)
        draws[start:end] = bank_means.mean(axis=1)
    return draws


def fixed_seed_bank_bootstrap(
    values: np.ndarray,
    *,
    repeats: int,
    seed: int,
) -> np.ndarray:
    state_effect = values.mean(axis=1)  # [bank, state, comparison]
    n_banks, n_states, n_comparisons = state_effect.shape
    rng = np.random.default_rng(seed)
    draws = np.empty((n_banks, repeats, n_comparisons), dtype=np.float64)
    for bank in range(n_banks):
        for start in range(0, repeats, 128):
            end = min(start + 128, repeats)
            indices = rng.integers(0, n_states, size=(end - start, n_states))
            counts = sample_counts(indices, n_states)
            draws[bank, start:end] = (counts @ state_effect[bank]) / n_states
    return draws


def crossed_seed_bank_bootstrap(
    values: np.ndarray,
    *,
    repeats: int,
    seed: int,
) -> np.ndarray:
    n_banks, n_seeds, n_states, n_comparisons = values.shape
    rng = np.random.default_rng(seed)
    draws = np.empty((n_banks, repeats, n_comparisons), dtype=np.float64)
    for bank in range(n_banks):
        for start in range(0, repeats, 64):
            end = min(start + 64, repeats)
            chunk = end - start
            sampled_seeds = rng.integers(0, n_seeds, size=(chunk, n_seeds))
            sampled_states = rng.integers(0, n_states, size=(chunk, n_states))
            seed_counts = sample_counts(sampled_seeds, n_seeds)
            state_counts = sample_counts(sampled_states, n_states)
            draws[bank, start:end] = np.einsum(
                "rs,ri,sik->rk",
                seed_counts,
                state_counts,
                values[bank],
                optimize=True,
            ) / (n_seeds * n_states)
    return draws


def summarize_primary(
    observed: np.ndarray,
    draws: np.ndarray,
    *,
    upper_quantile: float,
    method: str,
    repeats: int,
) -> list[dict[str, object]]:
    rows = []
    for k, reference in enumerate(REFERENCES):
        low, high = np.quantile(draws[:, k], [0.025, 0.975])
        upper = np.quantile(draws[:, k], upper_quantile)
        rows.append(
            {
                "candidate": CANDIDATE.removesuffix("_cost"),
                "reference": DISPLAY[reference],
                "lambda": 0.002,
                "cost_difference_candidate_minus_reference": float(observed[k]),
                "ci95_low": float(low),
                "ci95_high": float(high),
                "bonferroni_adjusted_one_sided_upper": float(upper),
                "adjusted_upper_below_zero": bool(upper < 0.0),
                "bootstrap_replicates": repeats,
                "inference_method": method,
            }
        )
    return rows


def summarize_sensitivity(
    observed: np.ndarray,
    draws: np.ndarray,
    *,
    upper_quantile: float,
    method: str,
    repeats: int,
) -> list[dict[str, object]]:
    rows = []
    for k, reference in enumerate(REFERENCES):
        low, high = np.quantile(draws[:, k], [0.025, 0.975])
        upper = np.quantile(draws[:, k], upper_quantile)
        rows.append(
            {
                "candidate": CANDIDATE.removesuffix("_cost"),
                "reference": DISPLAY[reference],
                "lambda": 0.002,
                "cost_difference_candidate_minus_reference": float(observed[k]),
                "sensitivity_q025": float(low),
                "sensitivity_q975": float(high),
                "adjusted_one_sided_upper_quantile": float(upper),
                "adjusted_upper_below_zero": bool(upper < 0.0),
                "sensitivity_replicates": repeats,
                "sensitivity_method": method,
                "population_confidence_interval": False,
            }
        )
    return rows


def analytic_check(values: np.ndarray) -> list[dict[str, object]]:
    x = values.mean(axis=1)  # [bank, state, comparison]
    observed = x.mean(axis=(0, 1))
    n_banks, n_states, _ = x.shape
    standard_error = np.sqrt(
        sum(x[bank].var(axis=0, ddof=1) / n_states for bank in range(n_banks))
    ) / n_banks
    rows = []
    for k, reference in enumerate(REFERENCES):
        rows.append(
            {
                "reference": DISPLAY[reference],
                "estimate": float(observed[k]),
                "stratified_state_cluster_standard_error": float(standard_error[k]),
                "normal_ci95_low": float(observed[k] - 1.959963984540054 * standard_error[k]),
                "normal_ci95_high": float(observed[k] + 1.959963984540054 * standard_error[k]),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-state", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=104_920)
    parser.add_argument("--upper-quantile", type=float, default=0.9875)
    args = parser.parse_args()

    values, banks, seeds = load_crossed_array(args.per_state)
    observed = values.mean(axis=(0, 1, 2))
    fixed_draws = fixed_seed_state_bootstrap(values, repeats=args.repeats, seed=args.seed)
    crossed_draws = crossed_seed_state_bootstrap(values, repeats=args.repeats, seed=args.seed)
    fixed_bank_draws = fixed_seed_bank_bootstrap(values, repeats=args.repeats, seed=args.seed + 1)
    crossed_bank_draws = crossed_seed_bank_bootstrap(values, repeats=args.repeats, seed=args.seed + 1)

    args.output.mkdir(parents=True, exist_ok=True)
    fixed_rows = summarize_primary(
        observed,
        fixed_draws,
        upper_quantile=args.upper_quantile,
        method="fixed-seed state-clustered stratified bootstrap",
        repeats=args.repeats,
    )
    crossed_rows = summarize_sensitivity(
        observed,
        crossed_draws,
        upper_quantile=args.upper_quantile,
        method="crossed seed/state bootstrap with shared state indices across seeds",
        repeats=args.repeats,
    )
    write_rows(args.output / "global_primary_fixed_seed_state_clustered.csv", fixed_rows)
    write_rows(args.output / "global_crossed_seed_state_sensitivity.csv", crossed_rows)
    write_rows(args.output / "analytic_state_cluster_check.csv", analytic_check(values))

    bank_fixed_rows: list[dict[str, object]] = []
    bank_crossed_rows: list[dict[str, object]] = []
    bank_observed = values.mean(axis=(1, 2))
    for b, bank in enumerate(banks):
        for k, reference in enumerate(REFERENCES):
            fixed_low, fixed_high = np.quantile(fixed_bank_draws[b, :, k], [0.025, 0.975])
            crossed_low, crossed_high = np.quantile(crossed_bank_draws[b, :, k], [0.025, 0.975])
            base = {
                "bank": bank,
                "candidate": CANDIDATE.removesuffix("_cost"),
                "reference": DISPLAY[reference],
                "lambda": 0.002,
                "cost_difference_candidate_minus_reference": float(bank_observed[b, k]),
                "bootstrap_replicates": args.repeats,
            }
            bank_fixed_rows.append(
                {
                    **base,
                    "ci95_low": float(fixed_low),
                    "ci95_high": float(fixed_high),
                    "candidate_significantly_better_95": bool(fixed_high < 0),
                    "candidate_significantly_worse_95": bool(fixed_low > 0),
                    "inference_method": "fixed-seed state-clustered bootstrap",
                }
            )
            bank_crossed_rows.append(
                {
                    **base,
                    "sensitivity_q025": float(crossed_low),
                    "sensitivity_q975": float(crossed_high),
                    "candidate_lower_than_reference_q975": bool(crossed_high < 0),
                    "candidate_higher_than_reference_q025": bool(crossed_low > 0),
                    "sensitivity_method": "crossed seed/state bootstrap",
                    "population_confidence_interval": False,
                }
            )
    write_rows(args.output / "bankwise_fixed_seed_state_clustered.csv", bank_fixed_rows)
    write_rows(args.output / "bankwise_crossed_seed_state_sensitivity.csv", bank_crossed_rows)

    report = {
        "status": "V104E_PAIRED_INFERENCE_REPAIR_PASS",
        "input": str(args.per_state),
        "banks": banks,
        "model_seeds": seeds,
        "physical_states": int(values.shape[0] * values.shape[2]),
        "crossed_rows": int(np.prod(values.shape[:3])),
        "comparisons": [DISPLAY[name] for name in REFERENCES],
        "point_estimates_unchanged": True,
        "primary_method": "fixed-seed state-clustered stratified bootstrap",
        "sensitivity_method": "crossed seed/state bootstrap with shared state indices across seeds",
        "all_primary_adjusted_upper_bounds_below_zero": all(
            bool(row["adjusted_upper_below_zero"]) for row in fixed_rows
        ),
        "all_crossed_sensitivity_adjusted_upper_quantiles_below_zero": all(
            bool(row["adjusted_upper_below_zero"]) for row in crossed_rows
        ),
        "bootstrap_seed": args.seed,
        "bootstrap_replicates": args.repeats,
        "bonferroni_upper_quantile": args.upper_quantile,
    }
    (args.output / "repair_summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
