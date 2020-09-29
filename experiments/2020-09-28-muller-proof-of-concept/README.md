# 2020-09-28 - Proof of concept runs for Muller plots

Pipeline

- Grab rando seed organisms
  - Selected seeds from phase-two seeds from 2020-09-03-pop-dynamics experiment.
- Use seed genotypes as ancestors. Run for N updates with full phylogeny tracking. Snapshot at resolution you want for muller plot.
- Extract sequences from phylogeny snapshots into single .spop file (use `analysis/phylogeny_seqs_to_detail.py` script)
- Run sequence spop file (generated in previous step) through analyze mode, output detail file with phenotypes.
- Build a genotype:phenotype lookup table (use `analysis/build_genotype_phenotype_map.py` script)
  - e.g., `python3 build_genotype_phenotype_map.py --run_dir ../runs/c100_s0/`
- Convert phylogeny data into format expected by muller plotting tool (in this case, ggmuller).
  - For ggmuller, you can use ./analysis/extract_muller_data.py.
  - e.g., `python3 extract_muller_data.py --run_dir ../runs/c100_s0/ --output_prefix c100-s0-test`
- Generate muller plot! (using ggmuller, see analysis/2020-09-28.Rmd)

Conditions

- c0 s0
- c30 s0
- c30 s1
- [x] c100 s0
- c100 s1

Observations

- u30 no sensors condition => phenotype switching didn't consistently evolve. Many runs just ignore tasks.
