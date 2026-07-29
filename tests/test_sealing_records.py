import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SealingRecordsTest(unittest.TestCase):
    def test_initial_push_and_pybullet_sealing_flags(self):
        pybullet = json.loads((ROOT / "artifacts/v104e/summary.json").read_text())
        pusht = json.loads((ROOT / "artifacts/v106/manifest.json").read_text())
        self.assertTrue(pybullet["sealed_before_outcomes"])
        self.assertTrue(pusht["router_sealed_before_audit_generation"])
        self.assertFalse(pusht["audit_used_for_training_threshold_or_latency"])

    def test_prospective_confirmation_seal_precedes_outcomes(self):
        seal = json.loads((ROOT / "artifacts/v107/frozen/v107_protocol_seal.json").read_text())
        self.assertFalse(seal["physical_outcomes_present_at_seal"])
        self.assertFalse(seal["audit_accessed_at_seal"])
        self.assertEqual(seal["fresh_reset_seed_overlap_count"], 0)


if __name__ == "__main__":
    unittest.main()
