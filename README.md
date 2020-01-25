# Xpbs

Convert of .sh script into Torque's .pbs or Slurm's script for use on a computer cluster with intel or gpu nodes

## Description

Working on computer cluster necessitates the querying of nodes, processors-per-node and memory resources that is conveniently done using directives in a script for job schedulers such as Torque or Slurm.
This script allows a user to pass a bash/sh script (e.g. a series of qiime2 commands) and returns a copy of the script within
From the user is only needed (1) email address and (2) path to a temporary folder
(email address is to get notifications when a job crashes/completes... and for nothing else!)
     
 # Install

```
git clone https://github.com/FranckLejzerowicz/Xpbs.git
cd Xpbs
python setup.py build_ext --inplace --force install
```
*_Note that python should be python3_

## Input

a bash script (the file extension needs not to be `.sh`)

## Outputs

A TORQUE's or SLURM's script (if GPU are queried), including directives for resources querying (the file extension shall be .pbs).

The would then needs to:
1. Check the written `.pbs` script for modified paths or errors (**strongly** advised)
2. Run `qsub <path>.pbs` (for TORQUE), or `squeue <path>.sh` (for SLURM)
  
## Usage

```
./Xpbs/scripts/run_Xpbs.py -i <input_path> -o <input_path> -j <job_name> [OPTIONS]
```
*It's possible that you first need to `chmod 755 ./Xpbs/script/run_Xpbs.py`*

### Optional arguments

```  
```


Bug Reports:
-----------
contact ``flejzerowicz@health.ucsd.edu``