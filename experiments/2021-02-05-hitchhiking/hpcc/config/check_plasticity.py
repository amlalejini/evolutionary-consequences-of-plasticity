import sys, errno, subprocess, csv

phenotypic_traits = ["not","nand","and","ornot","or","andnot","nor","xor","equals"]
even_traits = {"not", "and", "or"}#}, "nor", "equals"}
odd_traits = {"nand", "ornot", "andnot"}#, "xor", "equals"}
even_profile = "101010000"
odd_profile =  "010101000"
all_profile =  "111111000"

# Borrowed from Alex :^)
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

if __name__ == '__main__': 
    env_even = read_avida_dat_file('data/analysis/env_even/final_dominant.dat')[0]
    env_odd = read_avida_dat_file('data/analysis/env_odd/final_dominant.dat')[0]
    phenotype_even = "".join([env_even[trait] for trait in phenotypic_traits])
    phenotype_odd = "".join([env_odd[trait] for trait in phenotypic_traits])
    is_plastic = True
    for key in even_traits: 
        if env_even[key] != '1':
            is_plastic = False
            break
        if env_odd[key] != '0':
            is_plastic = False
            break
    for key in odd_traits: 
        if env_odd[key] != '1':
            is_plastic = False
            break
        if env_even[key] != '0':
            is_plastic = False
            break
    if is_plastic:
        print('Perfectly plastic!')
        with open('is_perfectly_plastic.txt', 'w') as out_fp:
            out_fp.write('true')
    else:
        if phenotype_even == phenotype_odd:
            print('Not plastic!')
        print('Not perfectly plastic!', phenotype_even, phenotype_odd)
