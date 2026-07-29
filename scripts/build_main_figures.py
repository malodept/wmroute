#!/usr/bin/env python3
"""Build the sealed-comparison and latency-boundary figures."""

from __future__ import annotations

import csv
import os
import tempfile
import sys
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "wmroute-mpl"))

import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "generated" / "figures"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def forest_plot() -> None:
    records: list[tuple[str, str, float, float, float]] = []
    for environment, path, low, high in (
        (
            "PyBullet",
            REPO_ROOT / "artifacts/v104e/repaired_inference/global_primary_fixed_seed_state_clustered.csv",
            "ci95_low",
            "ci95_high",
        ),
        (
            "PushT",
            REPO_ROOT / "artifacts/v106/global_primary_bootstrap.csv",
            "state_clustered_ci95_low",
            "state_clustered_ci95_high",
        ),
    ):
        for row in read_csv(path):
            records.append(
                (
                    environment,
                    row["reference"],
                    float(row["cost_difference_candidate_minus_reference"]),
                    float(row[low]),
                    float(row[high]),
                )
            )
    fig, ax = plt.subplots(figsize=(8.2, 5.2), constrained_layout=True)
    y = np.arange(len(records))[::-1]
    colors = ["#3b82f6" if record[0] == "PushT" else "#ef8354" for record in records]
    estimate = np.asarray([record[2] for record in records])
    low = np.asarray([record[3] for record in records])
    high = np.asarray([record[4] for record in records])
    ax.errorbar(
        estimate,
        y,
        xerr=np.vstack((estimate - low, high - estimate)),
        fmt="none",
        ecolor="#6b7280",
        elinewidth=2,
        capsize=3,
    )
    ax.scatter(estimate, y, c=colors, s=42, zorder=3)
    ax.axvline(0.0, color="#111827", linewidth=1, linestyle="--")
    ax.set_yticks(
        y,
        [f"{environment}: {reference}" for environment, reference, *_ in records],
    )
    ax.set_xlabel("Candidate minus reference decision cost (lower is better)")
    ax.set_title("Frozen audit comparisons with corrected inference")
    ax.grid(axis="x", alpha=0.2)
    fig.savefig(OUTPUT / "sealed_primary_forest.png", dpi=220)
    plt.close(fig)


def aggregate_v104e_policies() -> list[dict[str, float | str]]:
    grouped: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in read_csv(REPO_ROOT / "artifacts/v104e/policy_metrics.csv"):
        for key in ("regret_mean", "latency_ms_mean", "decision_cost_mean"):
            grouped[row["policy"]][key].append(float(row[key]))
    return [
        {
            "policy": policy,
            **{key: float(np.mean(values)) for key, values in metrics.items()},
        }
        for policy, metrics in grouped.items()
    ]


def latency_boundary() -> None:
    panels = [
        ("PyBullet", aggregate_v104e_policies()),
        (
            "PushT",
            [
                {
                    "policy": row["policy"],
                    "regret_mean": float(row["regret_mean_equal_seed"]),
                    "latency_ms_mean": float(row["latency_ms_mean_equal_seed"]),
                }
                for row in read_csv(
                    REPO_ROOT / "artifacts/v106/primary_policy_summary.csv"
                )
            ],
        ),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3), constrained_layout=True)
    color = {
        "Prediction-interface sequential router": "#7c3aed",
        "PushT prediction-interface sequential router": "#7c3aed",
        "Fixed Medium": "#2563eb",
        "Fixed Full": "#dc2626",
        "Oracle sequential": "#059669",
    }
    for ax, (environment, rows) in zip(axes, panels, strict=True):
        for row in rows:
            policy = str(row["policy"])
            ax.scatter(
                float(row["latency_ms_mean"]),
                float(row["regret_mean"]),
                s=55,
                color=color.get(policy, "#9ca3af"),
                zorder=3,
            )
            if policy in color:
                label = policy.replace("PushT ", "")
                if label == "Oracle sequential":
                    label = "Clairvoyant lower bound"
                ax.annotate(
                    label,
                    (float(row["latency_ms_mean"]), float(row["regret_mean"])),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=8,
                )
        ax.set_title(environment)
        ax.set_xlabel("Measured latency (ms)")
        ax.set_ylabel("Physical decision regret")
        ax.grid(alpha=0.2)
    fig.suptitle("Decision improvement is not latency saving", fontsize=13)
    fig.savefig(OUTPUT / "latency_regret_boundary.png", dpi=220)
    plt.close(fig)


def state_heterogeneity() -> None:
    rows = read_csv(REPO_ROOT / "artifacts/derived_state_heterogeneity.csv")
    environments = [row["environment"] for row in rows]
    full = np.asarray([float(row["full_better_rate"]) for row in rows])
    medium = np.asarray([float(row["medium_better_rate"]) for row in rows])
    y = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(7.2, 2.8), constrained_layout=True)
    ax.barh(y, medium, color="#2563eb", label="Medium lower cost")
    ax.barh(y, full, left=medium, color="#dc2626", label="Full lower cost")
    ax.set_yticks(y, environments)
    ax.set_xlim(0.0, 1.0)
    ax.set_xlabel("Fraction of physical states (tasks averaged)")
    ax.set_title("The preferred fixed capacity reverses across states")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.42), ncol=2, frameon=False)
    for index, (medium_rate, full_rate) in enumerate(zip(medium, full, strict=True)):
        ax.text(medium_rate / 2.0, index, f"{medium_rate:.1%}", ha="center", va="center", color="white")
        ax.text(
            medium_rate + full_rate / 2.0,
            index,
            f"{full_rate:.1%}",
            ha="center",
            va="center",
            color="white",
        )
    fig.savefig(OUTPUT / "state_capacity_heterogeneity.png", dpi=220)
    plt.close(fig)


def compute_price_frontier() -> None:
    rows = read_csv(REPO_ROOT / "artifacts/v106/compute_price_frontier.csv")
    candidate_name = "PushT prediction-interface sequential router"
    values: dict[float, dict[str, float]] = defaultdict(dict)
    for row in rows:
        values[float(row["lambda"])][row["policy"]] = float(row["decision_cost_mean"])
    references = [
        "Fixed Medium",
        "Fixed Full",
        "Task-only input router",
        "Margin sequential matched-rate",
        "Expected random input matched-rate",
    ]
    fig, ax = plt.subplots(figsize=(8.2, 4.5), constrained_layout=True)
    lambdas = np.asarray(sorted(values))
    for reference in references:
        difference = np.asarray(
            [values[lam][candidate_name] - values[lam][reference] for lam in lambdas]
        )
        ax.plot(lambdas, difference, marker="o", label=reference)
    ax.axhline(0.0, linewidth=1, linestyle="--")
    ax.set_xlabel(r"Compute price $\lambda$")
    ax.set_ylabel("Router minus reference decision cost")
    ax.set_title("PushT compute-price sensitivity")
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8, ncol=2)
    fig.savefig(OUTPUT / "compute_price_frontier.png", dpi=220)
    plt.close(fig)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    forest_plot()
    latency_boundary()
    state_heterogeneity()
    compute_price_frontier()
    print(f"Wrote figures to {OUTPUT}")


if __name__ == "__main__":
    main()
