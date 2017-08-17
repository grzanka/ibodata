import unittest

from ibodata.lateral_profile import LateralProfile

import numpy as np


class TestDistal(unittest.TestCase):
    def setUp(self):
        self.data = LateralProfile([[0, 1], [10, 20]])

    def test_check(self):
        self.assertTrue(np.array_equal(self.data.x, [0, 10]))


if __name__ == '__main__':
    unittest.main()
