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
from os.path import abspath, dirname

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


def Xpbs(
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
		gpu
):

	# get address from config file (which must exist)
	email_address = get_email_address(ROOT)

	# get the
	job_file = get_job_file(o_pbs, i_job, gpu)

	# get the absolute path of the working directory
	work_dir = get_work_dir(p_dir)

	# ff is not empty only if the --loc is active
	# (i.e. if user wishes that the job happens on /localscratch file copies)
	commands, ff_paths, ff_dirs = parse_command(i_script, loc)

	# pbs directives
	pbs = get_pbs(
		i_job,
		o_pbs,
		p_time,
		p_queue,
		p_nodes,
		p_procs,
		p_nodes_names,
		p_mem,
		gpu,
		email,
		email_address
	)

	# print-based, visual checks
	if not noq:
		check_pbs(pbs)
		check_command(job_file, commands)

	# set environment and working directory
	env = get_env(
		i_job,
		o_pbs,
		p_env,
		p_tmp,
		work_dir,
		gpu,
		loc,
		ff_paths
	)

	# write the psb file to provide to "qsub"
	write_job(i_job, job_file, pbs, env, loc, gpu, commands, ff_dirs)
	if run:
		print('Launched command: /bin/sh %s' % job_file)
		subprocess.Popen(['qsub', job_file])
		sys.exit(0)
