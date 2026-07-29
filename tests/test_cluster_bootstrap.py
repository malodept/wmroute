import unittest

import numpy as np

from wmroute.statistics import clustered_paired_bootstrap


class ClusterBootstrapTest(unittest.TestCase):
    def test_fixed_seed_is_reproducible(self):
        difference = np.array([-1.0, -1.0, 1.0, 1.0, -2.0, -2.0])
        cluster = np.array([0, 0, 1, 1, 2, 2])
        first = clustered_paired_bootstrap(
            difference, cluster, repetitions=500, seed=17
        )
        second = clustered_paired_bootstrap(
            difference, cluster, repetitions=500, seed=17
        )
        self.assertEqual(first, second)
        self.assertAlmostEqual(first.estimate, -2.0 / 3.0)


if __name__ == "__main__":
    unittest.main()
