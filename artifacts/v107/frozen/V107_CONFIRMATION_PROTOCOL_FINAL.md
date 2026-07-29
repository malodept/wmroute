# V107 Fresh Prediction-versus-Current-DINO Confirmation Protocol

## Status and temporal ordering

This document fixes the V107 confirmatory analysis before any V107 physical outcome is generated. V106 audit shards and V107 exploratory screens are development data only. They may motivate this design, but they are not confirmatory evidence. Every V107 row is audit-only and must be produced only after the protocol, state manifest, routers, thresholds, latency ledger, projection, source hashes, and confirmation manifest have been sealed.

## Confirmatory question

Under the fixed PushT decision protocol, does a task-conditioned interface derived from the Medium model's complete predicted candidate consequences yield lower priced physical decision cost than an optimistically latency-favoured current-DINO control that is action-conditioned and dimension matched?

The primary comparison is

```text
prediction / direct_gross_regression
minus
dino_action_pca43 / direct_gross_regression
```

Negative values favour the Medium-prediction interface.

## Frozen environment and sampling design

- Environment: `gym_pusht/PushT-v0`.
- Exact-reset physical evaluation.
- Horizon: 30.
- Candidate actions per query: 5.
- Tasks per physical state: 39, inherited unchanged from the sealed V106 protocol.
- Checkpoint pairs: the three fixed Medium/Full pairs with upstream seeds `92002`, `2026`, and `314159`.
- Fresh states: 1,600 audit-only physical states.
- Shards: 2 shards of 800 states.
- Generation base seeds: `2710003` and `2720003`.
- Global-state IDs: `10700000` through `10701599`.
- The reset seeds must not overlap any prior readable reset seed found by the pre-generation scan.
- No V107 state may be used for fitting, projection learning, threshold selection, latency selection, architecture selection, or debugging of scientific choices.

## Frozen interfaces

### Prediction interface

- Routing mode: sequential.
- Features: 22 task features plus the complete 43-dimensional Medium-derived prediction interface.
- Total feature dimension: 65.
- Medium compute is always paid before the routing decision.

### Current-DINO/action control

- Routing mode: input.
- Features: 22 task features plus a 43-dimensional projection of `[z_current, five candidate actions]`.
- Total feature dimension: 65.
- Projection: `StandardScaler` followed by full-solver PCA with 43 components and random seed `10726`.
- Projection fit data: V106 training states only.
- `z_current` is treated as already available; no fresh DINO encoder latency is charged. This deliberately favours the control.

## Frozen learner and thresholding

- Learner family: `StandardScaler + MLPRegressor`.
- Objective: direct regression of gross escalation benefit, independent of the deployment price.
- The six serialized source models are copied exactly from the V107 exploratory objective screen and identified by SHA-256.
- Scientific score implementation: deterministic NumPy float32 forward pass.
- Escalation comparison: strict `score > threshold` in float32 semantics.
- Router overhead is remeasured before V107 outcomes using 200 warm-up queries and 7 rounds of 1,000 queries.
- Thresholds are selected only on V106 validation states using 101 score quantiles plus infinities.
- Primary price: `lambda = 0.002` in

```text
decision cost = physical candidate-set regret + lambda * latency_ms
```

## Primary estimand

For each fresh physical state:

1. average the priced cost difference over the 39 fixed tasks within each checkpoint pair;
2. average those three checkpoint-pair effects within the state;
3. average over the 1,600 fresh physical states.

The estimand is therefore the mean of

```text
cost(prediction) - cost(dino_action_pca43)
```

with physical state as the primary sampling unit. The three checkpoint pairs are fixed-design replicates, not a random population of training runs.

## Primary inference and success gate

- Bootstrap unit: fresh physical state.
- Bootstrap repetitions: 20,000.
- Bootstrap seed: `107031`.
- Primary one-sided upper quantile: 0.95.
- Two-sided 95% interval is reported descriptively.

The primary gate passes only if all three conditions hold:

1. the aggregate point estimate is below zero;
2. the one-sided 95% bootstrap upper bound is below zero;
3. the point estimate is below zero for each of the three fixed checkpoint pairs.

There is one primary comparison. No secondary analysis may replace, rescue, or redefine this gate.

## Prespecified secondary outputs

The audit reports, without changing the primary gate:

- fixed Medium and fixed Full operating points;
- regret, latency, priced cost, and escalation rate by interface and checkpoint pair;
- a fixed-policy price sensitivity grid at `lambda` in `{0, 0.002, 0.005, 0.01, 0.025, 0.05}` using thresholds frozen at `0.002`;
- deterministic NumPy-versus-scikit-learn score diagnostics;
- per-state effects and exact bootstrap draws;
- input lineage and SHA-256 manifests.

These are secondary robustness or reconstruction outputs. They do not create additional confirmatory hypotheses.

## Allowed claim if the gate passes

> On a fresh exact-reset PushT bank, a frozen task-and-Medium-prediction router has lower priced physical decision cost than an optimistically latency-favoured, dimension-matched, action-conditioned current-DINO router, under the prespecified five-action, 39-task, three-checkpoint-pair protocol at lambda = 0.002.

## Claims that remain forbidden

- Prediction is causally sufficient or universally superior to current-state information.
- The result generalizes beyond the tested PushT family, tasks, candidate set, checkpoint pairs, and compute price.
- The router saves raw latency, energy, or total system compute.
- The result is closed-loop control evidence.
- The three checkpoint pairs define a population confidence interval over training randomness.
- The result establishes a new generic routing or value-of-information theory.

## Integrity rules

- Freeze must fail if any V107 outcome already exists.
- Generation and inference must verify the sealed manifest before execution.
- Audit must verify the state manifest, all raw/prepared lineage, model hashes, and protocol hashes.
- Audit output is written to a staging directory, postchecked, atomically moved into place, and postchecked again.
- Any code, model, projection, threshold, task, candidate, latency, seed, or analysis change after sealing requires a new version identifier and a new fresh outcome bank.
