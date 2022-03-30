# ----------------------------------------------------------------------------
# Copyright (c) 2022, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import subprocess
from Xpbs._io_utils import (
    get_job_file, get_work_dir, get_email_address, get_nodes_info, write_job)
from Xpbs._cmd import parse_command, get_conda_exes
from Xpbs._pbs import get_pbs
from Xpbs._check import check_command, check_pbs
from Xpbs._env import get_env


def run_xpbs(
        i_script: str,
        o_pbs: str,
        i_job: str,
        p_queue: str,
        p_env: str,
        p_dir: str,
        p_nodes: int,
        p_tmp: str,
        notmp: bool,
        p_procs: int,
        p_time: str,
        p_scratch_folder: str,
        p_mem: tuple,
        p_nodes_names: tuple,
        email: bool,
        run: bool,
        noq: bool,
        gpu: bool,
        rm: bool,
        torque: bool,
        loc: bool,
        chmod: str,
        p_pwd: str,
        show_config: bool,
        sinfo: bool,
        allocate: bool) -> None:
    """
    Main script to go from .sh script to the Slurm or Torque output script file.
    Wrties a Slurm/Torque script with directives and possibly re-localization
    of file if working on a scratch folder.

    Parameters
    ----------
    i_script : str
        Script of command lines to transform to Torque/Slurm job
    o_pbs: str
        Output job file name (default to <input>_TIMESTAMP.pbs)
    i_job: str
        Job name
    p_queue: str
        Queue or Partition name
    p_env: str
        Conda environment to run the job
    p_dir: str
        Output directory
    p_nodes: int
        Number of nodes
    p_tmp: str
        Alternative temp folder to the one defined in $TMPDIR
    notmp: bool
        Do not use a tmp folder
    p_procs: int
        Number of processors
    p_time: str
        Walltime limit (1 integers: hours).
    p_scratch_folder: str
        Scratch folder woth to moving files for computing
    p_mem: tuple
        Memory need (2 entries: (1) integer, (2) 'mb' or 'gb'
    p_nodes_names: tuple
        Node names
    email: bool
        Send email at job completion (always if fail).
    run: bool
        Run the job before exiting (subprocess)
    noq: bool
        Do not ask for user-input 'y/n' sanity check
    gpu: bool
        Switch from Torque to Slurm (including querying 1 gpu) [DEPRECATED]
    rm: bool
        Whether to remove the job's temporary and panfs/scratch files or not
    torque: bool
        Prepare for Torque instead of Slurm
    loc: bool
        Move the file to the scratch folder
    chmod: str
        Whether to change permission of output files (default: no)
    p_pwd: str
        Working directory to use instead of $SLURM_SUBMIT_DIR
    show_config: bool
        Show the current config file content
    sinfo: bool
        Print sinfo (also written in `~/.xsinfo`) -
        see [Xsinfo](https://github.com/FranckLejzerowicz/Xsinfo)
    allocate: bool
        Use info from `~/.xsinfo` to allocate suitable nodes/memory
    """

    # get address from config file (which must exist)
    email_address = get_email_address(show_config)
    nodes_info = get_nodes_info(torque, sinfo, allocate)

    # get the filename of the output torque (.pbs) or slurm job
    job_file = get_job_file(o_pbs, i_job, gpu, torque)

    # get the absolute path of the working directory
    work_dir = get_work_dir(p_dir)

    # ff is not empty only if the -l is active
    # (i.e. if user wishes that the job happens on /localscratch file copies)
    conda_exe = get_conda_exes(p_env)
    commands, outputs, ff_paths, ff_dirs = parse_command(
        i_script, p_scratch_folder, p_env, conda_exe, loc)

    # pbs directives
    pbs = get_pbs(i_job, o_pbs, p_time, p_queue, p_nodes, p_procs,
                  p_nodes_names, p_mem, gpu, torque, email, email_address)

    # print-based, visual checks
    if not noq:
        check_pbs(pbs)
        check_command(job_file, commands)

    # set environment and working directory
    env = get_env(i_job, o_pbs, p_env, p_tmp, notmp, work_dir, gpu,
                  torque, p_scratch_folder, ff_paths, ff_dirs, loc, p_pwd)

    # write the psb file to provide to "qsub"
    write_job(i_job, job_file, pbs, env, p_scratch_folder, gpu, torque, notmp,
              commands, outputs, ff_paths, ff_dirs, rm, chmod, loc)
    if run:
        print('Launched command: /bin/sh %s' % job_file)
        subprocess.Popen(['qsub', job_file])
