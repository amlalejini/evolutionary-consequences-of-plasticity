import argparse, os

base_str = '''
#######################################################
# Analyzes organisms in the specified population file #
#######################################################

SET i 200000
SET v unknown

FUNCTION SET_ENV_EVEN
  SET v env_even
  SetReactionValue NOT 1.0
  SetReactionValue NAND -1.0
  SetReactionValue AND 1.0
  SetReactionValue ORN -1.0
  SetReactionValue OR 1.0
  SetReactionValue ANDN -1.0
END

FUNCTION SET_ENV_ODD
  SET v env_odd
  SetReactionValue NOT -1.0
  SetReactionValue NAND 1.0
  SetReactionValue AND -1.0
  SetReactionValue ORN 1.0
  SetReactionValue OR -1.0
  SetReactionValue ANDN 1.0
END

FUNCTION ANALYZE_FILE
    # - One step knockouts of org
    #   - env even  => BATCH 0
    #   - env odd   => BATCH 1
    PURGE_BATCH 0
    PURGE_BATCH 1
    # Load population (into batch 0, 6)
    SET_BATCH 0
    LOAD <<KNOCKOUT_DIR>>$i_lineage_knockouts.spop
    # find dominant genotype (duplicate into 1, 2)
    DUPLICATE 0 1

    #   - env even  => BATCH 0
    SET_BATCH 0
    SET_ENV_EVEN
    RECALC
    DETAIL <<DATA_DIR>>$v/$i_lineage_knockouts.dat id update_born depth fitness length sequence gest_time merit efficiency task.0 task.1 task.2 task.3 task.4 task.5 task.6 task.7 task.8

    #   - env odd   => BATCH 1
    SET_BATCH 1
    SET_ENV_ODD
    RECALC
    DETAIL <<DATA_DIR>>$v/$i_lineage_knockouts.dat id update_born depth fitness length sequence gest_time merit efficiency task.0 task.1 task.2 task.3 task.4 task.5 task.6 task.7 task.8
END
'''

#SET i 0001
#ANALYZE_FILE

def main():
    # Setup command line args
    parser = argparse.ArgumentParser(description='Run submission script.')
    parser.add_argument('--knockout_dir',type=str, help='Directory that contains input .spop files?')
    parser.add_argument('--data_dir', type=str, help='Where to save the analysis results?')
    parser.add_argument('--output_dir', type=str, help='Where to output this config file?')
    
    # Load in command line arguments
    args = parser.parse_args()
    knockout_dir = args.knockout_dir
    if knockout_dir[-1] != '/': # Ensure these two directories end in / before using them in .replace()
        knockout_dir += '/'
    data_dir = args.data_dir
    if data_dir[-1] != '/': 
        data_dir += '/'
    output_dir = args.output_dir

    file_str = base_str
    file_str = file_str.replace('<<KNOCKOUT_DIR>>', knockout_dir)
    file_str = file_str.replace('<<DATA_DIR>>', data_dir)
    file_str += '\n\n'

    # Add lines to analyze each individual file
    num_files = len(os.listdir(knockout_dir))
    max_digits = len(str(num_files))
    for i in range(1, num_files + 1):
        s = (max_digits - len(str(i))) * '0' + str(i)
        file_str += 'SET i ' +  s + '\n'
        file_str += 'ANALYZE_FILE\n'

    # Write out resulting .cfg
    cfg_filename = os.path.join(output_dir, 'analyze_lineage_knockouts.cfg')
    print('Saving to:',  cfg_filename)
    with open(cfg_filename, 'w') as fp:
        fp.write(file_str)

if __name__ == '__main__':
    main()
