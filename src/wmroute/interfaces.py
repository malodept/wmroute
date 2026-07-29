"""Population and finite-partition values of routing information."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import ArrayLike


def _labels_to_keys(labels: ArrayLike | Sequence[ArrayLike], n: int) -> list[tuple]:
    if isinstance(labels, (list, tuple)) and labels:
        arrays = [np.asarray(x) for x in labels]
        if any(a.ndim != 1 or len(a) != n for a in arrays):
            raise ValueError("every label array must be one-dimensional and aligned")
        return list(zip(*(a.tolist() for a in arrays), strict=True))
    array = np.asarray(labels)
    if array.ndim != 1 or len(array) != n:
        raise ValueError("labels must be one-dimensional and aligned")
    return [(x,) for x in array.tolist()]


def conditional_group_means(
    realized_benefit: ArrayLike,
    labels: ArrayLike | Sequence[ArrayLike],
) -> np.ndarray:
    """Estimate E[B | G] by empirical means over a finite partition."""

    benefit = np.asarray(realized_benefit, dtype=np.float64)
    if benefit.ndim != 1 or not np.all(np.isfinite(benefit)):
        raise ValueError("realized_benefit must be a finite one-dimensional array")
    keys = _labels_to_keys(labels, len(benefit))
    sums: dict[tuple, float] = {}
    counts: dict[tuple, int] = {}
    for key, value in zip(keys, benefit, strict=True):
        sums[key] = sums.get(key, 0.0) + float(value)
        counts[key] = counts.get(key, 0) + 1
    means = {key: sums[key] / counts[key] for key in sums}
    return np.asarray([means[key] for key in keys], dtype=np.float64)


def _available_value_from_keys(benefit: np.ndarray, keys: list[tuple]) -> float:
    sums: dict[tuple, float] = {}
    counts: dict[tuple, int] = {}
    for key, value in zip(keys, benefit, strict=True):
        sums[key] = sums.get(key, 0.0) + float(value)
        counts[key] = counts.get(key, 0) + 1
    conditional = np.asarray(
        [sums[key] / counts[key] for key in keys], dtype=np.float64
    )
    return float(np.maximum(conditional, 0.0).mean())


def available_routing_value(
    realized_benefit: ArrayLike,
    labels: ArrayLike | Sequence[ArrayLike],
) -> float:
    """Return E[(E[B | G])_+] for an empirical finite interface."""

    conditional = conditional_group_means(realized_benefit, labels)
    return float(np.maximum(conditional, 0.0).mean())


def population_available_value(conditional_net_benefit: ArrayLike) -> float:
    """Return ``E[(E[B | G])_+]`` from values of ``E[B | G]``.

    The input is the conditional net benefit, not noisy realizations of
    ``B``.  This small distinction mirrors the population quantity used in
    the paper's Bayes rule.
    """

    conditional = np.asarray(conditional_net_benefit, dtype=np.float64)
    if conditional.size == 0 or not np.all(np.isfinite(conditional)):
        raise ValueError("conditional_net_benefit must be finite and non-empty")
    return float(np.maximum(conditional, 0.0).mean())


def nested_interface_value(
    coarse_conditional_benefit: ArrayLike,
    fine_conditional_benefit: ArrayLike,
    *,
    atol: float = 1e-12,
) -> float:
    """Return the population Jensen gap for two already-conditioned signals.

    Callers are responsible for establishing that the fine sigma-field
    refines the coarse one.  For finite empirical partitions, prefer
    :func:`prediction_interface_value`, which checks refinement directly.
    """

    coarse = np.asarray(coarse_conditional_benefit, dtype=np.float64)
    fine = np.asarray(fine_conditional_benefit, dtype=np.float64)
    try:
        coarse, fine = np.broadcast_arrays(coarse, fine)
    except ValueError as exc:
        raise ValueError("conditional-benefit arrays are not broadcastable") from exc
    if coarse.size == 0 or not np.all(np.isfinite(coarse)) or not np.all(
        np.isfinite(fine)
    ):
        raise ValueError("conditional-benefit arrays must be finite and non-empty")
    gap = float(np.maximum(fine, 0.0).mean() - np.maximum(coarse, 0.0).mean())
    if gap < -atol:
        raise ValueError(
            "negative gap: inputs do not satisfy the required nested-conditioning law"
        )
    return max(gap, 0.0)


def prediction_interface_value(
    realized_benefit: ArrayLike,
    task_only_labels: ArrayLike | Sequence[ArrayLike],
    prediction_interface_labels: ArrayLike | Sequence[ArrayLike],
    *,
    atol: float = 1e-12,
) -> float:
    """Return the empirical Jensen gap between nested routing interfaces.

    This estimator is guaranteed non-negative only when the prediction
    partition refines the task-only partition. The function checks that
    nesting condition instead of silently reporting a misleading value.
    """

    benefit = np.asarray(realized_benefit, dtype=np.float64)
    coarse = _labels_to_keys(task_only_labels, len(benefit))
    fine = _labels_to_keys(prediction_interface_labels, len(benefit))
    fine_to_coarse: dict[tuple, tuple] = {}
    for coarse_key, fine_key in zip(coarse, fine, strict=True):
        previous = fine_to_coarse.setdefault(fine_key, coarse_key)
        if previous != coarse_key:
            raise ValueError("prediction_interface_labels do not refine task_only_labels")
    gap = _available_value_from_keys(benefit, fine) - _available_value_from_keys(
        benefit, coarse
    )
    if gap < -atol:
        raise RuntimeError("negative Jensen gap despite a verified nested partition")
    return float(max(gap, 0.0))


def upper_tail_mask(score: ArrayLike, count: int) -> np.ndarray:
    """Select exactly ``count`` rows with largest score using stable tie-breaking."""

    values = np.asarray(score, dtype=np.float64)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise ValueError("score must be a finite one-dimensional array")
    if count < 0 or count > len(values):
        raise ValueError("count must lie between zero and len(score)")
    order = np.argsort(-values, kind="stable")
    mask = np.zeros(len(values), dtype=bool)
    mask[order[:count]] = True
    return mask


def matched_rate_selection_advantage(
    conditional_net_benefit: ArrayLike,
    selected: ArrayLike,
) -> float:
    """Return improvement over independent random routing at the same rate.

    If ``selected`` has mean ``q``, the quantity is

    ``E[b * selected] - q E[b]``.

    It isolates selection from escalation count.  It is non-negative for an
    exact upper-tail selection of ``b`` and can be negative for an arbitrary
    learned score.
    """

    benefit = np.asarray(conditional_net_benefit, dtype=np.float64)
    route = np.asarray(selected, dtype=bool)
    try:
        benefit, route = np.broadcast_arrays(benefit, route)
    except ValueError as exc:
        raise ValueError("conditional benefit and selected are not broadcastable") from exc
    if benefit.size == 0 or not np.all(np.isfinite(benefit)):
        raise ValueError("conditional_net_benefit must be finite and non-empty")
    rate = float(route.mean())
    return float(np.mean(benefit * route) - rate * np.mean(benefit))
