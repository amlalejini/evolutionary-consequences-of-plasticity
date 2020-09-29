# Experiment Log

Most experiments have README notes in each of their directories.

Here, we log information/changes that are not necessarily experiment specific.

## Code dependencies

Both 2020-08-17-capacity and 2020-08-19-phased use vanilla avida (the most recent Avida commit as of 2020-08-17).

2020-08-26 Avida merged with Avida+Empirical mashup version (from Dolson et al.'s Interpreting the Tape
of Life paper). We updated the code base to compile successfully against a newer version of Empirical.
This version: <https://github.com/amlalejini/Empirical/tree/2020-avida-plasticity>.

We automate various aspects of our experiment pipeline with Python scripts. These scripts require a variety of python packages be installed. We recommend using python virtual environments:

```bash
python3 -m venv pyenv
source pyenv/bin/activate
pip3 install -r requirements.txt
```

## Plans

Experimental knobs and levers

- Nutrients/tasks configurations
  - Temporal dynamics
    - all reward
    - half reward (env. A & env. B)
    - Fluctuating between rewarding/punishing task sets A and B
  - Task sets
    - (1) First 6 tasks, divided into A set and B set
    - (2) Use next 3 tasks as minimal-reward additional nutrients
    - (3) Use one (or maybe more) 3-input tasks as minimal-reward additional nutrients
- Sensors
  - Sensors+, Sensors-
- Fluctuation rates
  - u0 (constant), u3, u10, u30, u100, u300, u1000
- Overall design
  - Single phase - look at conditions with and without capacity for plasticity
  - Two phase - evolve populations with time to adapt to environment. 'Transfer' to fresh media.
    Use only phase two measurements.

Hitchhiker instruction options

- Inst_Prob_Die
  - When executed, there is a chance that the organism dies.
  - Relevant configuration parameter: KABOOM_PROB
- Inst_Poison
  - Relevant configuration parameter: POISON_PENALTY
- NOTE: we'll also want a completely neutral instruction to compare prevalence with.
  - Neutral instructions (we only need one): nop-X, nop-Y
  - Useful event: PrintInstructionData

Expected changes in population dynamics as a result of access to plasticity

- Non-plastic populations should have increased number of selective sweeps.
  - Predict greater numbers of MRCA changes
  - Shallower phylogenies
- Non-plastic populations experience more 'bottlenecking' events

Consequences of change in population dynamics

- Increased hitchhiking in non-plastic populations?
  - Measure hitchhiking instruction prevalence (as compared to nop-x) population-wide over time and
    along lineage (for lineage, need to output all instructions...).
  - Measure number of deleterious steps in lineage.
- Plastic populations see fewer bottleneck events. We expect to see more standing variation in
  plastic populations?
- Are plastic populations able to support low-payoff and more complex additional metabolic activity?
- Are there life history effects?
  - e.g., lifespan?
- Are non-plastic populations in a different part of the fitness landscape than plastic populations?
  - non-plastic populations more easily switch phenotypes via mutation
- Genetic architecture differences?

Experiments

- (1) Establish baseline expectations for population dynamics.
  - Experimental design: single phase (if noisy, move to double phase)
  - Environmental change rates: u0 (constant), u3, u10, u30, u100, u300, u1000
  - Sensors: sensors+, sensors-
  - Questions/analyses
    - Is there a difference between sensors+, sensors- for a given change rate?
    - Are sensors+ populations more similar to constant (sensors-)
  - Axes of comparison
    - MRCA changes (selective sweeps)
    - Standing variation (number of distinct genotypes) over time
    - Phylogenetic diversity
  - Number of replicates: 50?
- [maybe] Test expectations for population dynamics.
  - Same as above, but use two-phase experiment.
- Evolutionary consequences: genetic architecture, position in fitness landscape
- Evolutionary consequences: novel metabolic pathways.
- Evolutionary consequences: hitchhiking
  - try both Inst_Poison and Inst_Prob_Die (be sure to include nop-X)
- Supplemental experiments
  - Qualitatively reproduce results at different reward structures.
- Bottlenecking experiment?
  - Instead of fluctuating environment, bottleneck population at regular intervals.
  - Relevant avida parameter: KillProb

Investigating the consequences of plasticity

- Testing sweeps
  - use intermittent culls/bottlenecking events
  - contingency experiments
    - seed phase two with ancestor just before it evolves plasticity and just after it evolves plasticity (disallow plasticity too?)
  - Genome length
    - Look at genome length, can control with fixed length genomes
  - Execution length
  - Is it the fact that the plastic genomes have more building blocks in the genome?

Decisions to be made

- What level of rewards/punishments do we use?
- Use two phase or one phase experimental design?
  - Two phase is more complicated, but will probably be cleaner.
  - One phase is simpler, but does not guarantee all sensor+ populations actually exhibit plasticity.
- Which novel metabolic pathways (i.e., tasks) should we include for relevant experiments?
  - if we just fluctuate the first 6 tasks, we have the next 3 logic 9 tasks to use
  - we could also use all of the 3-input logic tasks as extra pathways (just make sure the sum of their rewards don’t exceed the reward for doing a single of the rewarded fluctuating tasks)
- What supplemental experiments will we need to evaluate the robustness of results?

Supplemental experiments

- Numerical model & maybe simplified agent-based model (bitstrings?)
- Reward structure
- What if the type of environmental fluctuation was different?
  - e.g., rewards varied smoothly instead of discrete reward & punishment stages
- If we were to make environments A and B less different (e.g., only cycle rewards / punishments for four "easiest" tasks), would we see this difference shrink?