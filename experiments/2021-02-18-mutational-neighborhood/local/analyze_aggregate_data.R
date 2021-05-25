# Summary: Plot several key variables for one- and two-step mutational neighborhoods on
#   representative genotypes 
#   Representative genotype = genotype of most abundant organism in final population
rm(list = ls())

# Load necessary libraries
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
df = read.csv('./data/aggregated_mutant_data.csv')
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

# Functions used in plotting (copied from Alex's analyses)
p_label <- function(p_value) {
  threshold = 0.0001
  if (p_value < threshold) {
    return(paste0("p < ", threshold))
  } else {
    return(paste0("p = ", p_value))
  }
}
is_outlier <- function(value, cond, data, column) {
  cond_data <- filter(data, treatment_factor==cond)
  q1 <- summary(cond_data[,column])[["1st Qu."]]
  q3 <- summary(cond_data[,column])[["3rd Qu."]]
  H <- 1.5 * IQR(cond_data[,column])
  return( (value < (q1-H)) || (value > (q3+H)) )
}


#### mutational robustness
# mutation robustness - fraction of one-step mutations that do *not* change the phenotype

# calculate column (simply the opposite of the volatility)
df$mutational_robustness = 1 - df$one_step_diff_pheno_fra
# Compute manual labels for geom_signif
stat.test <- df %>%
  wilcox_test(mutational_robustness ~ treatment_factor) %>%
  adjust_pvalue(method = "bonferroni") %>%
  add_significance() %>%
  add_xy_position(x="treatment_factor")
# Tweak y.position manually to account for scaled axis (edge case that triggers bad behavior in geom_signif)
stat.test$manual_position <-   stat.test$y.position * c(1.05,1.1,1.15)
stat.test$label <- mapply(p_label,stat.test$p.adj)
df$is_outlier <- mapply(
  is_outlier,
  df$mutational_robustness,
  df$treatment_factor,
  MoreArgs=list(data=df, column="mutational_robustness")
)
# Plot mutational stability!
ggp <- ggplot(df, aes(x=treatment_factor, y=mutational_robustness, fill=treatment_factor)) +
  geom_flat_violin(data=filter(summary_data,is_outlier==FALSE), 
    scale="width", position = position_nudge(x = .2, y = 0), alpha = .8) +
  geom_point(mapping=aes(color=treatment_factor), position = position_jitter(width = .15), size = .5, alpha = 0.8) +
  geom_boxplot(width = .1, outlier.shape = NA, alpha = 0.5) +
  scale_x_discrete( name="Condition") +
  scale_y_continuous( name='Mutational robustness', limits=c(0, 1)) +
  scale_fill_manual( values = color_map ) +
  scale_color_manual( values = color_map ) +
  # coord_flip() +
  #ggtitle('Mutational Robustness') +
  labs( subtitle=paste0( "Kruskal-Wallis, ", p_label(signif(kruskal.test(formula=mutational_robustness~treatment_factor, data=df)$p.value,digits=5)) ) ) +
  ggsignif::geom_signif( data=filter(stat.test, p.adj <= alpha),  aes(xmin=group1,xmax=group2,annotations=label,y_position=manual_position),  manual=TRUE, inherit.aes=FALSE ) +
  theme( legend.position="none" ) +
  ggsave( paste0("plots/mutational_robustness.png"), width=5, height=5 ) +
  ggsave( paste0("plots/mutational_robustness.pdf"), width=5, height=5 )
ggp

# Plot using ggp grid to match other manuscript figures
ggp_grid = plot_grid(
  ggp +
    theme( legend.position="none", axis.title.x=element_blank()) +
    ggtitle("Mutational robustness"),
  nrow=1, ncol=1, align="v", labels="")
ggp_grid
save_plot( paste0("plots/mutational_robustness.pdf"), ggp_grid, base_height=6, base_asp=1)


#### Two step "reversions"
# Two step reversions - Looking only at one-step mutations that *do* change the phenotype, what 
#   fraction of two-step mutations (the first mutation + one additional) that change the phenotype
#   again so that it returns to the original phenotype
# 

# Compute manual labels for geom_signif
stat.test <- df %>%
  wilcox_test(mean_two_step_reversion_frac__viable ~ treatment_factor) %>%
  adjust_pvalue(method = "bonferroni") %>%
  add_significance() %>%
  add_xy_position(x="treatment_factor")
# Tweak y.position manually to account for scaled axis (edge case that triggers bad behavior in geom_signif)
stat.test$manual_position <-   stat.test$y.position * c(0.95,0.90,0.88)
stat.test$label <- mapply(p_label,stat.test$p.adj)
df$is_outlier <- mapply(
  is_outlier,
  df$mean_two_step_reversion_frac__viable,
  df$treatment_factor,
  MoreArgs=list(data=df, column="mean_two_step_reversion_frac__viable")
)
# Plot!
two_step_reversion_fig <- ggplot( df, aes(x=treatment_factor, y=mean_two_step_reversion_frac__viable, fill=treatment_factor) ) +
  geom_flat_violin( scale="width", position = position_nudge(x = .2, y = 0), alpha = .8 ) +
  geom_point( mapping=aes(color=treatment_factor), position = position_jitter(width = .15), size = .5, alpha = 0.8 ) +
  geom_boxplot( width = .1, outlier.shape = NA, alpha = 0.5 ) +
  scale_x_discrete( name="Condition" ) +
  scale_y_continuous( name="Avg. frac of two-step mutations that revert the phenotype") +
  scale_fill_brewer( palette=cb_palette ) +
  scale_color_brewer( palette=cb_palette ) +
  labs( subtitle=paste0( "Kruskal-Wallis, ", p_label(signif(kruskal.test(formula=mean_two_step_reversion_frac__viable~treatment_factor, data=df)$p.value,digits=4)) ) ) +
  ggsignif::geom_signif( data=filter(stat.test, p.adj <= alpha), aes(xmin=group1,xmax=group2,annotations=label,y_position=manual_position), manual=TRUE, inherit.aes=FALSE ) +
  theme( legend.position="none" ) +
  ggsave( paste0("plots/mean_two_step_reversion_frac__viable.png"), width=5, height=5 ) +
  ggsave( paste0("plots/mean_two_step_reversion_frac__viable.pdf"), width=5, height=5 )
two_step_reversion_fig



#### Task site volatility
# Task site volatility - Fraction of one-step mutations at sites that encode for tasks 
#   that change the phenotype

# Compute manual labels for geom_signif
stat.test <- df %>%
  wilcox_test(one_step_task_diff_pheno_count ~ treatment_factor) %>%
  adjust_pvalue(method = "bonferroni") %>%
  add_significance() %>%
  add_xy_position(x="treatment_factor")
# Tweak y.position manually to account for scaled axis (edge case that triggers bad behavior in geom_signif)
stat.test$manual_position <-   stat.test$y.position * c(1.05,1.1,1.1)
stat.test$label <- mapply(p_label,stat.test$p.adj)
df$is_outlier <- mapply(
  is_outlier,
  df$mean_two_step_reversion_frac__viable,
  df$treatment_factor,
  MoreArgs=list(data=df, column="one_step_task_diff_pheno_count")
)
# Plot!
ggp <- ggplot(df, aes(x=treatment_factor, y=one_step_task_diff_pheno_count, fill=treatment_factor)) +
  geom_flat_violin(data=filter(summary_data,is_outlier==FALSE), 
    scale="width", position = position_nudge(x = .2, y = 0), alpha = .8) +
  geom_point(mapping=aes(color=treatment_factor), position = position_jitter(width = .15), size = .5, alpha = 0.8) +
  geom_boxplot(width = .1, outlier.shape = NA, alpha = 0.5) +
  scale_x_discrete( name="Condition") +
  scale_y_continuous( name='Fraction of muts. at task sites that change pheno.', limits=c(0, 1)) +
  scale_fill_manual( values = color_map ) +
  scale_color_manual( values = color_map ) +
  # coord_flip() +
  labs( subtitle=paste0( "Kruskal-Wallis, ", p_label(signif(kruskal.test(formula=one_step_task_diff_pheno_count~treatment_factor, data=df)$p.value,digits=5)) ) ) +
  ggsignif::geom_signif( data=filter(stat.test, p.adj <= alpha),  aes(xmin=group1,xmax=group2,annotations=label,y_position=manual_position),  manual=TRUE, inherit.aes=FALSE ) +
  theme( legend.position="none" ) +
  ggsave( paste0("plots/one_step_task_site_volatility.png"), width=5, height=5 ) +
  ggsave( paste0("plots/one_step_task_site_volatility.pdf"), width=5, height=5 )
ggp
