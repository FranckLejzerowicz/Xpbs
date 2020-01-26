# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys


def check_pbs(pbs):
    print('-------------')
    print('PBS commands:')
    print('-------------')
    for directive in pbs:
        print(directive)
    dec = input('continue to write commands: <y/n>')
    if dec != 'y':
        print('Exiting\n')
        sys.exit(1)


def check_command(job_file, commands):
    print()
    print('Command lines to write in %s' % job_file)
    for command in commands:
        print(command)
    dec = input('continue?: <y/n>')
    if dec != 'y':
        print('Exiting')
        sys.exit(1)
