# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest
import pkg_resources

#from Xpbs.Xpbs import Xpbs
ROOT = pkg_resources.resource_filename("Xpbs", '')

class TestXpbs(unittest.TestCase):

    def setUp(self):
        self.sh = '%s/test/test.sh' % ROOT
        self.pbs = '%s/test/test.pbs' % ROOT

#    def test_Xpbs(self):
 #       Xpbs(self.sh)
  #      self.assertEqual(self.sh, self.pbs)


if __name__ == '__main__':
    unittest.main()
