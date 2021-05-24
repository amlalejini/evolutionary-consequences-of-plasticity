rm(list = ls())

library(ggplot2)
library(ggridges)

df = read.csv('./trimmed_data.csv')

func_changes = c()

for(depth in sort(unique(df$tree_depth))){
  if(depth != 0){
    cat(depth, ' ')
    mut_count = nrow(df[df$is_mutation & df$tree_depth == depth,])
    change_count = nrow(df[df$is_function_change & df$tree_depth == depth,])
    func_changes = c(func_changes, rep(change_count / mut_count, mut_count))
  }
}
cat('\n')

#mean(func_changes)

df_out = data.frame(data = matrix(nrow = 0, ncol = 4))
colnames(df_out) = c('seed', 'environment', 'sensors', 'locus_func_changes_per_mut')
df_out[1,] = c(df$seed[1], df$environment[1], df$sensors[1], mean(func_changes))
write.csv(df_out, 'func_changes_per_mut.csv')
