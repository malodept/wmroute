# Scientific artifacts

This directory contains compact summaries **and the row-level audit evidence
needed for paper-facing inference recomputation**.

- `v104e/`: controlled PyBullet protocol, compact summaries, `per_state.csv`,
  three confirmation arrays, and `repaired_inference/`.
- `v106/`: initial PushT protocol, compact summaries, `per_state_primary.csv`, three
  primary arrays, declared sensitivity files, and the compute-price frontier.
- `v107/`: prospectively sealed second PushT bank, confirmation protocol, six
  frozen routers, current-DINO/action projection, per-state effects, exact
  bootstrap draws, price sensitivity, and repeated postchecks.
- `frozen_source_sha256.csv`: executed-source hashes.
- `v106_declared_dependency_inventory.csv`: declared upstream PushT dependency
  hashes; many external binaries remain separately licensed/distributed.
- `collector_runtime.json`: records that the archival collector did not train,
  generate outcomes, or modify thresholds.
- `sealed_result_archives.csv`: historical lookup record from the first
  collector. A later repair collection recovered a V104E result tar whose
  checksum matches its archived `.sha256` file.
- `derived_state_heterogeneity.csv`: unique-physical-state ordering after tasks
  and frozen seed effects are averaged.

The original V104E bootstrap output is retained for provenance. Corrected
paper-facing PyBullet intervals come only from
`v104e/repaired_inference/global_primary_fixed_seed_state_clustered.csv`; the
crossed-seed file is a sensitivity analysis.

Artifacts and hashes establish released-record consistency. Seal chronology is
supported by recovered records and logs but is not independently certified by
an external timestamp service.
