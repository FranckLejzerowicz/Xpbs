# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import click

from Xpbs.Xpbs import Xpbs
from Xpbs import __version__


@click.command()
@click.option(
    "-i", "--i-script", required=True, multiple=True,
    help="Command line or script of command lines"
)
@click.option(
    "-o", "--o-pbs", required=False, default=None,
    help="PBS job file name (default = Job_name.sh)"
)
@click.option(
    "-j", "--i-job", required=True, help="Job name"
)
@click.option(
    "-q", "--p-queue", required=False, default=None,
    type=click.Choice(['short4gb', 'med4gb', 'med8gb', 'long8gb', 'longmem', 'highmem', None]),
    help="Queue name"
)
@click.option(
    "-e", "--p-env", required=False, default=None,
    help="Conda environment to run the job"
)
@click.option(
    "-d", "--p-outdir", required=False, default='.',
    help="Output directory (default = .)"
)
@click.option(
    "-n", "--p-nodes", required=False, default=1,
    help="Number of nodes", show_default=True
)
@click.option(
    "-T", "--p-tmp", required=False, default=None,
    help="Alternative temp folder to the one defined in $TMPDIR"
)
@click.option(
    "-p", "--p-procs", required=False, default=4,
    help="Number of processors", show_default=True
)
@click.option(
    "-t", "--p-time", required=False, multiple=True,
    default=['10', '00', '00'], show_default=True,
    help="Walltime limit (max 3 integers: HH MM SS)"
)
@click.option(
    "-M", "--p-mem", required=False, multiple=True,
    default=['1', 'gb'], show_default=True,
    help="Expected memory usage (2 entries: (1) an integer, (2) one of ['b','kb', 'mb', 'gb'])"
)
@click.option(
    "-N", "--p-nodes-names", required=False, default=None,
    multiple=True, type=click.Choice(range(55)),
    help="Node names by the number(s), e.g. for brncl-04, enter '4'"
)
@click.option(
    "--email/--no-email", default=False,
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
    help="Do not ask sanity check"
)
@click.option(
    "--gpu/--no-gpu", default=False, show_default=True,
    help="Switch from Torque to Slurm (including querying 1 gpu)"
)
@click.option(
    "-v", "--verbose", required=False, is_flag=True,
    default=False, help="Show process.", show_default=True
)
@click.version_option(__version__, prog_name="Xpbs")


def run_Xpbs(
        i_script,
        o_pbs,
        i_job,
        p_queue,
        p_env,
        p_out_dir,
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
        verbose
):
    Xpbs(
        i_script,
        o_pbs,
        i_job,
        p_queue,
        p_env,
        p_out_dir,
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
        verbose
    )


if __name__ == "__main__":
    run_Xpbs()
