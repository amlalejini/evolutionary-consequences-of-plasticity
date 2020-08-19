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