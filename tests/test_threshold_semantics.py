import csv
import hashlib
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


class ThresholdSemanticsTest(unittest.TestCase):
    def test_v106_all_grid_semantics(self):
        path = ROOT / "artifacts/v106/threshold_semantics_audit.csv"
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 36)
        self.assertTrue(
            all(
                row["score_dtype"] == "float32"
                and row["comparison"] == "strict_greater_than"
                for row in rows
            )
        )
        task_only = [row for row in rows if row["interface"] == "task_only_baseline"]
        self.assertEqual(sum(int(row["equality_count"]) for row in task_only), 17_600)
        self.assertEqual(
            sum(int(row["pandas_float64_replay_changed_decisions"]) for row in rows),
            6_400,
        )
        # Rebuild every mask from the released float32 scores and exact threshold
        # strings, rather than merely trusting the audit CSV.
        import importlib.util
        script = ROOT / "scripts/build_replay_semantics_audits.py"
        spec = importlib.util.spec_from_file_location("replay_audit_test", script)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        rebuilt = module.build_v106_threshold_rows(ROOT)
        self.assertEqual(rows, [{key: str(value) for key, value in row.items()} for row in rebuilt])

    def test_v104e_archived_masks(self):
        path = ROOT / "artifacts/v104e/escalation_mask_checksums.csv"
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 15)
        for row in rows:
            archive = (
                ROOT
                / f"artifacts/v104e/arrays/confirmation_arrays_seed{row['capacity_seed']}.npz"
            )
            with np.load(archive) as payload:
                escalation = np.asarray(payload[row["policy_key"]], dtype=np.int8)
            self.assertEqual(
                hashlib.sha256(escalation.tobytes()).hexdigest(),
                row["mask_sha256"],
            )


if __name__ == "__main__":
    unittest.main()
