# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import sys
from os.path import dirname, abspath

from Xpbs._utils import get_nodes_ppn


def check_pbs(pbs):
    print('-------------')
    print('PBS commands:')
    print('-------------')
    for i in pbs:
        print(i)
    dec = input('continue to write commands: <y/n>')
    if dec != 'y':
        print('Exiting')
        sys.exit(1)


def get_pbs(
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
        # args, t
):
    pbs = ['#!/bin/bash']
    # if args['gpu']:
    if gpu:
        pbs.append('#SBATCH --export=ALL')
        pbs.append('#SBATCH --job-name=%s' % i_job)
        # if 'q' in args:
        if p_queue:
            print('Warning: no queue but a PARTITION (automatically set to "gpu")')
        pbs.append('#SBATCH --partition=gpu')
        pbs.append('#SBATCH --gres=gpu:1')
        # if 'm' in args:
        if email:
            pbs.append('#SBATCH --mail-type=END,FAIL')
        else:
            pbs.append('#SBATCH --mail-type=FAIL')
        pbs.append('#SBATCH --mail-user="%s"' % email_address)
        # if 'o' in args:
        if o_pbs:
            outdir = dirname(abspath(o_pbs))
        else:
            outdir = '${SLURM_SUBMIT_DIR}'
        pbs.append('#SBATCH -o %s/%s_%sj_slurm.o' % (outdir, i_job, '%'))
        pbs.append('#SBATCH -e %s/%s_%sj_slurm.e' % (outdir, i_job, '%'))
        # Specify number of CPUs (max 2 nodes, 32 processors per node) and of memory
        # if 'N' in args:
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
        pbs.append('#SBATCH --time=%s' % t)
    else:
        pbs.append('#PBS -V')
        pbs.append('#PBS -N %s' % i_job)
        # if 'q' in args:
        if p_queue:
            pbs.append('#PBS -q %s' % p_queue)
        # if 'm' in args:
        if email:
            pbs.append('#PBS -m ae')
        else:
            pbs.append('#PBS -m a')
        pbs.append('#PBS -M %s' % email_address)
        # if 'o' in args:
        if o_pbs:
            outdir = dirname(abspath(o_pbs))
        else:
            outdir = '${PBS_O_WORKDIR}'
        pbs.append('#PBS -o localhost:%s/%s_${PBS_JOBID}.o' % (outdir, i_job))
        pbs.append('#PBS -e localhost:%s/%s_${PBS_JOBID}.e' % (outdir, i_job))
        # Specify number of CPUs (nodes, processors per node) and of memory
        # if 'N' in args:
        if p_nodes_names:
            nodes_ppn = get_nodes_ppn(p_nodes_names, p_procs)
        else:
            nodes_ppn = 'nodes=%s:intel:ppn=%s' % (p_nodes, p_procs)
        pbs.append('#PBS -l %s' % nodes_ppn)
        pbs.append('#PBS -l mem=%s' % (''.join(p_mem)))
        # Tell PBS the anticipated run-time for your job, where walltime=HH:MM:SS
        pbs.append('#PBS -l walltime=%s' % t)
    return pbs
