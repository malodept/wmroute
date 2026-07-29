import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class TableReproductionTest(unittest.TestCase):
    def test_primary_snapshot(self):
        v104e = {
            row["reference"]: float(row["cost_difference_candidate_minus_reference"])
            for row in rows(ROOT / "artifacts/v104e/repaired_inference/global_primary_fixed_seed_state_clustered.csv")
        }
        v106 = {
            row["reference"]: float(row["cost_difference_candidate_minus_reference"])
            for row in rows(ROOT / "artifacts/v106/global_primary_bootstrap.csv")
        }
        self.assertAlmostEqual(v104e["Fixed Medium"], -0.0036772961183432016)
        self.assertAlmostEqual(v104e["Fixed Full"], -0.003746314265757149)
        self.assertAlmostEqual(v106["Fixed Medium"], -0.004307652735007721)
        self.assertAlmostEqual(v106["Fixed Full"], -0.002576937001531322)
        self.assertAlmostEqual(
            v106["Task-only input router"], -0.002619876386493737
        )

    def test_all_primary_gates_pass(self):
        combined = rows(ROOT / "artifacts/v104e/repaired_inference/global_primary_fixed_seed_state_clustered.csv") + rows(
            ROOT / "artifacts/v106/global_primary_bootstrap.csv"
        )
        self.assertEqual(len(combined), 9)
        self.assertTrue(all(row["adjusted_upper_below_zero"] == "True" for row in combined))

    def test_state_heterogeneity_snapshot(self):
        derived = {
            row["environment"]: row
            for row in rows(ROOT / "artifacts/derived_state_heterogeneity.csv")
        }
        self.assertAlmostEqual(float(derived["PyBullet"]["full_better_rate"]), 0.48125)
        self.assertAlmostEqual(float(derived["PushT"]["full_better_rate"]), 0.54875)


if __name__ == "__main__":
    unittest.main()
