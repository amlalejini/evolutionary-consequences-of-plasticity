rm(list = ls())
library(ggplot2)

# Handle command line args
arg_vec = commandArgs(trailingOnly = T) 
if(length(arg_vec)!= 1){
    print('Error! Expected exactly 1 argument: path of directory where we\'ll both load the input and save the output')
    quit()
}
data_path = arg_vec[1]

df = read.csv(paste0(data_path, '/cleaned_data.csv'))
df = df[df$tree_depth == max(df$tree_depth),]

not_mask =    df$not_functionality == 'Task Machinery'
nand_mask =   df$nand_functionality == 'Task Machinery'
and_mask =    df$and_functionality == 'Task Machinery'
andnot_mask = df$andnot_functionality == 'Task Machinery'
or_mask =     df$or_functionality == 'Task Machinery'
ornot_mask =  df$ornot_functionality == 'Task Machinery'

df_matrix = data.frame(data = matrix(nrow = 0, ncol = 4))
colnames(df_matrix) = c('base_task', 'extra_task', 'shared_count', 'base_count')

df_matrix[nrow(df_matrix) + 1,] = c('not', 'nand',   sum(not_mask & nand_mask), sum(not_mask))
df_matrix[nrow(df_matrix) + 1,] = c('not', 'and',    sum(not_mask & and_mask), sum(not_mask))
df_matrix[nrow(df_matrix) + 1,] = c('not', 'andnot', sum(not_mask & andnot_mask), sum(not_mask))
df_matrix[nrow(df_matrix) + 1,] = c('not', 'or',     sum(not_mask & or_mask), sum(not_mask))
df_matrix[nrow(df_matrix) + 1,] = c('not', 'ornot',  sum(not_mask & ornot_mask), sum(not_mask))

df_matrix[nrow(df_matrix) + 1,] = c('nand', 'not',    sum(nand_mask & not_mask), sum(nand_mask))
df_matrix[nrow(df_matrix) + 1,] = c('nand', 'and',    sum(nand_mask & and_mask), sum(nand_mask))
df_matrix[nrow(df_matrix) + 1,] = c('nand', 'andnot', sum(nand_mask & andnot_mask), sum(nand_mask))
df_matrix[nrow(df_matrix) + 1,] = c('nand', 'or',     sum(nand_mask & or_mask), sum(nand_mask))
df_matrix[nrow(df_matrix) + 1,] = c('nand', 'ornot',  sum(nand_mask & ornot_mask), sum(nand_mask))

df_matrix[nrow(df_matrix) + 1,] = c('and', 'nand',    sum(and_mask & nand_mask), sum(and_mask))
df_matrix[nrow(df_matrix) + 1,] = c('and', 'not',     sum(and_mask & not_mask), sum(and_mask))
df_matrix[nrow(df_matrix) + 1,] = c('and', 'andnot',  sum(and_mask & andnot_mask), sum(and_mask))
df_matrix[nrow(df_matrix) + 1,] = c('and', 'or',      sum(and_mask & or_mask), sum(and_mask))
df_matrix[nrow(df_matrix) + 1,] = c('and', 'ornot',   sum(and_mask & ornot_mask), sum(and_mask))

df_matrix[nrow(df_matrix) + 1,] = c('andnot', 'nand',    sum(andnot_mask & nand_mask), sum(andnot_mask))
df_matrix[nrow(df_matrix) + 1,] = c('andnot', 'and',     sum(andnot_mask & and_mask), sum(andnot_mask))
df_matrix[nrow(df_matrix) + 1,] = c('andnot', 'not',     sum(andnot_mask & not_mask), sum(andnot_mask))
df_matrix[nrow(df_matrix) + 1,] = c('andnot', 'or',      sum(andnot_mask & or_mask), sum(andnot_mask))
df_matrix[nrow(df_matrix) + 1,] = c('andnot', 'ornot',   sum(andnot_mask & ornot_mask), sum(andnot_mask))

df_matrix[nrow(df_matrix) + 1,] = c('or', 'nand',    sum(or_mask & nand_mask), sum(or_mask))
df_matrix[nrow(df_matrix) + 1,] = c('or', 'and',     sum(or_mask & and_mask), sum(or_mask))
df_matrix[nrow(df_matrix) + 1,] = c('or', 'andnot',  sum(or_mask & andnot_mask), sum(or_mask))
df_matrix[nrow(df_matrix) + 1,] = c('or', 'not',     sum(or_mask & not_mask), sum(or_mask))
df_matrix[nrow(df_matrix) + 1,] = c('or', 'ornot',   sum(or_mask & ornot_mask), sum(or_mask))

df_matrix[nrow(df_matrix) + 1,] = c('ornot', 'nand',    sum(ornot_mask & nand_mask), sum(ornot_mask))
df_matrix[nrow(df_matrix) + 1,] = c('ornot', 'and',     sum(ornot_mask & and_mask), sum(ornot_mask))
df_matrix[nrow(df_matrix) + 1,] = c('ornot', 'andnot',  sum(ornot_mask & andnot_mask), sum(ornot_mask))
df_matrix[nrow(df_matrix) + 1,] = c('ornot', 'or',      sum(ornot_mask & or_mask), sum(ornot_mask))
df_matrix[nrow(df_matrix) + 1,] = c('ornot', 'not',     sum(ornot_mask & not_mask), sum(ornot_mask))

df_matrix$shared_count = as.numeric(df_matrix$shared_count)
df_matrix$base_count = as.numeric(df_matrix$base_count)
df_matrix$fraction = df_matrix$shared_count / df_matrix$base_count

ggplot(df_matrix, aes(x = as.factor(extra_task), as.factor(base_task), fill = fraction)) +
  geom_tile() + 
  geom_text(aes(label = round(fraction, 2)), color = 'white') + 
  scale_fill_continuous(limits = c(0,1)) + 
  ylab('Base task') +
  xlab('Other task')


df_matrix$seed = unique(df$seed[1])
df_matrix$environment = unique(df$environment[1])
df_matrix$sensors = unique(df$sensors[1])
write.csv(df_matrix, paste0(data_path, '/overlap_data.csv'))
