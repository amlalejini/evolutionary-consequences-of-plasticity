# 2020-08-17 Experiment Notes

Exploratory runs.

Changing environment with and without sensors.

Conditions:
  - "-set EVENT_FILE events-chg-u30.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 0 -set REACTION_SENSORS_NEUTRAL 0.0"
  - "-set EVENT_FILE events-chg-u30.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0"
  - "-set EVENT_FILE events-chg-u300.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 0 -set REACTION_SENSORS_NEUTRAL 0.0"
  - "-set EVENT_FILE events-chg-u300.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0"
  - "-set EVENT_FILE events-const-all.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 0 -set REACTION_SENSORS_NEUTRAL 0.0"
  - "-set EVENT_FILE events-const-all.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0"

## Pipeline

- Use gen-sub script to generate HPCC experiment submission file.
  - this should take care of running the experiment (--run_experiment option) and running avida analyze mode (--run_analysis option)
- Use aggregate script to collect experiment data into single csv

## Findings

- the maybe neat result is that just turning sensors on dramatically changes the dynamics in the rapidly fluctuating environment
- I think this experimental setup is a little on the messy side to say too much about how pre-existing plasticity affects the evolution of more complex traits
- yeah, maybe the capacity for plasticity is having an impact
- maybe a neat result is that even though the u30 sensor-enabled populations see fewer generations, they evolve equals more often than sensor-disabled u30 populations

Discussion from slack:

(1) To me, the most striking result from this experiment is that just enabling sensors (and thus plasticity) makes the evolutionary history of populations evolving in a fluctuating environment look more like the evolutionary history of populations evolving in a constant environment than like populations evolving in the same fluctuating environment but without sensors. This is exactly what I expected, but it’s nice to see so clearly. (edited)

(2) Pre-existing plasticity seems like it might impact the evolution of more complex tasks. Not sure if this is a genetic architecture/evolvability thing or a population dynamics thing. This might depend on the rate/type of fluctuations.

(3) EQUALS evolved more often in the constant environment than in the fluctuating environment. I’m not totally sure what to make of this. But it sort of goes against the whole changing environments promote evolvability theory. I’m guessing the type of ‘evolvability’ matters. Are we looking at a different type of evolvability than what Luis and Rose have looked at in their related work?

Some next steps:

- A 2-phase evolution experiment where phase-1 rewards/punishes a set of tasks, let’s say tasks A, B, C, D. Phase 2 maintains the same background environment as phase 1 (depending on treatment) but introduces a new task, E (or new set of tasks) that is always rewarded. Because task E is introduced after populations have adapted to phase 1, it’s a little cleaner to make statements about pre-existing plasticity.
- dig more into evolutionary histories/population dynamics => this involves thinking more about hypotheses we have about how plasticity affects evolutionary dynamics and then making sure we can track the requisite data
- poke at the genetic architectures a bit to see if they differ (constant vs. fluctuating w/sensors vs fluctuating w/out sensors)
  - compute coding region for each task
  - look at graph properties
    - compare, cluster(?)

re (3): as far as I’m aware, most avida work with fluctuating environments and evolvability measures how many mutations change the phenotype. but often these phenotypic changes turn on/off traits that are relevant to the fluctuating environment — not resulting in entirely new phenotypic traits