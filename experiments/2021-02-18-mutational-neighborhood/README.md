# 2021-02-18 - Mutational neighborhood analyses

These analyses were an attempt to understand the genetic architectures evolved in the different treatments. 

The only result from this experiment included in the manuscript is the `mutational robustness` metric. 
While that metric is described in the paper and [supplemental material](https://lalejini.com/evolutionary-consequences-of-plasticity/), we include additional analyses here in case they are useful for future work. 

**NOTE**: This process draws _heavily_ from the pipeline and analyses in the 2021-02-18-knockouts expeirment. 
As such, it may be useful to read that readme before this one, or refer to it when details are omitted here because they are identical. 

## Structure
The files within are split into two directories: `hpcc` and `local`. 

- `hpcc` contains all the files necessary to generate and collate the data on a computing cluster (here we MSU's HPCC).
  - Some files in this folder are well documented, others are not. 
  - Instructions on how to use these scripts is identical to the knockout experiment, and we refer you there. 
- `local` contains files used to analyze and plot the data once it's been pulled off the cluster
  - These files are much more consistently commented 
  - A summary is included at the top of each analysis file to briefly describe what that particular file does

## Mutational neighborhood

In Avida, we can simulate a mutation on a given genotype simply by substituting the one instruction for another. 
While it is possible to perform any possible mutation, here we systematically create and test the one- and two-step mutants on a given genotype. 
To do this, we first create one-step mutants by systematically substituting each instruction in the genotype with _every_ other possible instruction. 
Once a one-step mutant is created, we repeat the process, only keeping the first mutation constant, to create two-step mutants. 
Since our genomes are locked at 100 instructions, and we have 32 instructions, a single genotype has 3,100 one-step mutants and millions of two-stem mutants. 
It should be noted that we technically use 33 instructions, because we included the inert knockout instruction (NopX), but it is excluded in most analyses. 

Once these mutants have been generated, we can test them in the environments the original genotype may have experienced. 
Thus, we can see how the mutations affect the performance of the genotype (e.g., does the mutation change which logic tasks are executed?).

## Usage

Again, to generate the data and run the analyses for this experiment, please refer to the steps outlined in the 2021-02-18-knockouts experiment.
The local and hpcc subdirectories behave identically between the two experiments.
