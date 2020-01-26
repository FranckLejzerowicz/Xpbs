# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
import subprocess
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
		gpu,
		verbose
):
	print(i_script)
	print(o_pbs)
	print(i_job)
	print(p_queue)
	print(p_env)
	print(p_dir)
	print(p_nodes)
	print(p_tmp)
	print(p_procs)
	print(p_time)
	print(p_mem)
	print(p_nodes_names)
	print(email)
	print(run)
	print(loc)
	print(noq)
	print(gpu)
	print(verbose)

	email_address = get_email_address(dirname(abspath( __file__ )))
	print(email_address)

	job_file = get_job_file(
		o_pbs, i_job, gpu
	)
	print(job_file)

	workdir = get_work_dir(p_dir)
	print(workdir)

	# ff is not empty only if the --loc is active
	# (i.e. if user wishes that the job happens on /localscratch file copies)
	commands, ff_paths, ff_dirs = parse_command(
		i_script, loc
	)
	print(commands)
	print(ff_paths)
	print(ff_dirs)

	# pbs directives
	pbs = get_pbs(
		gpu,
		p_time,
		p_queue,
		i_job,
		email,
		email_address,
		o_pbs,
		p_nodes,
		p_procs,
		p_nodes_names,
		p_mem,
	)
	print(pbs)

	if not noq:
		check_pbs(pbs)
		check_command(job_file, commands)

	# set environment and working directory
	env = get_env(
		i_job,
		o_pbs,
		p_env,
		p_tmp,
		p_dir,
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
