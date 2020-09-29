"""
This script is adapted from https://github.com/emilydolson/interpreting_the_tape_of_life/blob/master/source/scripts/extract_muller_data.py
"""

import pandas as pd
import argparse
import os
import copy

class Node():
    def __init__(self, id, parent="", seq="", phen=""):
        self.id = id
        self.parent = parent
        self.children = []
        self.seq = copy.deepcopy(seq)
        self.phenotype = phen

    def Print(self):
        print(f"id: {self.id}; parent: {self.parent}; children: {self.children}; seq: {self.seq}; phenotype: {self.phenotype}")


def lookup_phenotype(row, genotype_bank):
    if row["sequence"] in genotype_bank.index:
       return genotype_bank.loc[row["sequence"], "phenotype"]
    else:
        return "NONE"

def compress_phylogeny(root, nodes):
    """
    Compress phylogeny by phenotype.
    """
    new_id_map = {}
    next_id = 1
    nodes[root].new_id = 0
    new_id_map[root] = 0
    frontier = nodes[root].children

    adj_file = pd.DataFrame({"Identity":[], "Parent":[]})

    while frontier:
        #print("fontier:", frontier)
        new_frontier = []

        for n in frontier:
            if nodes[n].phenotype == "":
                #print(nodes[nodes[n].parent].phenotype)
                nodes[n].phenotype = nodes[nodes[n].parent].phenotype

            if nodes[n].phenotype == nodes[nodes[n].parent].phenotype:
                nodes[n].new_id = nodes[nodes[n].parent].new_id
            else:
                # print(nodes[n].phenotype, nodes[nodes[n].parent].phenotype)
                nodes[n].new_id = next_id
                adj_file = adj_file.append({"Identity":next_id, "Parent":nodes[nodes[n].parent].new_id}, ignore_index=True)
                next_id += 1

            new_id_map[nodes[n].id] = nodes[n].new_id
            new_frontier.extend(nodes[n].children)
            #print("children:", nodes[n].children, frontier, len(frontier))

        frontier = new_frontier

    return adj_file, new_id_map

def main():
    parser = argparse.ArgumentParser(description="Standards phylogeny file to ggmuller input files converter.")
    parser.add_argument("--run_dir", type=str, help="run directory")
    parser.add_argument("--output_prefix", "-out", type=str, help="Prefix to add to output file names")
    # Parse command line arguments.
    args = parser.parse_args()
    run_dir = args.run_dir

    if (args.output_prefix != None):
        adj_file_name = args.output_prefix + "_adjacency.csv"
        pop_file_name = args.output_prefix + "_pop_info.csv"
    else:
        adj_file_name = "adjacency.csv"
        pop_file_name = "pop_info.csv"


    # adj_file = adj_file.astype(dtype={"Identity":"object","Parent":"object"})
    pop_file = pd.DataFrame({"Identity":[], "Population":[], "Time":[]})

    genotype_bank_path = os.path.join(args.run_dir, f"phylogeny-snapshot-genotype-phenotype-table.csv")
    genotype_bank = ""
    genotype_bank = pd.read_csv(genotype_bank_path, index_col="sequence", na_filter=False)

    nodes = {}
    root = ""

    snapshot_files = [fname for fname in os.listdir(args.run_dir) if "phylogeny-snapshot-" in fname and ".csv" in fname and len(fname.split("-")) == 3]
    print(f"Found {len(snapshot_files)} files:")
    print("- " + "\n- ".join(snapshot_files))

    for filename in snapshot_files:
        snapshot_path = os.path.join(run_dir, filename)
        time = filename.split(".")[-2].split("-")[-1]

        df = pd.read_csv(snapshot_path)

        # Loop over each taxon on the phylogeny
        for i, row in df.iterrows():
            ancestors = row["ancestor_list"].strip("[] ").split(",")
            assert(len(ancestors) == 1)
            if ancestors[0] == "NONE":
                parent = -1
            else:
                parent = int(ancestors[0])

            phen = lookup_phenotype(row, genotype_bank)

            if row["id"] in nodes:
                nodes[row["id"]].parent = parent
                nodes[row["id"]].seq = row["sequence"]
                nodes[row["id"]].phenotype = phen
            else:
                nodes[row["id"]] = Node(row["id"], parent, row["sequence"], phen)

            if parent == -1:
                root = row["id"]
            elif parent in nodes:
                if row["id"] not in nodes[parent].children:
                    nodes[parent].children.append(row["id"])
            else:
                nodes[parent] = Node(parent)
                nodes[parent].children.append(row["id"])


            pop_file = pop_file.append({"Identity":row["id"], "Population":row["num_orgs"], "Time":time}, ignore_index=True)

    # # for node in nodes:
    # #     print("====")
    # #     print(f"{node}:")
    # #     nodes[node].Print()

    adj_file, new_id_map = compress_phylogeny(root, nodes)

    phenotypes = []
    for i,row in pop_file.iterrows():
        phenotypes.append(nodes[row["Identity"]].phenotype)

    pop_file["Phenotype"] = phenotypes

    pop_file["Identity"] = pop_file["Identity"].map(new_id_map)
    pop_file = pop_file.groupby(["Identity", "Phenotype", "Time"]).sum()
    pop_file = pop_file.reset_index()

    pop_file.to_csv(pop_file_name, index=False)
    adj_file.to_csv(adj_file_name, index=False)

    # adj_file.drop_duplicates(inplace=True)
    # print(adj_file)





if __name__ == "__main__":
    main()