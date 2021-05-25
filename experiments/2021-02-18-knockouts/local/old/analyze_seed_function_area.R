# Summary: Calculates the fraction of genomes space x updates area occupied by each possible 
#   site function
rm(list = ls())

# Load necessary libraries
library(ggplot2)
library(dplyr)

# Load and prep data from test seeds
df = read.csv('./data/trimmed_data/trimmed_data_200063.csv')
df = df[df$is_function_change,]
df$treatment = 'STATIC'
df_tmp = read.csv('./data/trimmed_data/trimmed_data_200111.csv')
df_tmp = df_tmp[df_tmp$is_function_change,]
df_tmp$treatment = 'PLASTIC'
df = rbind(df, df_tmp)
df_tmp = read.csv('./data/trimmed_data/trimmed_data_200248.csv')
df_tmp = df_tmp[df_tmp$is_function_change,]
df_tmp$treatment = 'NON-PLASTIC'
df = rbind(df, df_tmp)

# Define all the colors
high_level_color_map = c(
  'Other' = '#ff00ff',
  'Required' = '#000000',
  'Replication Machinery' = '#666666',
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
  'Both Vestigial' = '#c27ba0',
  'Odd task, even plastic' = '#20ffce',
  'Even task, odd plastic' = '#f8eb5d',
  'Odd plastic, even vestigial' = '#00ad82',
  'Even plastic, odd vesitigal' = '#c1b724'
)
# Define order colors will appear in bar plots
high_level_color_order = c(
  'Other',
  'Required',
  'Replication Machinery',
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
  'Both Plastic Machinery',
  'Odd task, even plastic',
  'Even task, odd plastic',
  'Odd plastic, even vestigial',
  'Even plastic, odd vesitigal'
)

# Group and summarize data to make it easier to calculate the fraction of the area
df_grouped = dplyr::group_by(df, treatment, high_level_functionality)
df_summary = dplyr::summarize(df_grouped, area = sum(high_level_length))
df_summary$area_frac = df_summary$area / (200001 * 100)
df_summary$high_level_factor = factor(df_summary$high_level_functionality, levels = high_level_color_order)

# Plot!
ggplot(df_summary, aes(x = high_level_factor, y = area_frac)) + 
  geom_col(aes(fill = as.factor(high_level_functionality))) + 
  geom_text(aes(y = area_frac + 0.12, label = round(area_frac, 2))) +
  scale_y_continuous(limits = c(0, 1)) +
  coord_flip() + 
  scale_fill_manual(values = high_level_color_map) +
  theme(legend.position = 'none') +
  facet_grid(cols = vars(as.factor(treatment)))

             
