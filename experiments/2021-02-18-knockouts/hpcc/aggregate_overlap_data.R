rm(list = ls())

base_dir = '/mnt/gs18/scratch/users/fergu358/plasticity/evolvability/2021-01-14-lineage-knockouts/data_phase_1/'

df = NA
initialized = F

for(treatment_dir in list.dirs(base_dir, recursive = F)){
    cat(treatment_dir, '\n')
    for(seed_dir in list.dirs(treatment_dir, recursive = F)){
        filename = paste0(seed_dir, '/overlap_data.csv')
        if(!file.exists(filename)){
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

write.csv(df, 'scraped_overlap_data.csv')
