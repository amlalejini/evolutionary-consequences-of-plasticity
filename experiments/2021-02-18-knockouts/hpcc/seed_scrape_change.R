rm(list = ls())

library(ggplot2)
library(dplyr)

df_clean = read.csv('trimmed_data.csv')
df = df_clean[df_clean$is_function_change == T,]

df$changes = 0
df$is_last_change = F
df_changes = data.frame(data = matrix(nrow = nrow(df), ncol = ncol(df)))
colnames(df_changes) = colnames(df)
cur_idx = 1
for(locus_idx in 1:100){
  df_locus = df[df$knockout_id == locus_idx,]
  cat(locus_idx, ':', nrow(df_locus),' ', '\n')
  df_locus = df_locus[order(df_locus$tree_depth),]
  df_locus$changes = 1:nrow(df_locus)
  df_locus[nrow(df_locus),]$is_last_change = T
  stop_idx = cur_idx + nrow(df_locus) - 1
  df_changes[cur_idx:stop_idx,] = df_locus
  cur_idx = stop_idx + 1
}
cat('\n')


df_changes$change_pct_mut = df_changes$changes / sum(df_clean$is_mutation)
df_changes$change_pct_depth = df_changes$changes / max(df_clean$tree_depth)
#ggplot(df_changes, aes(x = update_born, y = change_pct_mut, group = knockout_id)) +
#  geom_line(alpha = 0.1) +
#  #geom_point(alpha = 0.1, size = 0.2, color = 'red') + 
#  ggsave(paste0('./locus_slice_seeds/change_data/change_over_time_', seed, '.pdf'), units = 'in', width = 10, height = 8)

write.csv(df_changes, paste0('./change_data.csv'))
