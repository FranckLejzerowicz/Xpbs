# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
from os.path import dirname, abspath


def chunks(l, chunk_number):
    # Adapted from:
    # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    n = len(l) // chunk_number
    return [l[i:i + n] for i in range(0, len(l), n)]


def get_nodes_ppn(n_: tuple, p: int) -> str:
    """
    Distribute the number of processors requested among the requested nodes.

    :param n_: number of nodes requested.
    :param p: number of processors requested.
    :return:
    """
    # get the string version of the passed nodes numbers
    n = ['0%s' % n if int(n) < 10 else str(n) for n in n_]
    if p == 1:
        # get the barnacle nodes with one processor per node if one processor is queried
        nodes_ppn = 'nodes=' + '+'.join(['brncl-%s:ppn=1' % i for i in n])
    else:
        # otherwise get the number of nodes
        nn = len(n)
        # distribute the total numbers of processors of a number chunks equal to the number of nodes
        ps = [sum(x) for x in chunks(([1] * p), nn)]

        # this error is unlikely ot happen but would let people query the developer for a better way to do this!
        if sum(ps) != p:
            print('issue with the processors allocation\n- check function "get_nodes_ppn")')
            sys.exit(1)
        # make the directive for the distributed processors across node
        nodes_ppn = 'nodes=' + '+'.join(['brncl-%s:ppn=%s' % (i, ps[idx]) for idx, i in enumerate(n)])
    return nodes_ppn


def get_pbs(i_job: str, o_pbs: str, p_time: str, p_queue: str, p_nodes: int,
            p_procs: int, p_nodes_names: tuple, p_mem: tuple, gpu: bool,
            torque: bool, email: bool, email_address: str) -> list:
    """
    Collect the directives for the Torque or Slurm job.

    :param i_job: job name.
    :param o_pbs: output script filename.
    :param p_time: number of hours for the job to complete (or abort).
    :param p_queue: queue to add the job to.
    :param p_nodes: number of nodes to query.
    :param p_procs: number of processors to query.
    :param p_nodes_names: numeric names of the nodes to query.
    :param p_mem: memory usage (number, dimesion).
    :param gpu: whether to run on GPU or not (and hence use Slurm in our case).
    :param email: whether to send email at job completion.
    :param email_address: email address passed by the user.
    :return: script
    """

    # add a shebang that's hopefully universal here.
    pbs = ['#!/bin/bash']

    # if running on GPU : using Slurm
    if torque:
        pbs.append('#PBS -V')
        pbs.append('#PBS -N %s' % i_job)
        if p_queue:
            pbs.append('#PBS -q %s' % p_queue)
        if email:
            pbs.append('#PBS -m ae')
        else:
            pbs.append('#PBS -m a')
        pbs.append('#PBS -M %s' % email_address)
        if o_pbs:
            out_dir = dirname(abspath(o_pbs))
        else:
            out_dir = '${PBS_O_WORKDIR}'
        pbs.append('#PBS -o localhost:%s/%s_${PBS_JOBID}.o' % (out_dir, i_job))
        pbs.append('#PBS -e localhost:%s/%s_${PBS_JOBID}.e' % (out_dir, i_job))
        if p_nodes_names:
            nodes_ppn = get_nodes_ppn(p_nodes_names, p_procs)
        else:
            nodes_ppn = 'nodes=%s:intel:ppn=%s' % (p_nodes, p_procs)
        pbs.append('#PBS -l %s' % nodes_ppn)
        pbs.append('#PBS -l mem=%s' % (''.join(list(p_mem))))
        pbs.append('#PBS -l walltime=%s:00:00' % p_time)
    else:
        pbs.append('#SBATCH --export=ALL')
        pbs.append('#SBATCH --job-name=%s' % i_job)

        partition = '#SBATCH --partition=normal'
        if gpu:
            partition = '#SBATCH --partition=gpu'
            partition += '\n#SBATCH --gres=gpu:1'
        elif p_queue:
            partition = '#SBATCH --partition=%s' % p_queue
        pbs.append(partition)

        if email:
            pbs.append('#SBATCH --mail-type=END,FAIL,TIME_LIMIT_80')
        else:
            pbs.append('#SBATCH --mail-type=FAIL,TIME_LIMIT_80')
        pbs.append('#SBATCH --mail-user="%s"' % email_address)

        if o_pbs:
            out_dir = dirname(abspath(o_pbs))
        else:
            out_dir = '${SLURM_SUBMIT_DIR}'

        pbs.append('#SBATCH --output=%s/%s_%sj_slurm.o' % (out_dir, i_job, '%'))
        pbs.append('#SBATCH --error=%s/%s_%sj_slurm.e' % (out_dir, i_job, '%'))
        # Specify number of CPUs (max 2 nodes,
        # 32 processors per node) and of memory
        if gpu:
            if p_nodes_names:
                pbs.append('#SBATCH --nodelist=brncl-%s' % p_nodes_names[0])
            else:
                pbs.append('#SBATCH --nodelist=brncl-33')
            pbs.append('#SBATCH --nodes=1')
        else:
            pbs.append('#SBATCH --nodes=%s' % p_nodes)
            pbs.append('#SBATCH --ntasks-per-node=%s' % p_procs)

        m_num = float(p_mem[0])
        m_byt = p_mem[1]
        if m_byt == 'gb':
            m_num = int(m_num * 1000)
        elif m_byt == 'kb':
            m_num = int(m_num / 1000)
        pbs.append('#SBATCH --mem=%s' % m_num)
        pbs.append('#SBATCH --time=%s:00:00' % p_time)

    return pbs
