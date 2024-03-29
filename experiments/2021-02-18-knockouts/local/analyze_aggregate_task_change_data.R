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
df = read.csv('./data/task_data/task_changes_per_mut_summary.csv')
df$environment = 'fluctuating'
df[df$seed < 200100,]$environment = 'static'
df$sensors = 1
df[df$seed > 200100 & df$seed < 200200,]$sensors = 0
df$treatment = paste0(df$environment, 'x', df$sensors)
df$treatment_name = 'STATIC'
df[df$treatment == 'fluctuatingx0',]$treatment_name = 'PLASTIC'
df[df$treatment == 'fluctuatingx1',]$treatment_name = 'NON-PLASTIC'
df$treatment_factor = as.factor(df$treatment_name)


# Plotting variables
theme_set(theme_cowplot())
cb_palette <- "Paired"
alpha <- 0.05

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

# Compute manual labels for geom_signif
stat.test <- df %>%
  wilcox_test(task_changes_per_mut ~ treatment_factor) %>%
  adjust_pvalue(method = "bonferroni") %>%
  add_significance() %>%
  add_xy_position(x="treatment_factor")
# Tweak y.position manually to account for scaled axis (edge case that triggers bad behavior in geom_signif)
stat.test$manual_position <-   stat.test$y.position * c(0.95,0.90,0.88)
stat.test$label <- mapply(p_label,stat.test$p.adj)
df$is_outlier <- mapply(
  is_outlier,
  df$task_changes_per_mut,
  df$treatment_factor,
  MoreArgs=list(data=df, column="task_changes_per_mut")
)


# Plot the average number of tasks that change with a mutation (averaged per rep) for each treatment
task_change_mut_fig <- ggplot(df, aes(x=treatment_factor, y=task_changes_per_mut, fill=treatment_factor)) +
  geom_flat_violin( data=filter(summary_data,is_outlier==FALSE), scale="width", position = position_nudge(x = .2, y = 0), alpha = .8) +
  geom_point( mapping=aes(color=treatment_factor), position = position_jitter(width = .15), size = .5, alpha = 0.8) +
  geom_boxplot( width = .1, outlier.shape = NA, alpha = 0.5) +
  scale_x_discrete( name="Condition") +
  scale_y_continuous( name="Avg. number of tasks that toggle function with a mutation") +
  scale_fill_brewer( palette=cb_palette) +
  scale_color_brewer( palette=cb_palette) +
  # coord_flip() +
  labs( subtitle=paste0( "Kruskal-Wallis, ", p_label(signif(kruskal.test(formula=task_changes_per_mut~treatment_factor, data=df)$p.value,digits=4)))) +
  ggsignif::geom_signif( data=filter(stat.test, p.adj <= alpha), aes(xmin=group1,xmax=group2,annotations=label,y_position=manual_position), manual=TRUE, inherit.aes=FALSE) +
  theme( legend.position="none") +
  ggsave( paste0("plots/task_changes_per_mut.png"), width=5, height=5) +
  ggsave( paste0("plots/task_changes_per_mut.pdf"), width=5, height=5)
task_change_mut_fig
