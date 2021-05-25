# Summary: Examines the overlap between each pair of tasks
rm(list = ls())

# Load necessary libraries
library(ggplot2)
library(dplyr)

# Load and prep data
df = read.csv('./scraped_overlap_data.csv')
df = df[!is.na(df$fraction),]
data_grouped = dplyr::group_by(df, base_task, extra_task, environment, sensors)
data_summary = dplyr::summarize(data_grouped, frac_mean = mean(fraction), count = dplyr::n())
data_summary$sensors_str = 'No sensors'
data_summary[data_summary$sensors == 0,]$sensors_str = 'Sensors'
data_summary$treatment = 'STATIC'
data_summary[data_summary$environment == 'chg-u100' & data_summary$sensors == 0,]$treatment = 'PLASTIC'
data_summary[data_summary$environment == 'chg-u100' & data_summary$sensors == 1,]$treatment = 'NON-PLASTIC'
data_summary$base_task_factor = factor(data_summary$base_task, levels = c('not', 'and', 'or', 'nand', 'andnot', 'ornot'))
data_summary$extra_task_factor = factor(data_summary$extra_task, levels = c('not', 'and', 'or', 'nand', 'andnot', 'ornot'))


# Plot the fraction of base task sites that also encode for the other task
ggplot(data_summary, aes(x = extra_task_factor, base_task_factor, fill = frac_mean)) +
  geom_tile() + 
  geom_text(aes(label = round(frac_mean, 2)), color = 'white') + 
  scale_fill_continuous(limits = c(0,1)) + 
  #facet_grid(cols = vars(environment), rows = vars(sensors)) + 
  facet_wrap(vars(treatment), ncol = 2) +
  ylab('Base task') +
  xlab('Other task') + 
  labs(fill = 'Fraction of base task sites shared with other task') + 
  theme(legend.position = 'bottom') + 
  ggsave('overlap_treatment_summary.png', units = 'in', width = 8, height = 10)

# Compare the frac of overlapping sites to the same comparison in the static treatment 
data_summary$frac_mean_diff = 0
for(base_task in unique(data_summary$base_task)){
  for(extra_task in unique(data_summary$extra_task)){
    if(base_task == extra_task){
      next
    }
    static_frac = data_summary[data_summary$base_task == base_task & data_summary$extra_task == extra_task & data_summary$environment == 'ALL-u0',]$frac_mean
    for(env in unique(data_summary$environment)){
      env_mask = data_summary$base_task == base_task & data_summary$extra_task == extra_task & data_summary$environment == env
      for(sensors in unique(data_summary[env_mask,]$sensors)){
        mask = env_mask & data_summary$sensors == sensors
        data_summary[mask,]$frac_mean_diff = data_summary[mask,]$frac_mean - static_frac
      }
    }
  }
}

# Plot the difference between the overlap for each treatment and the overlap for the STATIC
to_plot = data_summary[data_summary$environment != 'ALL-u0',]
ggplot(to_plot, aes(x = extra_task_factor, base_task_factor, fill = frac_mean_diff)) +
  geom_tile() + 
  geom_text(aes(label = round(frac_mean_diff, 2)), color = 'black') + 
  #scale_fill_continuous(limits = c(-1,1)) + 
  scale_fill_gradient2(limits = c(-1,1)) +
  facet_grid(cols = vars(sensors_str), rows = vars(environment)) + 
  ylab('Base task') +
  xlab('Other task') + 
  ggsave('overlap_treatment_diff.png', units = 'in', width = 10, height = 5)
