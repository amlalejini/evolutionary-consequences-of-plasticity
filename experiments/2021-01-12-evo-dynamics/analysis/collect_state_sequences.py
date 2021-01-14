'''
Aggregate lineage .dat files, extract genotype sequences and compressed phenotype sequences.

NOTE: only collects sequences from conditions with a changing environment
'''

import argparse, os, copy, errno, csv, subprocess, sys, statistics

run_identifier = "RUN_"

traits = ["not", "nand", "and", "ornot", "or", "andnot"]
even_traits = {"not", "and", "or"}
odd_traits = {"nand", "ornot", "andnot"}
even_profile = "101010"
odd_profile = "010101"
all_profile = "111111"

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
    parser = argparse.ArgumentParser(description="Data aggregation script.")
    parser.add_argument("--data_dir", type=str, help="Where is the base output directory for runs?")
    parser.add_argument("--dump", type=str, help="Where to dump this?", default=".")
    parser.add_argument("--max_update", type=int, help="Total updates experiment ran for")

    args = parser.parse_args()

    data_dir = args.data_dir
    dump_dir = args.dump
    max_update = args.max_update

    if not os.path.exists(data_dir):
        print("Unable to find data directory")
        exit(-1)

    mkdir_p(dump_dir)

    # Aggregate run directories
    run_dirs = [run_dir for run_dir in os.listdir(data_dir) if run_identifier in run_dir]
    print(f"Found {len(run_dirs)} run directories")

    content_header = None
    content_lines = []
    for run_dir in run_dirs:
        run_path = os.path.join(data_dir, run_dir)
        # Skip over (but make note of) incomplete runs.
        if not os.path.exists(os.path.join(run_path, 'data', 'analysis')):
            print('Skipping: ', run_path)
            continue

        state_sequence_info = {}
        print(f"Processing: {run_path}")

        ############################################################
        # Extract commandline configuration settings (from cmd.log file)
        cmd_log_path = os.path.join(run_path, "cmd.log")
        cmd_params = extract_params_cmd_log(cmd_log_path)
        # Infer environmental change and change rate from events file
        chg_env = "chg" in cmd_params["EVENT_FILE"]
        env_cond = cmd_params["EVENT_FILE"].replace("events_", "").split("_phase")[0].lower()
        phase = "1" if "phase-one" in cmd_params["EVENT_FILE"] else "2"

        # Only collect data from changing environment.
        if not chg_env: continue

        state_sequence_info["chg_env"] = chg_env
        state_sequence_info["environment"] = env_cond
        state_sequence_info["phase"] = phase
        state_sequence_info["max_update"] = max_update

        for field in cmd_params:
            state_sequence_info[field] = cmd_params[field]
        ############################################################

        ############################################################
        # Extract data from dominant lineage
        # - mutation information will be the same for all lineage data files.
        lineage_env_all = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_all", "lineage_tasks.dat"))
        lineage_env_even = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_even", "lineage_tasks.dat"))
        lineage_env_odd = read_avida_dat_file(os.path.join(run_path, "data", "analysis", "env_odd", "lineage_tasks.dat"))
        if (len(lineage_env_all) != len(lineage_env_even)) or (len(lineage_env_all) != len(lineage_env_odd)):
            print("Lineage length mismatch!")
            exit(-1)
        updates = [int(line["update"]) for line in lineage_env_all]
        if updates != sorted(updates):
            print("lineage isn't ordered")
            exit(-1)

        # Extract phenotype sequence
        genotype_seq_states = []
        genotype_seq_starts = []
        genotype_seq_durations = []
        genotype_seq_mutations_from_parent = []
        genotype_seq_mutations_from_ancestor = []
        genotype_seq_state_cnt = 0

        muts_from_ancestor = 0
        for i in range(0, len(lineage_env_all)):
            # Compute mutations from parent
            muts_from_parent = lineage_env_all[i]["mutations_from_parent"].split(",")
            sub_mut_from_parent_cnt = 0
            ins_mut_from_parent_cnt = 0
            dels_mut_from_parent_cnt = 0
            for mut in muts_from_parent:
                if (len(mut) == 0): continue
                if (mut[0] == "M"): sub_mut_cnt += 1
                elif (mut[0] == "I"): ins_mut_cnt += 1
                elif (mut[0] == "D"): dels_mut_cnt += 1
                else: print("Unknown mutation type (" + str(mut) + ")!")
            total_muts_from_parent = sub_mut_from_parent_cnt + ins_mut_from_parent_cnt + dels_mut_from_parent_cnt
            muts_from_ancestor += total_muts_from_parent

            # Grab phenotype information from current genotype
            info_env_even = lineage_env_even[i]
            info_env_odd = lineage_env_odd[i]
            info_env_all = lineage_env_all[i]
            # Compute phenotype information
            phenotype_even = "".join([info_env_even[trait] for trait in traits])
            phenotype_odd = "".join([info_env_odd[trait] for trait in traits])
            phenotype_all = "".join([info_env_all[trait] for trait in traits])
            plastic_even_odd = phenotype_even != phenotype_odd
            phenotype_even_odd = phenotype_even + phenotype_odd
            match_score_even = simple_match_coeff(phenotype_even, even_profile)
            match_score_odd = simple_match_coeff(phenotype_odd, odd_profile)
            match_score_all = simple_match_coeff(phenotype_all, all_profile)
            match_score_even_odd = match_score_even + match_score_odd
            optimal_plastic = match_score_even == len(even_profile) and match_score_odd == len(odd_profile)

            state = phenotype_even_odd
            if i > 0:
                if genotype_seq_states[-1] != state:
                    genotype_seq_state_cnt += 1
            start = int(lineage_env_all[i]["update_born"])
            if start < 0: start = 0 # Clamp start update at 0 for sanity
            # update previous duration
            if i: genotype_seq_durations.append(start - genotype_seq_starts[-1])
            # update current start
            genotype_seq_starts.append(start)
            # update current state
            genotype_seq_states.append(state)
            # update current mutation accumulation information
            genotype_seq_mutations_from_parent.append(total_muts_from_parent)
            genotype_seq_mutations_from_ancestor.append(muts_from_ancestor)
        genotype_seq_durations.append(int(max_update) - genotype_seq_starts[-1])

        genotype_seq_unique_state_cnt = len(set(genotype_seq_states))
        genotype_seq_length = len(genotype_seq_states)

        # Compress genotype sequence into a phenotype sequence
        phenotype_seq_states = []
        phenotype_seq_starts = []
        phenotype_seq_durations = []
        for i in range(0, len(genotype_seq_states)):
            # If we're at the first state, just set start, states, and duration from source.
            if i == 0:
                phenotype_seq_states.append(genotype_seq_states[0])
                phenotype_seq_starts.append(genotype_seq_starts[0])
                phenotype_seq_durations.append(genotype_seq_durations[0])
                continue
            # Is this state the same as the previous state? Or, are we different?
            if genotype_seq_states[i] == phenotype_seq_states[-1]:
                # Same!
                # Increment duration
                phenotype_seq_durations[-1] += genotype_seq_durations[i]
                continue
            else:
                # Different!
                phenotype_seq_states.append(genotype_seq_states[i])
                phenotype_seq_starts.append(genotype_seq_starts[i])
                phenotype_seq_durations.append(genotype_seq_durations[i])
        phenotype_seq_unique_state_cnt = len(set(phenotype_seq_states))
        phenotype_seq_length = len(phenotype_seq_states)

        state_sequence_info["phen_seq_by_geno_state"] = f'"{",".join(genotype_seq_states)}"'
        state_sequence_info["phen_seq_by_geno_start"] = f'"{",".join(map(str, genotype_seq_starts))}"'
        state_sequence_info["phen_seq_by_geno_duration"] = f'"{",".join(map(str, genotype_seq_durations))}"'

        state_sequence_info["phen_seq_by_phen_state"] = f'"{",".join(phenotype_seq_states)}"'
        state_sequence_info["phen_seq_by_phen_start"] = f'"{",".join(map(str, phenotype_seq_starts))}"'
        state_sequence_info["phen_seq_by_phen_duration"] = f'"{",".join(map(str, phenotype_seq_durations))}"'

        state_sequence_info["genotype_seq_unique_state_cnt"] = genotype_seq_unique_state_cnt
        state_sequence_info["genotype_seq_length"] = genotype_seq_length
        state_sequence_info["phenotype_seq_unique_state_cnt"] = phenotype_seq_unique_state_cnt
        state_sequence_info["phenotype_seq_length"] = phenotype_seq_length

        ############################################################

        ############################################################
        # Setup output
        content_fields = list(state_sequence_info.keys())
        content_fields.sort()
        if content_header == None:
            content_header = ",".join(content_fields)
        elif content_header != ",".join(content_fields):
            print("Header mismatch!")
            exit(-1)
        content_line = [str(state_sequence_info[field]) for field in content_fields]
        content_lines.append(",".join(content_line))
        ############################################################

    # Write out sequences to file
    with open("lineage_sequences.csv", "w") as fp:
        fp.write(content_header + "\n")
        fp.write("\n".join(content_lines))

if __name__ == "__main__":
    main()