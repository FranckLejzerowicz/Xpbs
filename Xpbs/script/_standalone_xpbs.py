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
	"-i", "--i-script", nargs=1,
	help="Script of command lines to transform to Slurm/Torque job."
)
@click.option(
	"-o", "--o-pbs", default=None, type=str,
	help="Output job file name (default to <input>_TIMESTAMP.slm)"
)
@click.option(
	"-j", "--i-job", type=str, help="Job name."
)
@click.option(
	"-q", "--p-queue", default='normal',
	type=click.Choice(['normal', 'bigmem', 'accel', 'optimist']),
	help="Partition name."
)
@click.option(
	"-e", "--p-env", default=None, type=str,
	help="Conda environment to run the job."
)
@click.option(
	"-d", "--p-dir", help="Output directory", type=str,
	default='.', show_default=True
)
@click.option(
	"-n", "--p-nodes", default=1, type=int,
	help="Number of nodes", show_default=True
)
@click.option(
	"-p", "--p-procs", default=1, type=int,
	help="Number of processors", show_default=True
)
@click.option(
	"-T", "--p-tmp", default=None, type=str,
	help="Alternative temp folder to the one defined in $TMPDIR"
)
@click.option(
	"--notmp/--no-notmp", default=False, show_default=True,
	help="Do not set a temporary directory (use default)."
)
@click.option(
	"-t", "--p-time", default="10", show_default=True,
	help="Walltime limit (1 integers: hours)"
)
@click.option(
	"-l", "--p-scratch-path", show_default=True,
	default='/cluster/work/users/${USER}',
	help="scratch folder for moving files and computing"
)
@click.option(
	"-M", "--p-mem", nargs=2, show_default=False, default=('500', 'mb'),
	help="Expected memory usage needs two entries separated by a space: (1) an"
		 " integer and (2) one of 'mb', 'gb'. (Default: '500 mb')"
)
@click.option(
	"-N", "--p-nodes-names", default=None,
	multiple=True, type=click.Choice(map(str, range(74))),
	help="Node names by the number(s), e.g. for c-04, enter '4'"
)
@click.option(
	"-c", "--p-chmod", default=None, show_default=True,
	help="Change permission on all the output files (enter a 3 digit code)."
)
@click.option(
	"-w", "--p-pwd", default=None, show_default=True,
	help="Working directory to use instead of $SLURM_SUBMIT_DIR"
)
@click.option(
	"--email/--no-email", default=False, show_default=True,
	help="Send email at job completion (always if fail)"
)
@click.option(
	"--run/--no-run", default=False, show_default=True,
	help="Run the job before exiting (subprocess)"
)
@click.option(
	"--noq/--no-noq", default=True, show_default=True,
	help="Print script and ask for user-input 'y/n' sanity check"
)
@click.option(
	"--gpu/--no-gpu", default=False, show_default=True,
	help="Query a gpu"
)
@click.option(
	"--torque/--no-torque", default=False, show_default=True,
	help="Switch from Slurm to Torque"
)
@click.option(
	"--rm/--no-rm", default=True, show_default=True,
	help="Remove the job's scratch files."
)
@click.option(
	"--loc/--no-loc", default=True, show_default=True,
	help="Use scratch folder"
)
@click.option(
	"--show-config/--no-show-config", default=False, show_default=True,
	help="Show the current config file content"
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
		torque,
		loc,
		p_chmod,
		p_pwd,
		show_config
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
		torque,
		loc,
		p_chmod,
		p_pwd,
		show_config
	)


if __name__ == "__main__":
	standalone_xpbs()
