"""Paired, cluster-respecting uncertainty utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike


@dataclass(frozen=True)
class BootstrapResult:
    estimate: float
    ci_low: float
    ci_high: float
    repetitions: int


def clustered_paired_bootstrap(
    paired_difference: ArrayLike,
    cluster_id: ArrayLike,
    *,
    repetitions: int = 10_000,
    confidence: float = 0.95,
    seed: int = 0,
) -> BootstrapResult:
    """Bootstrap the mean paired difference by resampling whole clusters."""

    difference = np.asarray(paired_difference, dtype=np.float64)
    clusters = np.asarray(cluster_id)
    if difference.ndim != 1 or clusters.ndim != 1 or len(difference) != len(clusters):
        raise ValueError("paired_difference and cluster_id must be aligned vectors")
    if not np.all(np.isfinite(difference)):
        raise ValueError("paired_difference must be finite")
    if repetitions <= 0:
        raise ValueError("repetitions must be positive")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must lie strictly between zero and one")

    unique, inverse = np.unique(clusters, return_inverse=True)
    if len(unique) < 2:
        raise ValueError("at least two clusters are required")
    cluster_means = np.asarray(
        [difference[inverse == index].mean() for index in range(len(unique))],
        dtype=np.float64,
    )
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(unique), size=(repetitions, len(unique)))
    bootstrap_means = cluster_means[draws].mean(axis=1)
    alpha = 1.0 - confidence
    low, high = np.quantile(bootstrap_means, [alpha / 2.0, 1.0 - alpha / 2.0])
    return BootstrapResult(
        estimate=float(cluster_means.mean()),
        ci_low=float(low),
        ci_high=float(high),
        repetitions=int(repetitions),
    )


def crossed_state_seed_bootstrap_draws(
    state_by_seed: ArrayLike,
    *,
    repetitions: int = 10_000,
    seed: int = 0,
) -> np.ndarray:
    """Bootstrap a crossed physical-state by model-seed mean.

    ``state_by_seed`` has shape ``(n_states, n_seeds)``. Every replicate draws
    model-seed positions and one shared physical-state index vector; that same
    state vector is applied to every sampled seed position. This preserves the
    shared-state crossing of the experiment.
    """
    values = np.asarray(state_by_seed, dtype=np.float64)
    if values.ndim != 2:
        raise ValueError("state_by_seed must have shape (n_states, n_seeds)")
    n_states, n_seeds = values.shape
    if n_states < 2 or n_seeds < 1:
        raise ValueError("at least two states and one seed are required")
    if not np.all(np.isfinite(values)):
        raise ValueError("state_by_seed must be finite")
    if repetitions <= 0:
        raise ValueError("repetitions must be positive")
    rng = np.random.default_rng(int(seed))
    draws = np.empty(int(repetitions), dtype=np.float64)
    chunk_size = 256
    for start in range(0, int(repetitions), chunk_size):
        end = min(start + chunk_size, int(repetitions))
        chunk = end - start
        sampled_seed_positions = rng.integers(0, n_seeds, size=(chunk, n_seeds))
        sampled_state_indices = rng.integers(0, n_states, size=(chunk, n_states))
        for row in range(chunk):
            selected = values[:, sampled_seed_positions[row]]
            draws[start + row] = selected[sampled_state_indices[row], :].mean()
    return draws
