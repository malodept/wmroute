# Decision theory for prediction-interface routing

This document states the mathematical objects implemented in `src/wmroute/`
and used to organize the paper. The core rules are standard adaptations of
value-of-information, cost-sensitive cascade, and binary selection theory.
The paper-specific contribution is the paired physical protocol, information
restriction, deployment accounting, and frozen audit evidence.

## 1. Query, decisions, and paired outcomes

A query \(Q=(X,T,\mathcal A)\) contains a current observation \(X\), a
downstream task/loss specification \(T\), and a measurably enumerated finite
action set \(\mathcal A\). A frozen model-decision pipeline \(m\in\{M,F\}\)
selects

\[
A_m(Q)\in\arg\min_{a\in\mathcal A}
\ell_T\!\left(\widehat Y_m(Q,a)\right)
\]

with a fixed tie rule. Exact reset records \(Y(Q,a)\) for every candidate, so

\[
L_m(Q)=\ell_T\!\left(Y(Q,A_m)\right)
-\min_{a\in\mathcal A}\ell_T\!\left(Y(Q,a)\right)
\]

is observable for both models on the same physical query. This is finite-action
simulator regret, not unrestricted control value or a real-robot causal
estimand.

## 2. Sequential escalation

Let \(s_{\mathcal G}(Q)\) be the always-paid cost required to run Medium and
expose routing information \(\mathcal G\), and let \(d_F(Q)\) be the
additional cost of a complete Full pass after Medium. At price \(\lambda\),

\[
B=L_M-L_F-\lambda d_F.
\]

A binary \(\mathcal G\)-measurable policy has cost

\[
C_{\mathcal G}(\pi)=L_M+\lambda s_{\mathcal G}-\pi B.
\]

Writing \(b_{\mathcal G}=\mathbb E[B\mid\mathcal G]\), the Bayes rule and
available value are

\[
\pi^\star_{\mathcal G}=\mathbf 1\{b_{\mathcal G}>0\},\qquad
V(\mathcal G)=\mathbb E[(b_{\mathcal G})_+].
\]

These require integrability and unrestricted measurable binary decisions;
ties at zero may be resolved arbitrarily.

## 3. Standalone Full is not sequential always-escalate

Let \(c_M,c_F\) be standalone latencies. The Bayes sequential gain over
standalone Medium is

\[
V(\mathcal G)-\lambda\mathbb E[s_{\mathcal G}-c_M].
\]

Define the signed sequential-to-standalone Full latency gap

\[
\kappa_{\mathcal G}=s_{\mathcal G}+d_F-c_F.
\]

The gain over standalone Full is

\[
\mathbb E[(-b_{\mathcal G})_+]
-\lambda\mathbb E[\kappa_{\mathcal G}].
\]

The negative-part term is the value of retaining Medium on harmful escalation
queries; the second term charges the Medium-first computation that standalone
Full avoids.

## 4. Prediction-interface value

To attribute a nested-information contrast specifically to Medium's predicted
consequence, every other signal must be held fixed. Use

\[
\mathcal G_0=\sigma(T,R),\qquad
\mathcal G_1=\sigma(T,R,S_M),
\]

where \(R\) is any common regime descriptor. Then

\[
\operatorname{PIV}(S_M\mid T,R)
=V(\mathcal G_1)-V(\mathcal G_0)
=\mathbb E\!\left[
(\mathbb E[B\mid\mathcal G_1])_+
-(\mathbb E[B\mid\mathcal G_0])_+
\right]\ge0.
\]

Let \(U=\mathbb E[B\mid\mathcal G_1]\). The gap is positive exactly when a
positive-probability set of coarse outcomes has both
\(\mathbb E[U_+\mid\mathcal G_0]>0\) and
\(\mathbb E[(-U)_+\mid\mathcal G_0]>0\). If the always-paid interface costs
differ, subtract
\(\lambda\mathbb E[s_{\mathcal G_1}-s_{\mathcal G_0}]\).

The PushT task-only comparator routes before Medium and is latency advantaged.
It is evidence that the executed rich interface is useful relative to that
control; it is not a numerical estimator of the ideal same-protocol population
Jensen gap. PyBullet additionally exposes a regime descriptor and has no
confirmation-stage task-only comparator, so it is not an independent PIV test.

## 5. Learned selection regret

For \(\widehat\pi=\mathbf 1\{\widehat b>0\}\), condition on all development
data, validation-based threshold selection, and algorithmic randomness that
freeze the learned policy. Then

\[
\mathbb E[C_{\mathcal G}(\widehat\pi)]
-\mathbb E[C_{\mathcal G}(\pi^\star_{\mathcal G})]
=\mathbb E\!\left[
|b_{\mathcal G}|\mathbf 1\{\widehat\pi\ne\pi^\star_{\mathcal G}\}
\right]
\le\mathbb E[|\widehat b-b_{\mathcal G}|].
\]

If \(A<\infty\), \(\alpha\ge0\), \(\varepsilon\ge0\),
\(\Pr(|b_{\mathcal G}|\le t)\le At^\alpha\) for \(t>0\), and
\(|\widehat b-b_{\mathcal G}|\le\varepsilon\) almost surely, the excess cost
is at most \(A\varepsilon^{\alpha+1}\). For \(\varepsilon=0\), any sign
disagreement occurs only where \(b_{\mathcal G}=0\), so the weighted excess is
zero.

The initial PushT router does not literally regress priced \(B\). It regresses gross paired regret
reduction \(L_M-L_F\), then selects a price-specific threshold on validation
cost. In general,
\(\mathbb E[B\mid\mathcal G]=\mathbb E[L_M-L_F\mid\mathcal G]
-\lambda\mathbb E[d_F\mid\mathcal G]\). A constant threshold on a gross-benefit
score is Bayes-equivalent when the conditional expected incremental Full cost
is constant within the deployed checkpoint pair, or when its conditional
variation is absorbed into the score. Observing realized latency at routing
time is sufficient but not necessary. The executed audits satisfy the simpler
constant-within-checkpoint convention.

## 6. Scalar threshold obstruction

If a scalar score ranks a positive-benefit region entirely below a
negative-benefit region, every high-score threshold incurs weighted sign
regret. This is a sufficient obstruction to a single-crossing story, not a
general characterization, and failure of the empirical Medium-margin baseline
does not prove the proposition's setwise assumptions.

## 7. Matched-rate randomized selection

For an arbitrary rate \(q\), exact feasibility requires routing propensities.
Allow a \(\mathcal G\)-measurable \(g:\Omega\to[0,1]\) with
\(\mathbb E[g]=q\), and execute
\(\pi=\mathbf 1\{U\le g\}\) using an independent uniform random variable.
An upper-tail propensity in \(b_{\mathcal G}\), with fractional mass at a
threshold atom when needed, maximizes \(\mathbb E[b_{\mathcal G}g]\). Its
advantage over independent rate-\(q\) routing is

\[
\mathbb E[b_{\mathcal G}g^\star]-q\mathbb E[B]\ge0.
\]

The empirical input-random controls have a different acquisition-cost protocol
and are therefore not exact evaluations of this population identity.

## 8. Finite-audit observability versus population inference

If the record contains every candidate outcome, every frozen policy input and
decision, and all stochastic seeds needed for replay, finite-audit policy costs
and paired differences are deterministic functions of the record. Their finite
empirical means are exactly computable.

A target-population expectation requires an additional sampling law or known
design, declared task/seed weights, and appropriate moment conditions.
Confidence intervals require a method valid for the actual physical-state
clusters and crossed factors. Independence from router fitting prevents direct
reuse bias; it does not by itself imply target-law representativeness.

## 9. Information-preserving recoding

For a finite discrete signal in a standard-Borel space, a one-to-one measurable
recoding preserves its sigma-field and unrestricted measurable Bayes risks,
while coordinate-dependent geometry may change. It does **not** preserve a
restricted neural class, finite-sample learnability, regularization,
optimization, continuity, or compute. It is not a proof that the distinct
Medium and Full experiments are Blackwell-incomparable.

## 10. Status of statements

| Statement | Status |
|---|---|
| Bayes escalation by conditional advantage | Classical binary decision rule |
| Nested-interface Jensen gap | Classical value-of-information monotonicity |
| Plug-in weighted sign identity and margin refinement | Standard classification-style analysis |
| Fixed-rate upper-tail propensity | Standard rearrangement result |
| Standalone-Full duplication ledger | Protocol-specific accounting identity |
| Exact-reset finite-record observability | Paper-specific experimental construction |
| PushT prediction-refined versus withheld comparison | Distinctive finite-sample empirical evidence |
| Corrected controlled-PyBullet/initial-PushT routing gains | Evidence for the frozen tested interfaces |

No new Blackwell theorem, Le Cam deficiency estimator, population PIV estimator,
or finite-sample router learning rate is claimed.


### Phase 1 v4 clarification

The three checkpoint pairs are fixed design factors in primary inference. Crossed checkpoint/state outputs are empirical sensitivity quantiles, not confidence intervals for a checkpoint population. The compact release reconstructs paper-facing policy statistics but does not contain every candidate physical outcome or upstream prediction from first principles. Chronology evidence is self-authored rather than externally timestamped.
