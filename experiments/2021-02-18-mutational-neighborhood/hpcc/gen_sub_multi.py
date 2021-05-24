'''
Generate slurm job submission scripts - one per condition
'''

import argparse, os, sys, errno, subprocess, csv
from pyvarco import CombinationCollector

seed_offset = 200000
default_num_replicates = 30
job_time_request = "2:00:00"
job_memory_request = "8G"
executable = "avida"
base_script_filename = './base_script.txt'

# Create combo object to collect all conditions we'll run
combos = CombinationCollector()
combos.register_var('EVENT_FILE_PREFIX')
combos.register_var('DISABLE_SENSORS')

combos.add_val(
    'EVENT_FILE_PREFIX',
    [
        'events_env-all_rate-u0',
        'events_env-chg_rate-u100'
    ]
)

combos.add_val('DISABLE_SENSORS', ['0','1'])

combos.add_exception(
    {'EVENT_FILE_PREFIX': 'events_env-all_rate-u0', 'DISABLE_SENSORS': '0'}
)

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
    parser.add_argument("--old_dir", type=str, help="Directory containing avida output")
    parser.add_argument("--knockout_dir", type=str, help="Directory containing knockout output")
    parser.add_argument("--new_dir", type=str, help="Where output will be saved")
    parser.add_argument("--config_dir", type=str, help="Where is the configuration directory for experiment?")
    parser.add_argument("--analysis_dir", type=str, help="Where is the analysis directory for experiment?")
    parser.add_argument("--replicates", type=int, default=default_num_replicates, help="How many replicates should we run of each condition?")
    parser.add_argument("--job_dir", type=str, help="Where to output these job files?")

    # Load in command line arguments
    args = parser.parse_args()
    old_dir = args.old_dir
    knockout_dir = args.knockout_dir
    new_dir = args.new_dir
    config_dir = args.config_dir
    analysis_dir = args.analysis_dir
    num_replicates = args.replicates
    job_dir = args.job_dir

    # Get list of all combinations to run
    combo_list = combos.get_combos()
    # Calculate how many jobs we have, and what the last id will be
    num_jobs = num_replicates * len(combo_list)
    # final_job_id = seed_offset + num_jobs
    # num_digits = len(str(final_job_id))
    print(f'Generating {num_jobs} across {len(combo_list)} files!')

    # Create job file for each condition
    cur_job_id = 0
    cond_i = 0
    for condition_dict in combo_list:
        cur_seed = seed_offset + (cur_job_id * num_replicates)
        # job_id_str = str(cur_seed).zfill(num_digits)
        filename_prefix = f'RUN_C{cond_i}'
        job_name = f"C{cond_i}"
        file_str = base_sub_script
        file_str = file_str.replace("<<TIME_REQUEST>>", job_time_request)
        file_str = file_str.replace("<<ARRAY_ID_RANGE>>", f"1-{num_replicates}")
        file_str = file_str.replace("<<MEMORY_REQUEST>>", job_memory_request)
        file_str = file_str.replace("<<JOB_NAME>>", job_name)
        file_str = file_str.replace("<<CONFIG_DIR>>", config_dir)
        file_str = file_str.replace("<<ANALYSIS_DIR>>", analysis_dir)
        file_str = file_str.replace("<<EXEC>>", executable)
        file_str = file_str.replace("<<JOB_SEED_OFFSET>>", str(cur_seed))


        # ===================================================
        # ===================== Phase 2 =====================
        # ===================================================
        file_str = file_str.replace("<<OLD_DIR>>", \
            os.path.join(old_dir, f'{filename_prefix}_'+'${SEED}'))
        file_str = file_str.replace("<<KNOCKOUT_DIR>>", \
            os.path.join(knockout_dir, f'{filename_prefix}_'+'${SEED}'))
        file_str = file_str.replace("<<NEW_DIR>>", \
            os.path.join(new_dir, f'{filename_prefix}_'+'${SEED}'))

        # Format configuration parameters for the run
        env_file_name = 'environment.cfg'

        # Format commandline arguments for the run
        run_param_info = {}
        run_param_info["EVENT_FILE"] = f'{condition_dict["EVENT_FILE_PREFIX"]}_phase-two.cfg'
        run_param_info["ENVIRONMENT_FILE"] = env_file_name
        run_param_info["COPY_MUT_PROB"] = '0.0025'
        run_param_info["DISABLE_REACTION_SENSORS"] = condition_dict["DISABLE_SENSORS"]
        run_param_info["REACTION_SENSORS_NEUTRAL"] = '0.0'
        run_param_info["PHYLOGENY_SNAPSHOT_RES"] = '200000'
        run_param_info["SYSTEMATICS_RES"] = '10000'
        run_param_info["RANDOM_SEED"] = '${SEED}'
        run_param_info["FORCE_MRCA_COMP"] = "1"
        # Genome length controls
        run_param_info["DIVIDE_INS_PROB"] = "0.0"
        run_param_info["DIVIDE_DEL_PROB"] = "0.0"
        run_param_info["OFFSPRING_SIZE_RANGE"] = "1.0"

        fields = list(run_param_info.keys())
        fields.sort()
        # prepend hitchhiking avida config file (that includes nop-x instruction)
        run_params = f"-c avida.cfg " + " ".join([f"-set {field} {run_param_info[field]}" for field in fields])
        file_str = file_str.replace("<<RUN_PARAMS>>", run_params)

        mkdir_p(job_dir)
        with open(os.path.join(job_dir, f'{filename_prefix}.sb'), 'w') as fp:
            fp.write(file_str)
        cur_job_id += 1
        cond_i += 1

if __name__ == "__main__":
    main()
