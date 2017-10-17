import os
from datetime import datetime
import unittest

from ibodata.readers import FileReader

import numpy as np


class TestReaderRegularData(unittest.TestCase):
    def setUp(self):
        """
        source: path to directory with test files
        """
        self.source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_files", "2010-11-12_13_14_15")
        self.file_reader = FileReader(self.source)

    def test_regular_data(self):
        self.assertTrue(
            np.array_equal(self.file_reader.Lprofiles[0].profile.x, [6000, 7000, 8000, 9000,
                                                                     10003, 11003, 11100, 11200]))
        self.assertTrue(
            np.array_equal(self.file_reader.Lprofiles[0].profile.y, [0.0004, 0.00045, 0.0005, 0.000777,
                                                                     0.0008, 0.001, 0.00111, 0.0012]))

        self.assertEqual(self.file_reader.Lprofiles[0].date, datetime.strptime("2010-11-12_13_14_15",
                                                                               '%Y-%m-%d_%H_%M_%S'))

        self.assertTrue(
            np.array_equal(self.file_reader.Dprofiles[0].profile.x, [7998, 102, 202, 302, 402,
                                                                     502, 602, 702, 802, 902]))
        self.assertTrue(
            np.array_equal(self.file_reader.Dprofiles[0].profile.y, [0.004566, 0.004543, 0.004539, 0.004511431,
                                                                     0.004574, 0.004541, 0.004595, 0.004393, 0.004484,
                                                                     0.00452]))

        self.assertEqual(self.file_reader.Dprofiles[0].date, datetime.strptime("2010-11-12_13_14_15",
                                                                               '%Y-%m-%d_%H_%M_%S'))


class TestReaderCorruptedData(unittest.TestCase):
    def setUp(self):
        """
        source: path to directory with test files
        In '2010-11-12_13_14_16' directory:
        test.dat has axis named 'NOAXIS'
        test2.dat is missing axis name so it has 12 columns and only 11 names for them
        test3.dat is missing 'Wylicz' column
        test4.dat has rows with values, such as Inf, -Inf, NaN, which needs to be removed
        test5.data has correct data, but wrong extension
        """
        self.source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_files", "2010-11-12_13_14_16")
        self.file_reader = FileReader(self.source)

    def test_corrupted_data(self):
        self.assertTrue(len(self.file_reader.Lprofiles) == 1)
        self.assertTrue(len(self.file_reader.Dprofiles) == 0)

        self.assertTrue(
            np.array_equal(self.file_reader.Lprofiles[0].profile.x, [7000, 8000,
                                                                     10003, 11003, 11200]))
        self.assertTrue(
            np.array_equal(self.file_reader.Lprofiles[0].profile.y, [0.00045, 0.0005,
                                                                     0.0008, 0.001, 0.0012]))
