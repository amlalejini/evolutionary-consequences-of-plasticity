import argparse, os, copy, errno, csv, subprocess, sys



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

def main():
    parser = argparse.ArgumentParser(description="Data aggregation script.")
    parser.add_argument("--run_dir", type=str, help="Where should we look for all of the necessary avida junk?")

    args = parser.parse_args()
    run_dir = args.run_dir

    snapshot_files = [fname for fname in os.listdir(run_dir) if "phylogeny-snapshot-" in fname and ".csv" in fname]
    print(f"Found {len(snapshot_files)} files:")
    print("- " + "\n- ".join(snapshot_files))


    # Extract sequences from phylogeny file.
    sequence_set = set([])

    for snapshot in snapshot_files:
        snapshot_path = os.path.join(run_dir, snapshot)
        # target_path_head, target_path_tail = os.path.split(snapshot_files)


        # Collect set of sequences in this snapshot.
        with open(snapshot_path, "r") as fp:
            snapshot_content = fp.read().split("\n")

        header = snapshot_content[0].split(",")
        header_lu = {header[i]:i for i in range(0, len(header))}
        snapshot_content = snapshot_content[1:]
        for line in snapshot_content:
            if line == "": continue
            sequence = line.split(",")[header_lu["sequence"]]
            sequence_set.add(sequence)



    # Dump sequences into detail file.
    phylo_seq_detail_content = "#filetype genotype_data\n"
    phylo_seq_detail_content += "#format id hw_type inst_set sequence length\n\n"
    id_index = 0
    for seq in sequence_set:
        phylo_seq_detail_content += " ".join(map(str,[id_index, "0", "heads_default", seq, len(seq)])) + "\n"
        id_index += 1

    out_path = os.path.join(run_dir, "phylogeny-snapshot-sequences.spop")
    with open(out_path, "w") as fp:
        fp.write(phylo_seq_detail_content)

if __name__ == "__main__":
    main()