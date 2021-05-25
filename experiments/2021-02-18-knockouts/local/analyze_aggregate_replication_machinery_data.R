# Summary: Simply plots the fraction of sites that encode for replication machinery
rm(list = ls())

# Load necessary libraries
library(ggplot2)
library(ggridges)

# Load and prep the data
df = read.csv('./replication_frac_summary.csv')
df$treatment = 'STATIC'
df[df$environment == 'chg-u100' & df$sensors == 0,]$treatment = 'PLASTIC'
df[df$environment == 'chg-u100' & df$sensors == 1,]$treatment = 'NON-PLASTIC'
trt_order = c('STATIC', 'NON-PLASTIC', 'PLASTIC')
df$treatment_factor = factor(df$treatment, levels = trt_order)

# Use the right colors!
color_map = c(
  'STATIC' = '#b2df8a',
  'PLASTIC' = '#1f78b4',
  'NON-PLASTIC' = '#a6cee3'
)

# Plot!
ggplot(df, aes(x = replication_frac, y = treatment_factor, fill = as.factor(treatment))) + 
  geom_density_ridges2(position = position_nudge(y = 0.12), scale = 0.6) + 
  #geom_boxplot(width = 0.075, alpha = 0.3) + 
  geom_jitter(aes(color = as.factor(treatment)), position = position_jitter(height = 0.1), size = 0.5) + 
  scale_color_manual(values = color_map) + 
  scale_fill_manual(values = color_map) + 
  #scale_x_continuous(limits = c(0,1)) +
  xlab('Fraction of X loci') + 
  ylab('Condition') + 
  theme_classic() +
  theme(legend.position = 'none') + 
  ggsave('replication_frac.png', units = 'in', width = 10, height = 6)
