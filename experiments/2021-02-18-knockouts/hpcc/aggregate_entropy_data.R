rm(list = ls())

scrape_dir = function(dir_name){
    filename = paste0(dir_name, '/entropy_data.csv')
    if(!file.exists(filename)){ # If directory doesn't exist, say so and return
      print('Base directory not found:')
      print(dir_name)
      return(NA)
    }
    return(read.csv(filename))
}
   


####### Main ########


# OLD: Load in a whole list of directories from file
# Load list of directories
fp = file('./data_directories.txt', 'r')
dir_vec = c()
while(T){
    line = readLines(fp, n = 1)
    if(length(line) == 0){
        break
    }
    dir_vec = c(dir_vec, line)
}
output_path = './'
#dir_vec = dir_vec[1]

## NEW: Load a single file from command line arg
#arg_vec = commandArgs(trailingOnly = T) 
#if(length(arg_vec)!= 2){
#  print('Error! Expected exactly 2 arguments: filepath of data and path of directory where we\'ll save the output (in that order)')
#  quit()
#}
#data_path = arg_vec[1]
#output_path = arg_vec[2]
#dir_vec = c(data_path) # Mock dir_vec so we can use the same code as before

## Ensure output_path ends in a slash
#if(substr(output_path, nchar(output_path), nchar(output_path)) != '/'){
#  output_path = paste0(output_path, '/')
#}


data_aggregate = NA
next_idx = 1

# Iterate through each dir_name
for(dir_name in dir_vec[1:length(dir_vec)]){
  # Grab the data for this 
  data_seed = scrape_dir(dir_name)
  # Skip rest if data not found
  if(!is.data.frame(data_seed)){
      next
  }
  # Extract metadata from the path 
  dir_name_parts = strsplit(dir_name, '/')[[1]]   
  # Last part of path is the seed
  seed = dir_name_parts[length(dir_name_parts)]
  # Next to last part of path stores the rest of the metadata
  metadata = dir_name_parts[length(dir_name_parts) - 1]
  # I messed up and put underscores in a variable, so we fix that here
  metadata = gsub('EVENT_FILE_PREFIX', 'PREFIX', metadata)
  metadata_parts = strsplit(metadata, '__')[[1]]
  # Assign metadata values based on TAG_VALUE system
  prefix = NA
  sensors = NA
  env = NA
  for(metadata_pair in metadata_parts){
    pair_parts = strsplit(metadata_pair, '_')[[1]]
    if(pair_parts[1] == 'PREFIX'){
      prefix = pair_parts[2]
    }
    else if(pair_parts[1] == 'SENSORS'){
      sensors = pair_parts[2]
    }
  }
  env = gsub('events-', '', prefix)
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
write.csv(data_aggregate, paste0(output_path, 'entropy_data.csv'))
