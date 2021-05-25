# Summary: Looks at the fraction of sites in each replicate that serve a specific function
#   Example functions: Replication, ENV-A tasks, vestigial machinery, etc.
rm(list = ls())

# Load necessary libraries
library(ggplot2)
library(dplyr)
source('/research/tools/RainCloudPlots/tutorial_R/R_rainclouds.R')

# Load in aggregate data
data_summary = read.csv('summary_depth.csv')
data_summary = data_summary[!is.na(data_summary$seed),]
data_summary$treatment = 'STATIC'
data_summary[data_summary$environment != 'ALL-u0',]$treatment = 'NON-PLASTIC'
data_summary[data_summary$environment != 'ALL-u0' & data_summary$sensors == 0,]$treatment = 'PLASTIC'
data_summary$treatment_factor = factor(data_summary$treatment, levels = c('STATIC', 'NON-PLASTIC', 'PLASTIC'))
data_summary$hl_func_factor = factor(data_summary$high_level_functionality, levels = high_level_color_order)

# Plotting vars
color_map = c(
  'STATIC' = '#a6cee3',
  'NON-PLASTIC'= '#1f78b4',
  'PLASTIC' = '#b2df8a'
)

# Define all the colors
high_level_color_map = c(
  'Other' = '#666666',
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
  'Both Vestigial' = '#c27ba0'
)
# Define order colors will appear in bar plots
high_level_color_order = c(
  'Other',
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
  'Both Plastic Machinery'
)

# Grab the replicate id (as seed_offset) within the treatment
data_summary$seed_offset = 0
for(environment in unique(data_summary$environment)){
  for(sensors in unique(data_summary[data_summary$environment == environment,]$sensors)){
    mask = data_summary$environment == environment & data_summary$sensors == sensors
    seed_basis = min(data_summary[mask,]$seed)
    data_summary[mask,]$seed_offset = data_summary[mask,]$seed - seed_basis
  }
}

# Plot the fraction of sites for each replicate that coded for 'None' (i.e., did nothing of note)
ggplot(data_summary[data_summary$high_level_functionality == 'None',], aes(x = environment, y = pct)) + 
  geom_flat_violin(position = position_nudge(x = .2, y = 0),adjust =1)+
  geom_point(position = position_jitter(width = .15), size = .25)+
  coord_flip()+
  facet_grid(cols = vars(sensors))

# Plot the fraction of sites of each replicate that served each functionality
selected_env_mask = data_summary$environment %in% c('ALL-u0', 'chg-u100')
ggplot(data_summary[selected_env_mask,], aes(x = treatment_factor, y = pct, fill = treatment_factor, color = treatment_factor)) + 
  geom_flat_violin(position = position_nudge(x = .2, y = 0),adjust =1)+
  geom_point(position = position_jitter(width = .15), size = .25)+
  coord_flip()+
  facet_grid(cols = vars(hl_func_factor))+
  scale_fill_manual(values = color_map) +
  scale_color_manual(values = color_map) + 
  xlab('Condition') + 
  theme_classic() +
  theme(legend.position = 'none') + 
  ggsave('depth_breakdown.png', units = 'in', width = 20, height = 4)


# Plot the same thing, but with just boxplots
ggplot(data_summary[selected_env_mask,], aes(x = hl_func_factor, y = pct, fill = treatment_factor)) +
  geom_boxplot() + 
  ggsave('depth_breakdown_boxplots.png', units = 'in', width = 10, height = 4)
  
  
  
