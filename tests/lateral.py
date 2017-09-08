import unittest

from ibodata.lateral_profile import LateralProfile

import numpy as np


class TestLateralCheck(unittest.TestCase):
    def setUp(self):
        """
        data1: profile that's only increasing
        data2: normal profile
        data3: profile that's only decreasing
        """
        self.data1 = LateralProfile([[0, 1], [10, 20], [20, 30]])
        self.data2 = LateralProfile([[-3, 4], [-1, 8], [0, 8], [1, 4]])
        self.data3 = LateralProfile([[-1.5, 5], [0.5, 3], [1.5, 1]])

    def test_check(self):
        self.assertTrue(np.array_equal(self.data1.x, [0, 10, 20]))
        self.assertTrue(np.array_equal(self.data2.x, [-3, -1, 0, 1]))
        self.assertTrue(np.array_equal(self.data3.x, [-1.5, 0.5, 1.5]))
        self.assertTrue(np.array_equal(self.data1.y, [1, 20, 30]))
        self.assertTrue(np.array_equal(self.data2.y, [4, 8, 8, 4]))
        self.assertTrue(np.array_equal(self.data3.y, [5, 3, 1]))


class TestLateralNormalize(unittest.TestCase):
    def setUp(self):
        """
        data1: profile that's only increasing
        data2: normal profile
        data3: profile that's only decreasing
        """
        self.data1 = LateralProfile([[0, 1], [10, 20], [20, 30]])
        self.data2 = LateralProfile([[-3, 4], [-1, 8], [0, 8], [1, 4]])
        self.data3 = LateralProfile([[-1.5, 5], [0.5, 3], [1.5, 1]])

    def test_normalize(self):
        with self.assertRaises(ValueError):
            self.data1.normalize(1)
        with self.assertRaises(ValueError):
            self.data3.normalize(1)

        self.data2.normalize(1)

        self.assertTrue(np.array_equal(self.data2.x, [-2.25, -0.25, 0.75, 1.75]))
        self.assertAlmostEqual(self.data2.y[0], 0.0)
        self.assertAlmostEqual(self.data2.y[1], 1.09401709)
        self.assertAlmostEqual(self.data2.y[2], 1.09401709)
        self.assertAlmostEqual(self.data2.y[3], 0.0)


class TestLateralParameters(unittest.TestCase):
    def setUp(self):
        """
        data1: profile that's only increasing
        data2: normal profile (normalized, dt = 1)
        data3: profile that's only decreasing
        """
        self.data1 = LateralProfile([[0, 0], [10, 19], [20, 29]])
        self.data2 = LateralProfile([[-2.25, 0], [-0.25, 1.25], [0.75, 1.25], [1.75, 0]])
        self.data3 = LateralProfile([[-1.5, 4], [0.5, 2], [1.5, 0]])

    def test_penumbras(self):
        self.assertAlmostEqual(self.data2.penumbra_left(), 1.28)
        self.assertAlmostEqual(self.data1.penumbra_left(), 0.42105263)
        self.assertTrue(np.isnan(self.data3.penumbra_left()))

        self.assertAlmostEqual(self.data2.penumbra_right(), 0.64)
        self.assertTrue(np.isnan(self.data1.penumbra_right()))
        self.assertAlmostEqual(self.data3.penumbra_right(), 0.4)

    def test_field_ratio(self):
        self.assertTrue(np.isnan(self.data1.field_ratio(1)))
        self.assertTrue(np.isnan(self.data1.field_ratio(0.95)))
        with self.assertRaises(ValueError):
            self.data1.field_ratio(-0.0001)

        self.assertAlmostEqual(self.data2.field_ratio(1.0), 0.57142857)
        self.assertAlmostEqual(self.data2.field_ratio(0.9), 0.65714285)
        self.assertAlmostEqual(self.data2.field_ratio(0.95), 0.61428571)
        self.assertAlmostEqual(self.data2.field_ratio(0.5), 1.0)

        with self.assertRaises(ValueError):
            self.data2.field_ratio(-1.0)
        with self.assertRaises(ValueError):
            self.data2.field_ratio(1.2)

        self.assertTrue(np.isnan(self.data3.field_ratio(1)))
        self.assertTrue(np.isnan(self.data3.field_ratio(0.95)))

    def test_symmetry(self):
        self.assertTrue(np.isnan(self.data1.symmetry(1)))
        self.assertTrue(np.isnan(self.data1.symmetry(0.95)))
        with self.assertRaises(ValueError):
            self.data1.symmetry(-3)

        self.assertAlmostEqual(self.data2.symmetry(1.0), 37.5)
        self.assertAlmostEqual(self.data2.symmetry(0.95), 30.23255813)
        self.assertAlmostEqual(self.data2.symmetry(0.9), 23.91304347)
        self.assertAlmostEqual(self.data2.symmetry(0.5), 7.14285714)

        self.assertTrue(np.isnan(self.data3.symmetry(1)))
        self.assertTrue(np.isnan(self.data3.symmetry(0.95)))
        with self.assertRaises(ValueError):
            self.data3.symmetry(3)

    def test_flatness_90(self):
        self.assertTrue(np.isnan(self.data1.flatness_90()))

        self.assertAlmostEqual(self.data2.flatness_90(), 0)

        self.assertTrue(np.isnan(self.data3.flatness_90()))

    def test_flatness_50(self):
        self.assertTrue(np.isnan(self.data1.flatness_50()))

        self.assertAlmostEqual(self.data2.flatness_50(), 8.695652170)

        self.assertTrue(np.isnan(self.data3.flatness_50()))

    def test_asymmetry(self):
        self.assertAlmostEqual(self.data1.asymmetry(), -100.0)
        self.assertAlmostEqual(self.data2.asymmetry(), 0.0)
        self.assertAlmostEqual(self.data3.asymmetry(), 39.28571428)


if __name__ == '__main__':
    unittest.main()
