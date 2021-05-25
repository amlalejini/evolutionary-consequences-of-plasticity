rm(list = ls())

library(ggplot2)
library(dplyr)
library(ggridges)


df = read.csv('./vestigial_summary.csv')
df$treatment = 'STATIC'
df[df$environment == 'chg-u100' & df$sensors == 0,]$treatment = 'PLASTIC'
df[df$environment == 'chg-u100' & df$sensors == 1,]$treatment = 'NON-PLASTIC'

ggplot(df, aes(y = as.factor(treatment), x = vestigial_frac)) +
  geom_density_ridges2(position = position_nudge(y = 0.4), scale = 0.35) +
  geom_boxplot(width = 0.2) + 
  geom_jitter(height = 0.2) +
  coord_flip()
  
