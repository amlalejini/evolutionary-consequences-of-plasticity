'''
Summarize information from execution traces.
'''

import argparse, os, sys, errno, subprocess, csv, re

run_identifier = "RUN_"

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

def extract_params_cmd_log(path):
    content = None
    with open(path, "r") as fp:
        content = fp.read().strip()
    content = content.replace("./avida", "")
    params = [param.strip() for param in content.split("-set") if param.strip() != ""]
    cfg = {param.split(" ")[0]:param.split(" ")[1] for param in params}
    return cfg

def genome_from_genfile(genome_file):
    """
    Given a file pointer to a .gen (from avida analyze mode), return the genome as a list of instructions.
    """
    with open(genome_file, "r") as gen_fp:
        sequence = [line.strip() for line in gen_fp if (line.strip() != "") and (not "#" in line)]
    return sequence

def extract_site_sequence(trace_file):
    """
    Given a file pointer to an execution trace produced by avida's analyze mode,
     return the site usage (list where index represents the site and the value represents executions at that site)
    """
    execution_states = []
    execution_site_sequence = []
    execution_inst_sequence = []
    # Step 1: chunk the trace
    with open(trace_file, "r") as trace_fp:
        current_state = -1
        for line in trace_fp:
            if "---------------------------" in line:
                current_state += 1
                execution_states.append("")
            else:
                execution_states[current_state] += line
    # Step 2: extract site execution sequence
    for si in range(0, len(execution_states) - 1):
        state = execution_states[si]
        if "# Final Memory" in state:
            # print ("Multiple runs in trace!?")
            break
        # get instruction head location
        m = re.search(pattern = "IP:(\d+)", string = state)
        instr_head = int(m.group(1))
        # get current instruction
        m = re.search(pattern = "IP:\d+\s\((.*)\)\n", string = state)
        current_instruction = str(m.group(1))
        # store our findings
        execution_site_sequence.append(int(instr_head))
        execution_inst_sequence.append(current_instruction)
    return {"sites": execution_site_sequence, "instructions": execution_inst_sequence}

# sites toggled on in a but not in b
# def get_chunk_sizes(sites):
#     sites.sort()
#     chunk_sizes = []
#     for i in range(0, len(sites)):
#         if not i:
#             chunk_sizes.append(1)
#             continue
#         # if previous site is contiguous with this site, increment chunk size
#         if sites[i] == (sites[i-1] + 1):
#             # part of previous chunk
#             chunk_sizes[-1] += 1
#         else:
#             # start a new chunk
#             chunk_sizes.append(1)
#     return chunk_sizes

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
        env_cond = cmd_params["EVENT_FILE"].replace("events_", "").split("_phase")[0].lower()
        phase = "1" if "phase-one" in cmd_params["EVENT_FILE"] else "2"

        events_info = cmd_params["EVENT_FILE"].strip("events_").strip(".cfg").split("_")
        events_info = {param.split("-")[0]:param.split("-")[1] for param in events_info}
        change_rate = int(events_info["rate"].strip("u"))

        summary_info["chg_env"] = chg_env
        summary_info["environment"] = env_cond
        summary_info["phase"] = phase
        summary_info["change_rate"] = change_rate

        if cmd_params["DISABLE_REACTION_SENSORS"] == "1": continue

        for field in cmd_params:
            summary_info[field] = cmd_params[field]

        ############################################################

        ############################################################
        # Load genome file
        genome_path = os.path.join(run_path, "data", "analysis", "env_all", "final_dominant.gen")
        genome_sequence = genome_from_genfile(genome_path)
        ############################################################

        ############################################################
        # Extract trace data for env-a an env-b
        # ENV-A (even)
        env_a_trace_path = os.path.join(run_path, "data", "analysis", "env_even", "trace") # even
        # get file name
        trace_a_fname = [fname for fname in os.listdir(env_a_trace_path) if ".trace" in fname][0]
        # Append to path
        env_a_trace_path = os.path.join(env_a_trace_path, trace_a_fname)
        # ENV-B (odd)
        env_b_trace_path = os.path.join(run_path, "data", "analysis", "env_odd", "trace") # odd
        # get file name
        trace_b_fname = [fname for fname in os.listdir(env_b_trace_path) if ".trace" in fname][0]
        # Append to path
        env_b_trace_path = os.path.join(env_b_trace_path, trace_b_fname)

        # parse trace data
        env_a_trace_data = extract_site_sequence(env_a_trace_path)
        env_b_trace_data = extract_site_sequence(env_b_trace_path)

        sites_executed_env_a = set(env_a_trace_data["sites"])
        sites_executed_env_b = set(env_b_trace_data["sites"])

        # Which sites are toggled based on environmental context?
        toggled_sites = sites_executed_env_a ^ sites_executed_env_b
        num_toggled_sites = len(toggled_sites)
        summary_info["dominant_num_toggled_sites"] = num_toggled_sites

        # Which instructions are executed?
        env_a_execution = [i in sites_executed_env_a for i in range(len(genome_sequence))]
        env_b_execution = [i in sites_executed_env_b for i in range(len(genome_sequence))]
        toggled_execution = [env_a_execution[i] ^ env_b_execution[i] for i in range(len(genome_sequence))]
        # which sites are unexecuted nops? (we don't want these to break up/count toward chunk size)
        unexecuted_nops = [ (not (env_a_execution[i] or env_b_execution[i])) and "nop-" in genome_sequence[i] for i in range(len(genome_sequence))]

        chunk_sizes = []
        cur_chunk_size = 0
        in_chunk = False
        for site_i in range(len(genome_sequence)):
            toggled = toggled_execution[site_i]
            unexecuted_nop = unexecuted_nops[site_i]
            # we don't care about unexecuted nops
            if unexecuted_nop: continue
            if toggled and not in_chunk:
                in_chunk = True
                cur_chunk_size = 1
            elif toggled and in_chunk:
                cur_chunk_size += 1
            elif not toggled and in_chunk:
                chunk_sizes.append(cur_chunk_size)
                in_chunk = False
                cur_chunk_size = 0
        if cur_chunk_size: chunk_sizes.append(cur_chunk_size)

        summary_info["dominant_toggled_chunk_sizes"] = ";".join(map(str, chunk_sizes))
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
    if summary_header == None: return
    with open(os.path.join(dump_dir, "trace_summary.csv"), "w") as fp:
        out_content = ",".join(summary_header) + "\n" + "\n".join(summary_content_lines)
        fp.write(out_content)


if __name__ == "__main__":
    main()