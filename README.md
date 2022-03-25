# Xpbs

Convert of .sh script into Torque's .pbs or Slurm's script for use on a computer cluster with intel or gpu nodes

## Description

Working on computer cluster necessitates the querying of nodes, 
processors-per-node and memory resources that is conveniently 
done using directives in a script for job schedulers such 
as [Slurm](https://slurm.schedmd.com/documentation.html) or
[Torque](http://docs.adaptivecomputing.com/torque/4-0-2/help.htm).
This script allows a user to pass a bash/sh script (e.g. a series of 
qiime2 commands) and returns a copy of the script within
From the user is only needed (1) email address and (2) path to a 
temporary folder (email address is to get notifications when a job 
crashes/completes... and for nothing else!)
     
 # Install

```
git clone https://github.com/FranckLejzerowicz/Xpbs.git
cd Xpbs
pip install -e .
```
*_Note that python should be python3_

## Requisite

**Attention**:

1. upon first use, the user is asked for and email address, that will be written
in `Xpbs/config.txt`. This file can be edited afterwards if you want to change
your email address.
2. please setup a temporary directory an environment variable `$TMPDIR` for
temporary files to be removed after the job completes:
  `export $TMPDIR="/Users/edith/temporary_dir""`
 

## Input

Two type of inputs passed to `-i` or `--i-script` are possible:
1. A path to a file containing bash command line(s) (the file extension needs 
not to be `.sh`)
2. Directly a command line (between double quotes,
e.g. `-i "tar xpfz archive.tar.gz"`) 

It might be of great importance for you to use the option `-e` to give the name
of a conda environment within which you have installed a software that the job 
will use.  

## Outputs

A _Torque_'s or _Slurm_'s script (if GPU are queried), including directives for
resources querying (the file extension shall be .pbs).

The would then needs to:
1. Check the written `.pbs` script for modified paths or errors (**strongly**
advised)
    * especially if option `-l` is used (copy job input files and execute
on the given "/localscratch" folder, as in this case some existing path may be copied that should not be, as for example program executatble paths...) 
    * **attention**: if option `--run` is used, it is impossible to check
(use with caution) 
3. Run `qsub <path>.pbs` (for Torque), or `squeue <path>.sh` (for Slurm)
  
## Usage

```
Xpbs -i <input_path> -o <output_path> -j <job_name> [OPTIONS]
```

It is not very necessary to set values for the options `-q` and `-d`, as well 
as for option `-N` unless you ```

### Bug Reports

contact `franck.lejzerowicz@gmail.com`

### Acknowledgments

Tomasz Kosciolek had been the one providing me with a first example of PBS
script that collect nice job info (temp path, setup) - Thanks Tomek!
