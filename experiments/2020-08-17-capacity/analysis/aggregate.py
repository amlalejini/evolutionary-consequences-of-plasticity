'''
Aggregate data
'''

import argparse, os, sys, errno, subprocess, csv

run_identifier = "RUN_"

phenotypic_traits = ["not","nand","and","ornot","or","andnot","nor","xor","equals"]
even_traits = {"not", "and", "or", "nor", "equals"}
odd_traits = {"nand", "ornot", "andnot", "xor", "equals"}
even_profile = "101010101"
odd_profile = "010101011"
all_profile = "111111111"

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
        if line == "# Legend:":
            legend_start = line_i + 1
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
    parser.add_argument("--data_dir", type=str, help="Where is the base output directory for each run?")
    parser.add_argument("--analysis_dir", type=str, help="Where are is the output of avida analysis?")
    parser.add_argument("--dump", type=str, help="Where to dump this?", default=".")

    args = parser.parse_args()
    data_dir = args.data_dir
    analysis_dir = args.analysis_dir
    dump_dir = args.dump

    if not os.path.exists(data_dir):
        print("Unable to find data directory.")
        exit(-1)
    if not os.path.exists(analysis_dir):
        print("Unable to find analysis directory.")
        exit(-1)

    mkdir_p(dump_dir)

    # Aggregate run directories.
    run_dirs = [run_dir for run_dir in os.listdir(data_dir) if run_identifier in run_dir]
    print(f"Found {len(run_dirs)} run directories.")
    # Aggregate analysis directories.
    analysis_dirs = {run_dir for run_dir in os.listdir(analysis_dir) if run_identifier in run_dir}
    print(f"Found {len(analysis_dirs)} analysis directories.")

    # Double check that run_dir is in both data directory and in analysis directory.
    if set(run_dirs) != analysis_dirs:
        print("Run directories not same as analysis directories.")
        exit(-1)

    # For each run directory:
    # - get id, get command line configuration settings
    summary_header = None
    summary_content_lines = []
    for run_dir in run_dirs:
        # run_id = run_dir.split("_")[-1]
        run_path = os.path.join(data_dir, run_dir)
        analysis_path = os.path.join(analysis_dir, run_dir)
        ############################################################
        # Extract commandline configuration settings (from cmd.log file)
        cmd_log_path = os.path.join(run_path, "cmd.log")
        cmd_params = extract_params_cmd_log(cmd_log_path)
        # Infer environmental change and change rate from events file
        chg_env = not "const" in cmd_params["EVENT_FILE"]
        chg_rate = cmd_params["EVENT_FILE"].split(".")[0].split("-")[-1] if chg_env else "u0"
        cmd_params["change_rate"] = chg_rate
        cmd_params["changing_env"] = str(int(chg_env))
        # Write command params to file in analysis directory.
        with open(os.path.join(analysis_path, "cmd_params.csv"), "w") as fp:
            fp.write("\n".join(["parameter,value"] + [f"{param},{cmd_params[param]}" for param in cmd_params]))
        ############################################################

        # Extract environment information.
        final_dom_env_all = read_avida_dat_file(os.path.join(analysis_path, "final_dominant", "env_all", "final_dominant.dat"))[0]
        final_dom_env_odd = read_avida_dat_file(os.path.join(analysis_path, "final_dominant", "env_odd", "final_dominant.dat"))[0]
        final_dom_env_even = read_avida_dat_file(os.path.join(analysis_path, "final_dominant", "env_even", "final_dominant.dat"))[0]


        lineage_env_all = read_avida_dat_file(os.path.join(analysis_path, "final_dominant", "env_all", "lineage_tasks.dat"))
        lineage_env_odd = read_avida_dat_file(os.path.join(analysis_path, "final_dominant", "env_odd", "lineage_tasks.dat"))
        lineage_env_even = read_avida_dat_file(os.path.join(analysis_path, "final_dominant", "env_even", "lineage_tasks.dat"))
        if len({len(lineage_env_all), len(lineage_env_even), len(lineage_env_odd)}) != 1:
            print("lineage length mismatch!")
            exit(-1)

        info = {}
        info["genome_length"] = final_dom_env_all["genome_length"]

        info["phenotype_even"] = "".join([final_dom_env_even[trait] for trait in phenotypic_traits])
        info["phenotype_odd"] = "".join([final_dom_env_odd[trait] for trait in phenotypic_traits])
        info["phenotype_all"] = "".join([final_dom_env_all[trait] for trait in phenotypic_traits])
        info["phenotype_task_order"] = ";".join(phenotypic_traits)

        info["plastic_odd_even"] = info["phenotype_even"] != info["phenotype_odd"]

        info["equals_odd+even"] = final_dom_env_even["equals"] == "1" and final_dom_env_odd["equals"] == "1"
        info["equals"] = final_dom_env_even["equals"] == "1" or final_dom_env_odd["equals"] == "1" or final_dom_env_all["equals"] == "1"

        info["match_score_even"] = simple_match_coeff(info["phenotype_even"], even_profile)
        info["match_score_odd"] = simple_match_coeff(info["phenotype_odd"], odd_profile)
        info["match_score_all"] = simple_match_coeff(info["phenotype_all"], all_profile)
        info["match_score_odd_even"] = info["match_score_odd"] + info["match_score_even"]

        info["lineage_length"] = len(lineage_env_all)

        # aggregate lineage information
        aggregate_lineage = []

        info["equals_odd+even_update"] = None
        info["equals_odd+even_generation"] = None
        info["equals_all_update"] = None
        info["equals_all_generation"] = None
        info["plastic_odd_even_update"] = None
        info["plastic_odd_even_generation"] = None

        for i in range(len(lineage_env_all)):
            generation = i
            update = lineage_env_all[i]["update_born"]
            info_i = {}
            info_i["phenotype_even"] = "".join([lineage_env_even[i][trait] for trait in phenotypic_traits])
            info_i["phenotype_odd"] = "".join([lineage_env_odd[i][trait] for trait in phenotypic_traits])
            info_i["plastic_odd_even"] = info_i["phenotype_even"] != info_i["phenotype_odd"]
            info_i["equals_odd+even"] = lineage_env_even[i]["equals"] == "1" and lineage_env_odd[i]["equals"] == "1"
            info_i["equals_all"] = lineage_env_all[i]["equals"] == "1"
            info_i["match_score_even"] = simple_match_coeff(info_i["phenotype_even"], even_profile)
            info_i["match_score_odd"] = simple_match_coeff(info_i["phenotype_odd"], odd_profile)
            # info_i["match_score_all"] = simple_match_coeff(info_i["phenotype_all"], all_profile)
            info_i["match_score_odd_even"] = info_i["match_score_odd"] + info_i["match_score_even"]

            aggregate_lineage.append(info_i)

            if (info["equals_odd+even_update"] == None) and (info_i["equals_odd+even"]):
                info["equals_odd+even_update"] = update

            if (info["equals_odd+even_generation"] == None) and (info_i["equals_odd+even"]):
                info["equals_odd+even_generation"] = generation

            if (info["equals_all_update"] == None) and (info_i["equals_all"]):
                info["equals_all_update"] = update

            if (info["equals_all_generation"] == None) and (info_i["equals_all"]):
                info["equals_all_generation"] = generation

            if (info["plastic_odd_even_update"] == None) and (info_i["plastic_odd_even"]):
                info["plastic_odd_even_update"] = update

            if (info["plastic_odd_even_generation"] == None) and (info_i["plastic_odd_even"]):
                info["plastic_odd_even_generation"] = generation

        # Write to summary file.
        param_fields=list(cmd_params.keys())
        param_fields.sort()
        info_fields = list(info.keys())
        info_fields.sort()
        summary_fields = ",".join(param_fields + info_fields)
        if summary_header == None:
            summary_header = summary_fields
        elif summary_header != summary_fields:
            print("Header mismatch!")
            exit(-1)

        summary_line = [str(cmd_params[param]) for param in param_fields] + [str(info[field]) for field in info_fields]
        summary_content_lines.append(",".join(summary_line))

    # write out aggregate data
    with open(os.path.join(dump_dir, "aggregate.csv"), "w") as fp:
        out_content = summary_header + "\n" + "\n".join(summary_content_lines)
        fp.write(out_content)



if __name__ == "__main__":
    main()