rm(list = ls())

base_dir = '/mnt/gs18/scratch/users/fergu358/plasticity/evolvability/landscape_data_two_step/data/'
first_seed = 200000

initialized = F
df = NA

for(seed_offset in 0:99){
    filename = paste0(base_dir, 'RUN_C0_', as.integer(first_seed + seed_offset), '/mutant_func_changes.csv')
    if(!file.exists(filename)){
        cat('File not found: ', filename, '\n')
        next    
    }
    df_tmp = read.csv(filename)
    df_tmp$seed = first_seed + seed_offset
    df_tmp$environment = 'u0-ALL'
    df_tmp$sensors = F
    if(!initialized){
        df = df_tmp    
        initialized = T
    }
    else{
        df = rbind(df, df_tmp)    
    }
}
for(seed_offset in 100:199){
    filename = paste0(base_dir, 'RUN_C1_', as.integer(first_seed + seed_offset), '/mutant_func_changes.csv')
    if(!file.exists(filename)){
        cat('File not found: ', filename, '\n')
        next    
    }
    df_tmp = read.csv(filename)
    df_tmp$seed = first_seed + seed_offset
    df_tmp$environment = 'chg-u100'
    df_tmp$sensors = T
    df = rbind(df, df_tmp)    
}
for(seed_offset in 200:299){
    filename = paste0(base_dir, 'RUN_C2_', as.integer(first_seed + seed_offset), '/mutant_func_changes.csv')
    if(!file.exists(filename)){
        cat('File not found: ', filename, '\n')
        next    
    }
    df_tmp = read.csv(filename)
    df_tmp$seed = first_seed + seed_offset
    df_tmp$environment = 'chg-u100'
    df_tmp$sensors = F
    df = rbind(df, df_tmp)    
}
write.csv(df, 'aggregated_mutant_functionality_data.csv')
