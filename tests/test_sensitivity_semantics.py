import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SensitivitySemanticsTest(unittest.TestCase):
    def test_crossed_outputs_are_quantiles_not_ci(self):
        paths = [
            ROOT
            / "artifacts/v104e/repaired_inference/global_crossed_seed_state_sensitivity.csv",
            ROOT
            / "artifacts/v106/repaired_inference/crossed_seed_state_sensitivity.csv",
        ]
        for path in paths:
            with path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertTrue(rows)
            self.assertIn("sensitivity_q025", rows[0])
            self.assertIn("sensitivity_q975", rows[0])
            self.assertNotIn("ci95_low", rows[0])
            self.assertTrue(
                all(row["population_confidence_interval"] == "False" for row in rows)
            )


if __name__ == "__main__":
    unittest.main()
