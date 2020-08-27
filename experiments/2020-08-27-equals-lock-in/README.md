# 2020-08-27 Experiment Notes

Begin to tease apart why the first experiment showed replicates in the u300 enviornment often evolve EQUALS at some point in the lineage, but lose EQUALS by the final dominant organism. 

To test this, we bump the reward for EQUALS to be greater than or equal to the punshisment incurred by doing the wrong set of tasks in the environment

Conditions:
  - Constant rewards, original EQU reward: "-set EVENT_FILE events-const.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0"
  - Constant rewards, EQU reward equal to (would be) punishment: "-set EVENT_FILE events-const-equal.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0"
  - Constant rewards, EQU reward equal to 2x (would be) punishment: "-set EVENT_FILE events-const-greater.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0"
  - 30 updates per fluctuation, original EQU reward: "-set EVENT_FILE events-chg-u30.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0"
  - 30 updates per fluctuation, EQU reward equal to punishments: "-set EVENT_FILE events-chg-u30-equal.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0"
  - 30 updates per fluctuation, EQU reward equal to 2x punishments: "-set EVENT_FILE events-chg-u30-greater.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0"
  - 300 updates per fluctuation, original EQU reward: "-set EVENT_FILE events-chg-u300.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0"
  - 300 updates per fluctuation, EQU reward equal to punishments: "-set EVENT_FILE events-chg-u300-equal.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0"
  - 300 updates per fluctuation, EQU reward equal to 2x punishments: "-set EVENT_FILE events-chg-u300-greater.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0"
