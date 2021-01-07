#!/bin/bash

EXP_TAG=2021-01-07-validation
CONFIG_DIR=/mnt/home/lalejini/devo_ws/plastic-evolvability-avida/experiments/${EXP_TAG}/hpcc/config
DATA_DIR=/mnt/scratch/lalejini/data/avida-plasticity/${EXP_TAG}
REPLICATES=100
ANALYSIS_FILE=/mnt/home/lalejini/devo_ws/plastic-evolvability-avida/experiments/${EXP_TAG}/hpcc/avida_analysis_final_dom.cfg

python3 gen-sub.py --config_dir ${CONFIG_DIR} --data_dir ${DATA_DIR} --replicates ${REPLICATES} --run_experiment --run_analysis --analysis_file ${ANALYSIS_FILE}

