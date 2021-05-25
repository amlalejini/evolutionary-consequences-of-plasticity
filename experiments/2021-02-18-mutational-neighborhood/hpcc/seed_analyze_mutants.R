# Clear any existing data
rm(list = ls())

# Load in relevant libraries
library(dplyr)
library(ggplot2)
library(ggridges)

########################################################
##############    SECTION 0: DATA PREP    ############## 
########################################################

# Flag which determines where data is loaded from and saved to
is_local = F

# Load in master data file
if(is_local){
  df = read.csv('./data/seeds/mut_data/200248.csv') # Local testing
  plot_dir = './plots/'
}else{
  df = read.csv('./two_step_mutant_data.csv') # HPCC
  plot_dir = './'
}

# Load in clean data (output from an another script) to extract the high-level functionality of each site in the final dominant genotype
if(is_local){
  df_cleaned = read.csv('./data/seeds/cleaned_data/200248.csv')
} else {
  df_cleaned = read.csv('./cleaned_data.csv')
}
df_cleaned = df_cleaned[df_cleaned$tree_depth == max(df_cleaned$tree_depth),] # We only care about the reprsentative genotype and its knockouts
clean_base_org = df_cleaned[df_cleaned$knockout_id == 0,] # The final dominant (i.e., representative) genotype!

# Prep the data and add some helper columns
df$parent_muts = as.character(df$parent_muts)
df$is_viable = df$gest_time_even != 0 & df$gest_time_odd != 0
base_org = df[df$parent_muts == '0',] # The original, non-mutated final dominant org
df$matches_base = df$task_profile_odd == base_org$task_profile_odd & df$task_profile_even == base_org$task_profile_even

# Seperate out the one-step mutants, as well as grabbing their mutation data
one_step_muts = dplyr::filter(df, nchar(df$parent_muts) %in% c(5,6))
one_step_muts = mutate(rowwise(one_step_muts), first_mut_locus = strsplit(parent_muts, '-')[[1]][2])
one_step_muts$first_mut_locus = as.numeric(one_step_muts$first_mut_locus)
one_step_muts = mutate(rowwise(one_step_muts), first_mut_inst = strsplit(parent_muts, '-')[[1]][3])
one_step_muts = mutate(rowwise(one_step_muts), previous_func = df_cleaned[df_cleaned$knockout_id == (first_mut_locus + 1),]$high_level_functionality)
#one_step_muts = one_step_muts[one_step_muts$first_mut_inst != 'G',]

# Do the same for two-step mutants
two_step_muts = dplyr::filter(df, nchar(df$parent_muts) > 6)
two_step_muts = mutate(rowwise(two_step_muts), first_mut = strsplit(parent_muts, '_')[[1]][1])
two_step_muts = mutate(rowwise(two_step_muts), first_mut_locus = strsplit(first_mut, '-')[[1]][2])
two_step_muts = mutate(rowwise(two_step_muts), first_mut_inst = strsplit(first_mut, '-')[[1]][3])
two_step_muts = mutate(rowwise(two_step_muts), second_mut = strsplit(parent_muts, '_')[[1]][2])
two_step_muts = mutate(rowwise(two_step_muts), second_mut_locus = strsplit(second_mut, '-')[[1]][2])
two_step_muts = mutate(rowwise(two_step_muts), second_mut_inst = strsplit(second_mut, '-')[[1]][3])


########################################################
############  SECTION 1: BASIC STATISTICS   ############ 
########################################################
# Section includes 
# - Mutational stability of final dominant genotype's one-step neighborhood
# - Fraction of one-step mutants that are viable
# - Fraction of one-step mutatns that change phenotype
# - Fraction of two-step mutants that revert a changed phenotype back to the original phenotype

# For each one-step mutant, calculate the number of two-step mutants that match the base organism's phenotypic profile
one_step_muts$two_step_matches = 0
one_step_muts$two_step_count = 0
for(row_idx in 1:nrow(one_step_muts)){
  org = one_step_muts[row_idx,] # Grab organism
  if(org$first_mut_locus == 'G'){
    next
  }
  cat(row_idx, ' ') # Visual indicator
  org_two_step_muts = two_step_muts[
    ((two_step_muts$first_mut == org$parent_muts) |  
       (two_step_muts$second_mut_locus == org$first_mut_locus & two_step_muts$second_mut_inst == org$first_mut_inst)) &
      (two_step_muts$second_mut_inst != 'G')
    ,] # Two step mutants that are not the knockout inst (G), and that have the same mutation as the one-step (as either their first or second mut)
  one_step_muts[row_idx,]$two_step_count = nrow(org_two_step_muts)
  one_step_muts[row_idx,]$two_step_matches = sum(org_two_step_muts$matches_base)
}
cat('\n')

# Turn two-step matches in a fraction of all two-step mutations
one_step_muts$two_step_matches_frac = one_step_muts$two_step_matches /one_step_muts$two_step_count

# Summarize data and save out as a small .csv file
df_out = data.frame(data = matrix(nrow = 1, ncol = 0))
df_out$one_step_count = nrow(one_step_muts)
df_out$two_step_count = sum(two_step_muts$second_mut_inst != 'G')
df_out$one_step_viable_count = sum(one_step_muts$is_viable)
df_out$one_step_viable_frac = sum(one_step_muts$is_viable) / nrow(one_step_muts)
df_out$one_step_diff_pheno_count = sum(!one_step_muts$matches_base)
df_out$one_step_diff_pheno_frac = sum(!one_step_muts$matches_base) / nrow(one_step_muts)
task_mask = one_step_muts$previous_func %in% c('Odd Task Machinery', 'Even Task Machinery', 'Both Task Machinery', 'Odd task, even plastic', 'Even task, odd plastic',
                                               'Odd Recycled Even', 'Even Recycled Odd')
df_out$one_step_task_diff_pheno_count = sum(!one_step_muts[task_mask,]$matches_base)
df_out$one_step_task_diff_pheno_count = sum(!one_step_muts[task_mask,]$matches_base) / sum(task_mask)
df_out$one_step_diff_pheno_task_count = sum(!one_step_muts$matches_base)
df_out$one_step_diff_pheno_task_frac = sum(!one_step_muts$matches_base) / nrow(one_step_muts)
df_out$one_step_diff_pheno_viable_count = sum((!one_step_muts$matches_base) & one_step_muts$is_viable)
df_out$one_step_diff_pheno_viable_frac = sum((!one_step_muts$matches_base) & one_step_muts$is_viable) / nrow(one_step_muts)
df_out$mean_two_step_match_frac = mean(one_step_muts$two_step_matches_frac)
df_out$median_two_step_match_frac = median(one_step_muts$two_step_matches_frac)
df_out$mean_two_step_reversion_frac = mean(one_step_muts[!one_step_muts$matches_base,]$two_step_matches_frac)
df_out$median_two_step_reversion_frac = median(one_step_muts[!one_step_muts$matches_base,]$two_step_matches_frac)
df_out$mean_two_step_reversion_frac__viable = mean(one_step_muts[(!one_step_muts$matches_base) & one_step_muts$is_viable,]$two_step_matches_frac)
df_out$median_two_step_reversion_frac__viable = median(one_step_muts[(!one_step_muts$matches_base) & one_step_muts$is_viable,]$two_step_matches_frac)
write.csv(df_out, 'seed_mutation_data.csv')

# Dump a quick plot for the frac of two-step mutations that revert phenotype
ggplot(one_step_muts[!one_step_muts$matches_base,], aes(x = two_step_matches_frac, y = 1)) + 
  geom_density_ridges2() +
  scale_x_continuous(limits = c(-0.01,1)) + 
  xlab('Fraction of two-step mutations that "revert" phenotype') + 
  ylab('Frequency') + 
  ggsave(paste0(plot_dir, 'two_step_reversions.pdf'), units = 'in', width = 6, height = 4)



########################################################
########  SECTION 2: ARCHITECTURAL VOLATILITY   ########
########################################################
# Section includes 
# - Summary information on how many sites change function when the final dominant genotype is mutated


# Grab the two-step mutants where one of the mutations is a knockout
two_step_knockouts = two_step_muts[two_step_muts$first_mut_inst == 'G' | two_step_muts$second_mut_inst == 'G',]
two_step_knockouts = two_step_knockouts[!(two_step_knockouts$first_mut_inst == 'G' & two_step_knockouts$second_mut_inst == 'G'),]
# Grab the locus index of the knockout mutation. Default to the locus of the first mutation, and switch to the second mutation if it is a 'G' (nop-x instruction used for knockouts)
two_step_knockouts$knockout_locus = two_step_knockouts$first_mut_locus
two_step_knockouts[two_step_knockouts$second_mut_inst == 'G', ]$knockout_locus = two_step_knockouts[two_step_knockouts$second_mut_inst == 'G', ]$second_mut_locus
two_step_knockouts$knockout_locus = as.numeric(two_step_knockouts$knockout_locus)
# Grab the locus index of the focal mutation. Default to the locus of the first mutation, switching to the second if the first is a 'G'
two_step_knockouts$mutant_locus = two_step_knockouts$first_mut_locus
two_step_knockouts[two_step_knockouts$first_mut_inst == 'G', ]$mutant_locus = two_step_knockouts[two_step_knockouts$first_mut_inst == 'G', ]$second_mut_locus
two_step_knockouts$mutant_locus = as.numeric(two_step_knockouts$mutant_locus)
# Grab the high-level functionality of the representative genotype at that loci
two_step_knockouts$previous_func = NA
two_step_knockouts = mutate(rowwise(two_step_knockouts), previous_func = df_cleaned[df_cleaned$knockout_id == (knockout_locus + 1),]$high_level_functionality)

# Condense tasks into phenotypes
two_step_knockouts$phenotype_odd_int = as.numeric(strtoi(two_step_knockouts$task_profile_odd, base=2))
two_step_knockouts$phenotype_even_int = as.numeric(strtoi(two_step_knockouts$task_profile_even, base=2))
one_step_muts$phenotype_odd_int = as.numeric(strtoi(one_step_muts$task_profile_odd, base=2))
one_step_muts$phenotype_even_int = as.numeric(strtoi(one_step_muts$task_profile_even, base=2))

# Variable used within for loop
task_order = c('not', 'nand', 'and', 'ornot', 'or', 'andnot')
task_masks = c(32, 16, 8, 4, 2, 1)
func_changes_count = c()
func_changes_frac = c()

# For EACH one-step mutant, calculate the average/median number of loci that change function when a mutation occurs
for(row_idx in 1:nrow(one_step_muts)){
  org = one_step_muts[row_idx,] # Grab 'focal' one-step mutant. Likewise, its one mutation will be called the 'focal mutation' in this loop
  if(org$first_mut_inst == 'G' | org$gest_time_even ==  0 | org$gest_time_odd == 0){ # Skip knockout mutants and inviable orgs
    next
  }
  # Grab the two-step mutants that incorproate the focal mutation (can be either the first or second mutation the way they were saved (to save space))
  org_knockouts = as.data.frame(two_step_knockouts[
    ((two_step_knockouts$first_mut == org$parent_muts) |  
       (two_step_knockouts$second_mut_locus == org$first_mut_locus & two_step_knockouts$second_mut_inst == org$first_mut_inst)) 
    ,] )
  # Add columns to knockouts using the focal org for easy comparison
  org_knockouts$base_phenotype_even_int = org$phenotype_even_int
  org_knockouts$base_phenotype_odd_int = org$phenotype_odd_int
  org_knockouts$base_gest_time_odd = org$gest_time_odd
  org_knockouts$base_gest_time_even = org$gest_time_even
  # Iterate through each of the six tasks
  for(task_id in 1:length(task_order)){
    task = task_order[task_id]
    task_mask = task_masks[task_id]
    task_key = paste0(task,'_category')
    org_knockouts[,task_key] = 'No category'
    # Determine whether the task was performed by the focal org or two-step mutant (in each environment)
    org_knockouts$even_knockout = bitwAnd(org_knockouts$phenotype_even_int, task_mask) / task_mask
    org_knockouts$odd_knockout = bitwAnd(org_knockouts$phenotype_odd_int, task_mask) / task_mask
    org_knockouts$even_base = bitwAnd(org_knockouts$base_phenotype_even_int, task_mask) / task_mask
    org_knockouts$odd_base = bitwAnd(org_knockouts$base_phenotype_odd_int, task_mask) / task_mask
    # Use this info to categorize rows into what effect they had on the task
    org_knockouts[org_knockouts$even_base == 0 & org_knockouts$odd_base == 0 & org_knockouts$even_knockout == 0 & org_knockouts$odd_knockout == 0,task_key] = 'No change'
    org_knockouts[org_knockouts$even_base == 0 & org_knockouts$odd_base == 0 & org_knockouts$even_knockout == 0 & org_knockouts$odd_knockout == 1,task_key] = 'Appear P'
    org_knockouts[org_knockouts$even_base == 0 & org_knockouts$odd_base == 0 & org_knockouts$even_knockout == 1 & org_knockouts$odd_knockout == 0,task_key] = 'Appear P'
    org_knockouts[org_knockouts$even_base == 0 & org_knockouts$odd_base == 0 & org_knockouts$even_knockout == 1 & org_knockouts$odd_knockout == 1,task_key] = 'Appear NP'
    org_knockouts[org_knockouts$even_base == 0 & org_knockouts$odd_base == 1 & org_knockouts$even_knockout == 0 & org_knockouts$odd_knockout == 0,task_key] = 'Loss P'
    org_knockouts[org_knockouts$even_base == 0 & org_knockouts$odd_base == 1 & org_knockouts$even_knockout == 0 & org_knockouts$odd_knockout == 1,task_key] = 'No change'
    org_knockouts[org_knockouts$even_base == 0 & org_knockouts$odd_base == 1 & org_knockouts$even_knockout == 1 & org_knockouts$odd_knockout == 0,task_key] = 'P Inversion'
    org_knockouts[org_knockouts$even_base == 0 & org_knockouts$odd_base == 1 & org_knockouts$even_knockout == 1 & org_knockouts$odd_knockout == 1,task_key] = 'Loss of P'
    org_knockouts[org_knockouts$even_base == 1 & org_knockouts$odd_base == 0 & org_knockouts$even_knockout == 0 & org_knockouts$odd_knockout == 0,task_key] = 'Loss P'
    org_knockouts[org_knockouts$even_base == 1 & org_knockouts$odd_base == 0 & org_knockouts$even_knockout == 0 & org_knockouts$odd_knockout == 1,task_key] = 'P Inversion'
    org_knockouts[org_knockouts$even_base == 1 & org_knockouts$odd_base == 0 & org_knockouts$even_knockout == 1 & org_knockouts$odd_knockout == 0,task_key] = 'No change'
    org_knockouts[org_knockouts$even_base == 1 & org_knockouts$odd_base == 0 & org_knockouts$even_knockout == 1 & org_knockouts$odd_knockout == 1,task_key] = 'Loss of P'
    org_knockouts[org_knockouts$even_base == 1 & org_knockouts$odd_base == 1 & org_knockouts$even_knockout == 0 & org_knockouts$odd_knockout == 0,task_key] = 'Loss NP'
    org_knockouts[org_knockouts$even_base == 1 & org_knockouts$odd_base == 1 & org_knockouts$even_knockout == 0 & org_knockouts$odd_knockout == 1,task_key] = 'Appear of P'
    org_knockouts[org_knockouts$even_base == 1 & org_knockouts$odd_base == 1 & org_knockouts$even_knockout == 1 & org_knockouts$odd_knockout == 0,task_key] = 'Appear of P'
    org_knockouts[org_knockouts$even_base == 1 & org_knockouts$odd_base == 1 & org_knockouts$even_knockout == 1 & org_knockouts$odd_knockout == 1,task_key] = 'No change'
  }
  # Dilute specific categories into broader categories so they can actually be used (either non, task machinery, plasticity machinery)
  for(task in task_order){
    category_col = paste0(task, '_category')
    func_col = paste0(task, '_functionality')
    org_knockouts[func_col] = 'None'
    plastic_mask = org_knockouts[,category_col] %in% c('P Inversion', 'Loss of P')
    org_knockouts[plastic_mask, func_col] = rep('Plasticity Machinery', sum(plastic_mask))
    task_mask = org_knockouts[,category_col] %in% c('Loss P', 'Loss NP')
    org_knockouts[task_mask,func_col] = rep('Task Machinery', sum(task_mask))
  }
  # Look for vestigial sites. Vestigial means that the site was used in a task, but it currently doesn't even though the instruction
  #   has not changed since
  org_knockouts = mutate(rowwise(org_knockouts), previous_not_functionality = df_cleaned[df_cleaned$knockout_id == (knockout_locus + 1),]$not_functionality)
  org_knockouts = mutate(rowwise(org_knockouts), previous_nand_functionality = df_cleaned[df_cleaned$knockout_id == (knockout_locus + 1),]$nand_functionality)
  org_knockouts = mutate(rowwise(org_knockouts), previous_and_functionality = df_cleaned[df_cleaned$knockout_id == (knockout_locus + 1),]$and_functionality)
  org_knockouts = mutate(rowwise(org_knockouts), previous_or_functionality = df_cleaned[df_cleaned$knockout_id == (knockout_locus + 1),]$or_functionality)
  org_knockouts = mutate(rowwise(org_knockouts), previous_andnot_functionality = df_cleaned[df_cleaned$knockout_id == (knockout_locus + 1),]$andnot_functionality)
  org_knockouts = mutate(rowwise(org_knockouts), previous_ornot_functionality = df_cleaned[df_cleaned$knockout_id == (knockout_locus + 1),]$ornot_functionality)
  org_knockouts = as.data.frame(org_knockouts)
  for(task in task_order){
    func_col = paste0(task, '_functionality')
    prev_func_col = paste0('previous_', task, '_functionality')
    mask =  org_knockouts$knockout_locus != org_knockouts$mutant_locus & # Mutation did not occur at this site
            org_knockouts[,func_col] == 'None' & # Site is not encoding task or plasticity machinery 
            org_knockouts[,prev_func_col] %in% c('Task Machinery', 'Previous Task Machinery') # Previously, this site encoded for a site 
    org_knockouts[mask,func_col] = rep('Previous Task Machinery', sum(mask))
  }
  
  # Summarize loci into even vs odd functionality
  none_str = 'None'
  task_str = 'Task Machinery'
  plastic_str = 'Plasticity Machinery'
  vestigial_str = 'Previous Task Machinery'
  org_knockouts$odd_functionality = none_str
  org_knockouts$even_functionality = none_str
  
  # Odd / ENV-A (not, and, or); *must* encode one task and maybe other 
  odd_task_mask = 
    (org_knockouts$not_functionality == task_str & 
      org_knockouts$and_functionality %in% c(task_str, none_str, vestigial_str, plastic_str) & org_knockouts$or_functionality %in% c(task_str, none_str, vestigial_str, plastic_str)) | 
    (org_knockouts$and_functionality == task_str &   
      org_knockouts$not_functionality %in% c(task_str, none_str, vestigial_str, plastic_str) & org_knockouts$or_functionality %in% c(task_str, none_str, vestigial_str, plastic_str)) | 
    (org_knockouts$or_functionality == task_str &   
      org_knockouts$and_functionality %in% c(task_str, none_str, vestigial_str, plastic_str) &   org_knockouts$not_functionality %in% c(task_str, none_str, vestigial_str, plastic_str)) 
  org_knockouts[odd_task_mask,]$odd_functionality = rep(task_str, sum(odd_task_mask))
  odd_vestigial_mask =  
    (org_knockouts$not_functionality == vestigial_str &  
      org_knockouts$and_functionality %in% c(vestigial_str, none_str) & org_knockouts$or_functionality %in% c(vestigial_str, none_str)) | 
    (org_knockouts$and_functionality == vestigial_str &
      org_knockouts$not_functionality %in% c(vestigial_str, none_str) & org_knockouts$or_functionality %in% c(vestigial_str, none_str)) | 
    (org_knockouts$or_functionality == vestigial_str & 
       org_knockouts$and_functionality %in% c(vestigial_str, none_str) & org_knockouts$not_functionality %in% c(vestigial_str, none_str)) 
  org_knockouts[odd_vestigial_mask,]$odd_functionality = rep(vestigial_str, sum(odd_vestigial_mask))
  odd_plastic_mask =  
    (org_knockouts$not_functionality == plastic_str &
      org_knockouts$and_functionality %in% c(plastic_str, none_str, vestigial_str) & org_knockouts$or_functionality %in% c(plastic_str, none_str, vestigial_str)) |
    (org_knockouts$and_functionality == plastic_str & 
      org_knockouts$not_functionality %in% c(plastic_str, none_str, vestigial_str) & org_knockouts$or_functionality %in% c(plastic_str, none_str, vestigial_str)) | 
    (org_knockouts$or_functionality == plastic_str &   
      org_knockouts$and_functionality %in% c(plastic_str, none_str, vestigial_str) & org_knockouts$not_functionality %in% c(plastic_str, none_str, vestigial_str)) 
  org_knockouts[odd_plastic_mask,]$odd_functionality = rep(plastic_str, sum(odd_plastic_mask))
  
  # Same thing for Even / ENV-B (nand, andnot, ornot)
  even_task_mask =  
    (org_knockouts$nand_functionality == task_str & 
      org_knockouts$andnot_functionality %in% c(task_str, none_str, vestigial_str, plastic_str) & org_knockouts$ornot_functionality %in% c(task_str, none_str, vestigial_str, plastic_str)) |
    (org_knockouts$andnot_functionality == task_str &   
      org_knockouts$nand_functionality %in% c(task_str, none_str, vestigial_str, plastic_str) & org_knockouts$ornot_functionality %in% c(task_str, none_str, vestigial_str, plastic_str)) |
    (org_knockouts$ornot_functionality == task_str &
       org_knockouts$andnot_functionality %in% c(task_str, none_str, vestigial_str, plastic_str) & org_knockouts$nand_functionality %in% c(task_str, none_str, vestigial_str, plastic_str)) 
  org_knockouts[even_task_mask,]$even_functionality = rep(task_str, sum(even_task_mask))
  even_vestigial_mask =  
    (org_knockouts$nand_functionality == vestigial_str &   
      org_knockouts$andnot_functionality %in% c(vestigial_str, none_str) & org_knockouts$ornot_functionality %in% c(vestigial_str, none_str)) |
    (org_knockouts$andnot_functionality == vestigial_str & 
       org_knockouts$nand_functionality %in% c(vestigial_str, none_str) &   org_knockouts$ornot_functionality %in% c(vestigial_str, none_str)) |
    (org_knockouts$ornot_functionality == vestigial_str & 
       org_knockouts$andnot_functionality %in% c(vestigial_str, none_str) &   org_knockouts$nand_functionality %in% c(vestigial_str, none_str)) 
  org_knockouts[even_vestigial_mask,]$even_functionality = rep(vestigial_str, sum(even_vestigial_mask))
  even_plastic_mask =  
    (org_knockouts$nand_functionality == plastic_str & 
       org_knockouts$andnot_functionality %in% c(plastic_str, none_str, vestigial_str) & org_knockouts$ornot_functionality %in% c(plastic_str, none_str, vestigial_str)) |
    (org_knockouts$andnot_functionality == plastic_str & 
       org_knockouts$nand_functionality %in% c(plastic_str, none_str, vestigial_str) & org_knockouts$ornot_functionality %in% c(plastic_str, none_str, vestigial_str))  |
    (org_knockouts$ornot_functionality == plastic_str &   
       org_knockouts$andnot_functionality %in% c(plastic_str, none_str, vestigial_str) &   org_knockouts$nand_functionality %in% c(plastic_str, none_str, vestigial_str)) 
  org_knockouts[even_plastic_mask,]$even_functionality = rep(plastic_str, sum(even_plastic_mask))
  
  
  # Determine high level functionality using even and odd summaries
  org_knockouts$high_level_functionality = 'Other' # Useful for testing. We should *not* see other in the final output
  org_knockouts$gest_time_even = as.numeric(org_knockouts$gest_time_even)
  org_knockouts$gest_time_odd = as.numeric(org_knockouts$gest_time_odd)
  org_knockouts$base_gest_time_even = as.numeric(org_knockouts$base_gest_time_even)
  org_knockouts$base_gest_time_odd = as.numeric(org_knockouts$base_gest_time_odd)
  # Truly none
  mask = org_knockouts$odd_functionality == none_str & org_knockouts$even_functionality == none_str
  org_knockouts[mask,]$high_level_functionality = rep('None', sum(mask))
  # Replication machinery
  mask = org_knockouts$gest_time_odd > (org_knockouts$base_gest_time_odd + 2) | org_knockouts$gest_time_even > (org_knockouts$base_gest_time_even + 2)
  org_knockouts[mask,]$high_level_functionality = rep('Replication Machinery', sum(mask))
  # Task Machinery
  mask = org_knockouts$odd_functionality == task_str & org_knockouts$even_functionality == none_str
  org_knockouts[mask,]$high_level_functionality = rep('Odd Task Machinery', sum(mask))
  mask = org_knockouts$odd_functionality == none_str & org_knockouts$even_functionality == task_str
  org_knockouts[mask,]$high_level_functionality = rep('Even Task Machinery', sum(mask))
  mask = org_knockouts$odd_functionality == task_str & org_knockouts$even_functionality == task_str
  org_knockouts[mask,]$high_level_functionality = rep('Both Task Machinery', sum(mask))
  # Vestigials
  mask = org_knockouts$odd_functionality == vestigial_str & org_knockouts$even_functionality == none_str
  org_knockouts[mask,]$high_level_functionality = rep('Vestigial Odd', sum(mask))
  mask = org_knockouts$odd_functionality == none_str & org_knockouts$even_functionality == vestigial_str
  org_knockouts[mask,]$high_level_functionality = rep('Vestigial Even', sum(mask))
  mask = org_knockouts$odd_functionality == vestigial_str & org_knockouts$even_functionality == vestigial_str
  org_knockouts[mask,]$high_level_functionality = rep('Both Vestigial', sum(mask))
  # Recycling
  mask = org_knockouts$odd_functionality == task_str & org_knockouts$even_functionality == vestigial_str
  org_knockouts[mask,]$high_level_functionality = rep('Odd Recycled Even', sum(mask))
  mask = org_knockouts$odd_functionality == vestigial_str & org_knockouts$even_functionality == task_str
  org_knockouts[mask,]$high_level_functionality = rep('Even Recycled Odd', sum(mask))
  # Plasticity
  mask = org_knockouts$odd_functionality == plastic_str & org_knockouts$even_functionality == none_str
  org_knockouts[mask,]$high_level_functionality = rep('Odd Plastic Machinery', sum(mask))
  mask = org_knockouts$odd_functionality == none_str & org_knockouts$even_functionality == plastic_str
  org_knockouts[mask,]$high_level_functionality = rep('Even Plastic Machinery', sum(mask))
  mask = org_knockouts$odd_functionality == plastic_str & org_knockouts$even_functionality == plastic_str
  org_knockouts[mask,]$high_level_functionality = rep('Both Plastic Machinery', sum(mask))
  # Task + plastic
  mask = org_knockouts$odd_functionality == task_str & org_knockouts$even_functionality == plastic_str
  org_knockouts[mask,]$high_level_functionality = rep('Odd task, even plastic', sum(mask))
  mask = org_knockouts$odd_functionality == plastic_str & org_knockouts$even_functionality == task_str
  org_knockouts[mask,]$high_level_functionality = rep('Even task, odd plastic', sum(mask))
  # Plastic + vestigial
  mask = org_knockouts$odd_functionality == plastic_str & org_knockouts$even_functionality == vestigial_str
  org_knockouts[mask,]$high_level_functionality = rep('Odd plastic, even vestigial', sum(mask))
  mask = org_knockouts$odd_functionality == vestigial_str & org_knockouts$even_functionality == plastic_str
  org_knockouts[mask,]$high_level_functionality = rep('Even plastic, odd vestigial', sum(mask))
  # Required
  mask = org_knockouts$gest_time_even == 0 | org_knockouts$gest_time_odd == 0
  org_knockouts[mask,]$high_level_functionality = rep('Required', sum(mask))
  
  # Does has the function of this site changed?
  org_knockouts$func_match = org_knockouts$high_level_functionality ==  org_knockouts$previous_func
  num_changes = sum(!org_knockouts$func_match) # The actual number of sites that changed function
  func_changes_count = c(func_changes_count,  num_changes)
  frac_changes = sum(!org_knockouts$func_match) / nrow(org_knockouts) # The _fraction_ of sites that changed function
  func_changes_frac = c(func_changes_frac,  frac_changes)
  cat(row_idx, '[', frac_changes, ']', '   ') # Visual indicator of progress
}
cat('\n')

# Create a small data frame and save it to file
df_out = data.frame(data = matrix(nrow = 1, ncol = 0))
df_out$mean_frac_changes = mean(func_changes_frac)
df_out$median_frac_changes = median(func_changes_frac)
df_out$mean_count_changes = mean(func_changes_count)
df_out$median_count_changes = median(func_changes_count)
write.csv(df_out, './mutant_func_changes.csv')

