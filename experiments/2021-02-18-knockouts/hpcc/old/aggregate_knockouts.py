'''
Aggregate data
'''

import argparse, os, sys, errno, subprocess, csv

phenotypic_traits = ["not","nand","and","ornot","or","andnot"]#,"nor","xor","equals"]
even_traits = {"not", "and", "or"}#, "nor", "equals"}
odd_traits = {"nand", "ornot", "andnot", "xor"}#, "equals"}
even_profile = "101010"#101"
odd_profile = "010101"#011"
all_profile = "111111"#111"

"""
This is functionally equivalent to the mkdir -p [fname] bash command
"""
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def extract_params_cmd_log(path):
    content = None
    with open(path, "r") as fp:
        content = fp.read().strip()
    content = content.replace("./avida", "")
    params = [param.strip() for param in content.split("-set") if param.strip() != ""]
    cfg = {param.split(" ")[0]:param.split(" ")[1] for param in params}
    return cfg

def read_avida_dat_file(path):
    content = None
    with open(path, "r") as fp:
        content = fp.read().strip().split("\n")
    legend_start = 0
    legend_end = 0
    # Where does the legend table start?
    for line_i in range(0, len(content)):
        line = content[line_i].strip()
        if line == "# Legend:":         # Handles analyze mode detail files.
            legend_start = line_i + 1
            break
        if "#  1:" in line:             # Handles time.dat file.
            legend_start = line_i
            break
    # For each line in legend table, extract field
    fields = []
    for line_i in range(legend_start, len(content)):
        line = content[line_i].strip()
        if line == "":
            legend_end = line_i
            break
        fields.append( line.split(":")[-1].strip().lower().replace(" ", "_") )
    data = []
    for line_i in range(legend_end, len(content)):
        line = content[line_i].strip()
        if line == "": continue
        data_line = line.split(" ")
        if len(data_line) != len(fields):
            print("data fields mismatch!")
            print(fields)
            print(data_line)
            exit(-1)
        data.append({field:value for field,value in zip(fields, data_line)})
    return data

def simple_match_coeff(a, b):
    if len(a) != len(b):
        print(f"Length mismatch! {a} {b}")
        exit(-1)
    return sum(ai==bi for ai,bi in zip(a,b))

def main():
    parser = argparse.ArgumentParser(description="Run submission script.")
    parser.add_argument("--data_dir_file", type=str, help="Filename that lists all data directories")
    parser.add_argument("--output_dir", type=str, help="Where to dump this?", default=".")

    args = parser.parse_args()
    data_dir_filename = args.data_dir_file
    output_dir = args.output_dir

    mkdir_p(output_dir)

    # Aggregate run directories.
    run_dirs = []  
    with open(data_dir_filename, 'r') as fp:
        for line in fp:
            line = line.strip()
            if line != '':
                run_dirs.append(line)


    # For each run directory:
    # - get id, get command line configuration settings
    summary_header = None
    summary_content_lines = []
    file_str = ''
    for run_dir in run_dirs:
        if not os.path.exists(os.path.join(run_dir, 'data', 'analysis')):
            print('Skipping: ', run_dir)
            continue
        summary_info = {} # Hold summary information about run. (one entry per run)
        print(f"processing {run_dir}")
        ############################################################
        # Extract commandline configuration settings (from cmd.log file)
        cmd_log_path = os.path.join(run_dir, "cmd.log")
        cmd_params = extract_params_cmd_log(cmd_log_path)
        # Infer environmental change and change rate from events file
        chg_env = "chg" in cmd_params["EVENT_FILE"]
        env_cond = cmd_params["EVENT_FILE"].split(".")[0].replace("events-", "").lower()
        seed = cmd_params["RANDOM_SEED"]
        sensors = cmd_params["DISABLE_REACTION_SENSORS"]
        summary_info["chg_env"] = chg_env
        summary_info["environment"] = env_cond
        for field in cmd_params:
            summary_info[field] = cmd_params[field]
        ############################################################


        ############################################################
        # Extract environment-specific one-step mutant information.
        if not os.path.exists(os.path.join(run_dir, "data", "analysis", "env_all", "knockouts.dat")):
            print('Skipping (all): ', run_dir)
            continue
        if not os.path.exists(os.path.join(run_dir, "data", "analysis", "env_odd", "knockouts.dat")):
            print('Skipping (odd): ', run_dir)
            continue
        if not os.path.exists(os.path.join(run_dir, "data", "analysis", "env_even", "knockouts.dat")):
            print('Skipping (even): ', run_dir)
            continue
        muts_env_all = read_avida_dat_file(os.path.join(run_dir, "data", "analysis", "env_all", "knockouts.dat"))
        muts_env_odd = read_avida_dat_file(os.path.join(run_dir, "data", "analysis", "env_odd", "knockouts.dat"))
        muts_env_even = read_avida_dat_file(os.path.join(run_dir, "data", "analysis", "env_even", "knockouts.dat"))
        # (each of these files should only have one genotype in them)

        if len(muts_env_all) <= 1 and len(muts_env_even) <= 1 and len(muts_env_odd) <= 1:
            print("Unexpected number of genotypes in final_dominant data files.")
            exit(-1)

        for org_id in range(len(muts_env_all)):
            phenotype_even = "".join([muts_env_even[org_id][trait] for trait in phenotypic_traits])
            phenotype_odd = "".join([muts_env_odd[org_id][trait] for trait in phenotypic_traits])
            phenotype_all = "".join([muts_env_all[org_id][trait] for trait in phenotypic_traits])
            phenotype_task_order = ";".join(phenotypic_traits)

            change_odd_even = phenotype_even != phenotype_odd

            match_score_even = simple_match_coeff(phenotype_even, even_profile)
            match_score_odd = simple_match_coeff(phenotype_odd, odd_profile)
            match_score_all = simple_match_coeff(phenotype_all, all_profile)

            file_str += \
                str(chg_env) + ',' + \
                env_cond + ',' + \
                sensors + ',' + \
                seed + ',' + \
                str(org_id) + ',' + \
                muts_env_all[org_id]['fitness'] + ',' + \
                muts_env_odd[org_id]['fitness'] + ',' + \
                muts_env_even[org_id]['fitness'] + ',' + \
                phenotype_all + ',' + \
                phenotype_odd + ',' + \
                phenotype_even + ',' + \
                phenotype_task_order + ',' + \
                str(change_odd_even) + ',' + \
                str(match_score_all) + ',' + \
                str(match_score_odd) + ',' + \
                str(match_score_even) + \
                '\n'
    
    # write out aggregate data
    with open(os.path.join(output_dir, "knockout_data.csv"), "w") as fp:
        out_content = 'chg_env,environment,sensors,seed,org_id,fit_all,fit_odd,fit_even,phenotype_all,phenotype_odd,phenotype_even,phenotype_task_order,change_odd_even,match_score_all,match_score_odd,match_score_even\n' + file_str
        fp.write(out_content)



if __name__ == "__main__":
    main()
