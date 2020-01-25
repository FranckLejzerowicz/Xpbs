# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import glob, os, sys
from Xpbs._utils import (
	get_time,
	get_job_file,
	get_work_dir,
	get_email_address
)


def Xpbs(
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
	print(i_script)
	print(o_pbs)
	print(i_job)
	print(p_queue)
	print(p_env)
	print(p_out_dir)
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

	email_address = get_email_address('config.txt')
	print(email_address)

	t = get_time(p_time)
	print(t)

	jobfile = get_job_file(
		o_pbs, i_job, gpu
	)
	print(jobfile)

	workdir = get_work_dir(p_out_dir)
	print(workdir)
	print(workdirfdsa)

	# pbs directives
	pbs = get_pbs(
		t,
		gpu,
		p_queue,
		i_job,
		email,
		email_address,
		o_pbs,
		p_nodes,
		p_procs,
		p_nodes_names,
		p_mem,

		args, t
	)


	# actual commands to run
	# ff is not empty only if the --loc is active
	# (i.e. if user wishes that the job happens on /localscratch file copies)
	clis, ff_paths, ff_dirs = parse_command(args)
	if not args['noq']:
		check_pbs(pbs)
		check_command(jobfile, clis)
	# set environment and working directory
	env = get_env(args, workdir, ff_paths)
	# write the psb file to provide to "qsub"
	write_job(jobfile, args, pbs, env, clis, ff_dirs)
	if args['run']:
		run_job(jobfile)














def collect_ff(abs_line, ff_paths, ff_dirs, args):
	"""
	This function is run when the --loc options is ON
	It will copy all the files that the job works on into
	the compute node /localscratch where the job will perform
	and the copy back the results in the original folder
	"""
	for abs_i in abs_line.strip().split():
		if os.path.exists(abs_i):
			abs_d = os.path.dirname(abs_i)
			# if args['nop']:
				# absli = li
			# else:
				# absli = os.path.abspath(li)
			ff_paths[abs_i] = '${locdir}%s' % abs_i
			ff_dirs[abs_d] = '${locdir}%s' % os.path.dirname(abs_i)
		elif abs_i[0] == '/':
			abs_d = os.path.dirname(abs_i)
			abs_d = os.path.dirname(abs_i)
			ff_dirs[abs_d] = '${locdir}%s' % os.path.dirname(abs_i)


def parse_command(args):
	clis = []
	ff_paths = {}
	ff_dirs = {}
	for i in args['i']:
		if os.path.isfile(i):
			with open(i) as f:
				for line in f:
					# if args['nop']:
						# clis.append(' '.join([x if os.path.exists(x) else x for x in line.strip().split()]))
					# else:
						# clis.append(' '.join([os.path.abspath(x) if os.path.exists(x) else x for x in line.strip().split()]))
					abs_line = ' '.join([os.path.abspath(x) if os.path.exists(x) or len(glob.glob(x)) else x for x in line.strip().split()])
					clis.append(abs_line)
					if args['loc']:
						collect_ff(abs_line, ff_paths, ff_dirs, args)
		else:
			# if args['nop']:
				# clis = [' '.join([x if os.path.exists(x) else x for x in args['c']])]
			# else:
				# clis = [' '.join([os.path.abspath(x) if os.path.exists(x) else x for x in args['c']])]
			abs_line = ' '.join([os.path.abspath(x) if os.path.exists(x) or len(glob.glob(x)) else x for x in args['i']])
			clis = [abs_line]
			if args['loc']:
				collect_ff(abs_line, ff_paths, ff_dirs, args)
			break
	return clis, ff_paths, ff_dirs


def check_command(jobfile, clis):
	print()
	print('Command lines to write in %s (for PBS queuing)' % jobfile)
	for cli in clis:
		print(cli)
	dec = input('continue?: <y/n>')
	if dec != 'y':
		print('Exiting')
		sys.exit(1)





def get_env(args, workdir, ff_paths):
	"""
	Get the lines to be written as header to the job
	Including:
		- the conda environment for the job
		- the temporary directory
	"""
	env = ['set -e', 'uname -a']
	if 'e' in args:
		if args['e'] == 'mmvec':
			env.append('echo "module load tensorflow_1.14.0"')
			env.append('module load tensorflow_1.14.0')
		elif args['e'] == 'virtualenv__rhapsody_ve_new':
			home_dir = os.path.expanduser("~")
			cur_env = args['e'].replace('virtualenv__', '')
			env.append('echo "Virtualenv environment is %s"' % cur_env)
			env.append('source %s/%s/bin/activate' % (home_dir, cur_env))
		else:
			env.append('echo "Conda environment is %s"' % args['e'])
			env.append('source activate %s' % args['e'])

	# temporary folder
	if 'T' in args:
		env.append("export TMPDIR='%s'" % args['T'].rstrip('/'))

	if args['gpu']:
		env.append('mkdir -p $TMPDIR/%s_${SLURM_JOB_ID}' % args['j'])
		env.append('export TMPDIR=$TMPDIR/%s_${SLURM_JOB_ID}' % args['j'])
		env.append("echo Temporary directory is $TMPDIR")
	else:
		env.append('mkdir -p $TMPDIR/%s_${PBS_JOBNUM}' % args['j'])
		env.append('export TMPDIR=$TMPDIR/%s_${PBS_JOBNUM}' % args['j'])
		env.append("echo Temporary directory is $TMPDIR")

	# if running on /localscratch
	if args['loc']:
		# get the output directory for the job
		if args['gpu']:
			if os.path.exists(args['d']) and args['d'] != '.':
				locdir='/localscratch/%s_${SLURM_JOB_ID}/%s' % (args['j'], args['d'].strip('/'))
			else:
				locdir='/localscratch/%s_${SLURM_JOB_ID}' % args['j']
		else:
			if os.path.exists(args['d']) and args['d'] != '.':
				locdir='/localscratch/%s_${PBS_JOBNUM}/%s' % (args['j'], args['d'].strip('/'))
			else:
				locdir='/localscratch/%s_${PBS_JOBNUM}' % args['j']
		env.append('locdir=%s' % locdir)
		# create fresh folder
		env.append('rm -rf ${locdir}')
		env.append('mkdir -p ${locdir}')
		env.append('cd ${locdir}')
		for f_home in sorted(ff_paths):
			# env.append('rsync -aq %s ${locdir}' % f_home)
			env.append('cp -r --parents %s ${locdir}' % f_home)
		env.append('echo Working directory is ${locdir}')
	else:
		### Switch to working directory; default is home directory.
		if args['gpu']:
			env.append('cd $SLURM_SUBMIT_DIR')
			env.append('echo Working directory is $SLURM_SUBMIT_DIR')
		else:
			env.append('cd $PBS_O_WORKDIR')
			env.append('echo Working directory is $PBS_O_WORKDIR')

	### Display the job context
	env.append('echo Running on host `hostname`')
	env.append('echo Time is `date`')
	env.append('echo Directory is `pwd`')
	# example of handling the specifically set environmental variables, here for display
	# Calculate the number of processors/nodes allocated to this run.
	if args['gpu']:
		env.append('echo Using ${SLURM_NPROCS} processors across ${SLURM_NNODES} nodes')
	else:
		env.append('NPROCS=`wc -l < $PBS_NODEFILE`')
		env.append('NNODES=`uniq $PBS_NODEFILE | wc -l`')
		env.append('echo Using ${NPROCS} processors across ${NNODES} nodes')
	if 'o' in args:
		outdir = os.path.abspath(os.path.dirname(args['o']))
	else:
		if args['gpu']:
			outdir = '${SLURM_SUBMIT_DIR}'
		else:
			outdir = '${PBS_O_WORKDIR}'
	if args['gpu']:
		env.append('echo "%s/%s_${SLURM_JOB_ID}_slurm.o"' % (outdir, args['j']))
		env.append('echo "%s/%s_${SLURM_JOB_ID}_slurm.e"' % (outdir, args['j']))
	else:
		env.append('echo "%s/%s_*.o"' % (outdir, args['j']))
		env.append('echo "%s/%s_*.e"' % (outdir, args['j']))
	return env



def write_job(jobfile, args, pbs, env, clis, ff_dirs):
	with open(jobfile, 'w') as o:
		for i in pbs:
			o.write('%s\n' % i)
		o.write('\n')
		o.write('\n')
		for e in env:
			o.write('%s\n' % e)
		o.write('echo "%s"\n' % os.path.abspath(jobfile))
		o.write('\n')
		o.write('\n')
		if args['loc']:
			for f_home, f_loc in ff_dirs.items():
				o.write('mkdir -p %s\n' % f_loc)
		o.write('\n')
		o.write('\n')
		for cli in clis:
			if args['loc']:
				for f_home, f_loc in ff_dirs.items():
					if f_home in cli:
						cli = cli.replace(f_home, f_loc)
			o.write('%s\n' % cli)
		o.write('\n')
		o.write('\n')
		if args['loc']:
			for f_home, f_loc in ff_dirs.items():
				o.write('rsync -auq %s/ %s\n' % (f_loc, f_home))
			if args['gpu']:
				o.write('cd $SLURM_SUBMIT_DIR\n')
			else:
				o.write('cd $PBS_O_WORKDIR\n')
			o.write('rm -rf ${locdir}\n')
		if args['gpu']:
			o.write('\nrm -fr $TMPDIR/%s_${SLURM_JOB_ID}\n' % args['j'])
			o.write('echo "rm -fr $TMPDIR/%s_${SLURM_JOB_ID}"\n' % args['j'])
		else:
			o.write('\nrm -fr $TMPDIR/${PBS_JOBNAME}_${PBS_JOBNUM}\n')
			o.write('echo "rm -fr $TMPDIR/${PBS_JOBNAME}_${PBS_JOBNUM}"\n')
		o.write('echo "Done!"\n')
			

def run_job(jobfile):
	import subprocess
	print('Launched command: /bin/sh %s' % jobfile)
	subprocess.Popen(['qsub', jobfile])
	sys.exit(0)
