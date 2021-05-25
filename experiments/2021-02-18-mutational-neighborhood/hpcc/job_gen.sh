#!/bin/bash

# What is the name of this experiment?
EXP_TAG="2021-02-18-mutational_landscape_2"
# Where is this experiment located (i.e., where is the repo sitting?)
EXP_DIR=/mnt/home/fergu358/research/plasticity/evolutionary-consequences-of-plasticity/experiments/${EXP_TAG}
# Where is the existing data (from the other experiment) that we will use to create the mutants?
BASE_DATA_DIR=/mnt/research/devolab/fergujini/2021-02-08-evo-dynamics
# Where is the existing KNOCKOUT data? (used for a specific analysis)
BASE_KNOCKOUT_DIR=/mnt/gs18/scratch/users/fergu358/plasticity/evolvability/architecture_data_2
# Where should we output files?
BASE_OUTPUT_DIR=/mnt/gs18/scratch/users/fergu358/plasticity/evolvability/landscape_data_two_step

# How many replicates were in the existing data?
REPLICATES=100
# Where are the AVIDA config files located?
CONFIG_DIR=${EXP_DIR}/hpcc/config
# Where is this "job_gen" file (and the seed scripts) located?
ANALYSIS_DIR=${EXP_DIR}/analysis/landscape_analysis_two_step
# Where would you like to save the job files?
JOB_DIR=${BASE_OUTPUT_DIR}/two_step_jobs
# What's the specific directory containing the existing replicate directories?
INPUT_DIR=${BASE_DATA_DIR}/phase-2
# What's the specific directory containing the existing *knockout* replicate directories?
KNOCKOUT_DIR=${BASE_KNOCKOUT_DIR}/data
# Where should we output the replicate files? (can be the same as BASE_OUTPUT_DIR if you'd like)
OUTPUT_DIR=${BASE_OUTPUT_DIR}/data


##### NO CONFIGURATION NEEDED BELOW THIS POINT

mkdir -p ${JOB_DIR}
mkdir -p ${OUTPUT_DIR}

python3 gen_sub_multi.py --old_dir ${INPUT_DIR} --knockout_dir ${KNOCKOUT_DIR} --new_dir ${OUTPUT_DIR} --config_dir ${CONFIG_DIR} --analysis_dir ${ANALYSIS_DIR} --replicates ${REPLICATES} --job_dir ${JOB_DIR}
