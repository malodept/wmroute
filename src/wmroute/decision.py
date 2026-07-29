"""Core cost and realized-benefit definitions."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray


def realized_net_benefit(
    medium_loss: ArrayLike,
    full_loss: ArrayLike,
    incremental_cost: ArrayLike,
    compute_price: float,
) -> NDArray[np.float64]:
    """Return the realized net benefit of escalating from Medium to Full.

    Positive values mean that the physical-loss reduction exceeds the priced
    incremental computation:

        B = L_medium - L_full - lambda * delta_cost.
    """

    if compute_price < 0:
        raise ValueError("compute_price must be non-negative")
    medium = np.asarray(medium_loss, dtype=np.float64)
    full = np.asarray(full_loss, dtype=np.float64)
    delta = np.asarray(incremental_cost, dtype=np.float64)
    try:
        medium, full, delta = np.broadcast_arrays(medium, full, delta)
    except ValueError as exc:
        raise ValueError("losses and incremental_cost are not broadcastable") from exc
    if not np.all(np.isfinite(medium)) or not np.all(np.isfinite(full)):
        raise ValueError("loss arrays must be finite")
    if not np.all(np.isfinite(delta)) or np.any(delta < 0):
        raise ValueError("incremental_cost must be finite and non-negative")
    return medium - full - float(compute_price) * delta


def priced_decision_cost(
    physical_loss: ArrayLike,
    measured_cost: ArrayLike,
    compute_price: float,
) -> NDArray[np.float64]:
    """Return physical loss plus priced measured computation."""

    if compute_price < 0:
        raise ValueError("compute_price must be non-negative")
    loss = np.asarray(physical_loss, dtype=np.float64)
    cost = np.asarray(measured_cost, dtype=np.float64)
    try:
        loss, cost = np.broadcast_arrays(loss, cost)
    except ValueError as exc:
        raise ValueError("physical_loss and measured_cost are not broadcastable") from exc
    if not np.all(np.isfinite(loss)):
        raise ValueError("physical_loss must be finite")
    if not np.all(np.isfinite(cost)) or np.any(cost < 0):
        raise ValueError("measured_cost must be finite and non-negative")
    return loss + float(compute_price) * cost
