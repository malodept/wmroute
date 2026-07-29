import unittest

import numpy as np

from wmroute.routing import (
    bayes_gain_over_fixed_full,
    bayes_gain_over_fixed_medium,
    plugin_excess_cost,
    sequential_cost,
    sequential_latency,
)


class RoutingCostTest(unittest.TestCase):
    def test_overhead_is_paid_for_every_query(self):
        latency = sequential_latency(
            [False, True],
            medium_latency=2.0,
            full_incremental_latency=3.0,
            interface_latency=0.5,
        )
        np.testing.assert_allclose(latency, [2.5, 5.5])

    def test_sequential_cost(self):
        cost = sequential_cost(
            medium_loss=[4.0, 4.0],
            full_loss=[1.0, 1.0],
            escalation=[False, True],
            medium_latency=2.0,
            full_incremental_latency=3.0,
            interface_latency=0.5,
            compute_price=0.1,
        )
        np.testing.assert_allclose(cost, [4.25, 1.55])

    def test_plugin_identity(self):
        excess = plugin_excess_cost([2.0, -3.0, 1.0], [-1.0, -2.0, 4.0])
        self.assertAlmostEqual(excess, 2.0 / 3.0)

    def test_fixed_policy_decompositions_include_overhead(self):
        conditional = np.array([2.0, -3.0])
        gain_medium = bayes_gain_over_fixed_medium(
            conditional,
            fixed_medium_latency=2.0,
            sequential_base_latency=2.5,
            compute_price=0.1,
        )
        self.assertAlmostEqual(gain_medium, 0.95)

        gain_full = bayes_gain_over_fixed_full(
            conditional,
            fixed_full_latency=3.0,
            sequential_base_latency=2.5,
            full_incremental_latency=3.0,
            compute_price=0.1,
        )
        self.assertAlmostEqual(gain_full, 1.25)


if __name__ == "__main__":
    unittest.main()
