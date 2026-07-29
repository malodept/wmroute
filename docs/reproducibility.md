# Reproducibility

This public release is designed for **paper-facing recomputation**. It includes
compact arrays, per-state tables, seals, manifests, threshold records, and the
code needed to reproduce the reported audit statistics, tables, and figures
without a simulator or GPU.

## One-command check

```bash
python -m pip install -r requirements/verification.txt
python -m pip install -e .
bash scripts/run_all_checks.sh
```

The checks cover:

- routing-cost and value-of-information identities;
- state-clustered and crossed state/seed bootstrap semantics;
- strict float32 threshold replay;
- prospective-confirmation seal status and primary gate;
- exact reconstruction of the 20,000 confirmation bootstrap draws;
- paper-facing result snapshots;
- table and figure generation.

## Reproduction levels

1. **Paper-facing verification:** fully supported by this repository.
2. **Audit recomputation from released per-state records:** supported.
3. **Physical outcome regeneration:** not included in this public candidate.
   It requires external PushT/PyBullet environments, DINOv2 assets, upstream
   predictor checkpoints, and environment-specific execution infrastructure.

The exact executed source snapshot and additional provenance records are kept
in a separate private audit package while redistribution rights are reviewed.
