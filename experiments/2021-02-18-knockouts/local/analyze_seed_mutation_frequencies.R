# Summary: Investigate the mutations that occured along a lineage
  # Look for patterns such as contingency loci, specific instructions that were mutated to/from
rm(list = ls())

# Load necessary libraries
library(ggplot2)
library(dplyr)

# Iterate through each replicate (assuming all trimmed_data files have been downloaded)
for(filename in list.files('./data/trimmed_data/')){
  print(filename)
  seed = strsplit(strsplit(filename, '\\.')[[1]][1], '_')[[1]][3]
  
  # Load and prep data
  df = read.csv(paste0('./data/trimmed_data/', filename))
  df = df[df$is_mutation,]
  
  # Plot by site to see if any particular sites are more highly likely to be mutated
  df_grouped = dplyr::group_by(df, knockout_id)
  df_summary = dplyr::summarize(df_grouped, count = dplyr::n())
  text_offset = max(df_summary$count) * 0.05
  ggplot(df_summary, aes(x = knockout_id, y = count)) + 
    geom_col() + 
    geom_text(aes(y = -2, label = count, angle = 90)) +
    ggsave(paste0('./plots/mut_sites_', seed, '.png'), units = 'in', width = 16, height = 10)

  # Plot by the instruction *before* the mutation, to see if certain instruction were "targeted"
  df_grouped = dplyr::group_by(df, original_char)
  df_summary = dplyr::summarize(df_grouped, count = dplyr::n())
  ggplot(df_summary, aes(x = as.factor(original_char), y = count)) + 
    geom_col() + 
    geom_text(aes(y = count + 20, label = count, angle = 90)) +
    ggsave(paste0('./plots/mut_pre_insts_', seed, '.png'), units = 'in', width = 16, height = 10)

  # Plot by the instruction *after* the mutation, to see if certain insts. were selected more often
  df_grouped = dplyr::group_by(df, previous_char)
  df_summary = dplyr::summarize(df_grouped, count = dplyr::n())
  ggplot(df_summary, aes(x = as.factor(previous_char), y = count)) + 
    geom_col() + 
    geom_text(aes(y = count + 20, label = count, angle = 90)) +
    ggsave(paste0('./plots/mut_post_insts_', seed, '.png'), units = 'in', width = 16, height = 10)
}
