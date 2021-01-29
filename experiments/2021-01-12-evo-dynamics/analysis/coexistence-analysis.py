"""
"""

from avida_phylogeny_converter import Convert_AvidaSpop_To_StdPhylogeny
import os, argparse, errno, subprocess

run_identifier = "RUN_"

analysis_script = """
#!/bin/sh

cwd=$(pwd)

"""

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

def main():
    parser = argparse.ArgumentParser(description="Phylogeny converter script.")
    parser.add_argument("--data_dir", type=str, help="Where is the base output directory for each run?")
    parser.add_argument("--dump", type=str, help="Where to dump this?", default=".")
    parser.add_argument("--update", type=int, help="Update to pull data for?")
    parser.add_argument("--config_dir", type=str, help="path to configuration directory (for avida analyze mode")
    parser.add_argument("--analyze_file", type=str, help="path to avida analyze file for coexistence runs")

    args = parser.parse_args()
    data_dir = args.data_dir
    dump_dir = args.dump
    config_dir = os.path.abspath(args.config_dir)
    analysis_fpath = os.path.abspath(args.analyze_file)
    update = args.update

    if not os.path.exists(data_dir):
        print("Unable to find data directory.")
        exit(-1)

    mkdir_p(dump_dir)

    # Aggregate run directories.
    run_dirs = [run_dir for run_dir in os.listdir(data_dir) if run_identifier in run_dir]
    print(f"Found {len(run_dirs)} run directories.")

    # Build analysis script
    analysis_commands = []

    for run_dir in run_dirs:
        run_path = os.path.abspath(os.path.join(data_dir, run_dir))
        run_id = os.path.split(run_path)[-1]
        analyze_fname = os.path.split(analysis_fpath)[-1]
        # Skip over (but make note of) incomplete runs.
        if not os.path.exists(os.path.join(run_path, 'data')):
            print('Skipping: ', run_path)
            continue
        print(f"Processing: {run_path}")

        cmd_log_path = os.path.join(run_path, "cmd.log")
        cmd_params = extract_params_cmd_log(cmd_log_path)
        # build avida analyze command

        analyze_params = " ".join([f"-set {param} {cmd_params[param]}" for param in cmd_params])
        analyze_params += f" -set ANALYZE_FILE {analyze_fname} -a"

        analysis_commands.append(  "############################")
        analysis_commands.append( f"# {run_id} ")
        analysis_commands.append(  "############################")
        analysis_commands.append( f"cd {run_path}" )
        analysis_commands.append( f"cp {os.path.join(config_dir, '*')} ./")
        analysis_commands.append( f"cp {analysis_fpath} ./")
        analysis_commands.append( f"./avida {analyze_params}" )

    with open("temp.sh", "w") as fp:
        fp.write(analysis_script + "\n".join(analysis_commands))

    subprocess.call("pwd")
    subprocess.run(["chmod", "755", "temp.sh"])
    subprocess.run("./temp.sh", shell=True)

    for run_dir in run_dirs:
        run_path = os.path.abspath(os.path.join(data_dir, run_dir))
        run_id = os.path.split(run_path)[-1]

        pop_fpath = os.path.join(run_path, "data", "coexistence-analysis", "env_all", f"detail-{update}.dat")
        out_fpath = os.path.join(dump_dir, f"{run_id}-phylo.csv")
        Convert_AvidaSpop_To_StdPhylogeny(pop_fpath, out_fpath)

if __name__ == "__main__":
    main()