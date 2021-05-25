# Summary: Plot how long it takes on average for a site to change function in each replicate
  # For example: Site 12 starts phase 2 as a ENV-A task encoding site, after 200 updates it changes
  #     to a vestigial site for ENV-A tasks. This would contribute a 200 to the mean 
rm(list = ls())
# Load necessary libraries
library(ggplot2)
library(ggridges)

# Load and prep data
df = read.csv('./architecture_functionality_summary.csv')
df$treatment = 'STATIC'
df[df$environment == 'chg-u100' & df$sensors == 0,]$treatment = 'PLASTIC'
df[df$environment == 'chg-u100' & df$sensors == 1,]$treatment = 'NON-PLASTIC'
trt_order = c('STATIC', 'NON-PLASTIC', 'PLASTIC')
df$treatment_factor = factor(df$treatment, levels = trt_order)

# Plotting variables
color_map = c(
  'STATIC' = '#b2df8a',
  'PLASTIC' = '#1f78b4',
  'NON-PLASTIC' = '#a6cee3'
)

# Plot the true mean of time between function changes
ggplot(df, aes(x = full_mean_length, y = treatment_factor, fill = as.factor(treatment))) + 
  geom_density_ridges2(position = position_nudge(y = 0.12)) + 
  #geom_boxplot(width = 0.1) + 
  geom_jitter(aes(color = as.factor(treatment)), position = position_jitter(height = 0.1), size = 0.5) + 
  scale_color_manual(values = color_map) + 
  scale_fill_manual(values = color_map) + 
  xlab('Average time (in updates) between site functionality change') + 
  ylab('Condition') + 
  theme_classic() +
  theme(legend.position = 'none') + 
  ggsave('avg_time_between_func_changes.png', units = 'in', width = 10, height = 6)

# Plot the true weighted of time between function changes (was confused by the weighting, should be the same as the above plot)
#ggplot(df, aes(x = weighted_mean, y = treatment_factor, fill = as.factor(treatment))) + 
#  geom_density_ridges2(position = position_nudge(y = 0.12), scale = 0.6) + 
#  #geom_boxplot(width = 0.05, alpha = 0.3) + 
#  geom_jitter(aes(color = as.factor(treatment)), position = position_jitter(height = 0.1), size = 0.5) + 
#  scale_color_manual(values = color_map) + 
#  scale_fill_manual(values = color_map) + 
#  #xlab('Average time (in updates) between site functionality change') + 
#  ylab('Condition') + 
#  theme_classic() +
#  theme(legend.position = 'none') + 
#  ggsave('avg_time_between_func_changes_weighted_mean.png', units = 'in', width = 10, height = 6)
