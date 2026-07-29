import unittest

import numpy as np

from wmroute.decision import realized_net_benefit
from wmroute.interfaces import (
    available_routing_value,
    matched_rate_selection_advantage,
    nested_interface_value,
    population_available_value,
    prediction_interface_value,
    upper_tail_mask,
)


class DecisionValueTest(unittest.TestCase):
    def test_realized_net_benefit(self):
        value = realized_net_benefit([3.0, 1.0], [1.0, 2.0], [2.0, 2.0], 0.25)
        np.testing.assert_allclose(value, [1.5, -1.5])

    def test_bayes_available_value(self):
        benefit = np.array([2.0, -1.0, -3.0, 2.0])
        labels = np.array([0, 0, 1, 1])
        self.assertAlmostEqual(available_routing_value(benefit, labels), 0.25)

    def test_prediction_interface_jensen_gap(self):
        benefit = np.array([2.0, -2.0, 3.0, -1.0])
        task = np.array([0, 0, 1, 1])
        prediction = [task, np.array([0, 1, 0, 1])]
        self.assertAlmostEqual(
            prediction_interface_value(benefit, task, prediction), 0.75
        )

    def test_population_jensen_gap(self):
        coarse = np.zeros(4)
        fine = np.array([2.0, -2.0, 1.0, -1.0])
        self.assertAlmostEqual(population_available_value(fine), 0.75)
        self.assertAlmostEqual(nested_interface_value(coarse, fine), 0.75)

    def test_upper_tail_beats_matched_random(self):
        benefit = np.array([-3.0, -1.0, 1.0, 4.0])
        selected = upper_tail_mask(benefit, count=2)
        advantage = matched_rate_selection_advantage(benefit, selected)
        self.assertAlmostEqual(advantage, 1.125)


if __name__ == "__main__":
    unittest.main()
