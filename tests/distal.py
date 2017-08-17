import unittest

from ibodata.depth_profile import DepthProfile

import numpy as np

class TestDistal(unittest.TestCase):

    def setUp(self):
        self.data = DepthProfile([[0,1], [10, 20]])

    def test_check(self):
        self.assertTrue(np.array_equal(self.data.x, [0,11]))


if __name__ == '__main__':
    unittest.main()
