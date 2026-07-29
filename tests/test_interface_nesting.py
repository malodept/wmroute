import unittest

import numpy as np

from wmroute.interfaces import prediction_interface_value, upper_tail_mask


class InterfaceNestingTest(unittest.TestCase):
    def test_non_nested_partition_is_rejected(self):
        benefit = np.arange(4, dtype=float)
        coarse = np.array([0, 0, 1, 1])
        non_nested = np.array([0, 1, 0, 1])
        with self.assertRaises(ValueError):
            prediction_interface_value(benefit, coarse, non_nested)

    def test_exact_stable_upper_tail(self):
        mask = upper_tail_mask([1.0, 3.0, 3.0, 0.0], 2)
        np.testing.assert_array_equal(mask, [False, True, True, False])


if __name__ == "__main__":
    unittest.main()
