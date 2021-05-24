rm(list = ls())

load_dat_file = function(filename){
    if(!file.exists(filename)){ # If file doesn't exist, say so and return
      print('File not found:')
      print(filename)
      return(NA)
    }
    # Load in odd data and format it
    data_file = read.csv(filename, sep =  ' ', header = F, comment.char = '#')
    colnames(data_file) = c('knockout_id', 'update_born','tree_depth','fitness',
        'genome_length','genome_sequence','gestation_time', 'merit', 'rep_efficiency',
        'not','nand','and','ornot','or','andnot','nor','xor','equals')
    data_file$genome_sequence = as.character(data_file$genome_sequence)
    data_file$task_profile = paste0(data_file$not, data_file$nand, data_file$and, data_file$ornot, 
        data_file$or, data_file$andnot)
    return(data_file)
}

scrape_dir = function(dir_name){
    if(!file.exists(dir_name)){ # If directory doesn't exist, say so and return
      print('Base directory not found:')
      print(dir_name)
      return(NA)
    }
    odd_files = list.files(paste0(dir_name, '/data/lineage_knockout_data/env_odd/'))
    print(odd_files)
    even_files = list.files(paste0(dir_name,'/data/lineage_knockout_data/env_even/'))
    if(length(odd_files) != length(even_files)){
      print('Mismatch in odd and even files:')
      print(dir_name)
      return(NA)
    }
    data_dir = NA
    for(filename in odd_files){
        print(filename)
        data_step = NA
        for(env in c('odd', 'even')){
            data_file = load_dat_file(
                paste0(dir_name, '/data/lineage_knockout_data/env_', env, '/', filename))
            cols_to_rename = c('fitness', 'gestation_time', 'merit', 'rep_efficiency','task_profile',
                'not','nand','and','ornot','or','andnot','nor','xor','equals')
            for(col in cols_to_rename){
                data_file[,paste0(col, '_', env)] = data_file[,col]
            }
            data_file = data_file[, !colnames(data_file) %in% cols_to_rename]
            data_file = data_file[, !is.na(colnames(data_file))]
            if(!is.data.frame(data_step)){
                data_step = data_file
            } else {
                data_step = merge(data_step, data_file)
            }
        }
        if(!is.data.frame(data_dir)){
            data_dir = data_step
        } else {
            data_dir = rbind(data_dir, data_step)
        }
    }
    return(data_dir)
}
   


####### Main ########


# OLD: Load in a whole list of directories from file
# Load list of directories
#fp = file('./data_directories.txt', 'r')
#dir_vec = c()
#while(T){
#    line = readLines(fp, n = 1)
#    if(length(line) == 0){
#        break
#    }
#    dir_vec = c(dir_vec, line)
#}
#dir_vec = dir_vec[1]

# NEW: Load a single file from command line arg
arg_vec = commandArgs(trailingOnly = T) 
if(length(arg_vec)!= 2){
  print('Error! Expected exactly 2 arguments: filepath of data and path of directory where we\'ll save the output (in that order)')
  quit()
}
data_path = arg_vec[1]
output_path = arg_vec[2]
dir_vec = c(data_path) # Mock dir_vec so we can use the same code as before

# Ensure output_path ends in a slash
if(substr(output_path, nchar(output_path), nchar(output_path)) != '/'){
  output_path = paste0(output_path, '/')
}


data_aggregate = NA
next_idx = 1

# Iterate through each dir_name
for(dir_name in dir_vec[1:length(dir_vec)]){
  # Grab the data for this 
  data_seed = scrape_dir(dir_name)
  print(nrow(data_seed))
  # Skip rest if data not found
  if(!is.data.frame(data_seed)){
      next
  }
  # Exract info about run from cmd.log
  s = readLines(file(paste0(dir_name, '/cmd.log')))
  env_raw = strsplit(regmatches(s, regexpr('-set EVENT_FILE \\S+\\s', s, perl = T)), ' ')[[1]]
  env = if(length(grep('env-all', env_raw)) > 0) 'ALL-u0' else 'chg-u100'
  seed_raw = strsplit(regmatches(s, regexpr('-set RANDOM_SEED \\d+\\s', s, perl = T)), ' ')[[1]]
  seed = as.character(seed_raw[length(seed_raw)])
  sensors_raw = strsplit(regmatches(s, regexpr('-set DISABLE_REACTION_SENSORS \\d+\\s', s, perl = T)), ' ')[[1]]
  sensors = as.character(sensors_raw[length(sensors_raw)])
  # Inject the metadata into the data frame
  data_seed$seed = seed
  data_seed$environment = env
  data_seed$sensors = sensors
  # If this is out first data frame, use it to shape the aggregate dataframe!
  if(!is.data.frame(data_aggregate)){
    data_aggregate = 
        data.frame(data = matrix(ncol = ncol(data_seed), nrow = nrow(data_seed) * length(dir_vec)))
    colnames(data_aggregate) = colnames(data_seed)
  }
  # Insert the seed's data into the aggregate data frame
  last_idx = next_idx + nrow(data_seed) - 1
  data_aggregate[next_idx:last_idx,] = data_seed
  next_idx = last_idx
  print(paste(seed))
}
# Trim off any extra rows (from holes caused by runs that failed)
#data_aggregate = data_aggregate[!is.na(data_aggregate$knockout_id),]
# Save the data!
write.csv(data_aggregate, paste0(output_path, 'knockout_data.csv'))
