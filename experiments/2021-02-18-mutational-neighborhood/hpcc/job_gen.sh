#!/bin/bash

EXP_TAG="2021-02-18-mutational_landscape_2"
EXP_DIR=/mnt/home/fergu358/research/plasticity/evolutionary-consequences-of-plasticity/experiments/${EXP_TAG}
BASE_DATA_DIR=/mnt/research/devolab/fergujini/2021-02-08-evo-dynamics
BASE_KNOCKOUT_DIR=/mnt/gs18/scratch/users/fergu358/plasticity/evolvability/architecture_data_2
BASE_OUTPUT_DIR=/mnt/gs18/scratch/users/fergu358/plasticity/evolvability/landscape_data_two_step

REPLICATES=100
CONFIG_DIR=${EXP_DIR}/hpcc/config
ANALYSIS_DIR=${EXP_DIR}/analysis/landscape_analysis_two_step
JOB_DIR=${BASE_OUTPUT_DIR}/two_step_jobs
## JOB_DIR=./jobs
INPUT_DIR=${BASE_DATA_DIR}/phase-2
KNOCKOUT_DIR=${BASE_KNOCKOUT_DIR}/data
OUTPUT_DIR=${BASE_OUTPUT_DIR}/data


mkdir -p ${JOB_DIR}
mkdir -p ${OUTPUT_DIR}

python3 gen_sub_multi.py --old_dir ${INPUT_DIR} --knockout_dir ${KNOCKOUT_DIR} --new_dir ${OUTPUT_DIR} --config_dir ${CONFIG_DIR} --analysis_dir ${ANALYSIS_DIR} --replicates ${REPLICATES} --job_dir ${JOB_DIR}
