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
    parser.add_argument("--update", type=int, help="Update to pull data for?")

    args = parser.parse_args()
    data_dir = args.data_dir
    dump_dir = args.dump
    update = args.update

    if not os.path.exists(data_dir):
        print("Unable to find data directory.")
        exit(-1)

    mkdir_p(dump_dir)

    # Aggregate run directories.
    run_dirs = [run_dir for run_dir in os.listdir(data_dir) if run_identifier in run_dir]
    print(f"Found {len(run_dirs)} run directories.")

    extra_tasks_over_time_header = None
    extra_tasks_over_time_write_header = True
    with open(os.path.join(dump_dir, "extra_tasks_ot.csv"), "w") as fp:
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
        print(f"Processing: {run_path}")

        ############################################################
        # Extract commandline configuration settings (from cmd.log file)
        cmd_log_path = os.path.join(run_path, "cmd.log")
        cmd_params = extract_params_cmd_log(cmd_log_path)
        # Infer environmental change and change rate from events file
        chg_env = "chg" in cmd_params["EVENT_FILE"]
        env_cond = cmd_params["EVENT_FILE"].split("_")[0].replace("events-", "").lower()
        phase = "1" if "phase-one" in cmd_params["EVENT_FILE"] else "2"
        env_tasks = cmd_params["ENVIRONMENT_FILE"].split("_")[0].replace("environment-","").lower()
        extra_task_val = "0." + cmd_params["ENVIRONMENT_FILE"].replace(".cfg", "").split("_")[-1].replace("val_", "")

        summary_info["chg_env"] = chg_env
        summary_info["environment"] = env_cond
        summary_info["update"] = update
        summary_info["phase"] = phase
        summary_info["task_set"] = env_tasks
        summary_info["extra_task_value"] = extra_task_val
        for field in cmd_params:
            summary_info[field] = cmd_params[field]
        ############################################################


        ############################################################
        # Extract lineage file information
        # lineage_path = os.path.join(run_dir, "data", "lineage.csv")
        # lineage_content = None
        # with open(lineage_path, "r") as fp:
        #     lineage_content = fp.read().strip().split("\n")
        # lineage_header = lineage_content[0].split(",")
        # lineage_content = lineage_content[1:]
        # lineage_data = [ {lineage_header[i]:l[i] for i in range(len(l))} for l in csv.reader(lineage_content, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True) ]
        # lineage_data = [line for line in filter(lambda x: int(x["update"]) == update, lineage_data) ]
        # if len(lineage_data) != 1:
        #     print("Failed to find requested update in lineage data file.")
        #     exit(-1)
        # lineage_data = lineage_data[0]
        # lineage_content = None

        # for field in lineage_data:
        #     if field == "update": continue
        #     summary_info[f"lineages_{field}"] = lineage_data[field]
        ############################################################

        ############################################################
        # Extract time information
        time_data = read_avida_dat_file(os.path.join(run_path, "data", "time.dat"))
        task_data = read_avida_dat_file(os.path.join(run_path, "data", "tasks.dat"))
        # average generation
        summary_info["average_generation"] = [line["average_generation"] for line in time_data if int(line["update"]) == update][0]

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
            summary_info[f"pop_extra_tasks_{proportion}"] = sum([int(int(final_tasks_data[trait]) > threshold) for trait in extra_traits if trait in final_tasks_data])
            summary_info[f"extra_tasks_discovered_{proportion}"] = len(final_discovered_tasks[proportion])

        ############################################################

        ############################################################
        # Extract tasks over time
        # header = ["extra_tasks_discovered_{:}", "seed", ""]
        # summary_info["environment"]
        # cmd_params["DISABLE_REACTION_SENSORS"]
        # summary_info["extra_task_value"]
        # summary_info["seed"]
        # update
        # num_discovered
        # num_performed
        # task_ot_info = []

        # num_discovered = {prop: set([]) for prop in extra_trait_thresholds}
        # for line in task_data:
        #     info = {}
        #     info["environment"] = summary_info["environment"]
        #     info["seed"] = cmd_params["RANDOM_SEED"]
        #     info["DISABLE_REACTION_SENSORS"] = cmd_params["DISABLE_REACTION_SENSORS"]
        #     info["extra_task_value"] = summary_info["extra_task_value"]
        #     info["update"] = line["update"]

        #     # update num discovered
        #     num_performed = {prop: 0 for prop in extra_trait_thresholds}
        #     for trait in extra_traits:
        #         if not trait in line: continue
        #         for prop in extra_trait_thresholds:
        #             threshold = extra_trait_thresholds[prop]
        #             if int(line[trait]) >= threshold:
        #                 num_performed[prop] += 1
        #                 num_discovered[prop].add(trait)
        #     for prop in extra_trait_thresholds:
        #         info[f"extra_tasks_discovered_{prop}"] = len(num_discovered[prop])
        #         info[f"extra_tasks_performed_{prop}"] = num_discovered[prop]

        #     task_ot_info.append(info)

        # task_ot_header_fields = [field for field in task_ot_info[0]]
        # task_ot_header_fields.sort()
        # task_ot_header = ",".join(task_ot_header_fields)


        # task_ot_content = "\n".join([ ",".join([str(info[field]) for field in task_ot_header_fields]) for info in task_ot_info ])

        # with open(os.path.join(dump_dir, "extra_tasks_ot.csv"), "a") as fp:
        #     if extra_tasks_over_time_write_header:
        #         extra_tasks_over_time_write_header = False
        #         extra_tasks_over_time_header = task_ot_header
        #         fp.write(task_ot_header + "\n")
        #     elif extra_tasks_over_time_header != task_ot_header:
        #         print("task ot header mismatch!")
        #         exit(-1)
        #     fp.write(task_ot_content)
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
        summary_info["genome_length"] = dom_env_all["genome_length"]

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

        # How many 'extra' traits does the final dominant organism perform (in any environment)?
        # extra_task_cnt = sum([int(any([int(dom_env_all[trait]) > 0, int(dom_env_even[trait]) > 0, int(dom_env_odd[trait]) > 0])) for trait in extra_traits if trait in dom_env_all])

        summary_info["dom_phenotype_even"] = phenotype_even
        summary_info["dom_phenotype_odd"] = phenotype_odd
        summary_info["dom_phenotype_all"] = phenotype_all
        summary_info["dom_phenotype_task_order"] = phenotype_task_order
        summary_info["dom_plastic_odd_even"] = plastic_odd_even
        summary_info["dom_match_score_even"] = match_score_even
        summary_info["dom_match_score_odd"] = match_score_odd
        summary_info["dom_match_score_all"] = match_score_all
        summary_info["dom_match_score_odd_even"] = match_score_odd_even
        summary_info["dom_optimal_plastic"] = optimal_plastic
        # summary_info["dom_extra_tasks"] = extra_task_cnt
        ############################################################

        ############################################################
        # Extract mutation accumulation data from lineage
        # - mutation information will be the same for all lineage data files.
        # lineage_env_all = read_avida_dat_file(os.path.join(run_dir, "data", "analysis", "env_all", "lineage_tasks.dat"))
        # summary_info["lineage_length_genotypes"] = len(lineage_env_all)
        # sub_mut_cnt = 0
        # ins_mut_cnt = 0
        # dels_mut_cnt = 0
        # for i in range(len(lineage_env_all)):
        #     muts_from_parent = lineage_env_all[i]["mutations_from_parent"].split(",")
        #     for mut in muts_from_parent:
        #         if (len(mut) == 0): continue
        #         if (mut[0] == "M"): sub_mut_cnt += 1
        #         elif (mut[0] == "I"): ins_mut_cnt += 1
        #         elif (mut[0] == "D"): dels_mut_cnt += 1
        #         else: print("Unknown mutation type (" + str(mut) + ")!")
        # total_muts = sub_mut_cnt + ins_mut_cnt + dels_mut_cnt
        # summary_info["substitution_mut_cnt"] = sub_mut_cnt
        # summary_info["insertion_mut_cnt"] = ins_mut_cnt
        # summary_info["deletion_mut_cnt"] = dels_mut_cnt
        # summary_info["total_mut_cnt"] = total_muts
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
