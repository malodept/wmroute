# Claim ledger

| Claim | Status | Safe wording |
|---|---|---|
| Medium-derived prediction features help routing | Supported directly in PushT | On the fresh PushT audit, the post-Medium router beats a latency-advantaged prediction-withheld task-only router. |
| PyBullet independently isolates prediction value | Not supported | PyBullet supports the frozen task-prediction-regime router relative to fixed, margin, and random references; it has no confirmation-stage task-only control. |
| Routing beats Fixed Medium and Full in priced cost | Supported at \(\lambda=0.002\) | Both environment-specific candidate-minus-fixed point estimates are negative; PushT intervals and repaired PyBullet intervals exclude zero. |
| The PyBullet inference survived repair | Supported | Shared-state pairing was restored; point estimates were unchanged and all four fixed-seed primary and crossed-sensitivity Bonferroni-adjusted percentile-bootstrap upper bounds remain below zero. |
| The router saves compute or latency | Rejected | The sequential router is slower than both fixed policies and only lowers a priced decision objective in the low-price regime. |
| The advantage is a continuous frontier | Rejected | PushT is favorable through the declared \(\lambda=0.01\), but unfavorable against every listed reference at \(0.025\) and \(0.05\). |
| Full is uniformly the better expert | Rejected empirically | Medium and Full reverse ordering across unique physical states after task and seed averaging. |
| Medium and Full are Blackwell/Le Cam incomparable | Not identified | The experiments show reversals for evaluated decision families, not universal experiment incomparability. |
| The learned-to-clairvoyant gap is Bayes selection regret | Rejected | The plotted lower bound uses realized audit outcomes and zero router overhead; the gap mixes unavailable information, learning error, and protocol differences. |
| `1/5001` is a confirmatory p-value | Rejected | It is a descriptive plus-one tail fraction under the specified matched-count random-policy generator. |
| The result generalizes to arbitrary world models | Not supported | Both audits use related calibrated DINO-style interfaces and finite candidate sets. |
| Prediction is causally responsible feature by feature | Not identified | The current controls establish policy-level utility of the rich PushT interface, not causal attribution beyond state/current-latent alternatives. |

## Required headline qualifiers

Any abstract, README, talk, or application statement about a compute-decision
trade-off must also state that:

1. sequential latency exceeds both fixed policies;
2. the direct prediction-withheld comparison is PushT-specific;
3. PyBullet uncertainty is post-audit repaired with unchanged point estimates;
4. the result is restricted to a low compute-price range.

## Statistical conventions

- Candidate-minus-reference differences are paired; negative favors candidate.
- The physical state is the primary sampling cluster.
- The initial PushT audit averages tasks and the three fixed seed effects per state before
  resampling 1,600 states.
- The repaired controlled-PyBullet primary conditions on the three frozen seeds, averages
  their effects per physical state, resamples states within each of six fixed
  equally weighted banks, and uses the 0.9875 one-sided Bonferroni-adjusted percentile-bootstrap quantile.
- The controlled-PyBullet crossed sensitivity resamples seed positions but shares one sampled
  state-index vector across seeds within each bank.
- With only three model seeds, claims are conditional on or sensitive to these
  observed replications; they are not precise population-of-training-runs
  inference.
- Development, frozen audit, post-audit statistical repair, and future new
  experiments must remain explicitly distinguished.


### Phase 1 v4 clarification

The three checkpoint pairs are fixed design factors in primary inference. Crossed checkpoint/state outputs are empirical sensitivity quantiles, not confidence intervals for a checkpoint population. The compact release reconstructs paper-facing policy statistics but does not contain every candidate physical outcome or upstream prediction from first principles. Chronology evidence is self-authored rather than externally timestamped.

## Prospective current-DINO/action confirmation

The prospective confirmation uses a second, non-overlapping 1,600-state PushT bank generated only after
one primary comparison, six routers, a dimension-matched current-DINO/action
projection, thresholds, latency accounting, reset seeds, and a 20,000-draw
state bootstrap were sealed. The primary effect is -0.002549 priced decision
cost with 95% interval [-0.002867, -0.002238] and one-sided 95% upper bound
-0.002286. All three fixed checkpoint-pair effects are negative. The control
routes before Medium, receives current DINO and all five actions, and pays no
DINO encoder latency. This supports incremental value beyond that tested
control, not universal causal superiority of prediction over state.
