rm(list = ls())

base_dir = '/mnt/gs18/scratch/users/fergu358/plasticity/evolvability/architecture_data/'

df = NA
initialized = F

for(treatment_dir in list.dirs(base_dir, recursive = F)){
    cat(treatment_dir, '\n')
    for(seed_dir in list.dirs(treatment_dir, recursive = F)){
        filename = paste0(seed_dir, '/architecture_functionality_data.csv')
        if(!file.exists(filename)){
            cat('Cannot find file: ', filename)
            next
        }
        if(!initialized){
            df = read.csv(filename)
            cat(df$seed[1], ' ')
            initialized = T
        }else{
            df_tmp = read.csv(filename)
            cat(df_tmp$seed[1], ' ')
            df = rbind(df, df_tmp)
        }
    }
    cat('\n')
}

write.csv(df, 'architecture_functionality_summary.csv')
