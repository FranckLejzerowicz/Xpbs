# ----------------------------------------------------------------------------
# Copyright (c) 2022, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
import datetime
import subprocess
import pkg_resources
from datetime import datetime as dt
from os.path import abspath, exists, expanduser, isfile
from pathlib import Path

ROOT = pkg_resources.resource_filename("Xpbs", "")


def write_job(i_job: str, job_file: str, pbs: list, env: list,
              p_scratch_folder: str, gpu: bool, torque: bool, notmp: bool,
              commands: list, outputs: list, ff_paths: set, ff_dirs: set,
              rm: bool, chmod: str, loc: bool) -> None:
    """
    Write the actual .pbs / slurm .sh script based on
    the info collected from the command line.

    :param i_job: job name.
    :param job_file: output filename for the job.
    :param pbs: actual series of commands, incl. the HPC directives.
    :param env: command to setup the environment.
    :param p_scratch_folder: Folder for moving files and computing in (default = do not move to scratch).
    :param gpu: whether to run on GPU or not (and hence use Slurm in our case)
    :param commands: commands list.
    :param outputs: output files to potentially chmod.
    :param ff_paths: files to be moved for /localscratch jobs.
    :param ff_dirs: folders to move on scratch.
    :param chmod: whether to change permission of output files (default: no).
    :param rm: whether to remove the job's temporary and panfs/scratch files or not.
    :return: None
    """

    with open(job_file, 'w') as o:

        # write the header directives
        for i in pbs:
            o.write('%s\n' % i)
        o.write('\n')
        o.write('\n')

        # write the environment loading command
        for e in env:
            o.write('%s\n' % e)
        o.write('echo "Job file:"\n')
        o.write('echo "%s"\n' % abspath(job_file))
        o.write('\n')
        o.write('\n')

        # if running on scratch, write commands
        # to make directory for moved files/folders
        if p_scratch_folder and loc:
            for ff in set(ff_dirs):
                o.write('mkdir -p %s\n' % ff)
                o.write('mkdir -p ${locdir}%s\n' % ff)
            o.write('\n')
            o.write('\n')

        # write the actual commands script
        for command in commands:
            # if running on scratch, including the actual files/folders moves
            if p_scratch_folder and loc:
                for ff in ff_dirs:
                    if ff in command:
                        if ff[0] == '/':
                            command = command.replace(
                                ' %s' % ff, ' ${locdir}%s' % ff)
                        else:
                            command = command.replace(
                                ' %s' % ff, ' ${locdir}/%s' % ff)
                for ff in ff_paths:
                    if ff in command:
                        if ff[0] == '/':
                            command = command.replace(
                                ' %s' % ff, ' ${locdir}%s' % ff)
                        else:
                            command = command.replace(
                                ' %s' % ff, ' ${locdir}/%s' % ff)
            o.write('%s\n' % command)
        o.write('\n')
        o.write('\n')

        # if running on scratch, write commands that move files back
        if p_scratch_folder and loc:
            copied_dirs = set([
                x for x in sorted(ff_dirs)
                for y in sorted(ff_dirs) if x not in y
            ])
            for ff in sorted(ff_dirs):
                if ff not in copied_dirs:
                    if ff[0] == '/':
                        o.write('if [ -d ${locdir}%s/ ]; then rsync -auq ${'
                                'locdir}%s/ %s/; fi\n' % (ff, ff, ff))
                    else:
                        o.write('if [ -d ${locdir}/%s/ ]; then rsync -auq ${'
                                'locdir}/%s/ %s/; fi\n' % (ff, ff, ff))
            for ff in set(outputs):
                if ff[0] == '/':
                    o.write('if [ -f ${locdir}%s ]; then rsync -auq ${'
                            'locdir}%s %s; fi\n' % (ff, ff, ff))
                else:
                    o.write('if [ -f ${locdir}/%s ]; then rsync -auq ${'
                            'locdir}/%s %s; fi\n' % (ff, ff, ff))
            if torque:
                o.write('cd $PBS_O_WORKDIR\n')
            else:
                o.write('cd $SLURM_SUBMIT_DIR\n')
            if rm:
                o.write('rm -rf ${locdir}\n')

        # write command to cleanse the temporary folder
        if rm and not notmp:
            o.write('\nrm -fr ${TMPDIR}\n')

        if chmod:
            if len(chmod) != len([
                x for x in chmod if x.isdigit() and int(x) < 8]):
                print('Problem with the entered chmod "%s"\nIgnoring' % chmod)
            else:
                o.write('\n\n')
                for output in set(outputs):
                    o.write('if [ -f %s ]; then chmod %s %s; fi\n' % (
                        output, chmod, output))
        o.write('echo "Done!"\n')


def get_job_file(o_pbs, i_job, gpu, torque):
    """
    Get the filename of the output torque (.pbs) or slurm job.

    :param o_pbs: output filename passed by user (mandatory).
    :param i_job: job name passed by user (mandatory).
    :param gpu: whether to run on GPU or not (and hence use Slurm in our case)
    :return:
    """

    # create an output file name by default based on the input and the date
    if not o_pbs:
        # get the date time of now
        cur_time = str(
            datetime.datetime.now()
        ).split('.')[0].replace(
            ' ', '-'
        ).replace(
            ':', '-'
        )
        # add .pbs or _slurm.sh depending on whether it is to run on GPU.
        if torque:
            job_file = '%s/%s_%s.pbs' % (abspath('.'), i_job, cur_time)
        else:
            job_file = '%s/%s_%s.slm' % (abspath('.'), i_job, cur_time)
    # if the output filename was provided, just keep it
    else:
        job_file = o_pbs
    return job_file


def get_work_dir(p_dir: str):
    """
    Get the absolute path of the working directory.

    :param p_dir: working directory passed by user.
    :return: absolute path of this working directory.
    """
    if exists(p_dir):
        work_dir = abspath(p_dir)
    else:
        work_dir = str(Path.home())
    return work_dir


def write_conf(conf: str) -> str:
    """Collect the email address of the user
    and write it somewhere it can be reused.

    Parameters
    ----------
    conf : str
        Path to the config file

    Returns
    -------
    email : str
        email address of the user.
    """
    email = ''
    c = 0
    while '@' not in email and '.' not in email:
        if c:
            email = input('Please enter a valid email address: ')
        else:
            email = input(
                '%s\nThis is probably the first time you run Xpbs.\n'
                'Hence a config file with you email will be created\n'
                '(so you get emailed when a job fails)\n%s\n'
                'Please enter an email address: ' % ('-' * 50, '-' * 50))
        c += 1
    o = open(conf, 'w')
    o.write('%s\n' % email)
    o.close()
    print('Written:', conf)
    print('If you want to change the email address, edit this file.')
    return email


def validate_email(conf: str, show_config: bool):
    """
    Checks that the content of the existing config file
    is a valid email address.

    Parameters
    ----------
    conf : str
        Path to the config file
    show_config : bool
        Whether to show the first line of the config file or not.

    Returns
    -------
    email : str
        email address of the user.
    """
    # parse the first line of the config file
    with open(conf) as f:
        for line in f:
            email = line.strip()
            break
    if show_config:
        print(line)
        sys.exit(0)
    # stop if issue encountered (e.g. not edited, not correctly edited)
    if '@' not in email:
        raise IOError("Problem with %s:\n- needs an email address\n" % conf)
    elif len(email.split('@')) != 2 or '.' not in email.split('@')[-1]:
        raise IOError("Problem with %s:\n- no valid email address\n" % conf)
    return email


def get_email_address(show_config: bool) -> str:
    """
    Collect the email address from the edited config file.

    Parameters
    ----------
    show_config : bool
        Whether to show the first line of the config file or not.

    Returns
    -------
    email : str
        email address of the user.
    """
    # get the config file shipped with the package and hopefully edited by user
    conf = '%s/config.txt' % ROOT
    # check if exists or quit
    if isfile(conf):
        email = validate_email(conf, show_config)
    else:
        email = write_conf(conf)
    return email


def get_nodes_info(torque: bool, sinfo: bool, allocate: bool) -> list:
    """
    Collect the nodes info from the output of Xsinfo.

    Parameters
    ----------
    torque : bool
        Switch from Slurm to Torque
    sinfo : bool
        Print sinfo in stdout (it will also be written in `~/.xsinfo`)
    allocate : bool
        Use info from `~/.xsinfo` to allocate suitable nodes/memory

    Returns
    -------
    nodes : list
        Nodes info.
    """
    nodes = []
    if torque:
        print('No node collection mechanism yet for PBS/Torque!')
    else:
        if sinfo or allocate:
            fp = '%s/.xsinfo/%s.tsv' % (expanduser('~'), str(dt.now().date()))
            if not isfile(fp):
                subprocess.call('Xsinfo')
            with open(fp) as f:
                for line in f:
                    nodes.append(line.strip().split('\t'))
    return nodes
