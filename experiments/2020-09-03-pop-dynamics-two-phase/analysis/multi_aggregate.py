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
    parser.add_argument("--update", type=int, help="Update to pull data for?")

    args = parser.parse_args()
    data_dir_filename = args.data_dir_file
    output_dir = args.output_dir
    update = args.update

    mkdir_p(output_dir)

    # Aggregate run directories.
    run_dirs = []  
    with open(data_dir_filename, 'r') as fp:
        for line in fp:
            line = line.strip()
            if line != '':
                run_dirs.append(line)

    # Start phylodiveristy over time file
    phylo_ot_header = None
    phylo_ot_write_header = True
    with open(os.path.join(output_dir, "phylodiversity_ot.csv"), "w") as fp:
        fp.write("")

    # For each run directory:
    # - get id, get command line configuration settings
    summary_header = None
    summary_content_lines = []
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
        summary_info["chg_env"] = chg_env
        summary_info["environment"] = env_cond
        summary_info["update"] = update
        for field in cmd_params:
            summary_info[field] = cmd_params[field]
        ############################################################


        ############################################################
        # Extract phylodiversity file information
        phylo_path = os.path.join(run_dir, "data", "phylodiversity.csv")
        phylo_content = None
        with open(phylo_path, "r") as fp:
            phylo_content = fp.read().strip().split("\n")
        phylo_header = phylo_content[0].split(",")
        phylo_content = phylo_content[1:]
        phylodiversity = [ {phylo_header[i]:l[i] for i in range(len(l))} for l in csv.reader(phylo_content, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True) ]
        
        
        ###################
        # Write out phylodiversity over time
        phylo_ot_lines = []
        for timestep in phylodiversity:
            # add: chg_env, environment, cmd_params
            phylo_info = {}
            phylo_info["chg_env"] = chg_env
            phylo_info["environment"] = env_cond
            for field in cmd_params:
                phylo_info[field] = cmd_params[field]
            for field in timestep:
                phylo_info[field] = timestep[field]
            fields = list(phylo_info.keys())
            fields.sort()
            if phylo_ot_header == None:
                phylo_ot_header = fields
            elif phylo_ot_header != fields:
                print("Header mismatch!")
            phylo_ot_lines.append(",".join([str(phylo_info[field]) for field in fields]))
        # write out lines
        with open(os.path.join(output_dir, "phylodiversity_ot.csv"), "a") as fp:
            if phylo_ot_write_header:
                phylo_ot_write_header = False
                fp.write(",".join(phylo_ot_header) + "\n")
            fp.write("\n".join(phylo_ot_lines))
        phylo_ot_lines = None
        ###################

        # Keep only final phylodiversity data.
        phylodiversity = [line for line in filter(lambda x: int(x["update"]) == update, phylodiversity) ]
        if len(phylodiversity) != 1:
            print("Failed to find requested update in phylodiversity data file.")
            exit(-1)
        phylodiversity = phylodiversity[0]
        phylo_content = None

        for field in phylodiversity:
            if field == "update": continue
            summary_info[f"phylo_{field}"] = phylodiversity[field]

        ########

        ############################################################
        # Extract lineage file information
        lineage_path = os.path.join(run_dir, "data", "lineage.csv")
        lineage_content = None
        with open(lineage_path, "r") as fp:
            lineage_content = fp.read().strip().split("\n")
        lineage_header = lineage_content[0].split(",")
        lineage_content = lineage_content[1:]
        lineage_data = [ {lineage_header[i]:l[i] for i in range(len(l))} for l in csv.reader(lineage_content, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True) ]
        lineage_data = [line for line in filter(lambda x: int(x["update"]) == update, lineage_data) ]
        if len(lineage_data) != 1:
            print("Failed to find requested update in lineage data file.")
            exit(-1)
        lineage_data = lineage_data[0]
        lineage_content = None

        for field in lineage_data:
            if field == "update": continue
            summary_info[f"lineages_{field}"] = lineage_data[field]
        ############################################################

        ############################################################
        # Extract time information
        time_data = read_avida_dat_file(os.path.join(run_dir, "data", "time.dat"))
        # average generation
        summary_info["average_generation"] = [line["average_generation"] for line in time_data if int(line["update"]) == update][0]
        ############################################################

        ############################################################
        # Extract environment-specific final dominant information.
        dom_env_all = read_avida_dat_file(os.path.join(run_dir, "data", "analysis", "env_all", "final_dominant.dat"))
        dom_env_odd = read_avida_dat_file(os.path.join(run_dir, "data", "analysis", "env_odd", "final_dominant.dat"))
        dom_env_even = read_avida_dat_file(os.path.join(run_dir, "data", "analysis", "env_even", "final_dominant.dat"))
        # (each of these files should only have one genotype in them)

        if len(dom_env_all) != 1 and len(dom_env_even) != 1 and len(dom_env_odd) != 1:
            print("Unexpected number of genotypes in final_dominant data files.")
            exit(-1)

        dom_env_all = dom_env_all[0]
        dom_env_odd = dom_env_odd[0]
        dom_env_even = dom_env_even[0]

        # Collect dominant genotype data.
        summary_info["genome_length"] = dom_env_all["genome_length"]

        phenotype_even = "".join([dom_env_even[trait] for trait in phenotypic_traits])
        phenotype_odd = "".join([dom_env_odd[trait] for trait in phenotypic_traits])
        phenotype_all = "".join([dom_env_all[trait] for trait in phenotypic_traits])
        phenotype_task_order = ";".join(phenotypic_traits)

        plastic_odd_even = phenotype_even != phenotype_odd

        match_score_even = simple_match_coeff(phenotype_even, even_profile)
        match_score_odd = simple_match_coeff(phenotype_odd, odd_profile)
        match_score_all = simple_match_coeff(phenotype_all, all_profile)
        match_score_odd_even = match_score_even + match_score_odd

        optimal_plastic = match_score_even == len(even_profile) and match_score_odd == len(odd_profile)

        summary_info["phenotype_even"] = phenotype_even
        summary_info["phenotype_odd"] = phenotype_odd
        summary_info["phenotype_all"] = phenotype_all
        summary_info["phenotype_task_order"] = phenotype_task_order
        summary_info["plastic_odd_even"] = plastic_odd_even
        summary_info["match_score_even"] = match_score_even
        summary_info["match_score_odd"] = match_score_odd
        summary_info["match_score_all"] = match_score_all
        summary_info["match_score_odd_even"] = match_score_odd_even
        summary_info["optimal_plastic"] = optimal_plastic
        ############################################################

        ############################################################
        # Extract mutation accumulation data from lineage
        # - mutation information will be the same for all lineage data files.
        lineage_env_all = read_avida_dat_file(os.path.join(run_dir, "data", "analysis", "env_all", "lineage_tasks.dat"))
        summary_info["lineage_length_genotypes"] = len(lineage_env_all)
        sub_mut_cnt = 0
        ins_mut_cnt = 0
        dels_mut_cnt = 0
        for i in range(len(lineage_env_all)):
            muts_from_parent = lineage_env_all[i]["mutations_from_parent"].split(",")
            for mut in muts_from_parent:
                if (len(mut) == 0): continue
                if (mut[0] == "M"): sub_mut_cnt += 1
                elif (mut[0] == "I"): ins_mut_cnt += 1
                elif (mut[0] == "D"): dels_mut_cnt += 1
                else: print("Unknown mutation type (" + str(mut) + ")!")
        total_muts = sub_mut_cnt + ins_mut_cnt + dels_mut_cnt
        summary_info["substitution_mut_cnt"] = sub_mut_cnt
        summary_info["insertion_mut_cnt"] = ins_mut_cnt
        summary_info["deletion_mut_cnt"] = dels_mut_cnt
        summary_info["total_mut_cnt"] = total_muts
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
    with open(os.path.join(output_dir, "aggregate.csv"), "w") as fp:
        out_content = ",".join(summary_header) + "\n" + "\n".join(summary_content_lines)
        fp.write(out_content)



if __name__ == "__main__":
    main()
