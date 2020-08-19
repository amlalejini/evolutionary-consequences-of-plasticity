'''
todo - write out a configuration file!

Generate slurm job submission script.
'''

import argparse, os, sys, errno, subprocess, csv

seed_offset = 1000
default_num_replicates = 30
job_time_request = "48:00:00"
job_memory_request = "4G"
job_name = "avida"
executable = "avida"

run_configs = [
    # SENSORS+, CHANGING ENVIRONMENT (u30)
    "-set EVENT_FILE events-chg-u30.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 0 -set REACTION_SENSORS_NEUTRAL 0.0",
    # SENSORS-, CHANGING ENVIRONMENT (u30)
    "-set EVENT_FILE events-chg-u30.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0",

    # SENSORS+, CHANGING ENVIRONMENT (u300)
    "-set EVENT_FILE events-chg-u300.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 0 -set REACTION_SENSORS_NEUTRAL 0.0",
    # SENSORS-, CHANGING ENVIRONMENT (u300)
    "-set EVENT_FILE events-chg-u300.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0",

    # SENSORS+, CONST ENVIRONMENT
    "-set EVENT_FILE events-const-all.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 0 -set REACTION_SENSORS_NEUTRAL 0.0",
    # SENSORS+, CONST ENVIRONMENT
    "-set EVENT_FILE events-const-all.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0",
]

base_sub_script = \
"""#!/bin/bash
########## Define Resources Needed with SBATCH Lines ##########

#SBATCH --time=<<TIME_REQUEST>>          # limit of wall clock time - how long the job will run (same as -t)
#SBATCH --array=<<ARRAY_ID_RANGE>>
#SBATCH --mem=<<MEMORY_REQUEST>>        # memory required per node - amount of memory (in bytes)
#SBATCH --job-name <<JOB_NAME>>         # you can give your job a name for easier identification (same as -J)
#SBATCH --account=devolab

########## Command Lines to Run ##########

EXEC=<<EXEC>>
CONFIG_DIR=<<CONFIG_DIR>>

module load GCCcore/9.1.0

<<SUBMISSION_LOGIC>>

mkdir -p ${RUN_DIR}
cd ${RUN_DIR}
cp ${CONFIG_DIR}/*.cfg .
cp ${CONFIG_DIR}/*.org .

cp ${CONFIG_DIR}/${EXEC} .

<<RUN_COMMANDS>>

<<ANALYSIS_COMMANDS>>

rm ${EXEC}

"""

base_run_logic = \
"""
if [[ ${SLURM_ARRAY_TASK_ID} -eq <<SUB_ID>> ]] ; then
    RUN_DIR=<<RUN_DIR>>
    RUN_PARAMS=<<RUN_PARAMS>>
fi
"""

'''
This is functionally equivalent to the mkdir -p [fname] bash command
'''
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def main():
    parser = argparse.ArgumentParser(description="Run submission script.")
    parser.add_argument("--data_dir", type=str, help="Where is the base output directory for each run?")
    parser.add_argument("--config_dir", type=str, help="Where is the configuration directory for experiment?")
    parser.add_argument("--replicates", type=int, default=default_num_replicates, help="How many replicates should we run of each condition?")
    parser.add_argument("--run_experiment", action="store_true", help="Should we run the experiment?")
    parser.add_argument("--run_analysis", action="store_true", help="Should we run analyze mode?")
    parser.add_argument("--analysis_file", type=str, default="analysis.cfg", help="Path to the analysis script to use for avida analyze mode.")

    args = parser.parse_args()
    data_dir = args.data_dir
    config_dir = args.config_dir
    num_replicates = args.replicates

    run_exp = args.run_experiment
    run_analysis = args.run_analysis
    analysis_file_path = args.analysis_file

    submissions = []

    for condition_id in range(0, len(run_configs)):
        condition_params = run_configs[condition_id]
        print(f"Processing condition: {condition_params}")
        # Run N replicates of this condition.
        for i in range(1, num_replicates+1):
            # Compute the seed for this replicate.
            # RANDOM_SEED
            seed = seed_offset + (condition_id * num_replicates) + i
            run_cmd_cfg = condition_params + f" -set RANDOM_SEED {seed}"
            run_name = f"RUN_{seed}"
            run_dir = os.path.join(data_dir, run_name)
            # run_params = [param.strip() for param in run_cmd_cfg.split("-set") if param]
            submissions.append({"run_dir": run_dir, "run_params": run_cmd_cfg})

    print(f"Runs to submit: {len(submissions)}")
    print(f"Generating submission script...")
    if len(submissions) == 0: return

    sub_logic = ""
    array_id = 1
    for sub in submissions:
        run_params = sub["run_params"]
        run_logic = base_run_logic
        run_logic = run_logic.replace("<<SUB_ID>>", str(array_id))
        run_logic = run_logic.replace("<<RUN_DIR>>", sub["run_dir"])
        run_logic = run_logic.replace("<<RUN_PARAMS>>", f"'{run_params}'")
        sub_logic += run_logic
        array_id += 1

    script = base_sub_script
    script = script.replace("<<TIME_REQUEST>>", job_time_request)
    script = script.replace("<<ARRAY_ID_RANGE>>", f"1-{len(submissions)}")
    script = script.replace("<<MEMORY_REQUEST>>", job_memory_request)
    script = script.replace("<<JOB_NAME>>", job_name)
    script = script.replace("<<CONFIG_DIR>>", config_dir)
    script = script.replace("<<SUBMISSION_LOGIC>>", sub_logic)
    script = script.replace("<<EXEC>>", executable)

    # Add run commands if we're running the experiment.
    run_commands = ""
    if run_exp:
        print("Configuring slurm script to run experiment.")
        run_commands += 'echo "./${EXEC} ${RUN_PARAMS}" > cmd.log\n'
        run_commands += './${EXEC} ${RUN_PARAMS} > run.log'
    script = script.replace("<<RUN_COMMANDS>>", run_commands)

    analysis_commands = ""
    if run_analysis:
        print("Configuring slurm script to run analysis.")
        analysis_commands += "./${EXEC} ${RUN_PARAMS} -set ANALYZE_FILE " + analysis_file_path + " -a\n"
    script = script.replace("<<ANALYSIS_COMMANDS>>", analysis_commands)

    with open("sub.sb", "w") as fp:
        fp.write(script)

if __name__ == "__main__":
    main()
