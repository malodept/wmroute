import unittest
import numpy as np
from wmroute.statistics import crossed_state_seed_bootstrap_draws
class CrossedStateSeedBootstrapTest(unittest.TestCase):
    def test_shared_state_indices_are_preserved(self):
        values=np.repeat(np.arange(8,dtype=float)[:,None],3,axis=1); repetitions=25; seed=91
        actual=crossed_state_seed_bootstrap_draws(values,repetitions=repetitions,seed=seed)
        rng=np.random.default_rng(seed); rng.integers(0,3,size=(repetitions,3)); states=rng.integers(0,8,size=(repetitions,8))
        expected=np.array([values[row,0].mean() for row in states])
        np.testing.assert_array_equal(actual,expected)
    def test_rejects_non_matrix_input(self):
        with self.assertRaises(ValueError): crossed_state_seed_bootstrap_draws(np.arange(10),repetitions=10)
if __name__=='__main__': unittest.main()
