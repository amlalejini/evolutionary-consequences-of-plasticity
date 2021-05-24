rm(list = ls())

base_dir = '/mnt/gs18/scratch/users/fergu358/plasticity/evolvability/architecture_data/'

df = NA
initialized = F

df_out = data.frame(data = matrix(nrow = 0, ncol = 4))
colnames(df_out) = c('seed', 'environment', 'sensors', 'vestigial_frac')

for(treatment_dir in list.dirs(base_dir, recursive = F)){
    cat(treatment_dir, '\n')
    for(seed_dir in list.dirs(treatment_dir, recursive = F)){
        filename = paste0(seed_dir, '/trimmed_data.csv')
        if(!file.exists(filename)){
            cat('\nCannot find file: ', filename, '\n')
            next
        }
        else{
            df_tmp = read.csv(filename)
            num = nrow(df_tmp[
                df_tmp$is_function_change & 
                df_tmp$high_level_functionality %in% c(
                        'Even Recycled Odd', 
                        'Odd Recycled Even', 
                        'Vestigial Odd', 
                        'Vestigial Even', 
                        'Both Vestigial', 
                        'Odd plastic, even vestigial',
                        'Even plastic, odd vestigial')
                    ,])
            denom = nrow(df_tmp[df_tmp$is_function_change,])
            vestigial_frac = num / denom
            df_tmp$vestigial_frac = vestigial_frac
            cat(df_tmp$seed[1], ' ')
            df_out[nrow(df_out) + 1,]  = c(
                df_tmp$seed[1], 
                as.character(df_tmp$environment)[1], 
                as.character(df_tmp$sensors)[1], 
                vestigial_frac
            )
        }
    }
    cat('\n')
}

write.csv(df_out, 'vestigial_count_summary.csv')
