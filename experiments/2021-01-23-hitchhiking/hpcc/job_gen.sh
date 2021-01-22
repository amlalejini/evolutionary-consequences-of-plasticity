#!/bin/bash

EXP_TAG=2021-01-23-hitchhiking
EXP_DIR=/mnt/home/lalejini/devo_ws/evolutionary-consequences-of-plasticity/experiments/${EXP_TAG}
BASE_DATA_DIR=/mnt/scratch/lalejini/data/avida-plasticity/${EXP_TAG}

REPLICATES=100
CONFIG_DIR=${EXP_DIR}/hpcc/config
JOB_DIR=${BASE_DATA_DIR}/jobs
# JOB_DIR=./jobs
PHASE_ONE_DIR=${BASE_DATA_DIR}/phase-1
PHASE_TWO_DIR=${BASE_DATA_DIR}/phase-2

python3 gen_sub_multi.py --phase_one_dir ${PHASE_ONE_DIR} --phase_two_dir ${PHASE_TWO_DIR} --config_dir ${CONFIG_DIR} --replicates ${REPLICATES} --job_dir ${JOB_DIR}