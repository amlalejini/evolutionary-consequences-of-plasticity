
rm(list = ls())

df = read.csv('./trimmed_data.csv')
df = df[df$is_mutation,]

func_changes = c()

task_order = c('not', 'nand', 'and', 'ornot', 'or', 'andnot')
task_masks = c(32, 16, 8, 4, 2, 1)
for(task_idx in 1:6){
  task_name = task_order[task_idx]
  task_mask = task_masks[task_idx]
  df[,paste0(task_name, '_even')] = bitwAnd(df$base_phenotype_odd_int, task_mask) / task_mask
  df[,paste0(task_name, '_odd')] = bitwAnd(df$base_phenotype_odd_int, task_mask) / task_mask
}

for(depth in sort(unique(df$tree_depth))){
  if(depth > 1){
    cat(depth, ' ')
    mut_count = nrow(df[df$is_mutation & df$tree_depth == depth,])
    change_not = (df[df$tree_depth == depth,]$not_even[1] != df[df$tree_depth == (depth - 1),]$not_even[1]) | (df[df$tree_depth == depth,]$not_odd[1] != df[df$tree_depth == (depth - 1),]$not_odd[1])
    change_nand = (df[df$tree_depth == depth,]$nand_even[1] != df[df$tree_depth == (depth - 1),]$nand_even[1]) | (df[df$tree_depth == depth,]$nand_odd[1] != df[df$tree_depth == (depth - 1),]$nand_odd[1])
    change_and = (df[df$tree_depth == depth,]$and_even[1] != df[df$tree_depth == (depth - 1),]$and_even[1]) | (df[df$tree_depth == depth,]$and_odd[1] != df[df$tree_depth == (depth - 1),]$and_odd[1])
    change_or = (df[df$tree_depth == depth,]$or_even[1] != df[df$tree_depth == (depth - 1),]$or_even[1]) | (df[df$tree_depth == depth,]$or_odd[1] != df[df$tree_depth == (depth - 1),]$or_odd[1])
    change_andnot = (df[df$tree_depth == depth,]$andnot_even[1] != df[df$tree_depth == (depth - 1),]$andnot_even[1]) | (df[df$tree_depth == depth,]$andnot_odd[1] != df[df$tree_depth == (depth - 1),]$andnot_odd[1])
    change_ornot = (df[df$tree_depth == depth,]$ornot_even[1] != df[df$tree_depth == (depth - 1),]$ornot_even[1]) | (df[df$tree_depth == depth,]$ornot_odd[1] != df[df$tree_depth == (depth - 1),]$ornot_odd[1])
    change_count = sum(change_not, change_and, change_or, change_nand, change_andnot, change_ornot)
    func_changes = c(func_changes, rep(change_count / mut_count, mut_count))
  }
}
cat('\n')


df_out = data.frame(data = matrix(nrow = 0, ncol = 4))
colnames(df_out) = c('seed', 'environment', 'sensors', 'task_changs_per_mut')
df_out[1,] = c(df$seed[1], df$environment[1], df$sensors[1], mean(func_changes))
write.csv(df_out, 'task_changes_per_mut.csv')

