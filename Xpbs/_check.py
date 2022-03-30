# ----------------------------------------------------------------------------
# Copyright (c) 2022, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys


def check_pbs(pbs: list) -> None:
    """
    Ask user to check for the directives.

    :param pbs: directives.
    :return: None
    """
    print('-------------')
    print('PBS commands:')
    print('-------------')
    for directive in pbs:
        print(directive)
    dec = input('continue to write commands: <y/n>')
    if dec != 'y':
        print('Exiting\n')
        sys.exit(1)


def check_command(job_file: str, commands: list) -> None:
    """
    Ask user to check for the job content.

    :param job_file: filename for the output script.
    :param commands: commands to write.
    :return: None
    """
    print()
    print('Command lines to write in %s' % job_file)
    for command in commands:
        print(command)
    dec = input('continue?: <y/n>')
    if dec != 'y':
        print('Exiting')
        sys.exit(1)
