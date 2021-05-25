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

task_vec = c('not', 'and', 'or', 'nand', 'andnot', 'ornot')
df_final = data_working[data_working$stop_update == max_update,]
df_plot = data.frame(data = matrix(nrow = 0, ncol = 3))
colnames(df_plot) = c('knockout_id', 'task', 'functionality')
required_mask = df_final$high_level_functionality == 'Required'
for(task in task_vec){
  df_final[,paste0(task, '_functionality')] = as.character(df_final[,paste0(task, '_functionality')])
  df_final[required_mask,paste0(task, '_functionality')] = 'Required'
  for(knockout_id in unique(df_final$knockout_id)){
    func = df_final[df_final$knockout_id == knockout_id,paste0(task, '_functionality')]
    df_plot[nrow(df_plot) + 1,] = c(knockout_id, task, func)
  }
}

# Define all the colors
color_map = c(
  'Required' = '#000000',
  'Replication Machinery' = '#666666',
  'None' = '#aaaaaa',
  'Task Machinery' = '#1155cc',
  'Previous Task Machinery' = '#a4c2f4',
  'Plasticity Machinery' = '#cc0000'
)
# Define order colors will appear in bar plots
color_order = c('None', 'Task Machinery', 'Previous Task Machinery', 'Plasticity Machinery', 'Required', 'Replication Machinery')

df_plot$knockout_id = as.numeric(df_plot$knockout_id)
df_plot$func_factor = factor(df_plot$functionality, levels = color_order)
df_plot$task_factor = factor(df_plot$task, levels = c('not', 'and', 'or', 'nand', 'andnot', 'ornot'))
ggplot(df_plot, aes(x = task_factor, y = knockout_id, fill = func_factor)) + 
  geom_raster() + 
  scale_fill_manual(values = color_map) + 
  scale_y_continuous(expand = c(0,0)) + 
  scale_x_discrete(expand = c(0,0)) +
  geom_vline(xintercept = which(df_plot$task == 'or')) +
  geom_vline(xintercept = c(3.5)) +
  ylab('Locus position') + 
  xlab('Task') + 
  labs(fill = 'Locus functionality') + 
  #theme(legend.position = 'bottom') + 
  #ggsave('locus_slice.png', units = 'in', width = 6, height = 10) +
  ggsave('locus_slice.pdf', units = 'in', width = 6, height = 10)
  
write.csv(df_plot, './locus_slice_data.csv')


## Define order colors will appear in bar plots
#color_order = c('None', 'Replication Machinery', 'Task Machinery', 'Previous Task Machinery', 'Plasticity Machinery')
#
#df_plot$func_factor = factor(df_plot$functionality, levels = color_order)
#ggplot(df_plot, aes(x = task_factor, y = knockout_id, fill = func_factor)) + 
#  geom_raster() + 
#  scale_fill_manual(values = color_map) + 
#  scale_y_continuous(expand = c(0,0)) + 
#  scale_x_discrete(expand = c(0,0)) +
#  ylab('Locus position') + 
#  xlab('Task') + 
#  labs(fill = 'Locus functionality') + 
#  theme(legend.position = 'bottom') +
#  coord_flip() +
#  ggsave('locus_slice_flip.png')


