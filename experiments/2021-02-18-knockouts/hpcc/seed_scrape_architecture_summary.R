rm(list = ls())

library(ggplot2)
library(dplyr)

# Handle command line args
arg_vec = commandArgs(trailingOnly = T) 
if(length(arg_vec)!= 1){
    print('Error! Expected exactly 1 argument: path of directory where we\'ll both load the input and save the output')
    quit()
}
data_path = arg_vec[1]

df = read.csv(paste0(data_path, '/cleaned_data.csv'))

# Only look at knockouts, not the original genotypes
data_working = df[df$knockout_id != 0,]

max_update = 200000

# Calculate the previous function of each site at each point in time
data_working = data_working[order(data_working$tree_depth),]
data_working$previous_high_level_functionality = NA
for(seed in unique(data_working$seed)){
  seed_mask = data_working$seed == seed
  for(knockout_id in unique(data_working[seed_mask,]$knockout_id)){
    cat(knockout_id, ' ')
    mask = seed_mask & data_working$knockout_id == knockout_id
    high_level_funcs = as.character(data_working[mask,]$high_level_functionality)
    data_working[mask,]$previous_high_level_functionality = c(NA, high_level_funcs[1:(length(high_level_funcs)-1)])
  }
  cat('\n')
}

# Determine which entries were the place of a mutation or a function change
rm(mask)
mask = is.na(data_working$previous_high_level_functionality) | 
  (data_working$previous_high_level_functionality != data_working$high_level_functionality)
data_working$is_function_change = F
data_working[mask,]$is_function_change = T
mask = (as.character(data_working$previous_char) != as.character(data_working$original_char)) & data_working$tree_depth != 0
data_working$is_mutation = F
data_working[mask,]$is_mutation = T
rm(mask)
data_trimmed = data_working[data_working$is_function_change | data_working$is_mutation,]

# Calculate the update where a function truly ends, even if it lasts through several lineage steps
data_trimmed$true_stop_update = NA
for(seed in unique(data_trimmed$seed)){
  seed_mask = data_trimmed$seed == seed
  for(knockout_id in unique(data_trimmed[seed_mask,]$knockout_id)){
    mask = seed_mask & data_trimmed$knockout_id == knockout_id & data_trimmed$is_function_change
    if(sum(mask) == 1){
      data_trimmed[mask,]$true_stop_update = max_update
    }
    else{
      start_updates = data_trimmed[mask,]$update_born
      data_trimmed[mask,]$true_stop_update = c(start_updates[2:length(start_updates)], max_update)
    }
  }
}

# Pull out how long the function of each site lasted
data_trimmed$high_level_length = NA
data_trimmed[data_trimmed$is_function_change,]$high_level_length = 
  data_trimmed[data_trimmed$is_function_change,]$true_stop_update - data_trimmed[data_trimmed$is_function_change,]$update_born
data_tmp = data.frame(data = matrix(nrow = 0, ncol = 6))
colnames(data_tmp) = c('seed', 'knockout_id', 'mean_length', 'median_length', 'count', 'unique_count')
for(seed in unique(data_trimmed$seed)){
  seed_mask = data_trimmed$seed == seed
  for(knockout_id in unique(data_trimmed[seed_mask,]$knockout_id)){
    mask = seed_mask & data_trimmed$knockout_id == knockout_id & data_trimmed$is_function_change
    lengths = data_trimmed[mask,]$high_level_length
    data_tmp[nrow(data_tmp) + 1,] = c(seed, knockout_id, mean(lengths), median(lengths), length(lengths), length(unique(as.character(data_trimmed[mask,]$high_level_functionality))))
  }
}

# Summarize data
mean_of_mean_lengths = mean(data_tmp$mean_length)
mean_of_median_lengths = mean(data_tmp$median_length)
median_of_mean_lengths = median(data_tmp$mean_length)
median_of_median_lengths = median(data_tmp$median_length)
full_mean = mean(data_trimmed[data_trimmed$is_function_change,]$high_level_length)
full_median = median(data_trimmed[data_trimmed$is_function_change,]$high_level_length)


data_trimmed = data_trimmed[order(data_trimmed$high_level_length),]
data_grouped = dplyr::group_by(data_trimmed, high_level_length)
data_summary = dplyr::summarize(data_grouped, count = dplyr::n())

data_summary = data_summary[!is.na(data_summary$high_level_length),]
data_summary$weight = data_summary$high_level_length * data_summary$count
data_summary$weighted_val = data_summary$high_level_length * data_summary$weight
weighted_avg = sum(data_summary$weighted_val) / sum(data_summary$weight)


# Save out a summary of this data
df_summary = data.frame(data = matrix(nrow = 0, ncol = 10))
colnames(df_summary) = c('seed', 'environment', 'sensors', 'full_mean_length', 'full_median_length', 
                         'mean_of_mean_lengths', 'mean_of_median_lengths', 'median_of_mean_lengths',
                         'median_of_median_lengths', 'weighted_mean')
df_summary[nrow(df_summary) + 1,] = 
  c(data_trimmed$seed[1], as.character(data_trimmed$environment)[1], data_trimmed$sensors[1],
      full_mean, full_median, mean_of_mean_lengths, mean_of_median_lengths, median_of_mean_lengths, median_of_median_lengths, weighted_avg)
write.csv(df_summary, paste0(data_path, '/architecture_functionality_data.csv'))
write.csv(data_trimmed, paste0(data_path, '/trimmed_data.csv'))
