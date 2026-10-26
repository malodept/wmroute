# V106 PushT → OmniSim V2 — pre-outcome commitment

Freeze prepared 2026-10-26, before any V2 external target-engine outcomes have been received. This is a prospective **amendment**, not the original 2026-10-25 exact-action-index protocol. V1 64-state results are historical and exploratory.

## Scientific design
128 untouched V106 physical states × five candidate actions × four unchanged OmniSim physics conditions = 2,560 target-engine launches. The primary physics is `physical_robustness_mu_0p5`; mu=.25, mu=1.0 and momentum-free are secondary. Preserve original V106 Medium/Full predictive checkpoints and binary route decisions, task family, latency and lambda=0.002 per ms. Do not recalibrate models/thresholds from V2 target outcomes.

Original selected Medium/Full candidate indices for V2 were unavailable. Instead of substituting arbitrary indices, each model's action is **partially identified** by all source-engine actions having original Pymunk regret within 1e-6 of the immutable published regret. The new source-only replay yields 29,952 model/seed/task classes (20,088 singleton and 9,864 ambiguous), with zero empty classes. Under each target engine, propagate all compatible candidates to lower/upper target task-loss and priced-cost bounds. This does not constitute exact action-index recovery.

Primary estimand: paired *erosion* in router-minus-Fixed-Medium priced decision cost: [OmniSim mu=.5] minus [Pymunk source]. Average all 117 seed×task observations within each physical state and then average equally across the 128 states. Inferential interval: 20,000 state-cluster bootstraps of all 128 states with replacement, NumPy default_rng seed 20261025. Conservative 95% interval = quantile .025 of bootstrap lower endpoints, quantile .975 of bootstrap upper endpoints. Entire interval >0 supports erosion; <0 supports improvement; otherwise inconclusive. Retain all geometrically flagged states and non-planar target rollouts, transparently flag them; missing rollouts invalidate the complete-primary-analysis claim.

## Cryptographic bytes (SHA256)

| File | SHA256 |
|---|---|
| V106_V2_PARTIAL_IDENTIFICATION_READY_20261026.zip | `ce721137cd662a3559e59a96fa0c7c4fcb086134871c7db964323cdb3373cfbb` |
| BLIND_ENGINE_PACKAGE_V2_128.tar.gz | `582b435f4395357201ece73261e4b7cda609e522ac8a5fbbd92720db5b7eddd7` |
| execution_inputs_blind.json inside TAR | `becd99eb33f7c64ab3dec606d221949df30bed254e1a510ccc351f1ae7c12af4` |
| V106_CROSSSIM_ROUTING_TRANSFER_V2_128_20261025.zip | `af290475ccb70e982dc36081cbf6cbefb380ebcf282eadfbae81e94e3a574a1b` |
| PROTOCOL_AMENDMENT_PARTIAL_IDENTIFICATION_20261026.md | `49733ea14daa73716dd5ec3a8a73ecd7df8042b29a8c2e952ba4f4edd598500e` |
| analyze_v2_partial_id.py | `f90c79346ba7dac511d3ab7d74d3000c29812efd78d1190df91233ebb3894cba` |
| v2_regret_compatible_action_sets.csv | `88fa2229c73d23da0dc3f866cd35fffbe90b859600f39aa5abed074cde9bc6fe` |
| v2_pymunk_replayed_candidates.npz | `ebd798a8b8ba071bf5a987644824e0b74ef3723cede11a9fe405d0a97d10c77f` |
| OLD64_TEST_RESULTS.json.txt | `c95cc2b41e820d9633ac164450f35c48837fb01aabaf90adb043991843ff8024` |

Cohort ledger internal JSON hash: `d5581af4c373196cd6bbe0fa6402f620c8810caff8330f3a2d91dae641d730dc`. Source V106 scientific task protocol hash: `0603397fcf3b5209ac2a92a70a334b23c61083b5ff7fc87e5972e52737bf514d`.

**Preservation rule:** Publish this commitment to a timestamped external repository **before** V2 target simulator executions. The above hashes only prove immutability if the corresponding files are retained. Any future amendment must be newly dated and transparently distinguished. The scientific package contains historical V1 fixtures but **no new V2 external outcomes**.
