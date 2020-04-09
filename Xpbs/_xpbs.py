# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
import subprocess
import pkg_resources

from Xpbs._io_utils import (
    get_job_file,
    get_work_dir,
    get_email_address,
    write_job
)
from Xpbs._cmd import parse_command
from Xpbs._pbs import get_pbs
from Xpbs._check import (
    check_command,
    check_pbs
)
from Xpbs._env import get_env

ROOT = pkg_resources.resource_filename("Xpbs", "")


def run_xpbs(i_script: str, o_pbs: str, i_job: str, p_queue: str,
             p_env: str, p_dir: str, p_nodes: int, p_tmp: str, p_procs: int,
             p_time: str, p_scratch_path: str, p_mem: tuple, p_nodes_names: str,
             email: bool, run: bool, noq: bool, gpu: bool, chmod: str) -> None:
    """
    Main script to go from (.sh) script to the output file
    :param i_script: Script of command lines to transform to Torque/Slurm job.
    :param o_pbs: Output job file name (default to <input>_TIMESTAMP.pbs).
    :param i_job: Job name
    :param p_queue: Queue name.
    :param p_env: Conda environment to run the job.
    :param p_dir: Output directory.
    :param p_nodes: Number of nodes.
    :param p_tmp: Alternative temp folder to the one defined in $TMPDIR.
    :param p_procs: Number of processors.
    :param p_time: Wall time limit (1 integers: hours).
    :param p_scratch_path: Folder for moving files and computing in (default = do not move to scratch).
    :param p_mem: Expected memory usage (2 entries: (1) an integer, (2) one of ['b', 'kb', 'mb', 'gb']).
    :param p_nodes_names: Node names by the number(s), e.g. for brncl-04, enter '4'.
    :param email: Send email at job completion (always if fail).
    :param run: Run the PBS job before exiting (subprocess).
    :param noq: Do not ask for user-input 'y/n' sanity check.
    :param gpu: Switch from Torque to Slurm (including querying 1 gpu).
    :param chmod: whether to change permission of output files (default: no).
    :return: torque/slurm script with directives and possibly re-localization of file if working on a scratch folder.
    """

    # get address from config file (which must exist)
    email_address = get_email_address(ROOT)

    # get the filename of the output torque (.pbs) or slurm job
    job_file = get_job_file(o_pbs, i_job, gpu)

    # get the absolute path of the working directory
    work_dir = get_work_dir(p_dir)

    # ff is not empty only if the -l is active
    # (i.e. if user wishes that the job happens on /localscratch file copies)
    commands, outputs, ff_paths, ff_dirs = parse_command(i_script, p_scratch_path, p_env)

    # pbs directives
    pbs = get_pbs(i_job, o_pbs, p_time, p_queue, p_nodes, p_procs,
                  p_nodes_names, p_mem, gpu, email, email_address)

    # print-based, visual checks
    if not noq:
        check_pbs(pbs)
        check_command(job_file, commands)

    # set environment and working directory
    env = get_env(i_job, o_pbs, p_env, p_tmp, work_dir, gpu, p_scratch_path, ff_paths)

    # write the psb file to provide to "qsub"
    write_job(i_job, job_file, pbs, env, p_scratch_path, gpu, commands, outputs, ff_dirs, chmod)
    if run:
        print('Launched command: /bin/sh %s' % job_file)
        subprocess.Popen(['qsub', job_file])
        sys.exit(0)
