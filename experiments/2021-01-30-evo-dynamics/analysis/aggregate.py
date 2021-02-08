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

env_order = ["even", "odd"]

max_pop_size = 3600

# because we want smaller file sizes, only keep fields that we want to look at
phylodiversity_time_series_fields = [
    "mean_evolutionary_distinctiveness",
    "min_evolutionary_distinctiveness",
    "max_evolutionary_distinctiveness",
    "variance_evolutionary_distinctiveness",
    "mean_pairwise_distance",
    "min_pairwise_distance",
    "max_pairwise_distance",
    "variance_pairwise_distance",
    "current_phylogenetic_diversity",
    "sum_pairwise_distance",
    "num_taxa_tree",
    "num_taxa_extant",
    "total_orgs",
    "ave_depth",
    "num_roots",
    "mrca_depth",
    "diversity"
]
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

def build_env_lookup(period_length, max_update):
    lookup = ["all" for i in range(0, max_update+1)]
    if period_length == 0:
        return lookup
    u = 0
    env_i = 0
    while u < len(lookup):
        for pi in range(period_length):
            if u >= len(lookup): break
            lookup[u] = env_order[env_i]
            u+=1
        env_i = (env_i + 1) % len(env_order)
    return lookup

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

        events_info = cmd_params["EVENT_FILE"].strip("events_").strip(".cfg").split("_")
        events_info = {param.split("-")[0]:param.split("-")[1] for param in events_info}
        change_rate = int(events_info["rate"].strip("u"))

        environment_lookup = build_env_lookup(period_length = change_rate, max_update = update)

        summary_info["chg_env"] = chg_env
        summary_info["environment"] = env_cond
        summary_info["update"] = update
        summary_info["phase"] = phase
        summary_info["change_rate"] = change_rate

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

        # Extract time series info
        # Only keep lines that fall within specified time series range.
        def keep_line(u): return u <= time_series_range[1] and u >= time_series_range[0]
        lineage_data = {line["update"]: line for line in lineage_data if keep_line(int(line["update"])) }
        # Grab the set of updates we have for our time series to check against other time series data for consistency
        time_series_updates = set(lineage_data.keys())
        # initialize info dictionary for each  time series update
        for u in time_series_updates: time_series_info[u] = {}

        # TODO - is there anything we want from this file?
        # done with lineage data
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
        phylo_data_ts = {line["update"]: {field: line[field] for field in phylodiversity_time_series_fields} for line in phylodiversity_data if keep_line(int(line["update"]))}
        phylo_data_ts_updates = set(phylo_data_ts.keys())
        if time_series_updates != phylo_data_ts_updates:
            print("Time series resolution mismatch (phylo)!")
            exit(-1)
        for u in time_series_updates:
            for field in phylo_data_ts[u]: time_series_info[u]["phylo_"+field] = phylo_data_ts[u][field]
        # done with phylodiversity data
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

        # Check time data ts updates against previous time series updates.
        time_data_ts_updates = set(time_data_ts.keys())
        if time_series_updates != time_data_ts_updates:
            print("Time series resolution mismatch (time)!")
            exit(-1)

        # Store time data time series info
        for u in time_series_updates:
            for field in time_data_ts[u]: time_series_info[u]["time_" + field] = time_data_ts[u][field]

        time_data = None # release time_data
        time_data_ts = None
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
        # primary_task_profiles_ot = [None for _ in range(len(lineage_env_all))]
        primary_task_profiles_ot = [{"muts_from_parent": None, "odd": None, "even": None, "const": None, "aggregate": None} for _ in range(len(lineage_env_all))]
        for i in range(len(lineage_env_all)):
            muts_from_parent = lineage_env_all[i]["mutations_from_parent"].split(",")
            for mut in muts_from_parent:
                if (len(mut) == 0): continue
                if (mut[0] == "M"): sub_mut_cnt += 1
                elif (mut[0] == "I"): ins_mut_cnt += 1
                elif (mut[0] == "D"): dels_mut_cnt += 1
                else: print("Unknown mutation type (" + str(mut) + ")!")

            ancestor_phenotype_even = "".join([lineage_env_even[i][trait] for trait in primary_traits])
            ancestor_phenotype_odd = "".join([lineage_env_odd[i][trait] for trait in primary_traits])
            ancestor_phenotype_const = "".join([lineage_env_all[i][trait] for trait in primary_traits])

            primary_task_profiles_ot[i]["even"] = ancestor_phenotype_even
            primary_task_profiles_ot[i]["odd"] = ancestor_phenotype_odd
            primary_task_profiles_ot[i]["const"] = ancestor_phenotype_const
            primary_task_profiles_ot[i]["muts_from_parent"] = len(muts_from_parent)

            if chg_env:
                primary_task_profiles_ot[i]["aggregate"] = ancestor_phenotype_even + ancestor_phenotype_odd
            else:
                primary_task_profiles_ot[i]["aggregate"] = ancestor_phenotype_const

        # save summary info about mutation accumulation
        total_muts = sub_mut_cnt + ins_mut_cnt + dels_mut_cnt
        summary_info["dominant_lineage_substitution_mut_cnt"] = sub_mut_cnt
        summary_info["dominant_lineage_insertion_mut_cnt"] = ins_mut_cnt
        summary_info["dominant_lineage_deletion_mut_cnt"] = dels_mut_cnt
        summary_info["dominant_lineage_total_mut_cnt"] = total_muts
        # analyze lineage task profiles
        task_profile_volatility = 0
        for i in range(len(primary_task_profiles_ot)):
            ##### Task profile volatility
            if i:
                current_profile = primary_task_profiles_ot[i]["aggregate"]
                previous_traits = primary_task_profiles_ot[i-1]["aggregate"]
                task_profile_volatility += int(current_profile != previous_traits)

        summary_info["dominant_lineage_trait_volatility"] = task_profile_volatility

        # analyze mutation outcomes
        num_muts_that_change_aggregate_phenotype = 0
        num_muts_that_change_unexpressed_phenotype = 0
        num_muts_that_change_expressed_phenotype = 0
        num_mut_steps = 0
        for i in range(len(primary_task_profiles_ot)):
            if not i: continue
            update_born = int(lineage_env_all[i]["update_born"])
            mutated = primary_task_profiles_ot[i]["muts_from_parent"] > 0
            if not mutated: continue
            prev_profile = primary_task_profiles_ot[i-1]
            cur_profile = primary_task_profiles_ot[i]
            num_mut_steps += 1
            # Did this mutation change the aggregate phenotype?
            change_agg = prev_profile["aggregate"] != cur_profile["aggregate"]
            if chg_env:
                cur_env = environment_lookup[update_born]
                alt_env = "odd" if cur_env == "even" else "even"
                # Did this mutation change the unexpressed phenotype?
                change_unexpressed = prev_profile[alt_env] != cur_profile[alt_env]
                # Did this mutation change the expressed phenotype?
                change_expressed = prev_profile[cur_env] != cur_profile[cur_env]
            else:
                # Did this mutation change the unexpressed phenotype?
                change_unexpressed = False
                # Did this mutation change the expressed phenotype?
                change_expressed = prev_profile["const"] != cur_profile["const"]
            num_muts_that_change_aggregate_phenotype += int(change_agg)
            num_muts_that_change_unexpressed_phenotype += int(change_unexpressed)
            num_muts_that_change_expressed_phenotype += int(change_expressed)

        summary_info["dominant_lineage_num_mut_steps_that_change_aggregate_phenotype"] = num_muts_that_change_aggregate_phenotype
        summary_info["dominant_lineage_num_mut_steps_that_change_unexpressed_phenotype"] = num_muts_that_change_unexpressed_phenotype
        summary_info["dominant_lineage_num_mut_steps_that_change_expressed_phenotype"] = num_muts_that_change_expressed_phenotype
        summary_info["dominant_lineage_num_mut_steps"] = num_mut_steps

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
