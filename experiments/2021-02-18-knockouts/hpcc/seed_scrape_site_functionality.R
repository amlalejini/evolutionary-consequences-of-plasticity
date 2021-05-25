rm(list = ls())

df = read.csv('./cleaned_data.csv')
df = df[df$tree_depth == max(df$tree_depth) & df$knockout_id != 0,]

high_level_func_options = c(
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
  'Even plastic, odd vestigial'
)


df_out = data.frame(data = matrix(nrow = 0, ncol = 5))
colnames(df_out) = c('seed', 'environment', 'sensors', 'high_level_functionality', 'loci_count')
for(high_level_func in high_level_func_options){
  count = sum(df$high_level_functionality == high_level_func)
  cat(high_level_func, count, '\n')
  df_out[nrow(df_out) + 1,] = c(df$seed[1], df$environment[1], df$sensors[1], high_level_func, count)
}
write.csv(df_out, 'high_level_functionality_summary.csv')

