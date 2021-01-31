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

## Controls to do

- [ ] Hitchhiking
  - Repeat hitchhiking experiments, but use half of tasks for constant environment to confirm that results are not driven by extra machinery required in genome by ENV-ALL and plasticity conditions
    - deleterious: const-ENV-A, const-ENV-B
    - neutral: const-ENV-A, const-ENV-B

## Experiments

### 2020-10-07

Experiments

- (1) Extra metabolic tasks
  - Constant, u100
  - Try different reward levels for extra tasks
    - null rewards, too
- (2) Bottlenecking control
  - Is it that plasticity is stabilizing the population against repeated bottlenecking (due to frequent sweeps)?
  - Periodically cull the plastic population in phase 2
    - Keep 10, 20, 50%
- (3) architecture evolvability
  - Is it that the non-plastic architectures are less evolvable than the plastic architectures?
  - Is it that the plastic architectures are move evolvable than non-plastic architectures?
  - Move non-plastic and plastic architectures to
    - constant phase 2

## 2021-01-07 - validation

In these runs, we confirm our expectation that plasticity will evolve in a fluctuating environment when populations have access to sensory instructions.

Conditions

- Constant environment
  - sensors, no sensors
- Changing environment
  - sensors, no sensors

We only expect adaptive plasticity to evolve in the changing environment with sensors. In all other conditions, we do not expect to observe the evolution of adaptive plasticity.

## 2021-01-12 - evolutionary dynamics

In these runs, we compare the evolutionary dynamics of non-plastic populations with the evolutionary dynamics of populations in which plasticity evolved.

Conditions

- Non-plastic (no-sensors), fluctuating environment
- Plastic (sensors), fluctuating environment
- Non-plastic (no-sensors), constant environment

This experiment is conducted in two phases. In the first phase, we evolve populations for 200K updates. In the second phase, we evolve populations for another 200K updates; however, for sensor-enabled populations in fluctuating environments, we only transfer plastic populations to the second phase.

## 2021-01-14 - complex features

In these runs, we compare the capacity for plastic and non-plastic populations to evolve and retain complex features in fluctuating environments.

Conditions

- Non-plastic (no-sensors), fluctuating environment
- Plastic (sensors), fluctuating environment
- Non-plastic (no-sensors), constant environment

This experiment is conducted in two phases. In the first phase, we evolve populations for 200K updates. In the second phase, we evolve populations for another 200K updates; however, for sensor-enabled populations in fluctuating environments, we only transfer plastic populations to the second phase.

Controls/next steps

- control genome length
- repeat experiment with more extreme rewards/punishments for fluctuating tasks

## 2021-01-20 - complex features - fixed genome length

In these runs, we repeat our 2021-01-14 experiments, except we fix genome lengths of digital organisms. Additionally, we reduce the number of replicates due to constraints on computational resources.

## 2021-01-21 - complex features - task value

In these runs, we repeat our 2021-01-20 experiments, except we make the rewards and punishments for the fluctuating tasks more extreme (two-fold to four-fold effect).

## 2021-01-23 - hitchhiking

In these runs, we investigate the propensity for deleterious hitchhiking in plastic and non-plastic populations.
