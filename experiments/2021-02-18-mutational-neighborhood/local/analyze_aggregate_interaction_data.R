rm(list = ls())

# Load necessary libaries
library(ggplot2)

# Load and prep data
df_func = read.csv('./architecture/data/categorized_functionality_data_flat.csv')
df_mut = read.csv('./data/aggregated_mutant_data.csv')
df_combined = merge(df_func, df_mut, by = 'seed')
df_combined$treatment_factor = factor(df_combined$treatment, levels = c('STATIC', 'NON-PLASTIC', 'PLASTIC'))

# Plotting variables
color_map = c(
  'STATIC' = '#b2df8a',
  'PLASTIC' = '#1f78b4',
  'NON-PLASTIC' = '#a6cee3'
)

# Plot the fraction of one-step mutants that change phenotype by the number of task-encoding sites
# Used to see if there is a relationship between task-encoding sites and mutational volatility
ggplot(df_combined, aes(x = count_task, y = one_step_diff_pheno_frac, color = treatment_factor)) + 
  geom_smooth(method = "lm", se = FALSE) + 
  geom_point() + 
  scale_color_manual(values = color_map) + 
  xlab('Number of sites encoding tasks') + 
  ylab('Frac of one-step mutants that change phenotype')  + 
  labs(color = 'Condition') + 
  ggsave('./plots/frac_mut_pheno_changes_by_task_sites.png', units = 'in', height = 6, width = 8) +
  ggsave('./plots/frac_mut_pheno_changes_by_task_sites.pdf', units = 'in', height = 6, width = 8)


# Prep data further by adding in architecture data
df_architecture = read.csv('./data/aggregated_mutant_functionality_data.csv')
df_combined = merge(df_combined, df_architecture, by = 'seed')
df_combined$treatment_factor = factor(df_combined$treatment, levels = c('STATIC', 'NON-PLASTIC', 'PLASTIC'))


# Plot the fraction of "reverting" two step mutations by the number of vestigial sites
# Used to see if there is a relationship between the two
ggplot(df_combined, aes(x = count_vestigial, y = mean_two_step_reversion_frac__viable, color = treatment_factor)) + 
  geom_smooth(method = "lm", se = F) + 
  geom_point() + 
  scale_color_manual(values = color_map) + 
  xlab('Number of vestigial loci') + 
  ylab('Frac of two-step mutants that revert phenotype')  + 
  labs(color = 'Condition') + 
  ggsave('./plots/frac_two_step_reversions_by_vestigial_sites.png', units = 'in', height = 6, width = 8) +
  ggsave('./plots/frac_two_step_reversions_by_vestigial_sites.pdf', units = 'in', height = 6, width = 8)



# 
#ggplot(df_combined[df_combined$mean_count_changes  / df_combined$count_task < 6,], aes(x = treatment_factor, y = mean_count_changes / count_task, fill = treatment_factor)) + 
#  geom_boxplot() + 
#  scale_fill_manual(values = color_map) + 
#  xlab('Number of sites encoding tasks') + 
#  ylab('Frac of one-step mutants that change phenotype')  + 
#  labs(color = 'Condition')
