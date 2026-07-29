# Model and latency cards

## PushT

The frozen visual encoder is DINOv2 ViT-S/14. A \(4\times4\) pooled patch grid
is reduced to 64 dimensions with a frozen PCA transform. Each action-conditioned
predictor maps the current 64-D state and 2-D action to a future-latent
residual.

| Capacity | Predictor | Parameters | MACs per candidate |
|---|---|---:|---:|
| Medium | MLP, 2 GELU hidden layers, width 256 | 99,392 | 98,816 |
| Full | MLP, 3 GELU hidden layers, width 512 | 592,448 | 590,848 |

The predictors use AdamW, learning rate \(10^{-3}\), weight decay \(10^{-4}\),
batch size 256, at most 180 epochs, patience 25, gradient clipping at 1.0, and
three training seeds. Capacity-specific ridge calibrators (alpha 1.0) map the
predicted latent residual and action to physical block-pose displacement; each
calibrator was fit on 180 states / 900 action rows.

The frozen prediction-interface router is a scikit-learn MLP regressor with
hidden widths 128 and 64, ReLU activations, Adam, alpha \(10^{-4}\), learning
rate \(10^{-3}\), batch size 1,024, and 80 iterations without early stopping.
It is fit to the gross paired regret reduction $L_M-L_F$; a compute-price-specific
validation threshold absorbs the constant incremental Full cost within each
frozen seed. Its deployment score is an exported NumPy float32 forward pass.
Thresholds are
selected from 101 validation-score quantiles using a strict greater-than rule.

## Controlled PyBullet

The encoder is again DINOv2 ViT-S/14 pooled to a \(4\times4\) patch grid.
Each predictor is an action-conditioned Transformer that outputs a residual
for every latent token.

| Capacity | Model width | Heads | Layers |
|---|---:|---:|---:|
| Medium | 192 | 4 | 2 |
| Full | 384 | 6 | 3 |

Training uses AdamW, learning rate \(3\times10^{-4}\), weight decay
\(10^{-4}\), dropout 0.05, batch size 32 states, and 100 epochs. The objective
combines same-state action/future contrastive classification with latent
residual MSE. Frozen ridge interfaces map predicted latent summaries and
actions to physical XY displacement. The sealed router reuses the
prediction-only sequential candidate selected before the confirmation banks.

## Latency convention

The primary unit is one physical state, one downstream task, and five candidate
actions. World-model forward latencies were measured on NVIDIA H100 GPUs.
Router and task-interface components were measured single-threaded on the
associated HPC CPU nodes. PushT uses seven rounds, 200 warmups, 1,000 repeats
per round, 512 sampled queries, and the median of round medians; p90 accounting
is a declared sensitivity. PyBullet freezes the end-to-end component medians
from the pre-confirmation readiness audit.

Sequential latency is additive:

\[
c_{\rm seq}=c_M+h_{\rm interface}+
\mathbf 1\{\text{escalate}\}\,c_F.
\]

Fixed Full pays only \(c_F\) (plus its own decision operation). Therefore
escalation duplicates predictive computation rather than replacing Medium.
This is why the learned routers can reduce priced decision cost while remaining
slower than Fixed Full.

The exact CPU SKU was not recorded in the compact archival metadata. Absolute
latencies should therefore be interpreted as measurements of the frozen
hardware/software protocol, not portable hardware benchmarks.
