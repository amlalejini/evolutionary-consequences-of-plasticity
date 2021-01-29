"""
ORIGINAL SCRIPT FROM: https://github.com/alife-data-standards/converters-avida/blob/master/avida_converters/phylogeny.py

avida-to-standard-phylogeny.py

This script converts an avida .spop file into ALife standard-compliant phylogeny
file.

Currently outputs in format assumed by pandas.

Currently outputs each entry in output file in order they were read in from Avida
file.

Currently assumes Avida defaults in .spop fields.
"""

import argparse, os, copy
import pandas as pd

VALID_OUT_FORMATS = ["csv", "json"]
AVIDA_SET_FIELDS = ["parents", "cells", "gest_offset", "lineage"]
AVIDA_SET_DELIM = ","

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

def Convert_AvidaSpop_To_StdPhylogeny(input_fpath, output_fpath=None, output_format="csv", minimal_output=False):
    """Convert Avida .spop file (default population output file for Avida) to ALife
       standard phylogeny format.

    Args:
        input_fpath (str): The path to the target Avida .spop file.
        output_fpath (str): The full path (including file name) to write standard
            phylogeny file to. If set to 'None', will output in same location as
            the specified Avida .spop file.
        output_format (str): The output format. Must be one of a valid set of supported
            output formats ('CSV', 'JSON')
        minimal_output (boolean): Should output be minimal? If so, only output minimal
            requirements (+ available conventional fields) for phylogeny standard.

    Returns:
        bool: True if successful, False otherwise.

    Raises:
        ValueError: If input_fpath is invalid.
        ValueError: If output_format does not specify a supported format.
        ValueError: If Avida IDs are not unique in the given input file.

    """
    # Is input_fpath a valid file?
    if (not os.path.isfile(input_fpath)):
        raise ValueError("Failed to find provided input file ({})".format(input_fpath))

    # Is output_format valid?
    if (not output_format in VALID_OUT_FORMATS):
        raise ValueError("Invalid output format provided ({}). Valid arguments include: {}".format(output_format, VALID_OUT_FORMATS))

    output_fpath = output_fpath if (output_fpath != None) else input_fpath.replace(".spop", "_standard-phylogeny.{}".format(output_format))

    # -- surgery to get this to work on output of analyze mode genotype detail file --
    dat_file_contents = read_avida_dat_file(input_fpath)
    avida_data = {field:[] for field in dat_file_contents[0].keys()}
    for line in dat_file_contents:
        for field in line:
            avida_data[field].append(line[field])

    # Clean up avida data to play with standard.
    # avida_data["ancestor_list"] = [list(["none" if anc == "(none)" else anc for anc in anc_lst]) for anc_lst in avida_data.pop("parents")]
    avida_data["ancestor_list"] = [[anc_list] for anc_list in avida_data["parent_id"]]
    avida_data["origin_time"] = copy.deepcopy(avida_data["update_born"])
    avida_data["id"] = list(avida_data["genotype_id"])
    # -- end surgery --

    # Are all IDs unique?
    id_set = set(avida_data["id"])
    if (len(avida_data["id"]) != len(id_set)):
        raise ValueError("Avida organism IDs must be unique!")

    # Convert Avida data into pandas data frame.
    df = pd.DataFrame(data = avida_data)

    # Drop any fields we want to delete.
    del_fields = []
    if minimal_output:
        # What fields should we delete (if we're doing minimal output)?
        min_fields = ["id", "ancestor_list", "origin_time"]
        del_fields = [field for field in avida_data if not field in min_fields]
        df.drop(del_fields, axis=1, inplace=True)

    # Adjust the header so that standard fields are up front.
    stds_hd = ["id", "ancestor_list", "origin_time"]
    new_header = stds_hd + [field for field in avida_data if (not field in stds_hd) and (not field in del_fields)]
    # Write output in requested format.

    # print(len(df.id.unique()))
    df.set_index("id", inplace=True, drop=False)

    if (output_format == "csv"):
        with open(output_fpath, "w"):
            df.to_csv(output_fpath, sep=",", columns=new_header, index=False, index_label=False)
    elif (output_format == "json"):
        with open(output_fpath, "w"):
            df.to_json(output_fpath, orient="index")

    return True

def main():
    # Setup command line arguments.
    parser = argparse.ArgumentParser(description="Avida .spop to ALife standard-compliant phylogeny converter.")
    parser.add_argument("input", type=str, help="Input avida .spop file.")
    parser.add_argument("-output", "-out", type=str, help="Name to assign to standard-compliant output file.")
    parser.add_argument("-format", type=str, default="csv", help="What standard file format should this script output? Valid options: {}".format(VALID_OUT_FORMATS))
    parser.add_argument("-minimal", action="store_true", help="Store minimal data in output file.")
    parser.add_argument("-list_formats", "-lsf", action="store_true", help="List available output formats.")

    # Parse command line arguments.
    args = parser.parse_args()

    if (args.list_formats):
        print("Valid output formats include: {}".format(VALID_OUT_FORMATS))
        print("File an issue here to request new formats: https://github.com/alife-data-standards/converters-avida/issues")
        return

    # Extract/validate arguments
    in_fp = args.input
    out_fp = args.output
    out_format = args.format.lower()
    minimal_out = args.minimal

    print("Converting {}".format(in_fp))
    if (Convert_AvidaSpop_To_StdPhylogeny(in_fp, out_fp, out_format, minimal_out)):
        print("Success!")
    else:
        print("Ah! Something went wrong.")

if __name__ == "__main__":
    main()