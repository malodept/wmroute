#!/usr/bin/env python3
"""Verify the prospectively sealed PushT current-DINO/action confirmation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CONFIRMATION = ROOT / "artifacts" / "v107"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def assert_close(actual: float, expected: float, tol: float = 1e-15) -> None:
    if abs(float(actual) - float(expected)) > tol:
        raise RuntimeError(f"numeric mismatch: {actual} != {expected}")


def main() -> None:
    audit = CONFIRMATION / "audit"
    frozen = CONFIRMATION / "frozen"
    sealed = CONFIRMATION / "sealed_router"

    manifest = json.loads((audit / "manifest.json").read_text())
    for rel, expected in manifest["output_hashes"].items():
        path = audit / rel
        if not path.is_file():
            raise RuntimeError(f"missing prospective-confirmation audit file: {rel}")
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"prospective-confirmation audit hash mismatch: {rel}")

    confirmation = json.loads((frozen / "v107_confirmation_manifest.json").read_text())
    for rel, expected in confirmation["report_file_hashes"].items():
        path = CONFIRMATION / rel
        if not path.is_file():
            raise RuntimeError(f"missing prospective-confirmation sealed file: {rel}")
        if sha256_file(path) != expected:
            raise RuntimeError(f"prospective-confirmation sealed hash mismatch: {rel}")

    protocol = frozen / "v107_protocol.json"
    if sha256_file(protocol) != confirmation["protocol_sha256"]:
        raise RuntimeError("prospective-confirmation protocol digest mismatch")

    protocol_seal = json.loads((frozen / "v107_protocol_seal.json").read_text())
    router_seal = json.loads((sealed / "router_seal.json").read_text())
    if protocol_seal["physical_outcomes_present_at_seal"]:
        raise RuntimeError("prospective-confirmation outcomes were present at protocol seal")
    if protocol_seal["audit_accessed_at_seal"]:
        raise RuntimeError("prospective-confirmation audit was accessed at protocol seal")
    if router_seal["v107_physical_outcomes_present_at_seal"]:
        raise RuntimeError("prospective-confirmation outcomes were present at router seal")
    if router_seal["v107_states_or_rows_used_for_fit_threshold_or_latency"] != 0:
        raise RuntimeError("prospective-confirmation rows were used for development")
    if router_seal["v106_audit_shards_opened_by_freeze"]:
        raise RuntimeError("initial-audit shards were opened by the prospective-confirmation freeze")

    gate = json.loads((audit / "scientific_gate.json").read_text())
    if not gate["primary_gate_pass"]:
        raise RuntimeError("prospective-confirmation primary gate did not pass")
    if not gate["aggregate_point_negative"]:
        raise RuntimeError("prospective-confirmation aggregate point is not negative")
    if not gate["one_sided_95_upper_below_zero"]:
        raise RuntimeError("prospective-confirmation one-sided upper bound is not negative")
    if not gate["each_checkpoint_pair_point_negative"]:
        raise RuntimeError("a prospective-confirmation checkpoint-pair point is not negative")

    array_path = audit / "arrays" / "v107_primary_confirmation_arrays.npz"
    with np.load(array_path, allow_pickle=False) as data:
        difference = (
            data["prediction_cost_primary"]
            - data["dino_action_pca43_cost_primary"]
        )
        per_seed_state = difference.mean(axis=2)
        combined_state = per_seed_state.mean(axis=0)
        point = float(combined_state.mean())
        assert_close(point, gate["aggregate_point"])
        if np.max(np.abs(per_seed_state - data["per_seed_per_state_difference"])) != 0:
            raise RuntimeError("prospective-confirmation per-checkpoint state effects do not reproduce")
        if np.max(np.abs(combined_state - data["combined_per_state_difference"])) != 0:
            raise RuntimeError("prospective-confirmation combined state effects do not reproduce")

        expected_seed_points = np.asarray(
            [gate["checkpoint_pair_points"][str(int(seed))] for seed in data["upstream_model_seeds"]]
        )
        if np.max(np.abs(per_seed_state.mean(axis=1) - expected_seed_points)) > 1e-15:
            raise RuntimeError("prospective-confirmation checkpoint-pair points do not reproduce")

        rng = np.random.default_rng(107031)
        indices = rng.integers(0, combined_state.size, size=(20_000, combined_state.size))
        draws = combined_state[indices].mean(axis=1)
        archived_draws = data["primary_bootstrap_draws"]
        if np.max(np.abs(draws - archived_draws)) != 0:
            raise RuntimeError("prospective-confirmation bootstrap draws do not reproduce exactly")
        q025, q95, q975 = np.quantile(draws, [0.025, 0.95, 0.975])
        assert_close(q025, gate["state_clustered_ci95_low"])
        assert_close(q95, gate["one_sided_95_upper"])
        assert_close(q975, gate["state_clustered_ci95_high"])

    post = json.loads((audit / "technical_postcheck.json").read_text())
    repeat = json.loads((audit / "technical_postcheck_repeat.json").read_text())
    if post != repeat:
        raise RuntimeError("prospective-confirmation repeated postcheck differs")
    if not post["bootstrap_draws_exactly_reproduced"]:
        raise RuntimeError("prospective-confirmation postcheck did not reproduce bootstrap draws")

    print(
        json.dumps(
            {
                "status": "PROSPECTIVE_CONFIRMATION_VERIFICATION_PASS",
                "fresh_states": post["fresh_states"],
                "tasks": post["tasks"],
                "fixed_checkpoint_pairs": post["fixed_checkpoint_pairs"],
                "primary_point": post["primary_point"],
                "primary_ci95": [post["primary_ci95_low"], post["primary_ci95_high"]],
                "one_sided_95_upper": post["primary_one_sided_95_upper"],
                "primary_gate_pass": post["primary_gate_pass"],
                "output_hashes_verified": len(manifest["output_hashes"]),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
