rm(list = ls())


load_batch = function(batch_num){
    df_tmp_odd = read.csv(paste0('./data/mutant_data/env_odd/batch_',batch_num,'.dat')
        , sep = ' ', header = F, comment.char = '#')
    print('\todd:Data loaded')
    colnames(df_tmp_odd) = c('id','update_born','depth','fitness','length','sequence','gest_time',
        'merit','efficiency','not','nand','and','ornot','or','andnot','nor','xor','equals',
        'parent_muts')
    print('\todd:Columns renamed')
    df_tmp_odd$task_profile = paste0(
        as.character(df_tmp_odd$not),
        as.character(df_tmp_odd$and),
        as.character(df_tmp_odd$or),
        as.character(df_tmp_odd$nand),
        as.character(df_tmp_odd$andnot),
        as.character(df_tmp_odd$ornot))
    print('\todd:Task profile created')
    df_tmp_odd$fitness_odd =   as.numeric(df_tmp_odd$fitness)
    df_tmp_odd$gest_time_odd = as.numeric(df_tmp_odd$gest_time)
    df_tmp_odd$merit_odd =     as.numeric(df_tmp_odd$merit)
    df_tmp_odd$task_profile_odd = as.character(df_tmp_odd$task_profile)
    df_tmp_odd = df_tmp_odd[,c('id', 'parent_muts', 
        'fitness_odd', 'gest_time_odd', 'merit_odd', 'task_profile_odd')]

    df_tmp_even = read.csv(paste0('./data/mutant_data/env_even/batch_',batch_num,'.dat')
        , sep = ' ', header = F, comment.char = '#')
    print('\teven:Data loaded')
    colnames(df_tmp_even) = c('id','update_born','depth','fitness','length','sequence','gest_time',
        'merit','efficiency','not','nand','and','ornot','or','andnot','nor','xor','equals',
        'parent_muts')
    print('\teven:Columns renamed')
    df_tmp_even$task_profile = paste0(
        as.character(df_tmp_even$not),
        as.character(df_tmp_even$and),
        as.character(df_tmp_even$or),
        as.character(df_tmp_even$nand),
        as.character(df_tmp_even$andnot),
        as.character(df_tmp_even$ornot))
    print('\teven:Task profile created')
    df_tmp_even$fitness_even =   as.numeric(df_tmp_even$fitness)
    df_tmp_even$gest_time_even = as.numeric(df_tmp_even$gest_time)
    df_tmp_even$merit_even =     as.numeric(df_tmp_even$merit)
    df_tmp_even$task_profile_even = as.character(df_tmp_even$task_profile)
    df_tmp_even = df_tmp_even[,c('id', 'parent_muts', 
        'fitness_even', 'gest_time_even', 'merit_even', 'task_profile_even')]

    df_tmp = merge(df_tmp_odd, df_tmp_even)
    rm(df_tmp_odd)
    rm(df_tmp_even)
    return(df_tmp)
}

print('Batch 0')
df_0 = load_batch(0)
print('Batch 1')
df_1 = load_batch(1)
print('Batch 2')
df_2 = load_batch(2)
print('Batch 3')
df_3 = load_batch(3)
print('Batch 4')
df_4 = load_batch(4)
print('Batch 5')
df_5 = load_batch(5)
print('Combining all batches...')
df_all = rbind(df_0, df_1, df_2, df_3, df_4, df_5)
print('Combining finished!')
rm(df_0, df_1, df_0, df_2, df_3, df_4, df_5)
df_all$id = as.character(df_all$id)
print('Saving!')
write.csv(df_all, 'two_step_mutant_data.csv')
print('Done!')
