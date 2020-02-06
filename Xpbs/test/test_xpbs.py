# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest
import pkg_resources

from Xpbs._xpbs import run_xpbs
ROOT = pkg_resources.resource_filename("Xpbs", "test")


class TestXpbs(unittest.TestCase):

    def setUp(self):

        # first tests files
        self.sh1 = '%s/test.sh' % ROOT

        self.pbs1_1_fp = '%s/test_out1.pbs' % ROOT
        self.pbs1_1_out_fp = self.pbs1_1_fp.replace('.pbs', '_test.pbs')
        with open(self.pbs1_1_fp) as f_ref:
            self.pbs1_1 = f_ref.readlines()

        self.pbs1_2_fp = '%s/test_out2.pbs' % ROOT
        self.pbs1_2_out_fp = self.pbs1_2_fp.replace('.pbs', '_test.pbs')
        with open(self.pbs1_2_fp) as f_ref:
            self.pbs1_2 = f_ref.readlines()

        # second test files
        self.sh2 = '%s/test_loc.sh' % ROOT
        with open(self.sh2, 'w') as o:
            o.write('cp %s/to_print_for_test.txt  %s/to_print_for_test_copy.txt\n' % (ROOT, ROOT))

        self.pbs2_fp = '%s/test_loc.pbs' % ROOT
        self.pbs2_out_fp = self.pbs2_fp.replace('.pbs', '_test.pbs')
        with open(self.pbs2_fp) as f_ref:
            self.pbs2 = f_ref.readlines()

    def test_Xpbs1(self):

        run_xpbs(
            self.sh1, self.pbs1_1_out_fp, 'test1', None,
            None, '.', 1, None, 1, 1, None, ('1', 'mb'),
            None, False, False, True, False
        )
        with open(self.pbs1_1_out_fp) as f_ref:
            self.pbs1_1_out = f_ref.readlines()
        self.assertEqual(self.pbs1_1, self.pbs1_1_out)

    def test_Xpbs2(self):

        run_xpbs(
            self.sh1, self.pbs1_2_out_fp, 'test2', None,
            'q2', '.', 2, None, 10, 200, None, ('10', 'gb'),
            None, True, False, True, False
        )
        with open(self.pbs1_2_out_fp) as f_ref:
            self.pbs1_2_out = f_ref.readlines()
        self.assertEqual(self.pbs1_2, self.pbs1_2_out)

    def test_Xpbs3(self):

        run_xpbs(
            self.sh2, self.pbs2_out_fp, 'test3', None,
            'q2', '.', 2, None, 12, 10, '/localscratch', ('1', 'gb'),
            None, True, False, True, False
        )
        with open(self.pbs2_out_fp) as f_ref:
            self.pbs2_out = f_ref.readlines()
        self.assertEqual(self.pbs2, self.pbs2_out)


if __name__ == '__main__':
    unittest.main()
