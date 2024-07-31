import unittest
import numpy as np
from src.main.model.phototransduction import Phototransduction

class TestPhototransduction(unittest.TestCase):

    def setUp(self):
        self.model = Phototransduction()

    def test_initial_parameters(self):
        self.assertAlmostEqual(self.model.param['betaDark'], 4.1)
        self.assertAlmostEqual(self.model.param['concCaDark'], 0.3)

    def test_time_property(self):
        expected_time = np.arange(-self.model.stimulusOffset, 
                                  self.model.responseDuration - self.model.stimulusOffset, 
                                  self.model.dt)
        np.testing.assert_array_almost_equal(self.model.time, expected_time)

    def test_simulate_once(self):
        result = self.model.simulate_once(1, (0, 0.01), 1)
        self.assertIn('time', result)
        self.assertIn('PDEstar', result)

    def test_simulate(self):
        self.model.simulate(stimulusIntensities=[1, 2], stimulusDurations=[0.01, 0.02])
        self.assertEqual(len(self.model.results), 2)

if __name__ == '__main__':
    unittest.main()
