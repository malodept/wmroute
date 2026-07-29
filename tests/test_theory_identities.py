import unittest

import numpy as np

from wmroute.interfaces import (
    matched_rate_selection_advantage,
    nested_interface_value,
    upper_tail_mask,
)
from wmroute.routing import (
    bayes_gain_over_fixed_full,
    bayes_gain_over_fixed_medium,
    sequential_cost,
)


class TheoryIdentityTest(unittest.TestCase):
    def test_deployment_decomposition_matches_direct_costs(self):
        medium_loss = np.array([4.0, 1.0, 3.0, 2.0])
        full_loss = np.array([1.0, 3.0, 2.0, 4.0])
        fixed_medium_latency = 2.0
        fixed_full_latency = 3.0
        sequential_base_latency = 2.5
        full_incremental_latency = 3.0
        compute_price = 0.1

        benefit = (
            medium_loss
            - full_loss
            - compute_price * full_incremental_latency
        )
        bayes_route = benefit > 0.0
        routed = sequential_cost(
            medium_loss,
            full_loss,
            bayes_route,
            medium_latency=sequential_base_latency,
            full_incremental_latency=full_incremental_latency,
            interface_latency=0.0,
            compute_price=compute_price,
        )
        fixed_medium = medium_loss + compute_price * fixed_medium_latency
        fixed_full = full_loss + compute_price * fixed_full_latency

        np.testing.assert_allclose(
            fixed_medium.mean() - routed.mean(),
            bayes_gain_over_fixed_medium(
                benefit,
                fixed_medium_latency=fixed_medium_latency,
                sequential_base_latency=sequential_base_latency,
                compute_price=compute_price,
            ),
        )
        np.testing.assert_allclose(
            fixed_full.mean() - routed.mean(),
            bayes_gain_over_fixed_full(
                benefit,
                fixed_full_latency=fixed_full_latency,
                sequential_base_latency=sequential_base_latency,
                full_incremental_latency=full_incremental_latency,
                compute_price=compute_price,
            ),
        )

    def test_jensen_gap_requires_nested_conditioning_law(self):
        coarse = np.array([0.5, 0.5, -0.5, -0.5])
        fine = np.array([2.0, -1.0, 1.0, -2.0])
        self.assertAlmostEqual(nested_interface_value(coarse, fine), 0.5)
        with self.assertRaises(ValueError):
            nested_interface_value(np.ones(4), -np.ones(4))

    def test_upper_tail_is_at_least_matched_random(self):
        benefit = np.array([-4.0, -1.0, 0.0, 2.0, 7.0])
        for count in range(len(benefit) + 1):
            route = upper_tail_mask(benefit, count)
            self.assertGreaterEqual(
                matched_rate_selection_advantage(benefit, route),
                -1e-12,
            )


if __name__ == "__main__":
    unittest.main()
