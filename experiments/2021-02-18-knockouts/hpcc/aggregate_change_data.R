rm(list = ls())

base_dir = '/mnt/gs18/scratch/users/fergu358/plasticity/evolvability/architecture_data/data/'

df = NA
initialized = F

for(seed_dir in list.dirs(base_dir, recursive = F)){
    filename = paste0(seed_dir, '/change_data.csv')
    if(!file.exists(filename)){
        cat('missing file')
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

write.csv(df, 'scraped_change_data.csv')
