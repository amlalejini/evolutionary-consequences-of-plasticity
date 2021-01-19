'''
Script: divide_data.py

Utility script for dividing data into multiple, smaller files based on value of a specified column.
'''

import argparse, os, copy, errno, csv
import pandas as pd

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

def main():
    # Setup the commandline argument parser.
    parser = argparse.ArgumentParser(description="Divide data into multiple smaller files based on value of a specified column.")
    parser.add_argument("-d", "--divide_on", type=str, help="What column should we divide file on?")
    parser.add_argument("--file", type=str, help="What .csv file should we filter?")
    parser.add_argument("--dump", type=str, help="Where should we dump the output?", default="./dump")

    # Extract arguments from commandline
    args = parser.parse_args()
    divide_on = args.divide_on
    in_file = args.file
    dump_dir = args.dump

    # Load data
    data = pd.read_csv(in_file)

    # parse file name

    original_fname = os.path.basename(in_file)
    original_fname = os.path.splitext(original_fname)[0]

    # check if divide on column in data frame
    if not divide_on in data.columns:
        print("Dividing column not found.")
        print("Available columns include:")
        print("  " + "\n  ".join([name for name in data.columns]))
        exit(-1)

    mkdir_p(dump_dir)
    dividing_values = data[divide_on].unique()
    for value in dividing_values:
        filtered_df = data.loc[data[divide_on] == value]
        out_fname = f"{original_fname}_{divide_on}={value}.csv"
        out_fpath = os.path.join(dump_dir, out_fname)
        filtered_df.to_csv(out_fpath, index=False)
    print("Done!")



    # mkdir_p(dump_dir)




if __name__ == "__main__":
    main()