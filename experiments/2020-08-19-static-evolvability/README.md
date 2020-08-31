# 2020-08-17 Experiment Notes

Validate that there is no significant differences stemming from which set of tasks are rewarded. 

There are 9 logic tasks, with multiple "tiers" of reward from 1 to 5. Tiers 1 through 4 each have two tasks, while tier 5 has only one task (EQUALS).
Here we test the evolution of EQUALS when rewarding each of the 16 combinations stemming from rewarding _exactly one_ task from _each_ of tiers 1-4. 
EQUALS is always rewarded. 
An additional control run (configuration #16) rewards _all_ tasks

These environments are constant throughout the run, and sensors are not present.  


Conditions: (replace XX with a number in the range [00,16])
  - "-set EVENT_FILE events-const-XX.cfg -set COPY_MUT_PROB 0.0025 -set DISABLE_REACTION_SENSORS 1 -set REACTION_SENSORS_NEUTRAL 0.0"
