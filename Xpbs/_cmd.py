# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
import subprocess
from glob import glob
from os.path import abspath, dirname, exists, isfile, basename


def collect_ff(abs_line: str, ff_paths: dict,
               ff_dirs: dict) -> (dict, dict):
    """
    This function is run when the -l options is ON
    It will copy all the files that the job works on into
    the compute node /localscratch where the job will perform
    and the copy back the results in the original folder

    :param abs_line: list of absolute paths to a file or folder.
    :param ff_paths: local -> scratch file paths to be updated.
    :param ff_dirs: local -> scratch folder paths to be updated.
    :return: ff_paths and ff_dirs updated with new file and folder paths.
    """
    # for each term of the stripped and space-separated command
    for abs_i in abs_line.strip().split():
        # re-strip the possible quotes in file names
        abs_i_s = abs_i.strip('"').strip("'")
        # get the local -> scratch paths mapping of existing files/folders
        if exists(abs_i_s):
            abs_d = dirname(abs_i_s)
            ff_paths[abs_i_s] = '${locdir}%s' % abs_i_s
            ff_dirs[abs_d] = '${locdir}%s' % dirname(abs_i_s)
        # get only local -> scratch folder paths mapping for root based folders
        elif abs_i_s[0] == '/':
            abs_d = dirname(abs_i_s)
            ff_dirs[abs_d] = '${locdir}%s' % dirname(abs_i_s)
    return ff_paths, ff_dirs


def get_conda_exes(p_env: str) -> set:
    """
    Get the conda environment path(s)
    :param p_env: Conda environment to run the job.
    """
    conda_exe =  set()
    if p_env:
        conda_path = subprocess.getoutput('conda info --base')
        conda_exe_paths = glob('%s/envs/%s/bin/*' % (conda_path, p_env))
        conda_exe = set([basename(exe_path) for exe_path in conda_exe_paths])
    return conda_exe


def get_abs_line_q2init(line_input: str) -> (str, list):
    """
    Return the command without the qiime2 plugin/module call
    as this must stay unchanged (could be abspath'ed if a folder
    has a plugin/module name too...)

    :param line_input: native, passed command
    :return:
    """
    abs_line = []
    line = line_input
    # make sure a qiime command is not transformed into a abspath by mistake
    if line_input.startswith('qiime') or line_input.startswith('echo "qiime'):
        if ' -' in line_input:
            # keep the line part before first option and the rest to abspath
            abs_line.append(line_input[:line_input.index(' -')].strip())
            line = line_input[line_input.index(' -'):]
        else:
            # keep the entire line and nothing left to abspath
            abs_line.append(line_input.strip())
            line = ''
    # this may return the line unchanged, and this everything to abspath
    return line, abs_line


def collect_abs_paths(line_input: str, p_env: str) -> str:
    """
    Turn the words that have a path into abspath (except for executable).

    :param line_input: command line in list
    :param p_env: Conda environment to run the job.
    :return: concatenate string into abspath'ed command line
    """
    conda_exe = get_conda_exes(p_env)
    line, abs_line = get_abs_line_q2init(line_input)
    for x in line.strip().split():
        if x[0] in ['/', '-']:
            abs_line.append(x)
        elif exists(x) or len(glob(x)):
            if p_env and x in conda_exe:
                abs_line.append(x)
            elif subprocess.getstatusoutput('which %s' % x)[0]:
                abs_line.append(x)
            else:
                abs_line.append(abspath(x))
        else:
            abs_line.append(x)
    abs_line = ' '.join(abs_line)
    return abs_line


def get_commands_file(p_scratch_path: str, path: str, commands: list,
                      ff_paths: dict, ff_dirs: dict, p_env: str) -> (list, dict, dict):
    """
    Parse the .sh file and collect the actual script commands.

    :param p_scratch_path: Folder for moving files and computing in (default = do not move to scratch).
    :param path: script file.
    :param commands: full list of commands to be appended.
    :param ff_paths: files to move on scratch.
    :param ff_dirs: folders to move on scratch.
    :param p_env: Conda environment to run the job.
    :return:
        commands    : appended commands list.
        ff_paths    : files to be moved for /localscratch jobs.
        ff_dirs     : folders to be moved for /localscratch jobs.
    """

    with open(path) as f:
        # for each command of the script
        for line in f:
            # collect the absolute paths of the files/folders that exist or keep words as are
            abs_line = collect_abs_paths(line, p_env)
            # add this command with modified path to abspath as a new command
            commands.append(abs_line)
            # if it is asked to work on a scratch folder
            if p_scratch_path:
                if p_scratch_path[0] != '/':
                    print('scrtach folder path must by absolute, i.e. start with "/"'
                          '.. Do you mean "/%s" ?\nExiting...' % p_scratch_path)
                    sys.exit(1)
                # get the path to be moved to this scratch
                ff_paths, ff_dirs = collect_ff(
                    abs_line, ff_paths, ff_dirs
                )
    return commands, ff_paths, ff_dirs


def get_commands_args(p_scratch_path: str, i_script: list, ff_paths: dict,
                      ff_dirs: dict) -> (list, dict, dict):
    """
    ########################
    ## NOT USED CURRENTLY ##
    ########################
    Parse the argument directly passed in the command line to Xpby
    and make a pbs script transformation for them.

    :param p_scratch_path: Folder for moving files and computing in (default = do not move to scratch).
    :param i_script: direct command line.
    :param ff_paths: files to move on scratch.
    :param ff_dirs: folders to move on scratch.
    :return:
        commands    : appended commands list.
        ff_paths    : files to be moved for /localscratch jobs.
        ff_dirs     : folders to be moved for /localscratch jobs.
    """

    abs_line = []
    for x in i_script:
        if exists(x) or len(glob(x)):
            if subprocess.getoutput('which %s')[0]:
                abs_line.append(x)
            else:
                abs_line.append(abspath(x))
        else:
            abs_line.append(x)
    abs_line = ' '.join(abs_line)

    commands = [abs_line]
    if p_scratch_path:
        ff_paths, ff_dirs = collect_ff(
            abs_line, ff_paths, ff_dirs
        )
    return commands, ff_paths, ff_dirs


def parse_command(i_script: str, p_scratch_path: str, p_env: str) -> (list, dict, dict):
    """
    Main interpreter of the passed scripts / command to the -i option.

    :param i_script: script file.
    :param p_scratch_path: Folder for moving files and computing in (default = do not move to scratch).
    :param p_env: Conda environment to run the job.
    :return:
        commands    : appended commands list.
        ff_paths    : files to be moved for /localscratch jobs.
        ff_dirs     : folders to be moved for /localscratch jobs.
    """



    ff_dirs = {}
    ff_paths = {}
    commands = []
    # if the script file exists
    if isfile(i_script):
        # get the command from the file content
        commands, ff_paths, ff_dirs = get_commands_file(
            p_scratch_path, i_script, commands, ff_paths, ff_dirs, p_env
        )
    # if the script file does not exists
    # (-> it could be a command passed directly to the command line)
    else:
        # potential development to use "get_commands_args()"...
        print('%s does not exists\nExiting...' % i_script)
        sys.exit(1)
    return commands, ff_paths, ff_dirs
