# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
import datetime
from os.path import (
	abspath, exists, expanduser, isfile
)
from pathlib import Path


def write_job(
		i_job,
		job_file,
		pbs,
		env,
		loc,
		gpu,
		commands,
		ff_dirs
):
	with open(job_file, 'w') as o:
		for i in pbs:
			o.write('%s\n' % i)
		o.write('\n')
		o.write('\n')
		for e in env:
			o.write('%s\n' % e)
		o.write('echo "%s"\n' % abspath(job_file))
		o.write('\n')
		o.write('\n')
		if loc:
			for f_home, f_loc in ff_dirs.items():
				o.write('mkdir -p %s\n' % f_loc)
		o.write('\n')
		o.write('\n')
		for command in commands:
			if loc:
				for f_home, f_loc in ff_dirs.items():
					if f_home in command:
						command = command.replace(f_home, f_loc)
			o.write('%s\n' % command)
		o.write('\n')
		o.write('\n')
		if loc:
			for f_home, f_loc in ff_dirs.items():
				o.write('rsync -auq %s/ %s\n' % (f_loc, f_home))
			if gpu:
				o.write('cd $SLURM_SUBMIT_DIR\n')
			else:
				o.write('cd $PBS_O_WORKDIR\n')
			o.write('rm -rf ${locdir}\n')
		if gpu:
			o.write('\nrm -fr $TMPDIR/%s_${SLURM_JOB_ID}\n' % i_job)
			o.write('echo "rm -fr $TMPDIR/%s_${SLURM_JOB_ID}"\n' % i_job)
		else:
			o.write('\nrm -fr $TMPDIR/${PBS_JOBNAME}_${PBS_JOBNUM}\n')
			o.write('echo "rm -fr $TMPDIR/${PBS_JOBNAME}_${PBS_JOBNUM}"\n')
		o.write('echo "Done!"\n')


def get_job_file(o_pbs, i_job, gpu):
	if not o_pbs:
		cur_time = str(
			datetime.datetime.now()
		).split('.')[0].replace(
			' ', '-'
		).replace(
			':', '-'
		)
		if gpu:
			job_file = '%s/%s_%s_slurm.sh' % (abspath('.'), i_job, cur_time)
		else:
			job_file = '%s/%s_%s.pbs' % (abspath('.'), i_job, cur_time)
	else:
		job_file = o_pbs
	return job_file


def get_work_dir(p_dir):
	if exists(p_dir):
		work_dir = abspath(p_dir)
	else:
		work_dir = str(Path.home())
	return work_dir


def get_email_address(root):
	config = '%s/config.txt' % root
	if not isfile(config):
		print('Problem with config file:\n- %s do not exists\n-> Exiting...' % config)
		sys.exit(1)
	else:
		home_user = expanduser('~')
		with open(config) as f:
			for line in f:
				ls = line.strip().split()
				break
		if len(ls) != 2:
			print('Problem with config file:\n- %s does not contain two columns\n-> Exiting...' % config)
			sys.exit(1)
		if ls[0] == '$HOME' and ls[1] == 'your-email-address@whatever.yeah':
			print("Problem with config file:\n- %s need editing (see README's Requisites)\n-> Exiting..." % config)
			sys.exit(1)
		if ls[0] == home_user:
			email_address = ls[1]
		return email_address
