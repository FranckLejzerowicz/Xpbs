# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest
import subprocess
import pkg_resources

from Xpbs._xpbs import run_xpbs
from Xpbs._cmd import (
    get_conda_exes,
    get_abs_line_q2init,
    collect_abs_paths,
    get_commands_file,
    parse_command
)

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


class TestCmd(unittest.TestCase):

    def setUp(self):

        # first tests files
        self.cmd_lambda = 'ls * $HOME /home/flejzerowicz'
        self.cmd_qiime2 = 'qiime tools import --input-path /home/flejzerowicz'
        self.cmd_qiime2_red = 'qiime tools import  \\ \n'
        self.cmd_echo_qiime2 = 'echo "qiime tools import --input-path /home/flejzerowicz"'

        subprocess.call('conda create -n testforXpbx python'.split())
        self.default_exe = {'infotocap', 'wish', 'lzma', 'captoinfo','xz', 'lzcat', 'x86_64-conda_cos6-linux-gnu-ld', 'sqlite3',
         'lzmadec', 'idle3', 'xzgrep', 'tput', 'xzmore', 'lzegrep', '2to3-3.8', 'toe', 'xzegrep', 'ncurses6-config',
         'unlzma', 'tset', 'xzdec', 'infocmp', 'tclsh8.6', 'wish8.6', 'xzcat', 'reset', 'pip', 'clear', 'lzmore',
         'lzgrep', 'lzcmp', 'python3.8', 'wheel', 'python3', 'pydoc', 'ncursesw6-config', 'xzless', 'easy_install',
         'python3-config', 'sqlite3_analyzer', 'c_rehash', 'lzfgrep', 'lzdiff', 'xzfgrep', 'tic', 'openssl',
         'python3.8-config', 'tclsh', 'idle3.8', 'xzcmp', 'lzless', 'pydoc3.8', 'python', 'unxz', 'pydoc3', '2to3',
         'lzmainfo', 'xzdiff', 'tabs'}

    def test_get_conda_exes(self):
        conda_exe = get_conda_exes('')
        self.assertEqual(conda_exe, set())
        conda_exe = get_conda_exes('testforXpbx')
        self.assertEqual(conda_exe, self.default_exe)

    def test_get_abs_line_q2init(self):
        # self.cmd_lambda = 'ls * $HOME /home/flejzerowicz'
        # self.cmd_qiime2 = 'qiime tools import --input-path /home/flejzerowicz'
        # self.cmd_qiime2_red = 'qiime tools import \\ \n'
        # self.cmd_echo_qiime2 = 'echo "qiime tools import --input-path /home/flejzerowicz"'
        line, abs_line = get_abs_line_q2init(self.cmd_lambda)
        self.assertEqual(line, self.cmd_lambda)
        self.assertEqual(abs_line, [])
        line, abs_line = get_abs_line_q2init(self.cmd_qiime2)
        self.assertEqual(line, ' --input-path /home/flejzerowicz')
        self.assertEqual(abs_line, ['qiime tools import'])
        line, abs_line = get_abs_line_q2init(self.cmd_qiime2_red)
        self.assertEqual(line, '')
        self.assertEqual(abs_line, ['qiime tools import \\ \n'])
        line, abs_line = get_abs_line_q2init(self.cmd_echo_qiime2)
        self.assertEqual(line, ' --input-path /home/flejzerowicz"')
        self.assertEqual(abs_line, ['echo "qiime tools import'])

    def test_collect_abs_paths(self):
        pass

    def test_get_commands_file(self):
        pass

    def test_parse_command(self):
        pass

    def tearDown(self):
        subprocess.call('conda remove -n testforXpbx -all')




if __name__ == '__main__':
    unittest.main()
