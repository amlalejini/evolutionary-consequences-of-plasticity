# 2020-09-28 - Proof of concept runs for Muller plots

Pipeline

- Grab rando seed organisms
  - Select seeds from phase-two seeds from 2020-09-03-pop-dynamics experiment.
- Use seed genotypes as ancestors. Run for N updates with full phylogeny tracking (`-set SYSTEMATICS_TRACK_ALL 1`).
- Convert phylogeny data into format expected by muller plotting tool (in this case, ggmuller).
  - For ggmuller, you can use ./analysis/extract_muller_data.py.
- Generate muller plot! (using ggmuller, see analysis/2020-09-28.Rmd)

Conditions

- c0 s0
- c30 s0
- c30 s1
- [x] c100 s0
- c100 s1

Observations

- u30 no sensors condition => phenotype switching didn't consistently evolve. Many runs just ignore tasks.
