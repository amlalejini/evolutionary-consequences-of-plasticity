"""
Given a run directory that has processed phylogeny snapshot sequences (i.e., data/analysis/env_*/phylogeny-snapshot-*-sequences.dat files),
generate a genotype to phenotype lookup table that can be used by extract_muller_data.py.
"""

import argparse, os, copy, errno, csv, subprocess, sys, itertools

primary_traits = ["not","nand","and","ornot","or","andnot"]

def mkdir_p(path):
    """
    This is functionally equivalent to the mkdir -p [fname] bash command
    """
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

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

def extract_params_cmd_log(path):
    content = None
    with open(path, "r") as fp:
        content = fp.read().strip()
    content = content.replace("./avida", "")
    content = content.split("\n")[0]
    params = [param.strip() for param in content.split("-set") if param.strip() != ""]
    cfg = {param.split(" ")[0]:param.split(" ")[1] for param in params}
    return cfg

def main():
    parser = argparse.ArgumentParser(description="Run submission script.")
    parser.add_argument("--run_dir", type=str, help="Where is the base output directory for the run?")

    args = parser.parse_args()
    run_dir = args.run_dir

    if not os.path.exists(run_dir):
        print("Unable to find run directory.")
        exit(-1)

    # mkdir_p(dump_dir)

    # Skip over (but make note of) incomplete runs.
    if not os.path.exists(os.path.join(run_dir, 'data', 'analysis')):
        print('Failed to find analysis directory.')
        exit(-1)

    ############################################################
    # Extract commandline configuration settings (from cmd.log file)
    cmd_log_path = os.path.join(run_dir, "cmd.log")
    cmd_params = extract_params_cmd_log(cmd_log_path)
    # Infer environmental change and change rate from events file
    chg_env = "chg" in cmd_params["EVENT_FILE"]

    env_all_dat_path = os.path.join(run_dir, "data", "analysis", "env_all", f"phylogeny-snapshot-sequences.dat")
    env_even_dat_path = os.path.join(run_dir, "data", "analysis", "env_even", f"phylogeny-snapshot-sequences.dat")
    env_odd_dat_path = os.path.join(run_dir, "data", "analysis", "env_odd", f"phylogeny-snapshot-sequences.dat")

    # If changing environment, concatenate phenotype from env_odd and env_even
    fields = []
    if chg_env:
        fields = ["sequence","phenotype_even","phenotype_odd","phenotype"]
        seqs_env_even = read_avida_dat_file(env_even_dat_path)
        seqs_env_odd = read_avida_dat_file(env_odd_dat_path)
        # Number of genotypes across files must be the same.
        assert(len(seqs_env_even) == len(seqs_env_odd))

        # init sequences with even phenotype information
        sequences = {
                        seq_even["genome_sequence"]:
                        {
                            "sequence": seq_even["genome_sequence"],
                            "phenotype_even": "".join([seq_even[trait] for trait in primary_traits]),
                            "phenotype_odd": None,
                        }
                        for seq_even in seqs_env_even
                    }

        # add odd phenotypes in
        for seq_odd in seqs_env_odd:
            sequences[seq_odd["genome_sequence"]]["phenotype_odd"] = "".join([seq_odd[trait] for trait in primary_traits])
            sequences[seq_odd["genome_sequence"]]["phenotype"] = "[" + sequences[seq_odd["genome_sequence"]]["phenotype_even"] + sequences[seq_odd["genome_sequence"]]["phenotype_odd"] + "]"

    else:
        seqs_env_all = read_avida_dat_file(env_all_dat_path)
        # TODO

    out_content = ",".join(fields) + "\n"
    for seq in sequences:
        out_content += ",".join(str(sequences[seq][field]) for field in fields) + "\n"
    with open(os.path.join(run_dir, f"phylogeny-snapshot-genotype-phenotype-table.csv"), "w") as fp:
        fp.write(out_content)


if __name__ == "__main__":
    main()