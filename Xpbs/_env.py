# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from os.path import abspath, dirname, exists


def get_env(i_job: str, o_pbs: str, p_env: str, p_tmp: str, notmp: bool,
            work_dir: str, gpu: bool, slurm: bool, p_scratch_path: str,
            ff_paths: set, ff_dirs: set, loc: bool, p_pwd: str) -> list:
    """
    Get the lines to be written as header to the job
    Including:
    - the conda environment for the job
    - the temporary directory

    :param i_job: job name.
    :param o_pbs: output script filename.
    :param p_env: Conda environment to run the job.
    :param p_tmp: Alternative temp folder to the one defined in $TMPDIR.
    :param work_dir: Output directory.
    :param gpu: whether to run on GPU or not (and hence use Slurm in our case).
    :param p_scratch_path: Folder for moving files and computing in (default = do not move to scratch).
    :param ff_paths: files to be moved for /localscratch jobs.
    :param ff_dirs: folders to be moved for /localscratch jobs.
    :return: the commands for the compute environment.
    """
    # environment variables get collected / printed
    env = ['set -e', 'uname -a']
    # if a conda environment is used
    if p_env:
        # activate the env
        if p_env == 'virtualenv__mmvec':
            # and it is mmvec (specific here... should be deleted at some point!)
            env.append('source /home/flejzerowicz/virtualenv__mmvec/bin/activate')
            env.append('echo "Virtualenv environment is virtualenv__mmvec"')
            # env.append('echo "module load tensorflow_1.14.0"')
            # env.append('module load tensorflow_1.14.0')
        else:
            env.append('echo "Conda environment is %s"' % p_env)
            env.append('source activate %s' % p_env)

    # get the Torque / Slurm env variables ready for more generic usage below
    if gpu or slurm:
        job_id = 'SLURM_JOB_ID'
        job_dir = 'SLURM_SUBMIT_DIR'
        job_procs = 'SLURM_NPROCS'
        job_nodes = 'SLURM_NNODES'
    else:
        job_id = 'PBS_JOBID'
        job_dir = 'PBS_O_WORKDIR'
        job_procs = 'NPROCS'
        job_nodes = 'NNODES'

    if p_pwd:
        env.append("export %s='%s'" % (job_dir, p_pwd))

    env.append("CUR_JOBID=`echo ${%s} | cut -d'.' -f 1`" % job_id)

    if slurm:
        env.append("TMPDIR='/panfs/${USER}'")

    # set temporary folder
    if not notmp:
        if p_tmp:
            env.append("TMPDIR='%s'" % p_tmp.rstrip('/'))
        # create the temporary folder
        env.append('mkdir -p $TMPDIR/%s_${CUR_JOBID}' % i_job)
        env.append('export TMPDIR=$TMPDIR/%s_${CUR_JOBID}' % i_job)
        # env.append('mkdir -p $TMPDIR/%s_${%s}' % (i_job, job_id))
        # env.append('export TMPDIR=$TMPDIR/%s_${%s}' % (i_job, job_id))
        env.append("echo Temporary directory is $TMPDIR")

    # Display the job context
    env.append('echo Running on host `hostname`')
    env.append('echo Time is `date`')
    env.append('echo Directory is `pwd`')

    # example of handling the specifically set environmental variables,
    # here for display
    # Calculate the number of processors/nodes allocated to this run.
    if not gpu and not slurm:
        env.append('NPROCS=`wc -l < $PBS_NODEFILE`')
        env.append('NNODES=`uniq $PBS_NODEFILE | wc -l`')
    env.append('echo Using ${%s} processors across ${%s} nodes' % (
        job_procs, job_nodes))

    if o_pbs:
        out_dir = abspath(dirname(o_pbs))
    else:
        out_dir = '${%s}' % job_dir

    if gpu or slurm:
        env.append('jobstdout="%s/%s_${%s}_slurm.o"' % (out_dir, i_job, job_id))
        env.append('jobstderr="%s/%s_${%s}_slurm.e"' % (out_dir, i_job, job_id))
        # env.append('echo "%s/%s_${%s}_slurm.o"' % (out_dir, i_job, job_id))
        # env.append('echo "%s/%s_${%s}_slurm.e"' % (out_dir, i_job, job_id))
    else:
        env.append('jobstdout="%s/%s_${CUR_JOBID}.o"' % (out_dir, i_job))
        env.append('jobstderr="%s/%s_${CUR_JOBID}.e"' % (out_dir, i_job))
        # env.append('jobstdout="%s/%s_${%s}.o"' % (out_dir, i_job, job_id))
        # env.append('jobstderr="%s/%s_${%s}.e"' % (out_dir, i_job, job_id))
        # env.append('echo "%s/%s_*.o"' % (out_dir, i_job))
        # env.append('echo "%s/%s_*.e"' % (out_dir, i_job))
    env.append('echo "${jobstdout}"')
    env.append('echo "${jobstderr}"')

    # if running on /localscratch
    if p_scratch_path and loc:
        # get the output directory for the job
        # if exists(work_dir) and work_dir != '.':
        #     locdir = '%s/%s_${%s}/%s' % (p_scratch_path, i_job, job_id, work_dir.strip('/'))
        # else:
        locdir = '%s/%s_${%s}' % (p_scratch_path, i_job, job_id)
        env.append('locdir=%s' % locdir)
        # create fresh folder
        env.append('rm -rf ${locdir}')
        env.append('mkdir -p ${locdir}')
        env.append('cd ${locdir}')

        copied_dirs = set([x for x in sorted(ff_dirs) for y in sorted(ff_dirs) if x not in y])
        for ff in sorted(ff_dirs):
            if ff not in copied_dirs:
                env.append('if [ -d %s ]; then cp -r --no-preserve=mode --parents %s ${locdir}; fi 2>/dev/null\n' % (ff, ff))
        for ff in ff_paths:
            env.append('if [ -f %s ]; then cp -r --no-preserve=mode --parents %s ${locdir}; fi 2>/dev/null\n' % (ff, ff))
        env.append('echo Working directory is ${locdir}')
    else:
        ### Switch to working directory; default is home directory.
        env.append('cd $%s' % job_dir)
        env.append('echo Working directory is $%s' % job_dir)

    return env
