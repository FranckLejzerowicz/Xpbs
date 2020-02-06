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
from Xpbs._misc import chunks
from pathlib import Path


def get_time(p_time):
	time_args = [x if len(x) == 2 else '0%s' % x for x in p_time]
	time_args = [x if len(x) == 2 else x[1:] for x in time_args]
	if len(time_args):
		if len(time_args) == 1:
			time = '%s:00:00' % time_args[0]
		elif len(time_args) == 2:
			time = '%s:00' % ':'.join(time_args)
		else:
			time = ':'.join(time_args)
	else:
		print('Problem with time:', time_args)
		sys.exit(1)
	return time


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


def get_email_address(dir):
	path = '%s/config.txt' % dir
	if not isfile(path):
		print('Problem with config file:\n- %s do not exists\n-> Exiting...' % path)
		sys.exit(1)
	else:
		home_user = expanduser('~')
		with open(path) as f:
			for line in f:
				if line.startswith(home_user):
					email_address = line.strip().split()[-1]
		return email_address


def get_nodes_ppn(n_, p):
	n = ['0%s' % n if n < 10 else str(n) for n in n_]
	if p == 1:
		nodes_ppn =	'nodes=' + '+'.join(['brncl-%s:ppn=1' % i for i in n])
	else:
		nn = len(n)
		ps = [sum(x) for x in chunks(([1]*p), 0, nn)]
		if sum(ps) != p:
			print('issue with the processors allocation\n- check function "get_nodes_ppn")')
			sys.exit(1)
		nodes_ppn =	'nodes=' + '+'.join(['brncl-%s:ppn=%s' % (i, ps[idx]) for idx, i in enumerate(n)])
	return nodes_ppn
