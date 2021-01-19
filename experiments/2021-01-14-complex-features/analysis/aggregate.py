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

max_pop_size = 3600

extra_traits = {"nor","xor","equ","logic_3aa","logic_3ab","logic_3ac","logic_3ad","logic_3ae","logic_3af","logic_3ag","logic_3ah","logic_3ai","logic_3aj","logic_3ak","logic_3al","logic_3am","logic_3an","logic_3ao","logic_3ap","logic_3aq","logic_3ar","logic_3as","logic_3at","logic_3au","logic_3av","logic_3aw","logic_3ax","logic_3ay","logic_3az","logic_3ba","logic_3bb","logic_3bc","logic_3bd","logic_3be","logic_3bf","logic_3bg","logic_3bh","logic_3bi","logic_3bj","logic_3bk","logic_3bl","logic_3bm","logic_3bn","logic_3bo","logic_3bp","logic_3bq","logic_3br","logic_3bs","logic_3bt","logic_3bu","logic_3bv","logic_3bw","logic_3bx","logic_3by","logic_3bz","logic_3ca","logic_3cb","logic_3cc","logic_3cd","logic_3ce","logic_3cf","logic_3cg","logic_3ch","logic_3ci","logic_3cj","logic_3ck","logic_3cl","logic_3cm","logic_3cn","logic_3co","logic_3cp"}
extra_trait_thresholds = {prop: (max_pop_size * prop) for prop in [0.01, 0.05, 0.1] }
extra_trait_thresholds["0"] = 1

time_data_time_series_fields = ["average_generation"]

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

def read_csv(file_path):
    content = None
    with open(file_path, "r") as fp:
        content = fp.read().strip().split("\n")
    header = content[0].split(",")
    content = content[1:]
    lines = [{header[i]: l[i] for i in range(len(header))} for l in csv.reader(content, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)]
    return lines

def simple_match_coeff(a, b):
    if len(a) != len(b):
        print(f"Length mismatch! {a} {b}")
        exit(-1)
    return sum(ai==bi for ai,bi in zip(a,b))

def main():
    parser = argparse.ArgumentParser(description="Run submission script.")
    parser.add_argument("--data_dir", type=str, help="Where is the base output directory for each run?")
    parser.add_argument("--dump", type=str, help="Where to dump this?", default=".")
    parser.add_argument("--update", type=int, help="Update to pull data for?")
    parser.add_argument("--time_series_range", type=int, help="The range (in updates) to collect time series data?", nargs=2)

    args = parser.parse_args()
    data_dir = args.data_dir
    dump_dir = args.dump
    update = args.update
    time_series_range = args.time_series_range

    if not os.path.exists(data_dir):
        print("Unable to find data directory.")
        exit(-1)

    mkdir_p(dump_dir)

    # Aggregate run directories.
    run_dirs = [run_dir for run_dir in os.listdir(data_dir) if run_identifier in run_dir]
    print(f"Found {len(run_dirs)} run directories.")

    time_series_content = []
    time_series_header = None
    time_series_fpath = os.path.join(dump_dir, f"time_series_u{time_series_range[0]}-u{time_series_range[1]}.csv")
    with open(time_series_fpath, "w") as fp:
        fp.write("")
    # Only keep lines that fall within specified time series range.
    def keep_line(u): return u <= time_series_range[1] and u >= time_series_range[0]

    # For each run directory:
    # - get id, get command line configuration settings
    summary_header = None
    summary_content_lines = []
    for run_dir in run_dirs:
        run_path = os.path.join(data_dir, run_dir)
        # Skip over (but make note of) incomplete runs.
        if not os.path.exists(os.path.join(run_path, 'data', 'analysis')):
            print('Skipping: ', run_path)
            continue

        summary_info = {} # Hold summary information about run. (one entry per run)
        time_series_info = {}
        print(f"Processing: {run_path}")

        ############################################################
        # Extract commandline configuration settings (from cmd.log file)
        cmd_log_path = os.path.join(run_path, "cmd.log")
        cmd_params = extract_params_cmd_log(cmd_log_path)
        # Infer environmental change and change rate from events file
        chg_env = "chg" in cmd_params["EVENT_FILE"]
        env_cond = cmd_params["EVENT_FILE"].replace("events_", "").split("_phase")[0].lower()
        phase = "1" if "phase-one" in cmd_params["EVENT_FILE"] else "2"

        extra_task_val = "0.0"
        if "val" in cmd_params["ENVIRONMENT_FILE"]:
            extra_task_val = "0." + cmd_params["ENVIRONMENT_FILE"].replace(".cfg", "").split("_")[-1].replace("val-", "")

        summary_info["chg_env"] = chg_env
        summary_info["environment"] = env_cond
        summary_info["update"] = update
        summary_info["phase"] = phase
        summary_info["extra_task_value"] = extra_task_val

        for field in cmd_params:
            summary_info[field] = cmd_params[field]
        ############################################################

        ############################################################
        # Extract lineage file data
        lineage_path = os.path.join(run_path, "data", "lineage.csv")
        lineage_data = read_csv(lineage_path)
        # Extract summary info (for specified update)
        lineage_summary_data = [line for line in lineage_data if int(line["update"]) == update][0]
        for field in lineage_summary_data:
            if field == "update": continue
            summary_info["lineage_"+field] = lineage_summary_data[field]

        lineage_data = None
        lineage_summary_data = None
        ############################################################

        ############################################################
        # Extract phylodiversity time series data
        phylodiversity_path = os.path.join(run_path, "data", "phylodiversity.csv")
        phylodiversity_data = read_csv(phylodiversity_path)
        # Extract summary info
        phylo_summary_data = [line for line in phylodiversity_data if int(line["update"]) == update][0]
        for field in phylo_summary_data:
            if field == "update": continue
            summary_info["phylo_"+field] = phylo_summary_data[field]

        # Extract time series info
        phylodiversity_data = None
        phylo_summary_data = None
        ############################################################

        ############################################################
        # Extract information from dominant.csv
        dominant_path = os.path.join(run_path, "data", "dominant.csv")
        dominant_data = read_csv(dominant_path)
        dominant_summary_data = [line for line in dominant_data if int(line["update"]) == update][0]

        summary_info["dominant_lineage_length_taxa"] = dominant_summary_data["dominant_lineage_length"]
        summary_info["dominant_lineage_deleterious_steps"] = dominant_summary_data["dominant_deleterious_steps"]
        summary_info["dominant_lineage_phenotypic_volatility"] = dominant_summary_data["dominant_phenotypic_volatility"]
        summary_info["dominant_lineage_unique_phenotypes"] = dominant_summary_data["dominant_unique_phenotypes"]
        ############################################################

        ############################################################
        # Extract time.dat data
        time_data = read_avida_dat_file(os.path.join(run_path, "data", "time.dat"))
        # Summery information
        # - average generation
        summary_info["time_average_generation"] = [line["average_generation"] for line in time_data if int(line["update"]) == update][0]

        # Time series information
        time_data_ts = {line["update"]: {field: line[field] for field in time_data_time_series_fields} for line in time_data if keep_line(int(line["update"]))}

        # Grab the set of updates we have for our time series to check against other time series data for consistency
        time_series_updates = set(time_data_ts.keys())
        # initialize info dictionary for each  time series update
        for u in time_series_updates: time_series_info[u] = {}

        # Store time data time series info
        for u in time_series_updates:
            for field in time_data_ts[u]: time_series_info[u]["time_" + field] = time_data_ts[u][field]

        time_data = None # release time_data
        time_data_ts = None
        ############################################################

        ############################################################
        # Extract tasks.dat data
        task_data = read_avida_dat_file(os.path.join(run_path, "data", "tasks.dat"))
        # Extract summary info
        final_tasks_data = task_data[-1]
        if (final_tasks_data["update"] != str(update)):
            print(f"Final tasks update {final_tasks_data['update']} does not match requested analysis update {update}")
            exit(-1)

        final_discovered_tasks = {proportion:set([]) for proportion in extra_trait_thresholds}
        for line in task_data:
            for trait in extra_traits:
                if not trait in line: continue
                for proportion in extra_trait_thresholds:
                    threshold = extra_trait_thresholds[proportion]
                    if int(line[trait]) >= threshold:
                        final_discovered_tasks[proportion].add(trait)

        for proportion in extra_trait_thresholds:
            threshold = extra_trait_thresholds[proportion]
            summary_info[f"final_pop_extra_tasks_{proportion}"] = sum([int(int(final_tasks_data[trait]) > threshold) for trait in extra_traits if trait in final_tasks_data])
            summary_info[f"discovered_extra_tasks_{proportion}"] = len(final_discovered_tasks[proportion])

        # Extract time series information
        task_data_ts = {line["update"]: {field: line[field] for field in extra_traits} for line in task_data if keep_line(int(line["update"]))}
        for u in time_series_updates:
            task_counts = {proportion: set([]) for proportion in extra_trait_thresholds}
            for task in task_data_ts[u]:
                for proportion in extra_trait_thresholds:
                    threshold = extra_trait_thresholds[proportion]
                    if ( int(task_data_ts[u][task]) >= threshold):
                        task_counts[proportion].add(task)
            for proportion in extra_trait_thresholds:
                time_series_info[u][f"task_count_{proportion}"] = len(task_counts[proportion])

        task_data = None
        task_data_ts = None
        ############################################################


        ############################################################
        # Extract environment-specific final dominant information.
        dom_env_all = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_all", "final_dominant.dat"))
        dom_env_odd = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_odd", "final_dominant.dat"))
        dom_env_even = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_even", "final_dominant.dat"))
        # (each of these files should only have one genotype in them)

        if len(dom_env_all) != 1 and len(dom_env_even) != 1 and len(dom_env_odd) != 1:
            print("Unexpected number of genotypes in final_dominant data files.")
            exit(-1)

        dom_env_all = dom_env_all[0]
        dom_env_odd = dom_env_odd[0]
        dom_env_even = dom_env_even[0]

        # Collect dominant genotype data.
        summary_info["dominant_genome_length"] = dom_env_all["genome_length"]

        phenotype_even = "".join([dom_env_even[trait] for trait in primary_traits])
        phenotype_odd = "".join([dom_env_odd[trait] for trait in primary_traits])
        phenotype_all = "".join([dom_env_all[trait] for trait in primary_traits])
        phenotype_task_order = ";".join(primary_traits)

        plastic_odd_even = phenotype_even != phenotype_odd

        match_score_even = simple_match_coeff(phenotype_even, even_profile)
        match_score_odd = simple_match_coeff(phenotype_odd, odd_profile)
        match_score_all = simple_match_coeff(phenotype_all, all_profile)
        match_score_odd_even = match_score_even + match_score_odd

        optimal_plastic = match_score_even == len(even_profile) and match_score_odd == len(odd_profile)

        summary_info["dominant_phenotype_even"] = phenotype_even
        summary_info["dominant_phenotype_odd"] = phenotype_odd
        summary_info["dominant_phenotype_all"] = phenotype_all
        summary_info["dominant_phenotype_task_order"] = phenotype_task_order
        summary_info["dominant_plastic_odd_even"] = plastic_odd_even
        summary_info["dominant_match_score_even"] = match_score_even
        summary_info["dominant_match_score_odd"] = match_score_odd
        summary_info["dominant_match_score_all"] = match_score_all
        summary_info["dominant_match_score_odd_even"] = match_score_odd_even
        summary_info["dominant_optimal_plastic"] = optimal_plastic
        ############################################################

        ############################################################
        # Extract mutation accumulation data from dominant lineage
        # - mutation information will be the same for all lineage data files.
        lineage_env_all = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_all", "lineage_tasks.dat"))
        lineage_env_odd = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_odd", "lineage_tasks.dat"))
        lineage_env_even = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_even", "lineage_tasks.dat"))

        summary_info["dominant_lineage_length_genotypes"] = len(lineage_env_all)
        sub_mut_cnt = 0
        ins_mut_cnt = 0
        dels_mut_cnt = 0
        lineage_tasks_ot = [set([]) for _ in range(len(lineage_env_all))]
        extra_traits_discovered = set([])
        for i in range(len(lineage_env_all)):
            # collect mutation information for this ancestor
            muts_from_parent = lineage_env_all[i]["mutations_from_parent"].split(",")
            for mut in muts_from_parent:
                if (len(mut) == 0): continue
                if (mut[0] == "M"): sub_mut_cnt += 1
                elif (mut[0] == "I"): ins_mut_cnt += 1
                elif (mut[0] == "D"): dels_mut_cnt += 1
                else: print("Unknown mutation type (" + str(mut) + ")!")
            # collect task information for this ancestor
            for trait in extra_traits:
                even_expressed = int(lineage_env_even[i][trait]) > 0
                odd_expressed = int(lineage_env_odd[i][trait]) > 0
                if even_expressed or odd_expressed:
                    lineage_tasks_ot[i].add(trait)
                    extra_traits_discovered.add(trait)

        # save summary mutation info
        total_muts = sub_mut_cnt + ins_mut_cnt + dels_mut_cnt
        summary_info["dominant_lineage_substitution_mut_cnt"] = sub_mut_cnt
        summary_info["dominant_lineage_insertion_mut_cnt"] = ins_mut_cnt
        summary_info["dominant_lineage_deletion_mut_cnt"] = dels_mut_cnt
        summary_info["dominant_lineage_total_mut_cnt"] = total_muts
        # analyze lineage task information
        extra_traits_gained = 0   # total number of times that any trait is gained
        extra_traits_lost = 0     # total number of times that any trait is lost
        for i in range(len(lineage_tasks_ot)):
            current_traits = lineage_tasks_ot[i]
            if not i:
                traits_gained += len(current_traits)
            else:
                previous_traits = lineage_tasks_ot[i-1]
                # gained traits are traits in current_traits but not in previous traits
                gained_traits = current_traits - previous_traits
                # lost traits are traits in previous traits but not in current traits
                lost_traits = previous_traits - current_traits
                extra_traits_gained += len(gained_traits)
                extra_traits_lost += len(lost_traits)
        summary_info["dominant_lineage_extra_traits_gained"] = extra_traits_gained
        summary_info["dominant_lineage_extra_traits_lost"] = extra_traits_lost
        summary_info["dominant_lineage_extra_traits_discovered"] = extra_traits_discovered

        lineage_env_all = None
        lineage_env_odd = None
        lineage_env_even = None
        ############################################################

        ############################################################
        # Output time series data for this run
        # Add extra fields
        for u in time_series_info:
            time_series_info[u]["update"] = u # Make sure that update is a field on every line
            time_series_info[u]["RANDOM_SEED"] = summary_info["RANDOM_SEED"]
            time_series_info[u]["DISABLE_REACTION_SENSORS"] = summary_info["DISABLE_REACTION_SENSORS"]
            time_series_info[u]["chg_env"] = summary_info["chg_env"]
            time_series_info[u]["environment"] = summary_info["environment"]
            time_series_info[u]["extra_task_value"] = summary_info["extra_task_value"]

        time_series_fields = list(time_series_info[str(time_series_range[0])].keys())
        time_series_fields.sort()
        write_header = False
        if time_series_header == None:
            write_header = True
            time_series_header = ",".join(time_series_fields)
        elif time_series_header != ",".join(time_series_fields):
            print("Time series header mismatch!")
            exit(-1)
        time_series_content = []
        update_order = list(map(int, time_series_info.keys()))
        update_order.sort()
        for u in update_order:
            time_series_content.append(",".join([str(time_series_info[str(u)][field]) for field in time_series_fields]))
        with open(time_series_fpath, "a") as fp:
            if write_header: fp.write(time_series_header)
            fp.write("\n")
            fp.write("\n".join(time_series_content))
        time_series_content = []
        ############################################################

        ############################################################
        # Add summary_info to aggregate content
        summary_fields = list(summary_info.keys())
        summary_fields.sort()
        if summary_header == None:
            summary_header = summary_fields
        elif summary_header != summary_fields:
            print("Header mismatch!")
            exit(-1)
        summary_line = [str(summary_info[field]) for field in summary_fields]
        summary_content_lines.append(",".join(summary_line))
        ############################################################

    # write out aggregate data
    with open(os.path.join(dump_dir, "aggregate.csv"), "w") as fp:
        out_content = ",".join(summary_header) + "\n" + "\n".join(summary_content_lines)
        fp.write(out_content)

if __name__ == "__main__":
    main()
