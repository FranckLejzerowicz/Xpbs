# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
from os.path import dirname, abspath
from Xpbs._misc import chunks


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


def get_nodes_ppn(n_, p):
    n = ['0%s' % n if n < 10 else str(n) for n in n_]
    if p == 1:
        nodes_ppn = 'nodes=' + '+'.join(['brncl-%s:ppn=1' % i for i in n])
    else:
        nn = len(n)
        ps = [sum(x) for x in chunks(([1] * p), 0, nn)]
        if sum(ps) != p:
            print('issue with the processors allocation\n- check function "get_nodes_ppn")')
            sys.exit(1)
        nodes_ppn = 'nodes=' + '+'.join(['brncl-%s:ppn=%s' % (i, ps[idx]) for idx, i in enumerate(n)])
    return nodes_ppn


def get_pbs(
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
):
    pbs = ['#!/bin/bash']
    if gpu:
        pbs.append('#SBATCH --export=ALL')
        pbs.append('#SBATCH --job-name=%s' % i_job)
        if p_queue:
            print('Warning: no queue but a PARTITION (automatically set to "gpu")')
        pbs.append('#SBATCH --partition=gpu')
        pbs.append('#SBATCH --gres=gpu:1')
        if email:
            pbs.append('#SBATCH --mail-type=END,FAIL')
        else:
            pbs.append('#SBATCH --mail-type=FAIL')
        pbs.append('#SBATCH --mail-user="%s"' % email_address)
        if o_pbs:
            out_dir = dirname(abspath(o_pbs))
        else:
            out_dir = '${SLURM_SUBMIT_DIR}'
        pbs.append('#SBATCH -o %s/%s_%sj_slurm.o' % (out_dir, i_job, '%'))
        pbs.append('#SBATCH -e %s/%s_%sj_slurm.e' % (out_dir, i_job, '%'))
        # Specify number of CPUs (max 2 nodes, 32 processors per node) and of memory
        if p_nodes_names:
            pbs.append('#SBATCH --nodelist=brncl-%s' % p_nodes_names[0])
        else:
            pbs.append('#SBATCH --nodelist=brncl-33')
        pbs.append('#SBATCH --nodes=1')
        # pbs.append('#SBATCH --cpus-per-task=1')
        # pbs.append('#SBATCH --ntasks-per-node=1')

        m_num = float(p_mem[0])
        m_byt = p_mem[1]
        if m_byt == 'gb':
            m_num = int(m_num * 1000)
        pbs.append('#SBATCH --mem=%s' % m_num)
        # Tell PBS the anticipated run-time for your job, where walltime=HH:MM:SS
        pbs.append('#SBATCH --time=%s' % get_time(p_time))
    else:
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
        # Specify number of CPUs (nodes, processors per node) and of memory
        if p_nodes_names:
            nodes_ppn = get_nodes_ppn(p_nodes_names, p_procs)
        else:
            nodes_ppn = 'nodes=%s:intel:ppn=%s' % (p_nodes, p_procs)
        pbs.append('#PBS -l %s' % nodes_ppn)
        pbs.append('#PBS -l mem=%s' % (''.join(p_mem)))
        # Tell PBS the anticipated run-time for your job, where walltime=HH:MM:SS
        pbs.append('#PBS -l walltime=%s' % get_time(p_time))
    return pbs
