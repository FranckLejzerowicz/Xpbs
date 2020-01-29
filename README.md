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

## Requisite

**Attention**: it is necessary to edit the file: `Xpbs/config.txt`
This file must contain only one line and two columns, separated by a tab or space.
- The first column entry must be your _machine user home path_
  - to find you _machine user home path_, just go in a terminal and type:
    ```echo $HOME```. Then, copy and paste the returned characters as the first columns entry.
- The second column entry must be your email address

One valid example would be:
```
/home/edithpiaf lamome@belleville.fr
```
 

## Input

Two type of inputs passed to `-i` or `--i-script` are possible:
1. A path to a file containing bash command line(s) (the file extension needs not to be `.sh`)
2. Directly a command line (between double quotes, e.g. `-i "tar xpfz archive.tar.gz"`) 

## Outputs

A _Torque_'s or _Slurm_'s script (if GPU are queried), including directives for resources querying (the file extension shall be .pbs).

The would then needs to:
1. Check the written `.pbs` script for modified paths or errors (**strongly** advised)
    * especially if option `--loc` is used (copy job input files and execute on a /localscratch folder, as in this case some existing path may be copied that should not be, as for example program executatble paths...) 
    * **attention**: if option `--run` is used, it is impossible to check (use with caution) 
2. Run `qsub <path>.pbs` (for Torque), or `squeue <path>.sh` (for Slurm)
  
## Usage

```
./Xpbs/scripts/run_Xpbs.py -i <input_path> -o <output_path> -j <job_name> [OPTIONS]
```

It is not very necessary to set values for the options `-q` and `-d`, as well as for option `-N` unless you 
have a good idea of the nodes on which you want the job to be run...

*It's possible that you first need to* `chmod 755 ./Xpbs/script/run_Xpbs.py` *or to add the tool to your* `$PATH`

### Optional arguments

``` 
Usage: run_Xpbs.py [OPTIONS]

Options:
  -i, --i-script TEXT             Script of command lines to transform to
                                  Torque/Slurm job(Command line without '-'
                                  also works (e.g. 'tar cpfz file.tar.gz
                                  folder/*'))  [required]
  -o, --o-pbs TEXT                PBS job file name
  -j, --i-job TEXT                Job name  [required]
  -q, --p-queue [short4gb|med4gb|med8gb|long8gb|longmem|highmem]
                                  Queue name
  -e, --p-env TEXT                Conda environment to run the job
  -d, --p-dir TEXT                Output directory  [default: .]
  -n, --p-nodes INTEGER           Number of nodes  [default: 1]
  -T, --p-tmp TEXT                Alternative temp folder to the one defined
                                  in $TMPDIR
  -p, --p-procs INTEGER           Number of processors  [default: 4]
  -t, --p-time TEXT               Walltime limit (max 3 integers: HH MM SS)
                                  [default: 10, 00, 00]
  -M, --p-mem TEXT                Expected memory usage (2 entries: (1) an
                                  integer, (2) one of ['b', 'kb', 'mb', 'gb'])
                                  [default: 1, gb]
  -N, --p-nodes-names [0|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42|43|44|45|46|47|48|49|50|51|52|53|54]
                                  Node names by the number(s), e.g. for
                                  brncl-04, enter '4'
  --email / --no-email            Send email at job completion (always if
                                  fail)  [default: False]
  --run / --no-run                'Run the PBS job before exiting (subprocess)
                                  [default: False]
  --loc / --no-loc                Make copy of directory to /localscratch
                                  [default: False]
  --noq / --no-noq                Do not ask sanity check  [default: False]
  --gpu / --no-gpu                Switch from Torque to Slurm (including
                                  querying 1 gpu)  [default: False]
  --version                       Show the version and exit.
  --help                          Show this message and exit. 
```


### Bug Reports

contact `flejzerowicz@health.ucsd.edu`

### Acknowledgments

Tomasz Kosciolek had been the one providing me with a first example of PBS script that collect nice job info (temp path, setup) - Thanks Tomek!
