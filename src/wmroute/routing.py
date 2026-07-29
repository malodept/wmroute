"""Binary sequential-routing objectives."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .decision import priced_decision_cost


def optimal_binary_router(conditional_net_benefit: ArrayLike) -> NDArray[np.bool_]:
    """Escalate exactly where the conditional net benefit is positive."""

    benefit = np.asarray(conditional_net_benefit, dtype=np.float64)
    if not np.all(np.isfinite(benefit)):
        raise ValueError("conditional_net_benefit must be finite")
    return benefit > 0.0


def sequential_latency(
    escalation: ArrayLike,
    medium_latency: ArrayLike,
    full_incremental_latency: ArrayLike,
    interface_latency: ArrayLike = 0.0,
) -> NDArray[np.float64]:
    """Return total latency for a Medium-first sequential policy.

    The interface overhead is paid on every query. Full's incremental latency
    is paid only when the policy escalates.
    """

    route = np.asarray(escalation, dtype=bool)
    medium = np.asarray(medium_latency, dtype=np.float64)
    full_delta = np.asarray(full_incremental_latency, dtype=np.float64)
    interface = np.asarray(interface_latency, dtype=np.float64)
    try:
        route, medium, full_delta, interface = np.broadcast_arrays(
            route, medium, full_delta, interface
        )
    except ValueError as exc:
        raise ValueError("latency inputs are not broadcastable") from exc
    for name, array in (
        ("medium_latency", medium),
        ("full_incremental_latency", full_delta),
        ("interface_latency", interface),
    ):
        if not np.all(np.isfinite(array)) or np.any(array < 0):
            raise ValueError(f"{name} must be finite and non-negative")
    return medium + interface + route.astype(np.float64) * full_delta


def sequential_cost(
    medium_loss: ArrayLike,
    full_loss: ArrayLike,
    escalation: ArrayLike,
    medium_latency: ArrayLike,
    full_incremental_latency: ArrayLike,
    compute_price: float,
    interface_latency: ArrayLike = 0.0,
) -> NDArray[np.float64]:
    """Return the overhead-inclusive decision cost of a sequential policy."""

    route = np.asarray(escalation, dtype=bool)
    medium = np.asarray(medium_loss, dtype=np.float64)
    full = np.asarray(full_loss, dtype=np.float64)
    try:
        route, medium, full = np.broadcast_arrays(route, medium, full)
    except ValueError as exc:
        raise ValueError("loss and escalation inputs are not broadcastable") from exc
    selected_loss = np.where(route, full, medium)
    latency = sequential_latency(
        route, medium_latency, full_incremental_latency, interface_latency
    )
    return priced_decision_cost(selected_loss, latency, compute_price)


def plugin_excess_cost(
    conditional_net_benefit: ArrayLike,
    estimated_net_benefit: ArrayLike,
) -> float:
    """Evaluate E[|b| 1{sign(b_hat) != sign(b)}]."""

    truth = np.asarray(conditional_net_benefit, dtype=np.float64)
    estimate = np.asarray(estimated_net_benefit, dtype=np.float64)
    try:
        truth, estimate = np.broadcast_arrays(truth, estimate)
    except ValueError as exc:
        raise ValueError("benefit arrays are not broadcastable") from exc
    mismatch = (truth > 0.0) != (estimate > 0.0)
    return float(np.mean(np.abs(truth) * mismatch))


def bayes_gain_over_fixed_medium(
    conditional_net_benefit: ArrayLike,
    *,
    fixed_medium_latency: ArrayLike,
    sequential_base_latency: ArrayLike,
    compute_price: float,
) -> float:
    """Return the Bayes sequential router's gain over standalone Medium.

    ``conditional_net_benefit`` already prices the incremental Full
    computation.  The remaining subtraction is the always-paid latency gap
    between obtaining the sequential interface and running Fixed Medium.
    """

    if compute_price < 0:
        raise ValueError("compute_price must be non-negative")
    benefit = np.asarray(conditional_net_benefit, dtype=np.float64)
    medium = np.asarray(fixed_medium_latency, dtype=np.float64)
    base = np.asarray(sequential_base_latency, dtype=np.float64)
    try:
        benefit, medium, base = np.broadcast_arrays(benefit, medium, base)
    except ValueError as exc:
        raise ValueError("gain inputs are not broadcastable") from exc
    if benefit.size == 0 or not np.all(np.isfinite(benefit)):
        raise ValueError("conditional_net_benefit must be finite and non-empty")
    if (
        not np.all(np.isfinite(medium))
        or not np.all(np.isfinite(base))
        or np.any(medium < 0)
        or np.any(base < 0)
    ):
        raise ValueError("latencies must be finite and non-negative")
    available = np.maximum(benefit, 0.0).mean()
    overhead = np.mean(base - medium)
    return float(available - compute_price * overhead)


def bayes_gain_over_fixed_full(
    conditional_net_benefit: ArrayLike,
    *,
    fixed_full_latency: ArrayLike,
    sequential_base_latency: ArrayLike,
    full_incremental_latency: ArrayLike,
    compute_price: float,
) -> float:
    """Return the Bayes sequential router's gain over standalone Full.

    The negative-part value is reduced by the signed sequential-to-standalone Full latency gap incurred by
    running Medium and the interface before optionally running Full.  This is
    deliberately distinct from comparison with ``always escalate`` inside the
    sequential protocol.
    """

    if compute_price < 0:
        raise ValueError("compute_price must be non-negative")
    benefit = np.asarray(conditional_net_benefit, dtype=np.float64)
    fixed_full = np.asarray(fixed_full_latency, dtype=np.float64)
    base = np.asarray(sequential_base_latency, dtype=np.float64)
    full_delta = np.asarray(full_incremental_latency, dtype=np.float64)
    try:
        benefit, fixed_full, base, full_delta = np.broadcast_arrays(
            benefit, fixed_full, base, full_delta
        )
    except ValueError as exc:
        raise ValueError("gain inputs are not broadcastable") from exc
    if benefit.size == 0 or not np.all(np.isfinite(benefit)):
        raise ValueError("conditional_net_benefit must be finite and non-empty")
    for name, value in (
        ("fixed_full_latency", fixed_full),
        ("sequential_base_latency", base),
        ("full_incremental_latency", full_delta),
    ):
        if not np.all(np.isfinite(value)) or np.any(value < 0):
            raise ValueError(f"{name} must be finite and non-negative")
    optionality = np.maximum(-benefit, 0.0).mean()
    duplication = np.mean(base + full_delta - fixed_full)
    return float(optionality - compute_price * duplication)
