# 2020-08-19 Experiment Notes

Two-phase experiment. Evolve populations under different phase-1 conditions for X updates. After
X updates, introduce new tasks, but keep phase-1 environment as background.

Measure how many populations evolve to perform new tasks, and how long it took.

Also, change the reward structure to make task rewards/punishments less extreme.

## Things to change for next time

- This aggregate script is a little gross.
  - For multi-phased experiments, it's probably cleaner to have each dominant genotype in its own .gen file (from avida analyze mode)