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