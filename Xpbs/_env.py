# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from os.path import abspath, dirname, exists


def get_env(
        i_job,
        o_pbs,
        p_env,
        p_tmp,
        p_dir,
        gpu,
        loc,
        ff_paths
):
    """
    Get the lines to be written as header to the job
    Including:
    - the conda environment for the job
    - the temporary directory
    """
    env = ['set -e', 'uname -a']
    if p_env:
        if p_env == 'mmvec':
            env.append('echo "module load tensorflow_1.14.0"')
            env.append('module load tensorflow_1.14.0')
        else:
            env.append('echo "Conda environment is %s"' % p_env)
            env.append('source activate %s' % p_env)

    # temporary folder
    if p_tmp:
        env.append("export TMPDIR='%s'" % p_tmp.rstrip('/'))

    if gpu:
        job_id = 'SLURM_JOB_ID'
        job_dir = 'SLURM_SUBMIT_DIR'
        job_procs = 'SLURM_NPROCS'
        job_nodes = 'SLURM_NNODES'
    else:
        job_id = 'PBS_JOBNUM'
        job_dir = 'PBS_O_WORKDIR'
        job_procs = 'NPROCS'
        job_nodes = 'NNODES'
    env.append('mkdir -p $TMPDIR/%s_${%s}' % (i_job, job_id))
    env.append('export TMPDIR=$TMPDIR/%s_${%s}' % (i_job, job_id))
    env.append("echo Temporary directory is $TMPDIR")

    # if running on /localscratch
    if loc:
        # get the output directory for the job
        if exists(p_dir) and p_dir != '.':
            locdir = '/localscratch/%s_${%s}/%s' % (i_job, job_id, p_dir.strip('/'))
        else:
            locdir = '/localscratch/%s_${%s}' % (i_job, job_id)
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
        env.append('cd $%s' % job_dir)
        env.append('echo Working directory is $%s' % job_dir)

    ### Display the job context
    env.append('echo Running on host `hostname`')
    env.append('echo Time is `date`')
    env.append('echo Directory is `pwd`')

    # example of handling the specifically set environmental variables, here for display
    # Calculate the number of processors/nodes allocated to this run.
    if not gpu:
        env.append('NPROCS=`wc -l < $PBS_NODEFILE`')
        env.append('NNODES=`uniq $PBS_NODEFILE | wc -l`')
    env.append('echo Using ${%s} processors across ${%s} nodes' % (job_procs, job_nodes))

    if o_pbs:
        out_dir = abspath(dirname(o_pbs))
    else:
        out_dir = '${%s}' % job_dir

    if gpu:
        env.append('echo "%s/%s_${%s}_slurm.o"' % (out_dir, i_job, job_id))
        env.append('echo "%s/%s_${%s}_slurm.e"' % (out_dir, i_job, job_id))
    else:
        env.append('echo "%s/%s_*.o"' % (out_dir, i_job))
        env.append('echo "%s/%s_*.e"' % (out_dir, i_job))
    return env
