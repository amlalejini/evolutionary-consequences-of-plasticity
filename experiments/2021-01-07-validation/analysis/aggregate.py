'''
Aggregate data
'''

import argparse, os, sys, errno, subprocess, csv

run_identifier = "RUN_"

primary_traits = ["not","nand","and","ornot","or","andnot"]
even_traits = {"not", "and", "or"}
odd_traits = {"nand", "ornot", "andnot"}
even_profile = "101010"
odd_profile = "010101"
all_profile = "111111"

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
        # patch 3-input logic tasks because avida file format is nonsense
        if "Logic 3" in line:
            line = line.split("(")[0]

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
    parser.add_argument("--data_dir", type=str, help="Where is the base output directory for each run?")
    parser.add_argument("--dump", type=str, help="Where to dump this?", default=".")

    args = parser.parse_args()
    data_dir = args.data_dir
    dump_dir = args.dump

    if not os.path.exists(data_dir):
        print("Unable to find data directory.")
        exit(-1)

    mkdir_p(dump_dir)

    # Aggregate run directories.
    run_dirs = [run_dir for run_dir in os.listdir(data_dir) if run_identifier in run_dir]
    print(f"Found {len(run_dirs)} run directories.")

    # For each run directory:
    # - get id, get command line configuration settings
    summary_header = None
    summary_content_lines = []
    for run_dir in run_dirs:
        print(f"processing {run_dir}")
        run_path = os.path.join(data_dir, run_dir)
        info = {}
        ############################################################
        # Extract commandline configuration settings (from cmd.log file)
        cmd_log_path = os.path.join(run_path, "cmd.log")
        cmd_params = extract_params_cmd_log(cmd_log_path)
                # Infer environmental change and change rate from events file
        chg_env = "chg" in cmd_params["EVENT_FILE"]
        env_cond = cmd_params["EVENT_FILE"].split("_")[0].replace("events-", "").lower()
        phase = "2" if "phase-two" in cmd_params["EVENT_FILE"] else "1"
        info["chg_env"] = chg_env
        info["environment"] = env_cond
        info["phase"] = phase
        for field in cmd_params:
            info[field] = cmd_params[field]
        ############################################################

        ############################################################
        # Extract time information
        time_data = read_avida_dat_file(os.path.join(run_path, "data", "time.dat"))
        info["average_generation"] = time_data[-1]["average_generation"]
        info["update"] = time_data[-1]["update"]
        ############################################################

        ############################################################
        # Extract dominant organism information.
        dom_env_all = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_all", "final_dominant.dat"))[0]
        dom_env_odd = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_odd", "final_dominant.dat"))[0]
        dom_env_even = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_even", "final_dominant.dat"))[0]

        info["dom_genome_length"] = dom_env_all["genome_length"]
        info["dom_phenotype_even"] = "".join([dom_env_even[trait] for trait in primary_traits])
        info["dom_phenotype_odd"] = "".join([dom_env_odd[trait] for trait in primary_traits])
        info["dom_phenotype_all"] = "".join([dom_env_all[trait] for trait in primary_traits])
        info["dom_phenotype_task_order"] = ";".join(primary_traits)
        info["dom_plastic_odd_even"] = info["phenotype_even"] != info["phenotype_odd"]

        dom_match_score_even = simple_match_coeff(info["phenotype_even"], even_profile)
        dom_match_score_odd = simple_match_coeff(info["phenotype_odd"], odd_profile)
        info["dom_match_score_all"] = simple_match_coeff(info["phenotype_all"], all_profile)
        info["dom_match_score_odd_even"] = info["match_score_odd"] + info["match_score_even"]

        info["dom_optimal_plastic"] = dom_match_score_even == len(even_profile) and dom_match_score_odd == len(odd_profile)

        info["dom_match_score_even"] = dom_match_score_even
        info["dom_match_score_odd"] = dom_match_score_odd

        # todo - adaptive vs. non-adaptive plastic?
        info["dom_adaptive_plasticity"] = False
        if info["dom_plastic_odd_even"]:
            # is being plastic better than being non-plastic during even=>odd environment change?
            even_in_odd_match_score = simple_match_coeff(info["phenotype_even"], odd_profile)
            adaptive_in_odd = dom_match_score_odd > even_in_odd_match_score
            maladaptive_in_odd = dom_match_score_odd < even_in_odd_match_score
            # is being plastic better than being non-plastic during odd=>even environment change?
            odd_in_even_match_score = simple_match_coeff(info["phenotype_odd"], even_profile)
            adaptive_in_even = dom_match_score_even > odd_in_even_match_score
            maladaptive_in_even = dom_match_score_even < odd_in_even_match_score
            info["dom_adaptive_plasticity"] = (not (maladaptive_in_odd or maladaptive_in_even) ) and ( adaptive_in_even or adaptive_in_odd )

        ############################################################


        lineage_env_all = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_all", "lineage_tasks.dat"))
        lineage_env_odd = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_odd", "lineage_tasks.dat"))
        lineage_env_even = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_even", "lineage_tasks.dat"))

        if len({len(lineage_env_all), len(lineage_env_even), len(lineage_env_odd)}) != 1:
            print("lineage length mismatch!")
            exit(-1)

        info_fields = list(info.keys())
        info_fields.sort()
        summary_fields = ",".join(info_fields)

        if summary_header == None:
            summary_header = summary_fields
        elif summary_header != summary_fields:
            print("Header mismatch!")
            exit(-1)

        summary_line = [str(info[field]) for field in info_fields]
        summary_content_lines.append(",".join(summary_line))

    # write out aggregate data
    with open(os.path.join(dump_dir, "aggregate.csv"), "w") as fp:
        out_content = summary_header + "\n" + "\n".join(summary_content_lines)
        fp.write(out_content)

if __name__ == "__main__":
    main()