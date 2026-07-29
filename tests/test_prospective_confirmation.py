from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ProspectiveConfirmationTest(unittest.TestCase):
    def test_primary_gate_and_values(self) -> None:
        gate = json.loads(
            (ROOT / "artifacts/v107/audit/scientific_gate.json").read_text()
        )
        self.assertTrue(gate["primary_gate_pass"])
        self.assertAlmostEqual(gate["aggregate_point"], -0.0025493366853158186)
        self.assertAlmostEqual(gate["state_clustered_ci95_low"], -0.0028669004993478442)
        self.assertAlmostEqual(gate["state_clustered_ci95_high"], -0.002238474267725135)
        self.assertAlmostEqual(gate["one_sided_95_upper"], -0.002286383099371905)
        self.assertTrue(all(value < 0 for value in gate["checkpoint_pair_points"].values()))

    def test_seal_precedes_outcomes(self) -> None:
        seal = json.loads(
            (ROOT / "artifacts/v107/frozen/v107_protocol_seal.json").read_text()
        )
        self.assertFalse(seal["physical_outcomes_present_at_seal"])
        self.assertFalse(seal["audit_accessed_at_seal"])
        self.assertEqual(seal["fresh_reset_seed_overlap_count"], 0)


if __name__ == "__main__":
    unittest.main()
