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

instructions_of_interest = {
 "nop-a",
 "nop-b",
 "nop-c",
 "if-n-equ",
 "if-less",
 "if-label",
 "mov-head",
 "jmp-head",
 "get-head",
 "set-flow",
 "shift-r",
 "shift-l",
 "inc",
 "dec",
 "push",
 "pop",
 "swap-stk",
 "swap",
 "add",
 "sub",
 "nand",
 "h-copy",
 "h-alloc",
 "h-divide",
 "io",
 "h-search",
 "sense-react-nand",
 "sense-react-not",
 "sense-react-and",
 "sense-react-orn",
 "sense-react-or",
 "sense-react-andn",
 "nop-x",
 "poison",
 "prob-die"
}

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
    # ./avida -c avida-prob-die.cfg -set KABOOM_PROB 0.01 -set POISON_PENALTY 0.01 -set EVENT_FILE events-chg-u30_phase-two.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0 -set PHYLOGENY_SNAPSHOT_RES 200000 -set RANDOM_SEED 32507

    content = None
    with open(path, "r") as fp:
        content = fp.read().strip()
    # print("Content: ", content)
    content = content.replace("./avida", "")
    if " -c " in content:
        avida_cfg = content.split(" -c ")[-1].split(" ")[0].strip()
        content = content.replace(f"-c {avida_cfg}", "")
    else:
        avida_cfg = "avida.cfg"
    params = [param.strip() for param in content.split("-set") if param.strip() != ""]
    cfg = {param.split(" ")[0]:param.split(" ")[1] for param in params}
    cfg["avida_cfg"] = avida_cfg
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
    run_dirs = [run_dir for run_dir in os.listdir(data_dir) if run_identifier in run_dir][:3]
    print(f"Found {len(run_dirs)} run directories.")

    # For each run directory:
    # - get id, get command line configuration settings
    summary_header = None
    summary_content_lines = []

    instr_over_time_header = None
    instr_over_time_write_header = True
    with open(os.path.join(dump_dir, "instructions_ot.csv"), "w") as fp:
        fp.write("")

    for run_dir in run_dirs:
        run_path = os.path.join(data_dir, run_dir)
        # Skip over (but make note of) incomplete runs.
        if not os.path.exists(os.path.join(run_path, 'data', 'analysis')):
            print('Skipping: ', run_path)
            continue
        if not all([os.path.exists(os.path.join(run_path, "data", "analysis", e, "final_dominant.dat")) for e in ["env_all", "env_even", "env_odd"]]):
            print("Skipping: ", run_path)
            print("  missing analysis")
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
        hitchhiker = ""
        hitchhiker_magnitude = ""
        if "poison" in cmd_params["avida_cfg"]:
            hitchhiker = "poison"
            hitchhiker_magnitude = cmd_params["POISON_PENALTY"]
        elif "prob-die" in cmd_params["avida_cfg"]:
            hitchhiker = "prob-die"
            hitchhiker_magnitude = cmd_params["KABOOM_PROB"]

        summary_info["chg_env"] = chg_env
        summary_info["env_cond"] = env_cond
        summary_info["update"] = update
        summary_info["phase"] = phase
        summary_info["hitchhiker"] = hitchhiker
        summary_info["hitchhiker_magnitude"] = hitchhiker_magnitude

        for field in cmd_params:
            summary_info[field] = cmd_params[field]
        ############################################################

        ############################################################
        # Extract time information
        time_data = read_avida_dat_file(os.path.join(run_path, "data", "time.dat"))
        # task_data = read_avida_dat_file(os.path.join(run_path, "data", "tasks.dat"))
        # average generation
        summary_info["average_generation"] = [line["average_generation"] for line in time_data if int(line["update"]) == update][0]

        # Extract instruction data
        instruction_data = read_avida_dat_file(os.path.join(run_path, "data", "instruction.dat"))

        focal_instruction_data = [line for line in instruction_data if line["update"] == str(update)]
        assert(len(focal_instruction_data) == 1)
        focal_instruction_data = focal_instruction_data[0]
        for instr in instructions_of_interest:
            if not instr in focal_instruction_data:
                summary_info[f"pop_inst_count_{instr}"] = "0"
            else:
                summary_info[f"pop_inst_count_{instr}"] = focal_instruction_data[instr]
        ############################################################

        ############################################################
        # Extract instructions over time
        instr_ot_lines = []
        for line in instruction_data:
            instr_info = {}
            instr_info["chg_env"] = chg_env
            instr_info["env_cond"] = env_cond
            instr_info["hitchhiker"] = hitchhiker
            instr_info["hitchhiker_magnitude"] = hitchhiker_magnitude
            for field in cmd_params:
                instr_info[field] = cmd_params[field]
            for instr in instructions_of_interest:
                instr_info[instr] = line[instr] if instr in line else "0"
            fields = list(instr_info.keys())
            fields.sort()
            if instr_over_time_header == None:
                instr_over_time_header = fields
            elif instr_over_time_header != fields:
                print("Header mismatch!")
            instr_ot_lines.append(",".join([str(instr_info[field]) for field in fields]))
        with open(os.path.join(dump_dir, "instructions_ot.csv"), "a") as fp:
            if instr_over_time_write_header:
                instr_over_time_write_header = False
                fp.write(",".join(instr_over_time_header) + "\n")
            fp.write("\n".join(instr_ot_lines))
        instr_ot_lines = None
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
