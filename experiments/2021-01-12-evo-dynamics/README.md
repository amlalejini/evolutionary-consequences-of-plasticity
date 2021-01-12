# 2021-01-12 - evolutionary dynamics experiment

In these runs, we compare the evolutionary dynamics of non-plastic populations with the evolutionary dynamics of populations in which plasticity evolved.

Conditions

- Non-plastic (no-sensors), fluctuating environment
- Plastic (sensors), fluctuating environment
- Non-plastic (no-sensors), constant environment

This experiment is conducted in two phases. In the first phase, we evolve populations for 200K updates. In the second phase, we evolve populations for another 200K updates; however, for sensor-enabled populations in fluctuating environments, we only transfer plastic populations to the second phase.

Important configuration details

- Genomes are variables length (mutations: substitution, insertion, and deletion)