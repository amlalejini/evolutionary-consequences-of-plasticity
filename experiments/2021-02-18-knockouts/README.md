# 2021-02-18 - Lineage knockout analyses

These analyses were an attempt to understand the genetic architectures evolved in the different treatments. 

None of the results from these analyses are included in the manuscript and thus are not elaborated in the supplmental material. 
Instead, we simply leave the scripts here for future use! 

## Structure
The files within are split into two directories: `hpcc` and `local`. 

- `hpcc` contains all the files necessary to generate and collate the data on a computing cluster (here we MSU's HPCC).
  - Some files in this folder are well documented, others are not. 
  - Instructions on how to use these scripts is included below!
- `local` contains files used to analyze and plot the data once it's been pulled off the cluster
  - These files are much more consistently commented 
  - A summary is included at the top of each analysis file to briefly describe what that particular file does

## Knockouts

### Knockouts in Avida
- Genomes in Avida are lineage sequences of instructions
  - Thus, to knockout an instruction, we can just replace it with an inert instruction (here we used "NopX")
- Here, we create and test all possible knockouts on each genotype along a treatment's representative lineage (by systematically knocking out each of the 100 sites in each genotype)
- Knockouts give us _some_ insight into what a particular site is doing in the genome
  - _e.g._, if the original genotype performs NAND, but an organism with a knockout at site 12 does not perform NAND, site 12 must be involved in the NAND machinery
  - However, this techinique does not detect all machinery perfectly. Sometimes two or more sites interact in a way that a single knockout cannot detect

### Knockout and site classification

**Knockout classification**

For a given task, we can classify the effect of the knockout using the table below. 
The first four columns ask if the task was performed by the original / knockout organism in the given condition:
| Original - ENV-A  | Original - ENV-B  | Knockout - ENV-A  | Knockout - ENV-B  | Classification |
| ----------- | ----------- | ----------- | ----------- | ----------- |
| False | False | False | False | No change |
| False | False | False | True  | Appearance of plastic trait |
| False | False | True  | False | Appearance of plastic trait |
| False | False | True  | True  | Appearance of non-plastic trait |
| False | True  | False | False | Loss of plastic trait |
| False | True  | False | True  | No change |
| False | True  | True  | False | Plasticity inversion |
| False | True  | True  | True  | Loss of plasticity |
| True  | False | False | False | Loss of plastic trait |
| True  | False | False | True  | Plasticity Inversion |
| True  | False | True  | False | No change |
| True  | False | True  | True  | Loss of plasticity |
| True  | True  | False | False | Loss of non-plastic trait |
| True  | True  | False | True  | Appearance of plasticity |
| True  | True  | True  | False | Appearance of plasticity |
| True  | True  | True  | True  | No change |



**Site classification**

Next, we can use the knockout classification to classify the function of a site for a given task.
We list the functionality, and then all knockout classifications that would label a site with that functionality for the focal task.

- Task machinery
  - Loss of non-plastic trait
  - Loss of plastic trait
- Plasticity machinery
  - Plasticity inversion
  - Loss of plasticity
- Otherwise the site did not previously serve one of these functions for this task

We also included three additional site functionality labels with different rules:
- Replication machinery - where the knockout caused the gestation time in either environment to increase by more that 2 instruction executions 
  - 2 was a somewhat arbitrary constant used to avoid counting jump instructions as replication machinery
- Required machinery - where the knockout produced an organism incapable of reproduction 
- Vestigial machinery - where the site previously encoded a task but now it does not, even though the instruction has not changed
  - This implies that a mutation elsewhere in the genome broke the task
  - A site is marked as vestigial if it did not incur a mutation in this generation and if it was classified as either 'Task machinery' or 'Vestigial machinery' last generation


After classifying the sites of a genome using the six base tasks, we applied a layer of abstraction to analyze sites at the ENV-A (odd) and ENV-B (even) level. 
Note: Here we will use ENV-A and ENV-B, but the R scripts preceeded these terms, and so they use odd and even (respectively)

For ENV-A, the following classifications are assigned:
- ENV-A task machinery
  - Site encodes task machinery for at least one task in ENV-A
  - Site encodes task machinery, vestigial machinery, plasticity machinery, or nothing for the other ENV-A tasks (thus task machinery takes precedence)
- ENV-A plasticity machinery  
  - Site encodes plasticity machinery for at least one task in ENV-A
  - Site encodes plasticity machinery, vestigial machinery, or nothing for the other ENV-A tasks (thus plastic machinery takes precedence over vestigial machinery)
- ENV-A vestigial machinery
  - Site encodes vestitigal machinery for at least one task in ENV-A
  - For all other ENV-A tasks, site encodes either vestigial machinery or nothing

An identical classifcation system is followed for ENV-B tasks.


Finally, we apply one more level of abstraction, combinining ENV-A and ENV-B classifications to create one 'high-level' functionality classification for each site in the genome. 

| ENV-A  | ENV-B  | High-level classification |
| ----------- | ----------- | ----------- | 
| None | None | None |
| Task | None | ENV-A task machinery |
| None | Task | ENV-B task machinery |
| Task | Task | Both task machinery |
| Vestigial | None | ENV-A vestigial machinery |
| None | Vestigial | ENV-B vestigial machinery|
| Vestigial | Vestigial | Both vestigial machinery |
| Task | Vestigial | ENV-A recycled ENV-B |
| Vestigial | Task | ENV-B recycled ENV-A |
| Plastic | None | ENV-A plastic machinery |
| None | Plastic | ENV-B plastic machinery |
| Plastic | Plastic | Both plastic machinery |
| Task | Plastic | ENV-A task, ENV-B plastic |
| Plastic | Task | ENV-B task, ENV-A plastic |
| Plastic | Vestigial | ENV-A plastic, ENV-B vestigial |
| Vestigial | Plastic | ENV-B plastic, ENV-A vestigial |

Again, for the high-level functionality classification, we make two special cases (see above):
- Replication machinery - where the knockout caused the gestation time in either environment to increase by more that 2 time units 
- Required machinery - where the knockout produced an organism incapable of reproduction 

Once we have classified the function served be each locus in the genome, we use this data for a variety of analyses. 

## HPCC subdirectory

As mentioned above, the hpcc subdirectory contains everything necessary for generating the data needed for these analyses. 
Note that we are not evolving any organisms here, so this experiment has a very different structure than those that came before it. 
Instead of evolving populations, this experiment pulls the evolutionary history of an evolved population saved elsewhere on the system. 
It then creates the knockouts of organism along the reprsentative lineage, runs the knockouts, and analyzes them. 
This is all done via slurm jobs (described below). 
After the slurm jobs complete, you will need to run the aggregation scripts to collect the data from all the replicates and prepare it for download. 

To generate and analyze the knockouts for each replicate, you will need to modify the `job_gen.sh` file. 
This file contains all the information needed to determine where the existing data lives on the system, where we will store our knockouts, etc. 
Once that file has been edited, you simply need to run the file with the following command: 
```./job_gen.sh```
Once that's done, you will simply need to navigate to the job directory (which is specified in `job_gen.sh`) and queue the slurm files: 
```sbatch {FILENAME}.sb``` where FILENAME will likely look like RUN_C0 or something similar. 
The slurm files should handle everything from there. 
If you decide you need more control, check out `gen_sub_multi.py` or `base_script.txt`. 
If you need to edit the scripts that act on individual replicates, they are either R scripts prefixed with 'seed_', python scripts (e.g., generate_knockouts.py), or the other files in the directory (e.g., the instruction set or header_lineage.txt). 

After the slurm jobs finish, you can run the aggregation scripts in the hpcc directory. 
Don't forget your `module load R` !
All aggregation R scripts are prefixed with `aggregate_` and can be run with `Rscript {FILENAME}`.
Note that there are extra aggregation scripts in the `old` directory, but as the name implies they haven't been used in a long time and thus may be less likely to work or use outdated methods compared to the newer scripts. 

## Local subdirectory

Once you have aggregated the data on the hpcc, you can pull the aggregate data to your local computer using `scp`, `rsync`, etc. 
All data should be put in the `./local/data` subdirectory on your local machine. 
With the data downloaded, you should be able to run the R scripts with `Rscript {FILENAME}.R` or by opening them in RStudio. 
Data loading / plot saving may need tweaked, as it is likely errors in those two locations were made in the process of standardizing the analyses. 
Plots should be ouptut to the `./local/plots` directory. 
Again, like the `hpcc` directory, the `local` directory has an `old` subdirectory with older scripts that are less likely to work but are potentially useful for future reference. 

As mentioned above, each analysis script in the `local` directory should include a brief summary at the top of the file to give you a rough idea of what is going on. 
These files have _mostly_ been commented much more thoroughly than `hpcc` scripts, as well! 


If you have issues / questions, feel free to ping me! (Austin)
