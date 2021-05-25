# Summary: Creates a plot of task x genome site plot for selected seeds
  # Each tile in the plot shows what function (if any) that site plays for the given task
rm(list = ls())
# Load necessary libraries 
library(ggplot2)
library(dplyr)

# Load and prep data
df_static = read.csv('./locus_slice_seeds/200063_locus_slice_data.csv')
df_static$trt = 'STATIC'
df_plastic = read.csv('./locus_slice_seeds/200111_locus_slice_data.csv')
df_plastic$trt = 'PLASTIC'
df_nonplastic = read.csv('./locus_slice_seeds/200248_locus_slice_data.csv')
df_nonplastic$trt = 'NON-PLASTIC'
df_plot = rbind(df_static, df_nonplastic, df_plastic)

# Rename Previous -> Vestigial
df_plot$functionality = as.character(df_plot$functionality)
df_plot[df_plot$functionality == 'Previous Task Machinery',]$functionality = 'Vestigial Task Machinery'

# Define all the colors
# OLD
#color_map = c(
#  'Required' = '#000000',
#  'Replication Machinery' = '#666666',
#  'None' = '#aaaaaa',
#  'Task Machinery' = '#1155cc',
#  'Vestigial Task Machinery' = '#a4c2f4',
#  'Plasticity Machinery' = '#cc0000'
#)
color_map = c(
  'Required' = '#000000',
  'Replication Machinery' = '#575757',
  'None' = '#a6a6a6',
  'Task Machinery' = '#994455',
  'Vestigial Task Machinery' = '#ee99aa',
  'Plasticity Machinery' = '#eecc66'
)
# Define order colors will appear in bar plots
color_order = c('None', 'Task Machinery', 'Vestigial Task Machinery', 'Plasticity Machinery', 'Required', 'Replication Machinery')


# Data prep for plotting
df_plot$knockout_id = as.numeric(df_plot$knockout_id)
df_plot$func_factor = factor(df_plot$functionality, levels = color_order)
df_plot$task_factor = factor(df_plot$task, levels = c('not', 'and', 'or', 'nand', 'andnot', 'ornot'))
df_plot$trt_factor = factor(df_plot$trt, levels = c('STATIC', 'NON-PLASTIC', 'PLASTIC'))

# Plot!
ggp = ggplot(df_plot, aes(x = task_factor, y = knockout_id, fill = func_factor)) + 
  geom_tile() + 
  scale_fill_manual(values = color_map) + 
  scale_y_continuous(expand = c(0,0)) + 
  scale_x_discrete(expand = c(0,0)) +
  geom_vline(xintercept = which(df_plot$task == 'or')) +
  geom_vline(xintercept = c(3.5)) +
  ylab('Locus position') + 
  xlab('Task') + 
  labs(fill = 'Locus functionality') + 
  facet_grid(cols = vars(trt_factor)) +
  #theme(legend.position = 'bottom') + 
  #ggsave('locus_slice.png', units = 'in', width = 6, height = 10) +
  ggsave('locus_slice_combined.pdf', units = 'in', width = 10, height = 8)
ggp


# Experimental: Recolor facet labels to show the treatments clearly
# Grob coded adapted from: https://stackoverflow.com/a/60046113
color_map = c(
  'STATIC' = '#b2df8a',
  'PLASTIC' = '#1f78b4',
  'NON-PLASTIC' = '#a6cee3'
)
grob = ggplot_gtable(ggplot_build(ggp))
facet_grob_idxs <- which(grepl('strip-t', grob$layout$name) )
facet_order = c('STATIC', 'NON-PLASTIC', 'PLASTIC')
for(idx in 1:3){
  grob_idx = facet_grob_idxs[idx]
  fill_idx = which(grepl('rect', grob$grobs[[grob_idx]]$grobs[[1]]$childrenOrder))
  grob$grobs[[facet_grob_idxs[idx]]]$grobs[[1]]$children[[fill_idx]]$gp$fill = color_map[facet_order[idx]]
}
grid::grid.draw(grob)
ggsave(filename = 'locus_slice_combined_color_facets.pdf', plot = grob, units = 'in', width = 10, height = 8)
