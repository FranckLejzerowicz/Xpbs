#!/usr/local/bin/python3
# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import click

from Xpbs._xpbs import Xpbs
from Xpbs import __version__


@click.command()
@click.option(
    "-i", "--i-script", required=True, multiple=True,
    help="Script of command lines to transform to Torque/Slurm job"
         "(Command line without '-' also works (e.g. 'tar cpfz file.tar.gz folder/*'))"
)
@click.option(
    "-o", "--o-pbs", required=False, default=None, type=str,
    help="Output job file name (default to <input>_TIMESTAMP.pbs)"
)
@click.option(
    "-j", "--i-job", required=True, type=str, help="Job name"
)
@click.option(
    "-q", "--p-queue", required=False, default=None,
    type=click.Choice(['short4gb','med4gb','med8gb','long8gb','longmem','highmem']),
    help="Queue name"
)
@click.option(
    "-e", "--p-env", required=False, default=None, type=str,
    help="Conda environment to run the job"
)
@click.option(
    "-d", "--p-dir", required=False, help="Output directory", type=str,
    default = '.', show_default=True
)
@click.option(
    "-n", "--p-nodes", required=False, default=1, type=int,
    help="Number of nodes", show_default=True
)
@click.option(
    "-T", "--p-tmp", required=False, default=None, type=str,
    help="Alternative temp folder to the one defined in $TMPDIR"
)
@click.option(
    "-p", "--p-procs", required=False, default=4, type=int,
    help="Number of processors", show_default=True
)
@click.option(
    "-t", "--p-time", required=False,
    default="10", show_default=True,
    help="Walltime limit (1 integers: hours)"
)
@click.option(
    "-M", "--p-mem", required=False, nargs=2,
    default=["1", "gb"], show_default=True,
    help="Expected memory usage (2 entries: (1) an integer, (2) one of ['b', 'kb', 'mb', 'gb'])"
)
@click.option(
    "-N", "--p-nodes-names", required=False, default=None,
    multiple=True, type=click.Choice(map(str, range(55))),
    help="Node names by the number(s), e.g. for brncl-04, enter '4'"
)
@click.option(
    "--email/--no-email", default=False, show_default=True,
    help="Send email at job completion (always if fail)"
)
@click.option(
    "--run/--no-run", default=False, show_default=True,
    help="'Run the PBS job before exiting (subprocess)"
)
@click.option(
    "--loc/--no-loc", default=False, show_default=True,
    help="Make copy of directory to /localscratch"
)
@click.option(
    "--noq/--no-noq", default=False, show_default=True,
    help="Do not ask for user-input 'y/n' sanity check"
)
@click.option(
    "--gpu/--no-gpu", default=False, show_default=True,
    help="Switch from Torque to Slurm (including querying 1 gpu)"
)
@click.version_option(__version__, prog_name="Xpbs")


def run_Xpbs(
        i_script,
        o_pbs,
        i_job,
        p_queue,
        p_env,
        p_dir,
        p_nodes,
        p_tmp,
        p_procs,
        p_time,
        p_mem,
        p_nodes_names,
        email,
        run,
        loc,
        noq,
        gpu,
):
    Xpbs(
        i_script,
        o_pbs,
        i_job,
        p_queue,
        p_env,
        p_dir,
        p_nodes,
        p_tmp,
        p_procs,
        p_time,
        p_mem,
        p_nodes_names,
        email,
        run,
        loc,
        noq,
        gpu,
    )


if __name__ == "__main__":
    run_Xpbs()
