rm(list = ls())

base_dir = '/mnt/gs18/scratch/users/fergu358/plasticity/evolvability/architecture_data/data'

df = NA
initialized = F

df_out = data.frame(data = matrix(nrow = 0, ncol = 5))
colnames(df_out) = c('x', 'seed', 'environment', 'sensors', 'locus_func_changes_per_mut')

for(seed_dir in list.dirs(base_dir, recursive = F)){
    filename = paste0(seed_dir, '/func_changes_per_mut.csv')
    if(!file.exists(filename)){
        cat('\nCannot find file: ', filename, '\n')
        next
    }
    else{
        df_tmp = read.csv(filename)
        df_out[nrow(df_out) + 1,]  = df_tmp[1,]
    }
}
cat('\n')

write.csv(df_out, 'func_changes_per_mut_summary.csv')
