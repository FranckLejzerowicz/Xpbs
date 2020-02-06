# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from glob import glob
from os.path import (
    abspath, dirname, exists, isfile
)


def collect_ff(abs_line, ff_paths, ff_dirs):
    """
    This function is run when the --loc options is ON
    It will copy all the files that the job works on into
    the compute node /localscratch where the job will perform
    and the copy back the results in the original folder
    """
    for abs_i in abs_line.strip().split():
        abs_i_s = abs_i.strip('"').strip("'")
        if exists(abs_i_s):
            print('AAA')
            abs_d = dirname(abs_i_s)
            ff_paths[abs_i_s] = '${locdir}%s' % abs_i_s
            ff_dirs[abs_d] = '${locdir}%s' % dirname(abs_i_s)
        elif abs_i_s[0] == '/':
            abs_d = dirname(abs_i_s)
            ff_dirs[abs_d] = '${locdir}%s' % dirname(abs_i_s)
    return ff_paths, ff_dirs


def get_commands_file(loc, path, commands, ff_paths, ff_dirs):
    with open(path) as f:
        for line in f:
            abs_line = ' '.join(
                [abspath(x) if exists(x) or len(glob(x)) else x for x in
                 line.strip().split()]
            )
            commands.append(abs_line)
            if loc:
                ff_paths, ff_dirs = collect_ff(
                    abs_line, ff_paths, ff_dirs
                )
    return commands, ff_paths, ff_dirs


def get_commands_args(loc, i_script, ff_paths, ff_dirs):
    abs_line = ' '.join(
        [abspath(x) if exists(x) or len(glob(x)) else x for x in i_script]
    )
    commands = [abs_line]
    if loc:
        ff_paths, ff_dirs = collect_ff(
            abs_line, ff_paths, ff_dirs
        )
    return commands, ff_paths, ff_dirs


def parse_command(i_script, loc):
    commands = []
    ff_paths = {}
    ff_dirs = {}
    for path in i_script:
        if isfile(path):
            commands, ff_paths, ff_dirs = get_commands_file(
                loc, path, commands, ff_paths, ff_dirs
            )
        else:
            commands, ff_paths, ff_dirs = get_commands_args(
                loc, i_script, ff_paths, ff_dirs
            )
            break
    return commands, ff_paths, ff_dirs
