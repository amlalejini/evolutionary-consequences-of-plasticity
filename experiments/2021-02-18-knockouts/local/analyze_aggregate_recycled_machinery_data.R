# Summary: Simply plot the fraction of sites that are recycled
#   Recycled sites - Vestigial for ENV-A tasks and actively code for ENV-B or vice versa
#   Vestigial - Previously encoded for a task, but a mutation elsewhere broke the task 
#     - But the instruction at this site did not change
rm(list = ls())

# Load necessary libraries
library(ggplot2)
library(ggridges)

# Load and prep data
df = read.csv('./recycled_frac_summary.csv')
df$treatment = 'STATIC'
df[df$environment == 'chg-u100' & df$sensors == 0,]$treatment = 'PLASTIC'
df[df$environment == 'chg-u100' & df$sensors == 1,]$treatment = 'NON-PLASTIC'
trt_order = c('STATIC', 'NON-PLASTIC', 'PLASTIC')
df$treatment_factor = factor(df$treatment, levels = trt_order)

# Use the correct colors!
color_map = c(
  'STATIC' = '#b2df8a',
  'PLASTIC' = '#1f78b4',
  'NON-PLASTIC' = '#a6cee3'
)

ggplot(df, aes(x = recycled_frac, y = treatment_factor, fill = as.factor(treatment))) + 
  geom_density_ridges2(position = position_nudge(y = 0.12), scale = 0.6) + 
  #geom_boxplot(width = 0.05, alpha = 0.3) + 
  geom_jitter(aes(color = as.factor(treatment)), position = position_jitter(height = 0.1), size = 0.5) + 
  scale_color_manual(values = color_map) + 
  scale_fill_manual(values = color_map) + 
  #scale_x_continuous(limits = c(0,1)) +
  xlab('Fraction of X loci') + 
  ylab('Condition') + 
  theme_classic() +
  theme(legend.position = 'none') + 
  ggsave('recycled_frac.png', units = 'in', width = 6, height = 6) +
  ggsave('recycled_frac.pdf', units = 'in', width = 6, height = 6)
