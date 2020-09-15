# 2020-09-03 Population Dynamics - Two Phase

The goal of these runs is to further refine baseline expectations for population dynamics.
This is a continuation of the 8/28/2020 population dynamics experiment

Details

- Experimental design: two phase
    - First phase runs for 200k updates for all configurations
    - If sensors are not present, automatically run phase 2 for 200k additional updates
    - If sensirs _are_ present, only run the extra 200k updates if perfect plasticity evolved in the first phase 
    - Perfect plasticity = Responding to all rewarded tasks and no punished tasks regardless of which environmen is active
- Environmental change rates: u0 (constant), u3, u10, u30, u100, u300, u1000
- Sensors: sensors+, sensors-
- Questions/analyses
  - Is there a difference between sensors+, sensors- for a given change rate?
  - Are sensors+ populations more similar to constant (sensors-)?
- Axes of comparison
  - MRCA changes (selective sweeps)
  - Standing variation (number of distinct genotypes) over time
  - Phylogenetic diversity
- Number of replicates: 50

Some concerns

- Should we be collecting data at a higher resolution to better capture u3/u10/u30 temporal dynamics?
