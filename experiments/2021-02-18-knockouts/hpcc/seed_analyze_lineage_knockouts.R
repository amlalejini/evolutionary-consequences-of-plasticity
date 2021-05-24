# Clear any existing data
rm(list = ls())
# Set to false if running in RStudio, true otherwise
use_command_line_args = T

# Handle command line args
if(use_command_line_args){
  arg_vec = commandArgs(trailingOnly = T) 
  if(length(arg_vec)!= 2){
    print('Error! Expected exactly 2 arguments: filepath of data and path of directory where we\'ll save the output (in that order)')
    quit()
  }
  data_path = arg_vec[1]
  output_path = arg_vec[2]
}else{
  #data_path = './static/knockout_data.csv'#./data/knockout_u100_sensors.csv'
  #output_path = './static/'
  data_path = './non_plastic/knockout_data.csv'#./data/knockout_u100_sensors.csv'
  output_path = './non_plastic/'
}

# Load libraries
library(ggplot2)
library(dplyr)

# Plotting variables that will be used repeatedely 
color_task = '#1f78b4'
color_map = c(
  'None' = '#aaaaaa', 
  'Plasticity Machinery' = 'red', 
  'NOT Machinery' = color_task,
  'NAND Machinery' = color_task,
  'AND Machinery' = color_task,
  'ANDNOT Machinery' = color_task,
  'OR Machinery' = color_task,
  'ORNOT Machinery' = color_task,
  'Task Machinery' = color_task,
  'Previous Task Machinery' = '#a6cee3'
)

# Ensure output_path ends in a slash
if(substr(output_path, nchar(output_path), nchar(output_path)) != '/'){
  output_path = paste0(output_path, '/')
}

# Load in the data
cat('Loading data\n')
data = read.csv(data_path)
cat('Finished loading data\n')

# Quick data prep
# Condense tasks into phenotypes
data$count = data$not_even + data$nand_even + data$and_even + data$ornot_even + data$or_even + data$andnot_even
data$phenotype_odd_int = as.numeric(strtoi(data$task_profile_odd, base=2))
data$phenotype_even_int = as.numeric(strtoi(data$task_profile_even, base=2))
data$plasticity_int = bitwXor(data$phenotype_odd_int, data$phenotype_even_int)

cat('Trimming data\n')
# Grab only the columns that we need
data_plot = data[,c('knockout_id', 'update_born', 'tree_depth', 'seed', 'environment', 'sensors',
                        'phenotype_even_int', 'phenotype_odd_int', 'plasticity_int',
                        'genome_sequence', 'fitness_even', 'fitness_odd',
                        'gestation_time_odd', 'gestation_time_even', 'rep_efficiency_odd', 'rep_efficiency_even')]
cat('Finshed trimming data\n')
#data_plot = data_plot[data_plot$tree_depth < 500,]

# Grab the "base organism" for each knockout - the organism used to create that knockout
data_plot$base_phenotype_even_int = 0
data_plot$base_phenotype_odd_int = 0
data_plot$base_phenotype_plasticity_int = 0
data_plot$base_gestation_time_even = 0
data_plot$base_gestation_time_odd = 0
data_plot$base_rep_efficiency_even = 0
data_plot$base_rep_efficiency_odd = 0
data_plot$base_fitness_even = 0
data_plot$base_fitness_odd = 0
data_plot$original_char = NA
data_plot$genome_sequence = as.character(data_plot$genome_sequence)

# Order data by knockout id to make future operations easier
data_plot = data_plot[order(data_plot$knockout_id),]

# Fetch info from the "base org" for each knockout, where the base org is what was modified to create the knockout
max_depth = max(data_plot$tree_depth)
for(depth in unique(data_plot$tree_depth)){
  if(depth %% 100 == 0){
    print(paste0('depth: ', depth, ' / ', max_depth))
  }
  depth_mask = data_plot$tree_depth == depth
  base_org = data_plot[depth_mask & data_plot$knockout_id == 0,]
  base_org_sequence_vec = strsplit(base_org$genome_sequence, '')[[1]]
  data_plot[depth_mask, 
    c('base_phenotype_even_int', 
      'base_phenotype_odd_int', 
      'base_phenotype_plasticity_int', 
      'original_char', 
      'base_gestation_time_even', 
      'base_gestation_time_odd',
      'base_rep_efficiency_even', 
      'base_rep_efficiency_odd', 
      'base_fitness_even', 
      'base_fitness_odd')] = 
    c(rep(base_org[1,]$phenotype_even_int, sum(depth_mask)),
      rep(base_org[1,]$phenotype_odd_int, sum(depth_mask)),
      rep(base_org[1,]$plasticity_int, sum(depth_mask)),
      c(NA, base_org_sequence_vec),
      rep(base_org[1,]$gestation_time_even, sum(depth_mask)),
      rep(base_org[1,]$gestation_time_odd, sum(depth_mask)),
      rep(base_org[1,]$rep_efficiency_even, sum(depth_mask)),
      rep(base_org[1,]$rep_efficiency_odd, sum(depth_mask)),
      rep(base_org[1,]$fitness_even, sum(depth_mask)),
      rep(base_org[1,]$fitness_odd, sum(depth_mask))
      )
}
data_plot$base_phenotype_even_int = as.numeric(data_plot$base_phenotype_even_int)
data_plot$base_phenotype_odd_int = as.numeric(data_plot$base_phenotype_odd_int)
data_plot$gestation_time_even = as.numeric(data_plot$gestation_time_even)
data_plot$gestation_time_odd = as.numeric(data_plot$gestation_time_odd)
data_plot$base_gestation_time_even = as.numeric(data_plot$base_gestation_time_even)
data_plot$base_gestation_time_odd = as.numeric(data_plot$base_gestation_time_odd)
data_plot$base_fitness_even = as.numeric(data_plot$base_fitness_even)
data_plot$base_fitness_odd = as.numeric(data_plot$base_fitness_odd)


# Get locus specific functionality for all tasks
task_order = c('not', 'nand', 'and', 'ornot', 'or', 'andnot')
task_masks = c(32, 16, 8, 4, 2, 1)
for(task_id in 1:length(task_order)){
  task = task_order[task_id]
  task_mask = task_masks[task_id]
  task_key = paste0(task,'_category')
  data_plot[,task_key] = 'No category'
  data_plot$even_knockout = bitwAnd(data_plot$phenotype_even_int, task_mask) / task_mask
  data_plot$odd_knockout = bitwAnd(data_plot$phenotype_odd_int, task_mask) / task_mask
  data_plot$even_base = bitwAnd(data_plot$base_phenotype_even_int, task_mask) / task_mask
  data_plot$odd_base = bitwAnd(data_plot$base_phenotype_odd_int, task_mask) / task_mask
  data_plot[data_plot$even_base == 0 & data_plot$odd_base == 0 & data_plot$even_knockout == 0 & data_plot$odd_knockout == 0,task_key] = 'No change'
  data_plot[data_plot$even_base == 0 & data_plot$odd_base == 1 & data_plot$even_knockout == 0 & data_plot$odd_knockout == 1,task_key] = 'No change'
  data_plot[data_plot$even_base == 1 & data_plot$odd_base == 0 & data_plot$even_knockout == 1 & data_plot$odd_knockout == 0,task_key] = 'No change'
  data_plot[data_plot$even_base == 1 & data_plot$odd_base == 1 & data_plot$even_knockout == 1 & data_plot$odd_knockout == 1,task_key] = 'No change'
  data_plot[(data_plot$gestation_time_odd > (data_plot$base_gestation_time_odd + 2)) | (data_plot$gestation_time_even > (data_plot$base_gestation_time_even + 2)),task_key] = 'Replication Machinery'
  data_plot[data_plot$even_base == 0 & data_plot$odd_base == 0 & data_plot$even_knockout == 0 & data_plot$odd_knockout == 1,task_key] = 'Appear P'
  data_plot[data_plot$even_base == 0 & data_plot$odd_base == 0 & data_plot$even_knockout == 1 & data_plot$odd_knockout == 0,task_key] = 'Appear P'
  data_plot[data_plot$even_base == 0 & data_plot$odd_base == 0 & data_plot$even_knockout == 1 & data_plot$odd_knockout == 1,task_key] = 'Appear NP'
  data_plot[data_plot$even_base == 0 & data_plot$odd_base == 1 & data_plot$even_knockout == 0 & data_plot$odd_knockout == 0,task_key] = 'Loss P'
  data_plot[data_plot$even_base == 0 & data_plot$odd_base == 1 & data_plot$even_knockout == 1 & data_plot$odd_knockout == 0,task_key] = 'P Inversion'
  data_plot[data_plot$even_base == 0 & data_plot$odd_base == 1 & data_plot$even_knockout == 1 & data_plot$odd_knockout == 1,task_key] = 'Loss of P'
  data_plot[data_plot$even_base == 1 & data_plot$odd_base == 0 & data_plot$even_knockout == 0 & data_plot$odd_knockout == 0,task_key] = 'Loss P'
  data_plot[data_plot$even_base == 1 & data_plot$odd_base == 0 & data_plot$even_knockout == 0 & data_plot$odd_knockout == 1,task_key] = 'P Inversion'
  data_plot[data_plot$even_base == 1 & data_plot$odd_base == 0 & data_plot$even_knockout == 1 & data_plot$odd_knockout == 1,task_key] = 'Loss of P'
  data_plot[data_plot$even_base == 1 & data_plot$odd_base == 1 & data_plot$even_knockout == 0 & data_plot$odd_knockout == 0,task_key] = 'Loss NP'
  data_plot[data_plot$even_base == 1 & data_plot$odd_base == 1 & data_plot$even_knockout == 0 & data_plot$odd_knockout == 1,task_key] = 'Appear of P'
  data_plot[data_plot$even_base == 1 & data_plot$odd_base == 1 & data_plot$even_knockout == 1 & data_plot$odd_knockout == 0,task_key] = 'Appear of P'
  data_plot[data_plot$gestation_time_odd == 0 | data_plot$gestation_time_even == 0,task_key] = 'Required'
}

# Dilute specific categories into broader categories so they can actually be plotted
for(task in task_order){
  print(task)
  category_col = paste0(task, '_category')
  func_col = paste0(task, '_functionality')
  data_plot[func_col] = 'None'
  plastic_mask = data_plot[,category_col] %in% c('P Inversion', 'Loss of P')
  data_plot[plastic_mask, func_col] = rep('Plasticity Machinery', sum(plastic_mask))
  task_mask = data_plot[,category_col] %in% c('Loss P', 'Loss NP')
  data_plot[task_mask,func_col] = rep('Task Machinery', sum(task_mask))
  rep_mask = data_plot[,category_col] == 'Replication Machinery'
  data_plot[rep_mask,func_col] = rep('Replication Machinery', sum(rep_mask))
}

# Plot without vestigial sites
#ggplot(data_plot[data_plot$knockout_id > 0,], aes(x = tree_depth, y = knockout_id, fill = functionality)) + 
#  geom_raster() + 
#  scale_x_discrete(limits = c(0, max(data_plot$tree_depth)), expand = c(0,0)) +
#  scale_y_discrete(limits = c(1,100), expand = c(0,0)) + 
#  scale_fill_manual(values=color_map) + 
#  xlab('Step in lineage') + 
#  ylab('Locus') + 
#  labs(fill = 'Functionality')
  

# Propogate character and functionality to the next depth so we can look for vestigial sites
data_plot$stop_update = 0
data_plot$previous_char = ''
for(task in task_order){
  data_plot[,paste0('previous_', task, '_functionality')] = ''
}
max_id = max(data_plot$knockout_id)
for(knockout_id in unique(data_plot$knockout_id)){
  print(paste0('knockout: ', knockout_id, ' / ', max_id))
  birth_updates = data_plot[data_plot$knockout_id == knockout_id,]$update_born
  data_plot[data_plot$knockout_id == knockout_id,]$stop_update = 
    c(birth_updates[2:length(birth_updates)], 200000)
  original_chars = data_plot[data_plot$knockout_id == knockout_id,]$original_char
  data_plot[data_plot$knockout_id == knockout_id,]$previous_char = 
    c('', original_chars[1:length(original_chars)-1])
  for(task in task_order){
    functionalities = data_plot[data_plot$knockout_id == knockout_id, paste0(task, '_functionality')]
    data_plot[data_plot$knockout_id == knockout_id, paste0('previous_', task, '_functionality')] = 
    c('', functionalities[1:length(functionalities)-1])
  }
}

# Look for vestigial sites. Vestigial means that the site was used in a task, but it currently doesn't even though the instruction
#   has not changed since it last worked
for(depth in 1:max(data_plot$tree_depth)){#unique(data_plot$tree_depth)){
  if(depth %% 100 == 0){
    print(paste0('depth: ', depth, ' / ', max_depth))
  }
  for(task in task_order){
    func_col = paste0(task, '_functionality')
    prev_func_col = paste0('previous_', task, '_functionality')
    mask =  data_plot$tree_depth == depth &
            data_plot$original_char == data_plot$previous_char & 
            data_plot[,func_col] == 'None' & 
            data_plot[,prev_func_col] %in% c('Task Machinery', 'Previous Task Machinery')
    data_plot[mask,func_col] = 
      rep('Previous Task Machinery', sum(mask))
    if(depth < max(data_plot$tree_depth)){
      data_plot[data_plot$tree_depth == depth + 1, prev_func_col] = data_plot[data_plot$tree_depth == depth, func_col]
    }
  }
}

# Plot with vestigial sites
ggplot(data_plot[data_plot$knockout_id > 0,], 
       aes(xmin = update_born, xmax = stop_update, ymin = knockout_id, ymax = knockout_id + 1, fill = and_functionality)) + 
  geom_rect() + 
  scale_x_continuous(limits = c(-1, max(data_plot$stop_update)), expand = c(0,0)) +
  scale_y_discrete(limits = c(1,100), expand = c(0,0)) + 
  scale_fill_manual(values=color_map) + 
  xlab('Update') + 
  ylab('Locus') + 
  theme(legend.position = 'bottom') +
  labs(fill = 'Functionality')

# Summarize loci into even vs odd functionality
none_str = 'None'
task_str = 'Task Machinery'
plastic_str = 'Plasticity Machinery'
vestigial_str = 'Previous Task Machinery'
data_plot$odd_functionality = none_str
data_plot$even_functionality = none_str

# Odd
odd_task_mask = 
  (data_plot$not_functionality == task_str &  
     data_plot$and_functionality %in% c(task_str, none_str, vestigial_str, plastic_str) &  
     data_plot$or_functionality %in% c(task_str, none_str, vestigial_str, plastic_str)) |
  (data_plot$and_functionality == task_str &  
     data_plot$not_functionality %in% c(task_str, none_str, vestigial_str, plastic_str) &  
     data_plot$or_functionality %in% c(task_str, none_str, vestigial_str, plastic_str)) |
  (data_plot$or_functionality == task_str &  
     data_plot$and_functionality %in% c(task_str, none_str, vestigial_str, plastic_str) &  
     data_plot$not_functionality %in% c(task_str, none_str, vestigial_str, plastic_str)) 
data_plot[odd_task_mask,]$odd_functionality = rep(task_str, sum(odd_task_mask))
odd_vestigial_mask = 
  (data_plot$not_functionality == vestigial_str &  
     data_plot$and_functionality %in% c(vestigial_str, none_str) &  
     data_plot$or_functionality %in% c(vestigial_str, none_str)) |
  (data_plot$and_functionality == vestigial_str &  
     data_plot$not_functionality %in% c(vestigial_str, none_str) &  
     data_plot$or_functionality %in% c(vestigial_str, none_str)) |
  (data_plot$or_functionality == vestigial_str &  
     data_plot$and_functionality %in% c(vestigial_str, none_str) &  
     data_plot$not_functionality %in% c(vestigial_str, none_str)) 
data_plot[odd_vestigial_mask,]$odd_functionality = rep(vestigial_str, sum(odd_vestigial_mask))
odd_plastic_mask = 
  (data_plot$not_functionality == plastic_str &  
     data_plot$and_functionality %in% c(plastic_str, none_str, vestigial_str) &  
     data_plot$or_functionality %in% c(plastic_str, none_str, vestigial_str)) |
  (data_plot$and_functionality == plastic_str &  
     data_plot$not_functionality %in% c(plastic_str, none_str, vestigial_str) &  
     data_plot$or_functionality %in% c(plastic_str, none_str, vestigial_str)) |
  (data_plot$or_functionality == plastic_str &  
     data_plot$and_functionality %in% c(plastic_str, none_str, vestigial_str) &  
     data_plot$not_functionality %in% c(plastic_str, none_str, vestigial_str)) 
data_plot[odd_plastic_mask,]$odd_functionality = rep(plastic_str, sum(odd_plastic_mask))

# Even
even_task_mask = 
  (data_plot$nand_functionality == task_str &  
     data_plot$andnot_functionality %in% c(task_str, none_str, vestigial_str, plastic_str) &  
     data_plot$ornot_functionality %in% c(task_str, none_str, vestigial_str, plastic_str)) |
  (data_plot$andnot_functionality == task_str &  
     data_plot$nand_functionality %in% c(task_str, none_str, vestigial_str, plastic_str) &  
     data_plot$ornot_functionality %in% c(task_str, none_str, vestigial_str, plastic_str)) |
  (data_plot$ornot_functionality == task_str &  
     data_plot$andnot_functionality %in% c(task_str, none_str, vestigial_str, plastic_str) &  
     data_plot$nand_functionality %in% c(task_str, none_str, vestigial_str, plastic_str)) 
data_plot[even_task_mask,]$even_functionality = rep(task_str, sum(even_task_mask))
even_vestigial_mask = 
  (data_plot$nand_functionality == vestigial_str &  
     data_plot$andnot_functionality %in% c(vestigial_str, none_str) &  
     data_plot$ornot_functionality %in% c(vestigial_str, none_str)) |
  (data_plot$andnot_functionality == vestigial_str &  
     data_plot$nand_functionality %in% c(vestigial_str, none_str) &  
     data_plot$ornot_functionality %in% c(vestigial_str, none_str)) |
  (data_plot$ornot_functionality == vestigial_str &  
     data_plot$andnot_functionality %in% c(vestigial_str, none_str) &  
     data_plot$nand_functionality %in% c(vestigial_str, none_str)) 
data_plot[even_vestigial_mask,]$even_functionality = rep(vestigial_str, sum(even_vestigial_mask))
even_plastic_mask = 
  (data_plot$nand_functionality == plastic_str &  
     data_plot$andnot_functionality %in% c(plastic_str, none_str, vestigial_str) &  
     data_plot$ornot_functionality %in% c(plastic_str, none_str, vestigial_str)) |
  (data_plot$andnot_functionality == plastic_str &  
     data_plot$nand_functionality %in% c(plastic_str, none_str, vestigial_str) &  
     data_plot$ornot_functionality %in% c(plastic_str, none_str, vestigial_str)) |
  (data_plot$ornot_functionality == plastic_str &  
     data_plot$andnot_functionality %in% c(plastic_str, none_str, vestigial_str) &  
     data_plot$nand_functionality %in% c(plastic_str, none_str, vestigial_str)) 
data_plot[even_plastic_mask,]$even_functionality = rep(plastic_str, sum(even_plastic_mask))
  

# Plot odd or even functionality as a sanity check
# ggplot(data_plot[data_plot$knockout_id > 0,], 
#        aes(xmin = update_born, xmax = stop_update, ymin = knockout_id, ymax = knockout_id + 1, fill = even_functionality)) + 
#   geom_rect() + 
#   scale_x_continuous(limits = c(-1, max(data_plot$stop_update)), expand = c(0,0)) +
#   scale_y_discrete(limits = c(1,100), expand = c(0,0)) + 
#   scale_fill_manual(values=color_map) + 
#   xlab('Update') + 
#   ylab('Locus') + 
#   theme(legend.position = 'bottom') +
#   labs(fill = 'Functionality')

data_plot$high_level_functionality = 'Other'
data_plot$gestation_time_even = as.numeric(data_plot$gestation_time_even)
data_plot$gestation_time_odd = as.numeric(data_plot$gestation_time_odd)
data_plot$base_gestation_time_even = as.numeric(data_plot$base_gestation_time_even)
data_plot$base_gestation_time_odd = as.numeric(data_plot$base_gestation_time_odd)
# Truly none
mask = data_plot$odd_functionality == none_str & data_plot$even_functionality == none_str
data_plot[mask,]$high_level_functionality = rep('None', sum(mask))
# Replication machinery
mask = data_plot$gestation_time_odd > (data_plot$base_gestation_time_odd + 2) | data_plot$gestation_time_even > (data_plot$base_gestation_time_even + 2)
data_plot[mask,]$high_level_functionality = rep('Replication Machinery', sum(mask))
# Task Machinery
mask = data_plot$odd_functionality == task_str & data_plot$even_functionality == none_str
data_plot[mask,]$high_level_functionality = rep('Odd Task Machinery', sum(mask))
mask = data_plot$odd_functionality == none_str & data_plot$even_functionality == task_str
data_plot[mask,]$high_level_functionality = rep('Even Task Machinery', sum(mask))
mask = data_plot$odd_functionality == task_str & data_plot$even_functionality == task_str
data_plot[mask,]$high_level_functionality = rep('Both Task Machinery', sum(mask))
# Vestigials
mask = data_plot$odd_functionality == vestigial_str & data_plot$even_functionality == none_str
data_plot[mask,]$high_level_functionality = rep('Vestigial Odd', sum(mask))
mask = data_plot$odd_functionality == none_str & data_plot$even_functionality == vestigial_str
data_plot[mask,]$high_level_functionality = rep('Vestigial Even', sum(mask))
mask = data_plot$odd_functionality == vestigial_str & data_plot$even_functionality == vestigial_str
data_plot[mask,]$high_level_functionality = rep('Both Vestigial', sum(mask))
# Recycling
mask = data_plot$odd_functionality == task_str & data_plot$even_functionality == vestigial_str
data_plot[mask,]$high_level_functionality = rep('Odd Recycled Even', sum(mask))
mask = data_plot$odd_functionality == vestigial_str & data_plot$even_functionality == task_str
data_plot[mask,]$high_level_functionality = rep('Even Recycled Odd', sum(mask))
# Plasticity
mask = data_plot$odd_functionality == plastic_str & data_plot$even_functionality == none_str
data_plot[mask,]$high_level_functionality = rep('Odd Plastic Machinery', sum(mask))
mask = data_plot$odd_functionality == none_str & data_plot$even_functionality == plastic_str
data_plot[mask,]$high_level_functionality = rep('Even Plastic Machinery', sum(mask))
mask = data_plot$odd_functionality == plastic_str & data_plot$even_functionality == plastic_str
data_plot[mask,]$high_level_functionality = rep('Both Plastic Machinery', sum(mask))
# Task + plastic
mask = data_plot$odd_functionality == task_str & data_plot$even_functionality == plastic_str
data_plot[mask,]$high_level_functionality = rep('Odd task, even plastic', sum(mask))
mask = data_plot$odd_functionality == plastic_str & data_plot$even_functionality == task_str
data_plot[mask,]$high_level_functionality = rep('Even task, odd plastic', sum(mask))
# Plastic + vestigial
mask = data_plot$odd_functionality == plastic_str & data_plot$even_functionality == vestigial_str
data_plot[mask,]$high_level_functionality = rep('Odd plastic, even vestigial', sum(mask))
mask = data_plot$odd_functionality == vestigial_str & data_plot$even_functionality == plastic_str
data_plot[mask,]$high_level_functionality = rep('Even plastic, odd vestigial', sum(mask))
# Required
mask = data_plot$gestation_time_even == 0 | data_plot$gestation_time_odd == 0
data_plot[mask,]$high_level_functionality = rep('Required', sum(mask))

# Define all the colors
high_level_color_map = c(
  'Other' = '#ff00ff',
  'Required' = '#000000',
  'Replication Machinery' = '#666666',
  'None' = '#aaaaaa',
  'Odd Task Machinery' = '#1155cc',
  'Even Task Machinery' = '#cc0000',
  'Both Task Machinery' = '#8e7cc3',
  'Odd Recycled Even' = '#8ccabf', 
  'Even Recycled Odd' = '#f6b26b',
  'Vestigial Odd' = '#a4c2f4',
  'Vestigial Even' = '#ea9999',
  'Odd Plastic Machinery' = '#1c4587',
  'Even Plastic Machinery' = '#990000',
  'Both Plastic Machinery' = '#351c75',
  'Both Vestigial' = '#c27ba0',
  'Odd task, even plastic' = '#20ffce',
  'Even task, odd plastic' = '#f8eb5d',
  'Odd plastic, even vestigial' = '#00ad82',
  'Even plastic, odd vestigial' = '#c1b724'
)
# Define order colors will appear in bar plots
high_level_color_order = c(
  'Other',
  'Required',
  'Replication Machinery',
  'None',
  'Odd Task Machinery',
  'Even Task Machinery',
  'Both Task Machinery',
  'Vestigial Odd',
  'Vestigial Even',
  'Both Vestigial',
  'Odd Recycled Even', 
  'Even Recycled Odd',
  'Odd Plastic Machinery',
  'Even Plastic Machinery',
  'Both Plastic Machinery',
  'Odd task, even plastic',
  'Even task, odd plastic',
  'Odd plastic, even vestigial',
  'Even plastic, odd vestigial'
)

# Plot and save high level summary
ggplot(data_plot[data_plot$knockout_id > 0,], 
       aes(xmin = update_born, xmax = stop_update, ymin = knockout_id, ymax = knockout_id + 1, fill = high_level_functionality)) + 
  geom_rect() + 
  scale_x_continuous(limits = c(-1, max(data_plot$stop_update)), expand = c(0,0)) +
  scale_y_discrete(limits = c(1,100), expand = c(0,0)) + 
  scale_fill_manual(values=high_level_color_map) + 
  xlab('Update') + 
  ylab('Locus') + 
  theme(legend.position = 'bottom') +
  labs(fill = 'Functionality') + 
  ggsave(paste0(output_path, 'high_level_functionality.pdf'), units = 'in', width = 20, height=10)

# Calculate entropy for each site
data_entropy = data_plot[data_plot$knockout_id != 0,]
entropy_vec = rep(NA, length(unique(data_entropy$knockout_id)))
for(knockout_id in unique(data_entropy$knockout_id)){
  occurences = table(data_entropy[data_entropy$knockout_id == knockout_id,]$high_level_functionality)
  probs = occurences / sum(occurences)
  entropy_vec[knockout_id] = -1 * sum(probs * log2(probs))
}
entropy_data = data.frame(locus_idx = 1:length(entropy_vec), entropy = entropy_vec)

# Summarize functionality at each depth
data_grouped_depth = dplyr::group_by(data_plot[data_plot$knockout_id != 0,], tree_depth, high_level_functionality)
data_summary_depth = dplyr::summarize(data_grouped_depth, n = n())
data_summary_depth$pct = data_summary_depth$n / 100
data_summary_depth$high_level_functionality = as.character(data_summary_depth$high_level_functionality)

# Summarize functionality across all depths
data_grouped_total = dplyr::group_by(data_plot[data_plot$knockout_id != 0,], high_level_functionality)
data_summary_total = dplyr::summarize(data_grouped_total, n = n())
data_summary_total$pct = data_summary_total$n / sum(data_summary_total$n)
data_summary_total$high_level_functionality = as.character(data_summary_total$high_level_functionality)

# Write out all data!
write.csv(entropy_data,       paste0(output_path, 'entropy_data.csv'))
write.csv(data_summary_depth, paste0(output_path, 'summary_depth.csv'))
write.csv(data_summary_total, paste0(output_path, 'summary_total.csv'))
write.csv(data_plot,          paste0(output_path, 'cleaned_data.csv'))

# Plot functionalities as percentage of ALL sites (current and past)
#data_summary_total$high_level_functionality = factor(data_summary_total$high_level_functionality, levels = high_level_color_order)
#ggplot(data_summary_total, aes(x = as.factor(high_level_functionality), y = pct, fill = as.factor(high_level_functionality))) + 
#  geom_col() + 
#  geom_text(aes(y = pct + 0.03, label = round(pct, 3))) +
#  scale_fill_manual(values = high_level_color_map) + 
#  scale_y_continuous(limits = c(0,1)) +
#  theme(legend.position = 'none') + 
#  xlab('Functionality') + 
#  ylab('Percentage of all sites across time') + 
#  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1))

# Plot functionalities as percentage of sites at specific depths
#data_summary_depth$high_level_functionality = factor(data_summary_depth$high_level_functionality, levels = high_level_color_order)
#max_depth = max(data_summary_depth$tree_depth)
#ggplot(data_summary_depth[data_summary_depth$tree_depth %in% c(0,1000,2000,3000,max_depth),], aes(x = as.factor(high_level_functionality), y = pct, fill = as.factor(high_level_functionality))) + 
#  geom_col() + 
#  geom_text(aes(y = pct + 0.03, label = round(pct, 3))) +
#  scale_fill_manual(values = high_level_color_map) + 
#  scale_y_continuous(limits = c(0,1.03)) +
#  theme(legend.position = 'none') + 
#  xlab('Functionality') + 
#  ylab('Percentage of all sites across time') + 
#  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1)) + 
#  facet_wrap(vars(tree_depth))
