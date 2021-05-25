rm(list = ls())

base_dir = '/mnt/gs18/scratch/users/fergu358/plasticity/evolvability/architecture_data_2/data/'

df = NA
initialized = F

df_out = data.frame(data = matrix(nrow = 0, ncol = 5))
colnames(df_out) = c('seed', 'environment', 'sensors', 'high_level_functionality', 'loci_count')

for(seed_dir in list.dirs(base_dir, recursive = F)){
    filename = paste0(seed_dir, '/high_level_functionality_summary.csv')
    if(!file.exists(filename)){
        cat('\nCannot find file: ', filename, '\n')
        next
    }
    else{
        df_tmp = read.csv(filename)
        df_out = rbind(df_out, df_tmp)
    }
}
cat('\n')
write.csv(df_out, 'aggregated_high_level_functionality_summary.csv')
