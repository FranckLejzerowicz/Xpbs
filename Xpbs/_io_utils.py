# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
import datetime
from os.path import abspath, exists, expanduser, isfile
from pathlib import Path


def write_job(i_job: str, job_file: str, pbs: list, env: list, p_scratch_path: str,
              gpu: bool, commands: list, outputs: list, ff_dirs: dict, chmod: str) -> None:
    """
    Write the actual .pbs / slurm .sh script based on
    the info collected from the command line.

    :param i_job: job name.
    :param job_file: output filename for the job.
    :param pbs: actual series of commands, incl. the HPC directives.
    :param env: command to setup the environment.
    :param p_scratch_path: Folder for moving files and computing in (default = do not move to scratch).
    :param gpu: whether to run on GPU or not (and hence use Slurm in our case)
    :param commands: commands list.
    :param outputs: output files to potentially chmod.
    :param ff_dirs: folders to move on scratch.
    :param chmod: whether to change permission of output files (default: no).
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

        # if running on scratch, write commands to make directory for moved files/folders
        if p_scratch_path:
            for f_home, f_loc in ff_dirs.items():
                o.write('mkdir -p %s\n' % f_loc)
            o.write('\n')
            o.write('\n')

        # write the actual commands script
        for command in commands:
            # if running on scratch, including the actual files/folders moves
            if p_scratch_path:
                for f_home, f_loc in ff_dirs.items():
                    if f_home in command:
                        command = command.replace(f_home, f_loc)
            o.write('%s\n' % command)
        o.write('\n')
        o.write('\n')

        # if running on scratch, write commands that move files back
        if p_scratch_path:
            for f_home, f_loc in ff_dirs.items():
                o.write('rsync -auq %s/ %s\n' % (f_loc, f_home))
            if gpu:
                o.write('cd $SLURM_SUBMIT_DIR\n')
            else:
                o.write('cd $PBS_O_WORKDIR\n')
            o.write('rm -rf ${locdir}\n')

        # write command to cleanse the temporary folder
        if gpu:
            o.write('\nrm -fr $TMPDIR/%s_${SLURM_JOB_ID}\n' % i_job)
            o.write('echo "rm -fr $TMPDIR/%s_${SLURM_JOB_ID}"\n' % i_job)
        else:
            o.write('\nrm -fr $TMPDIR/${PBS_JOBNAME}_${PBS_JOBNUM}\n')
            o.write('echo "rm -fr $TMPDIR/${PBS_JOBNAME}_${PBS_JOBNUM}"\n')

        if chmod:
            if len(chmod) != len([x for x in chmod if x.isdigit() and int(x) < 8]):
                print('Problem with the entered chmod "%s"\nIgnoring' % chmod)
            else:
                o.write('\n\n')
                for output in set(outputs):
                    o.write('chmod %s %s\n' % (chmod, output))
        o.write('echo "Done!"\n')


def get_job_file(o_pbs, i_job, gpu):
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
        if gpu:
            job_file = '%s/%s_%s_slurm.sh' % (abspath('.'), i_job, cur_time)
        else:
            job_file = '%s/%s_%s.pbs' % (abspath('.'), i_job, cur_time)
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


def get_email_address(root: str) -> str:
    """
    Collect the email address from the edited config file.

    :param root: main directory of the package.
    :return: email address of the user.
    """

    # get the config file shipped with the package and hopefully edited by user
    config = '%s/config.txt' % root
    # check if exists or quit
    if not isfile(config):
        print('Problem with config file:\n- %s do not exists\n-> Exiting...' % config)
        sys.exit(1)
    else:
        # parse the first line of the config file
        with open(config) as f:
            for line in f:
                ls = line.strip().split()
                break
        # stop is any issue encountered (not two fields, not edited, not correctly edited)
        if len(ls) != 2:
            print('Problem with config file:\n- %s does not contain two columns\n-> Exiting...' % config)
            sys.exit(1)
        if ls[0] == '$HOME' and ls[1] == 'your-email-address@whatever.yeah':
            print("Problem with config file:\n- %s need editing (see README's Requisites)\n-> Exiting..." % config)
            sys.exit(1)
        # only get the actual $HOME value for the current user
        if ls[0] != expanduser('~'):
            print("Problem with config file: %s\n- The first field must be the value of $HOME"
                  "(see README's Requisites)\n-> Exiting..." % config)
            sys.exit(1)
        # return the passed email address and not just the dummy default
        email_address = ls[1]
        return email_address
