#!/bin/bash

CONFIG_DIR=/mnt/home/lalejini/devo_ws/plastic-evolvability-avida/experiments/2021-01-07/hpcc/config
DATA_DIR=/mnt/scratch/lalejini/data/avida-plasticity/2021-01-07
REPLICATES=100
ANALYSIS_FILE=/mnt/home/lalejini/devo_ws/plastic-evolvability-avida/experiments/2021-01-07/hpcc/avida_analysis_final_dom.cfg

python3 gen-sub.py --config_dir ${CONFIG_DIR} --data_dir ${DATA_DIR} --replicates ${REPLICATES} --run_experiment --run_analysis --analysis_file ${ANALYSIS_FILE}

