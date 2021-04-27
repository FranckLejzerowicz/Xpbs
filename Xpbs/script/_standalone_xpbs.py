# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import click
from Xpbs._xpbs import run_xpbs
from Xpbs import __version__


@click.command()
@click.option(
	"-i", "--i-script", required=True, nargs=1,
	help="Script of command lines to transform to Torque/Slurm job."
)
@click.option(
	"-o", "--o-pbs", required=False, default=None, type=str,
	help="Output job file name (default to <input>_TIMESTAMP.pbs)"
)
@click.option(
	"-j", "--i-job", required=True, type=str, help="Job name."
)
@click.option(
	"-q", "--p-queue", required=False, default=None,
	type=click.Choice(['short4gb','med4gb','med8gb','long8gb','longmem','highmem']),
	help="Queue name."
)
@click.option(
	"-e", "--p-env", required=False, default=None, type=str,
	help="Conda environment to run the job."
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
	"--notmp/--no-notmp", default=False, show_default=True,
	help="Do not set a temporary directory (use default)."
)
@click.option(
	"-p", "--p-procs", required=False, default=1, type=int,
	help="Number of processors", show_default=True
)
@click.option(
	"-t", "--p-time", required=False,
	default="10", show_default=True,
	help="Walltime limit (1 integers: hours)"
)
@click.option(
	"-l", "--p-scratch-path", show_default=True,
	default='/panfs/panfs1.ucsd.edu/panscratch/${USER}',
	help="panasas scratch folder for moving files and computing"
)
@click.option(
	"-M", "--p-mem", required=False, nargs=2, show_default=False, default=('1', 'gb'),
	help="Expected memory usage needs two entries separated by a space: "
		 "(1) an integer and (2) one of 'b', 'kb', 'mb', 'gb'. (Default: '1 gb')"
)
@click.option(
	"-N", "--p-nodes-names", required=False, default=None,
	multiple=True, type=click.Choice(map(str, range(74))),
	help="Node names by the number(s), e.g. for brncl-04, enter '4'"
)
@click.option(
	"-c", "--p-chmod", default=None, show_default=True,
	help="Change permission on all the output "
		 "files (enter a 3 digit code)."
)
@click.option(
	"--email/--no-email", default=False, show_default=True,
	help="Send email at job completion (always if fail)"
)
@click.option(
	"--run/--no-run", default=False, show_default=True,
	help="Run the PBS job before exiting (subprocess)"
)
@click.option(
	"--noq/--no-noq", default=False, show_default=True,
	help="Do not ask for user-input 'y/n' sanity check"
)
@click.option(
	"--gpu/--no-gpu", default=False, show_default=True,
	help="Switch from Torque to Slurm (including querying 1 gpu)"
)
@click.option(
	"--rm/--no-rm", default=True, show_default=True,
	help="Remove the job's temporary and panfs/scratch files."
)
@click.option(
	"--loc/--no-loc", default=True, show_default=True,
	help="Use panasas scratch folder"
)
@click.version_option(__version__, prog_name="Xpbs")


def standalone_xpbs(
		i_script,
		o_pbs,
		i_job,
		p_queue,
		p_env,
		p_dir,
		p_nodes,
		p_tmp,
		notmp,
		p_procs,
		p_time,
		p_scratch_path,
		p_mem,
		p_nodes_names,
		email,
		run,
		noq,
		gpu,
		rm,
		loc,
		p_chmod
):

	run_xpbs(
		i_script,
		o_pbs,
		i_job,
		p_queue,
		p_env,
		p_dir,
		p_nodes,
		p_tmp,
		notmp,
		p_procs,
		p_time,
		p_scratch_path,
		p_mem,
		p_nodes_names,
		email,
		run,
		noq,
		gpu,
		rm,
		loc,
		p_chmod
	)


if __name__ == "__main__":
	standalone_xpbs()
