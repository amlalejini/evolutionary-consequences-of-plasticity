# Summary: Analyzes the Shannon entropy of each site in the genome along a lineage
  # Note: this was scrapped pretty early on, as it didn't change much. 
  #   For example: A site alternating every 100 updates between function A and B would register the 
  #   same as site that toggles once at 100,000 updates
rm(lits = ls())

# Load necessary libraries
library(ggplot2)
library(dplyr)
source('/research/tools/RainCloudPlots/tutorial_R/R_rainclouds.R')

# Load in data
data_entropy = read.csv('entropy_data.csv')
data_entropy = data_entropy[!is.na(data_entropy$environment),]
# Create a few new colors to make plotting easier
data_entropy$environment = factor(data_entropy$environment, levels = c('ALL-u0', 'A-u0', 'B-u0', 'chg-u100', 'chg-u300'))
data_entropy$treatment = 'STATIC'
data_entropy[data_entropy$environment != 'ALL-u0',]$treatment = 'NON-PLASTIC'
data_entropy[data_entropy$environment != 'ALL-u0' & data_entropy$sensors == 0,]$treatment = 'PLASTIC'
color_map = c(
  'STATIC' = '#a6cee3',
  'NON-PLASTIC'= '#1f78b4',
  'PLASTIC' = '#b2df8a'
)

# Plot raw data
ggplot(data_entropy, aes(x = 1, y = entropy)) + 
  geom_flat_violin(position = position_nudge(x = .2, y = 0),adjust =1)+
  geom_point(position = position_jitter(width = .15), size = .25, alpha = 0.1)+
  coord_flip()+
  facet_grid(cols = vars(environment), rows = vars(sensors))


# Plot only the three main controls in designated colors
selected_env_mask = data_entropy$environment %in% c('ALL-u0', 'chg-u100')
data_entropy$treatment_factor = factor(data_entropy$treatment, levels = c('STATIC', 'NON-PLASTIC', 'PLASTIC'))
ggp = ggplot(data_entropy[selected_env_mask,], aes(x = treatment_factor, y = entropy, fill = treatment_factor)) + 
  geom_flat_violin(position = position_nudge(x = .2, y = 0),adjust =1)+
  coord_flip() +
  scale_fill_manual(values = color_map) +
  scale_color_manual(values = color_map) + 
  xlab('Condition') + 
  ylab('Entropy') +
  theme_classic() +
  theme(legend.position = 'none')
# Save without boxplots
ggp + 
  geom_point(aes(color = treatment_factor), position = position_jitter(width = .15), size = .25, alpha = 0.2)+
  ggsave('./plots/entropy.png', units = 'in', width = 4, height = 6) 
# Save with boxplots
ggp +
  geom_boxplot(width = 0.1) +
  geom_point(aes(color = treatment_factor), position = position_jitter(width = .15), size = .25, alpha = 0.2)+
  ggsave('./plots/entropy_boxplot.png', units = 'in', width = 4, height = 6) 


# Summarize data by seed
data_grouped = dplyr::group_by(data_entropy, seed, environment, sensors, treatment)
data_summary = dplyr::summarize(data_grouped, 
                                entropy_mean = mean(entropy), 
                                entropy_sd = sd(entropy), 
                                entropy_max = max(entropy), 
                                entropy_min = min(entropy), 
                                entropy_median = median(entropy))
# Plot summarized data
data_summary$environment = factor(data_summary$environment, levels = c('ALL-u0', 'A-u0', 'B-u0', 'chg-u100', 'chg-u300'))
ggplot(data_summary, aes(x = 1, y = entropy_mean)) + 
  geom_flat_violin(position = position_nudge(x = .2, y = 0),adjust =1)+
  geom_point(position = position_jitter(width = .15), size = .25, alpha = 0.5)+
  coord_flip()+
  facet_grid(cols = vars(environment), rows = vars(sensors))

# Plot summarized data
selected_env_mask = data_summary$environment %in% c('ALL-u0', 'chg-u100')
data_summary$treatment_factor = factor(data_summary$treatment, levels = c('STATIC', 'NON-PLASTIC', 'PLASTIC'))
ggp = ggplot(data_summary[selected_env_mask,], aes(x = treatment_factor, y = entropy_mean, fill = treatment_factor)) + 
  geom_flat_violin(position = position_nudge(x = .2, y = 0),adjust =1)+
  coord_flip() +
  scale_fill_manual(values = color_map) +
  scale_color_manual(values = color_map) + 
  xlab('Condition') + 
  ylab('Average Entropy') +
  theme_classic() +
  theme(legend.position = 'none')
# Save without boxplots
ggp + 
  geom_point(aes(color = treatment_factor), position = position_jitter(width = .15), size = .5, alpha = 0.8)+
  ggsave('./plots/entropy_summary.png', units = 'in', width = 4, height = 6) 
# Save with boxplots
ggp +
  geom_boxplot(width = 0.1) +
  geom_point(aes(color = treatment_factor), position = position_jitter(width = .15), size = .5, alpha = 0.8)+
  ggsave('./plots/entropy_summary_boxplot.png', units = 'in', width = 4, height = 6) 

