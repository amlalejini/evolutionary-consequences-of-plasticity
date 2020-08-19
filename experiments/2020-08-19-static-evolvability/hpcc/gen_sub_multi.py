'''
Generate slurm job submission scripts - one per condition
'''

import argparse, os, sys, errno, subprocess, csv
from pyvarco import CombinationCollector

seed_offset = 1000
default_num_replicates = 30
job_time_request = "48:00:00"
job_memory_request = "4G"
job_name = "avida"
executable = "avida"
base_script_filename = './base_script.txt'

# Create combo object to collect all conditions we'll run
combos = CombinationCollector()
combos.register_var('CONFIG_ID')
combos.add_val('CONFIG_ID', [str(i).zfill(2) for i in range(16)])

# Load in the base slurm file
with open(base_script_filename, 'r') as fp:
    base_sub_script = fp.read()

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
    parser.add_argument("--job_dir", type=str, help="Where to output these job files?")

    # Load in command line arguments
    args = parser.parse_args()
    data_dir = args.data_dir
    config_dir = args.config_dir
    num_replicates = args.replicates
    run_exp = args.run_experiment
    run_analysis = args.run_analysis
    analysis_file_path = args.analysis_file
    job_dir = args.job_dir
    
    # Get list of all combinations to run
    combo_list = combos.get_combos()    
    # Calculate how many jobs we have, and what the last id will be
    num_jobs = num_replicates * len(combo_list)
    final_job_id = seed_offset + num_jobs
    num_digits = len(str(final_job_id))
    print(f'Generating {num_jobs} across {len(combo_list)} files!')

    # Create job file for each condition
    cur_job_id = 0
    for condition_dict in combo_list:
        cur_seed = seed_offset + (cur_job_id * num_replicates)
        job_id_str = str(cur_seed).zfill(num_digits) 
        filename_prefix = f'{cur_seed}_avida__{combos.get_str(condition_dict)}'
        file_str = base_sub_script
        file_str = file_str.replace("<<TIME_REQUEST>>", job_time_request)
        file_str = file_str.replace("<<ARRAY_ID_RANGE>>", f"1-{num_replicates}")
        file_str = file_str.replace("<<MEMORY_REQUEST>>", job_memory_request)
        file_str = file_str.replace("<<JOB_NAME>>", job_name)
        file_str = file_str.replace("<<CONFIG_DIR>>", config_dir)
        file_str = file_str.replace("<<EXEC>>", executable)
        file_str = file_str.replace("<<RUN_DIR>>", os.path.join(data_dir, f'{filename_prefix}'))
        file_str = file_str.replace("<<JOB_SEED_OFFSET>>", str(cur_seed))
        # Format configuration parameters for the run
        run_params =  f'-set EVENT_FILE events-const-{condition_dict["CONFIG_ID"]}.cfg'
        run_params +=  ' -set COPY_MUT_PROB 0.0025'
        run_params +=  ' -set DISABLE_REACTION_SENSORS 1' 
        run_params +=  ' -set REACTION_SENSORS_NEUTRAL 0.0'
        run_params +=  ' -set RANDOM_SEED ${SEED}'
        # Add run commands if we're running the experiment.
        run_commands = ''
        if run_exp:
            run_commands += f'RUN_PARAMS={run_params}\n'
            run_commands += 'echo "./${EXEC} ${RUN_PARAMS}" > cmd.log\n'
            run_commands += './${EXEC} ${RUN_PARAMS} > run.log\n'
        file_str = file_str.replace("<<RUN_COMMANDS>>", run_commands)
        # Add analysis commands if we're analyzing the data
        analysis_commands = ""
        if run_analysis:
            analysis_commands += './${EXEC} ${RUN_PARAMS}'
            analysis_commands += ' -set ANALYZE_FILE ' + analysis_file_path 
            analysis_commands += ' -a\n'
        file_str = file_str.replace("<<ANALYSIS_COMMANDS>>", analysis_commands)

        with open(os.path.join(job_dir, f'{filename_prefix}.sb'), 'w') as fp:
            fp.write(file_str)
        cur_job_id += 1

if __name__ == "__main__":
    main()
