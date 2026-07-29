#!/usr/bin/env python3
"""Build deterministic paper-facing Markdown and LaTeX tables."""

from __future__ import annotations

import csv
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "generated" / "tables"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def primary_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
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
            rows.append(
                {
                    "environment": environment,
                    "reference": row["reference"],
                    "estimate": row["cost_difference_candidate_minus_reference"],
                    "low": row[low],
                    "high": row[high],
                    "pass": row["adjusted_upper_below_zero"],
                }
            )
    return rows


def write_primary_markdown(rows: list[dict[str, str]]) -> None:
    lines = [
        "# Frozen audit comparisons with repaired inference",
        "",
        "Negative candidate-minus-reference decision cost favors the prediction-interface router.",
        "",
        "| Environment | Reference | Difference | 95% CI | Adjusted upper-bound pass |",
        "|---|---|---:|---:|:---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['environment']} | {row['reference']} | "
            f"{float(row['estimate']):.6f} | "
            f"[{float(row['low']):.6f}, {float(row['high']):.6f}] | "
            f"{row['pass']} |"
        )
    (OUTPUT / "primary_comparisons.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_primary_latex(rows: list[dict[str, str]]) -> None:
    lines = [
        r"\begin{tabular}{llrrr}",
        r"\toprule",
        r"Environment & Reference & $\widehat\Delta C$ & 95\% CI & Gate \\",
        r"\midrule",
    ]
    for row in rows:
        reference = row["reference"].replace("&", r"\&")
        interval = f"[{float(row['low']):.4f}, {float(row['high']):.4f}]"
        gate = "Pass" if row["pass"] == "True" else "Fail"
        lines.append(
            f"{row['environment']} & {reference} & "
            f"{float(row['estimate']):.4f} & {interval} & {gate} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (OUTPUT / "primary_comparisons.tex").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_environment_summary() -> None:
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Evaluation & States & Tasks & Model seeds & Primary references \\",
        r"\midrule",
        r"PyBullet (6 regimes) & 12,000 & 81 & 3 & 4 \\",
        r"PushT (fresh bank) & 1,600 & 39 & 3 & 5 \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (OUTPUT / "environment_summary.tex").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_model_protocol_summary() -> None:
    v106 = json.loads(
        (REPO_ROOT / "artifacts/v106/v106_protocol.json").read_text(encoding="utf-8")
    )
    medium = v106["frozen_models"]["medium_seed2026"]
    full = v106["frozen_models"]["full_seed2026"]
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Evaluation / capacity & Architecture & Parameters & MACs/candidate & Interface dim. \\",
        r"\midrule",
        (
            r"PushT Medium & MLP 256$\times$2 & "
            f"{int(medium['parameter_count']):,} & "
            f"{int(medium['forward_macs_per_candidate']):,} & 65 \\\\"
        ),
        (
            r"PushT Full & MLP 512$\times$3 & "
            f"{int(full['parameter_count']):,} & "
            f"{int(full['forward_macs_per_candidate']):,} & --- \\\\"
        ),
        r"PyBullet Medium & Transformer 192/4/2 & --- & --- & 59 \\",
        r"PyBullet Full & Transformer 384/6/3 & --- & --- & --- \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (OUTPUT / "model_protocol_summary.tex").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_theory_evidence_map() -> None:
    lines = [
        r"\begin{tabular}{p{0.27\linewidth}p{0.25\linewidth}p{0.40\linewidth}}",
        r"\toprule",
        r"Object & Status & Empirical role \\",
        r"\midrule",
        r"Bayes escalation/value & Standard, adapted & Defines the priced escalation target and oracle. \\",
        r"Nested-interface Jensen gap & Standard value of information & Defines population prediction-interface value. \\",
        r"Standalone-Full decomposition & Protocol-specific identity & Separates optionality from the signed sequential-to-standalone Full latency gap. \\",
        r"Plug-in sign regret & Standard, adapted & Explains why noisy benefit scores can still select usefully. \\",
        r"Finite-audit observability & Protocol-specific formalization & A complete executed record makes candidate-level costs computable; the compact release recomputes paper-facing statistics. \\",
        r"Frozen audit policy gains & New empirical evidence & Tested in the controlled-PyBullet and initial-PushT audits under frozen protocols. \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (OUTPUT / "theory_evidence_map.tex").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_policy_summary() -> None:
    pybullet_grouped: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in read_csv(REPO_ROOT / "artifacts/v104e/policy_metrics.csv"):
        for key in (
            "regret_mean",
            "latency_ms_mean",
            "decision_cost_mean",
            "escalation_rate",
        ):
            pybullet_grouped[row["policy"]][key].append(float(row[key]))

    rows: list[tuple[str, str, float, float, float, float]] = []
    for policy in (
        "Prediction-interface sequential router",
        "Fixed Medium",
        "Fixed Full",
    ):
        metrics = pybullet_grouped[policy]
        rows.append(
            (
                "PyBullet",
                policy.replace("Prediction-interface sequential router", "Router"),
                sum(metrics["regret_mean"]) / len(metrics["regret_mean"]),
                sum(metrics["latency_ms_mean"]) / len(metrics["latency_ms_mean"]),
                sum(metrics["decision_cost_mean"]) / len(metrics["decision_cost_mean"]),
                sum(metrics["escalation_rate"]) / len(metrics["escalation_rate"]),
            )
        )

    pusht = {
        row["policy"]: row
        for row in read_csv(REPO_ROOT / "artifacts/v106/primary_policy_summary.csv")
    }
    for policy in (
        "PushT prediction-interface sequential router",
        "Fixed Medium",
        "Fixed Full",
    ):
        row = pusht[policy]
        rows.append(
            (
                "PushT",
                policy.replace("PushT prediction-interface sequential router", "Router"),
                float(row["regret_mean_equal_seed"]),
                float(row["latency_ms_mean_equal_seed"]),
                float(row["decision_cost_mean_equal_seed"]),
                float(row["escalation_rate_equal_seed"]),
            )
        )

    lines = [
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Evaluation & Policy & Regret & Latency (ms) & Decision cost & Escalation \\",
        r"\midrule",
    ]
    for environment, policy, regret, latency, cost, escalation in rows:
        lines.append(
            f"{environment} & {policy} & {regret:.5f} & {latency:.3f} & "
            f"{cost:.5f} & {100.0 * escalation:.1f}\\% \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (OUTPUT / "policy_summary.tex").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_compute_price_frontier() -> None:
    rows = read_csv(REPO_ROOT / "artifacts/v106/compute_price_frontier.csv")
    candidate_name = "PushT prediction-interface sequential router"
    by_lambda: dict[float, dict[str, float]] = defaultdict(dict)
    for row in rows:
        by_lambda[float(row["lambda"])][row["policy"]] = float(row["decision_cost_mean"])
    references = [
        "Fixed Medium",
        "Fixed Full",
        "Task-only input router",
        "Margin sequential matched-rate",
        "Expected random input matched-rate",
    ]
    lines = [
        r"\begin{tabular}{rrrrrr}",
        r"\toprule",
        r"$\lambda$ & vs. Medium & vs. Full & vs. task-only & vs. margin & vs. random \\",
        r"\midrule",
    ]
    for lam in sorted(by_lambda):
        candidate = by_lambda[lam][candidate_name]
        diffs = [candidate - by_lambda[lam][reference] for reference in references]
        lines.append(
            f"{lam:.3f} & " + " & ".join(f"{value:+.4f}" for value in diffs) + r" \\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (OUTPUT / "compute_price_frontier.tex").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows = primary_rows()
    if len(rows) != 9:
        raise RuntimeError(f"expected 9 primary comparisons, found {len(rows)}")
    write_primary_markdown(rows)
    write_primary_latex(rows)
    write_environment_summary()
    write_model_protocol_summary()
    write_theory_evidence_map()
    write_policy_summary()
    write_compute_price_frontier()
    print(f"Wrote {len(rows)} frozen audit comparisons to {OUTPUT}")


if __name__ == "__main__":
    main()
