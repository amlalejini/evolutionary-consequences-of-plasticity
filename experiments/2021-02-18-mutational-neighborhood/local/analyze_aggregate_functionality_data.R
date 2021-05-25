# Summary: Plots neighborhood architectural volatility
#   Neighborhood architectural volatility: The average fraction of site functions that change with 
#     a one-step mutation on the focal genotype
rm(list = ls())

# Load necessary libaries
library(ggplot2)
library(rstatix)
library(ggsignif)
library(scales)
library(cowplot)
library(RColorBrewer)
library(Hmisc)
library(boot)
source("https://gist.githubusercontent.com/benmarwick/2a1bb0133ff568cbe28d/raw/fb53bd97121f7f9ce947837ef1a4c65a73bffb3f/geom_flat_violin.R")

# Load and prep data
df = read.csv('./data/aggregated_mutant_functionality_data.csv')
df$treatment = 'STATIC'
df[df$environment == 'chg-u100',]$treatment = 'PLASTIC'
df[df$environment == 'chg-u100' & df$sensors == F,]$treatment = 'NON-PLASTIC'
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

p_label <- function(p_value) {
  threshold = 0.0001
  if (p_value < threshold) {
    return(paste0("p < ", threshold))
  } else {
    return(paste0("p = ", p_value))
  }
}

# Functions used in plotting / stats (copied from Alex's analyses)
is_outlier <- function(value, cond, data, column) {
  cond_data <- filter(data, treatment_factor==cond)
  q1 <- summary(cond_data[,column])[["1st Qu."]]
  q3 <- summary(cond_data[,column])[["3rd Qu."]]
  H <- 1.5 * IQR(cond_data[,column])
  return( (value < (q1-H)) || (value > (q3+H)) )
}
# Compute manual labels for geom_signif
stat.test <- df %>%
  wilcox_test(mean_count_changes ~ treatment_factor) %>%
  adjust_pvalue(method = "bonferroni") %>%
  add_significance() %>%
  add_xy_position(x="treatment_factor")
# Tweak y.position manually to account for scaled axis (edge case that triggers bad behavior in geom_signif)
stat.test$manual_position <-   stat.test$y.position * c(1.0, 1.03, 1.0)
stat.test$label <- mapply(p_label,stat.test$p.adj)
df$is_outlier <- mapply(
  is_outlier,
  df$mean_count_changes,
  df$treatment_factor,
  MoreArgs=list(data=df, column="mean_count_changes")
)

mutant_func_fig <- ggplot(df, aes(x=treatment_factor, y=mean_count_changes, fill=treatment_factor)) +
  geom_flat_violin(data=filter(summary_data,is_outlier==FALSE), 
    scale="width", position = position_nudge(x = .2, y = 0), alpha = .8) +
  geom_point(mapping=aes(color=treatment_factor), position = position_jitter(width = .15), size = .5, alpha = 0.8) +
  geom_boxplot(width = .1, outlier.shape = NA, alpha = 0.5) +
  scale_x_discrete( name="Condition") +
  scale_y_continuous( name='Neighborhood architectural volatility') +
  scale_fill_manual( values = color_map ) +
  scale_color_manual( values = color_map ) +
  labs( subtitle=paste0( "Kruskal-Wallis, ", p_label(signif(kruskal.test(formula=mean_count_changes~treatment_factor, data=df)$p.value,digits=4)) ) ) +
  ggsignif::geom_signif( data=filter(stat.test, p.adj <= alpha),  aes(xmin=group1,xmax=group2,annotations=label,y_position=manual_position),  manual=TRUE, inherit.aes=FALSE ) +
  theme( legend.position="none" ) +
  ggsave( paste0("plots/neighborhood_architectural_volatility.png"), width=5, height=5 ) +
  ggsave( paste0("plots/neighborhood_architectural_volatility.pdf"), width=5, height=5 )
mutant_func_fig
