# Summary: Analyze and plot the number of sites serving each function
rm(list = ls())

# Load the necessary libraries
library(ggplot2)
library(rstatix)
library(ggsignif)
library(scales)
library(cowplot)
library(RColorBrewer)
library(Hmisc)
library(boot)
source("https://gist.githubusercontent.com/benmarwick/2a1bb0133ff568cbe28d/raw/fb53bd97121f7f9ce947837ef1a4c65a73bffb3f/geom_flat_violin.R")

# Load and prep the data
df = read.csv('./architecture/data/aggregated_high_level_functionality_summary.csv')
df$treatment = 'STATIC'
df[df$environment == 'chg-u100',]$treatment = 'PLASTIC'
df[df$environment == 'chg-u100' & df$sensors == T,]$treatment = 'NON-PLASTIC'
df$treatment_factor = factor(df$treatment, levels = c('STATIC', 'NON-PLASTIC', 'PLASTIC'))

# Plotting variables
theme_set(theme_cowplot())
cb_palette <- "Paired"
alpha <- 0.05
color_map = c(
  'STATIC' = '#b2df8a',
  'PLASTIC' = '#1f78b4',
  'NON-PLASTIC' = '#a6cee3'
)


# Plot the average number of sites with serving each function for each treatment
ggplot(df, aes(x = as.factor(high_level_functionality), y = loci_count, fill = treatment_factor)) + 
  geom_boxplot() + 
  scale_fill_manual(values = color_map) + 
  theme(axis.text.x = element_text(angle = 90))


# Combine all the specific site functionalities into broader categories
#   e.g., ENV-A vestigial + ENV-B plastic is still vestigial machinery and should be counted as such
#   df_cat = tidy format
#   df_cat_flat = flat format
#   (Both were useful at the time, though only df_cat is used below)
df_cat = data.frame(data = matrix(nrow = 0, ncol = 4))
colnames(df_cat) = c('treatment', 'seed', 'category', 'count')
df_cat_flat = data.frame(data = matrix(nrow = 0, ncol = 8))
colnames(df_cat_flat) = c('treatment', 'seed', 'count_none', 'count_rep', 'count_required', 'count_task', 'count_vestigial', 'count_plastic')
for(seed in unique(df$seed)){
  df_seed = df[df$seed == seed,]
  none_count = sum(df_seed[df_seed$high_level_functionality %in% c('None'),]$loci_count)
  rep_count = sum(df_seed[df_seed$high_level_functionality %in% c('Replication Machinery'),]$loci_count)
  required_count = sum(df_seed[df_seed$high_level_functionality %in% c('Required'),]$loci_count)
  task_count = sum(df_seed[df_seed$high_level_functionality %in% c('Even Task Machinery', 'Odd Task Machinery', 'Both Task Machinery', 'Even Recycled Odd', 'Odd Recycled Even', 'Odd task, even plastic', 'Even task, odd plastic'),]$loci_count)
  vestigial_count = sum(df_seed[df_seed$high_level_functionality %in% c('Vestigial Even', 'Vestigial Odd', 'Both Vestigial', 'Even Recycled Odd', 'Odd Recycled Even', 'Odd plastic, even vestigial', 'Even plastic, odd vestigial'),]$loci_count)
  plastic_count = sum(df_seed[df_seed$high_level_functionality %in% c('Even Plastic Machinery', 'Odd Plastic Machinery', 'Both Plastic Machinery', 'Odd plastic, even vestigial', 'Even plastic, odd vestigial', 'Odd task, even plastic', 'Even task, odd plastic'),]$loci_count)
  df_cat_flat[nrow(df_cat_flat) + 1,] = c(df_seed$treatment[1], seed, none_count, rep_count, required_count, task_count, vestigial_count, plastic_count)
  df_cat[nrow(df_cat) + 1,] = c(df_seed$treatment[1], seed, 'None', none_count)
  df_cat[nrow(df_cat) + 1,] = c(df_seed$treatment[1], seed, 'Replication', rep_count)
  df_cat[nrow(df_cat) + 1,] = c(df_seed$treatment[1], seed, 'Required', required_count)
  df_cat[nrow(df_cat) + 1,] = c(df_seed$treatment[1], seed, 'Task', task_count)
  df_cat[nrow(df_cat) + 1,] = c(df_seed$treatment[1], seed, 'Vestigial', vestigial_count)
  df_cat[nrow(df_cat) + 1,] = c(df_seed$treatment[1], seed, 'Plastic', plastic_count)
  cat(seed, ' ')
}
cat('\n')


# Plot the number of sites in each category for each treatment 
df_cat$treatment_factor = factor(df_cat$treatment, levels = c('STATIC', 'NON-PLASTIC', 'PLASTIC'))
df_cat$count = as.numeric(df_cat$count)
ggplot(df_cat, aes(x = as.factor(category), y = count, fill = treatment_factor)) + 
  geom_boxplot() + 
  scale_fill_manual(values = color_map) + 
  theme(axis.text.x = element_text(angle = 15)) + 
  xlab('Site function') + 
  ylab('Number of sites') + 
  labs(fill = 'Condition') + 
  ggsave('./architecture/plots/site_categories.png', units = 'in', width = 8, height = 6) + 
  ggsave('./architecture/plots/site_categories.pdf', units = 'in', width = 8, height = 6) 

# Save off the data in case we want to use it again!
write.csv(df_cat, './architecture/data/categorized_functionality_data.csv')

# Fix data types
df_cat_flat$treatment_factor = factor(df_cat_flat$treatment, levels = c('STATIC', 'NON-PLASTIC', 'PLASTIC'))
for(col_name in c('count_none', 'count_rep', 'count_required', 'count_task', 'count_plastic', 'count_vestigial')){
  df_cat_flat[,col_name] = as.numeric(df_cat_flat[,col_name])
}

# Save off the data in case we want to use it again!
write.csv(df_cat_flat, './architecture/data/categorized_functionality_data_flat.csv')
