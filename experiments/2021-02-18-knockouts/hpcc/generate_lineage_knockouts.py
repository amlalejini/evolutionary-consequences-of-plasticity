import argparse

# Read in existing .spop file and return a list of dictionaries (one per organism)
def load_spop_file(filename):
    pop = []
    column_names = []
    header_str = ''
    with open(filename, 'r') as fp:
        for line in fp:
            line = line.strip()
            if line == '': # Skip empty lines 
                continue
            if line[0] == '#':
                header_str += line + '\n'
            line_parts = line.split(' ')
            if len(line_parts) == 0: # Skip any lines that have no spaces
                continue
            if line_parts[0] == '#format': # Grab column names from line that starts with '#format'
                column_names = line_parts[1:]
                print('Found column names: ' + str(column_names))
            elif line[0] == '#':
                pass
            else:
                org = {}
                #if len(line_parts) != len(column_names):
                #    print('Error: Organsim vs column name mismatch!')
                #    print('Organism columns:', len(line_parts))
                #    print('File columns:', len(column_names))
                #    print('Line:')
                #    print(line)
                #    quit(1)
                for col_idx in range(len(line_parts)):
                    org[column_names[col_idx]] = line_parts[col_idx]
                pop.append(org)
                
    return (pop, header_str)

# Literally do nothing (default cast)
def identity(x):
    return x

# Get the organism in the population with the greatest value of 'column_name'
    # cast_func can be used to cast to the appropriate type (data starts as a string)
def get_max_org_by_col(pop, column_name, cast_func = identity):
    max_val = None
    max_org = None
    tied_orgs = []
    if len(pop) < 1:
        print('Error: Population in get_max_org_by_col is empty!')
        quit(1)
    for org_idx in range(len(pop)):
        org = pop[org_idx]
        org_val = cast_func(org[column_name])
        if max_val == None or org_val > max_val:
            max_val = org_val
            max_org = org
            tied_orgs = []
        elif org_val == max_val:
            tied_orgs.append(org)
    if len(tied_orgs) != 0:
        print('Warning: max org tied with ' + str(len(tied_orgs)) + ' others!')
        for idx in range(len(tied_orgs)):
            print(idx)
            print(tied_orgs[idx])
    return max_org

# Avida instructions are represented by a character
    # These start by going through a-z in order
    # Next comes A-Z
    # After that ???
def get_inst_char_by_idx(idx):
    if idx < 26:
        return chr(ord('a') + idx)
    elif idx < 52:
        return chr(ord('A') + idx - 26)
    else:
        print('Error: Instruction set goes beyond a-z and A-Z, I don\'t know what to do!')
        quit(1)

# Load in an instruction set file, getting instruction names and generating their associated chars
def load_inst_set_file(filename):
    inst_set = []
    with open(filename, 'r') as fp:
        for line in fp:
            line = line.strip()
            if line == '': # Skip empty lines
                continue
            line_parts = line.split(' ')
            if len(line_parts) == 0:
                continue
            if line_parts[0] == 'INST':
                inst_set.append( (line_parts[0], get_inst_char_by_idx( len(inst_set) )) )
    return inst_set

# Function that writes all one-step mutants of the given organism to file 
def write_knockout_spop_file(filename, org, inst_set, header = '', cols_to_write = None):
    nop_x_char = 'G'
    cur_id = 0
    # Assemble the string for the base organism for all but id and sequence (which change per mutant)
    base_str = ''
    #TODO: Fix the order here
    base_sequence = org['sequence']
    if cols_to_write is None:
        for col_name in org:
            if cols_to_write is None or col_name in cols_to_write:
                if col_name == 'id':
                    base_str += '<<ID>> '
                elif col_name == 'sequence':
                    base_str += '<<SEQUENCE>> '
                else: 
                    base_str += org[col_name] + ' '
    else:
        for col_name in cols_to_write:
            if col_name == 'id':
                base_str += '<<ID>> '
            elif col_name == 'sequence':
                base_str += '<<SEQUENCE>> '
            else: 
                base_str += org[col_name] + ' '

    with open(filename, 'w') as fp:
        # Write the header
        fp.write(header + '\n')
        # Write the base organism
        fp.write(base_str.replace('<<ID>>', str(cur_id)).replace('<<SEQUENCE>>', org['sequence']) + '\n')
        cur_id += 1
        # Iterate through all loci in the base organism 
        for locus_idx in range(len(org['sequence'])):
            seq_prefix = base_sequence[:locus_idx]
            seq_suffix = base_sequence[(locus_idx + 1):]
            base_char = base_sequence[locus_idx]
            # Iterate through all possible instructions
            sequence = seq_prefix + nop_x_char + seq_suffix
            fp.write(base_str.replace('<<ID>>', str(cur_id)).replace('<<SEQUENCE>>', sequence)+ '\n')
            cur_id += 1


        


if __name__ == '__main__':
    # Handle command line arguments
    parser = argparse.ArgumentParser(description= \
        'Generate all one-step mutants for the dominant organism in .spop file and save those ' + \
        'mutants to a new .spop file')
    parser.add_argument('--input_file', type=str, help="Filename of population to analyze")
    parser.add_argument('--output_dir', type=str, help="Where to save the resulting files?")
    parser.add_argument('--inst_set_file', type=str, \
        help="File containing the instruction set for the run")
    parser.add_argument('--columns', type=str, help="Which columns to write out (comma separated)?")
    args = parser.parse_args()
    input_filename = args.input_file
    output_dir = args.output_dir
    inst_set_filename = args.inst_set_file
    cols_to_write_str = args.columns
    cols_to_write = cols_to_write_str.split(',')

    # Load in existing population
    old_pop, _ = load_spop_file(input_filename)

    # Load in header string
    with open('header_lineage.txt', 'r') as fp:
        header_str = fp.read()


    # Load in instruction set
    inst_set = load_inst_set_file(inst_set_filename)
    inst_count = len(inst_set)
    print('Instruction set contains: ' + str(inst_count) + ' instructions')

    # Get only the final organisms
    final_pop = []
    for org in old_pop:
        if org['update_deactivated'] == '-1':
            final_pop.append(org) 
    print(len(final_pop), 'orgs in final population!')

    # Grab final dominant organism
    dom_org = get_max_org_by_col(final_pop, 'num_units', cast_func = int) 
    dom_org_length = len(dom_org['sequence'])
    print('Dominant organism has ' + str(dom_org_length) + ' instructions')

    # Create an map to easily find organisms by their id
    org_id_map = {}
    for org in old_pop:
       org_id_map[org['id']] = org 
 
    # Extract the lineage of the final dominant organism
    cur_org = dom_org
    lineage = [dom_org]
    while cur_org['parents'] != '(none)':
        cur_org = org_id_map[cur_org['parents']]
        lineage.append(cur_org)
    print('Lineage length:', len(lineage))

    # We need a way to generate filenames
    # Use 1 through N, N = number of orgs in lineage, 0 is first org
    orgs_processed = 0
    max_digits = len(str(len(lineage)))
    for org in lineage:
        # Reset dominant org's id to 0 to make things simple
        org['id'] = 0
        
        # Get a zero-padded string to signify the org's place in the lineage
        org_num = len(lineage) - orgs_processed
        org_str = '0' * (max_digits - len(str(org_num))) + str(org_num)
 
        # Generate and save mutants in .spop file
        write_knockout_spop_file(output_dir + org_str + '_lineage_knockouts.spop', \
            org, inst_set, header_str, cols_to_write)
        
        orgs_processed += 1
    print('Done!')
