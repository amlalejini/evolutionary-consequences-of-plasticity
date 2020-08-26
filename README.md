# How does phenotypic plasticity affect the evolution of complex traits?

We use avida to evaluate the affect of phenotypic plasticity on the evolution of complex features.

- The _capacity_ for plasticity?
- Pre-existing plasticity?

Rationale

Changing environments can facilitate the evolution of complex features. Plasticity counteracts environmental change from the perspective of a genotype.

## Modifications to Avida

- Reaction sensor instructions
  - Inst_SenseReactNAND, ...

## Experiments

- Capacity for plasticity
  - Evolve populations with access to sensors (sensors+) and populations without access to sensors (sensors-).
  - Environments:
    - fluctuating (sensors+ vs sensors-)
      - [NOT, AND, OR, NOR | NAND, ORN, ANDN, XOR], EQU
    - constant (sensors+ vs sensors-)
      - NOT, AND, OR, NOR NAND, ORN, ANDN, XOR, EQU
  - Measure number of populations that achieve EQU
- Pre-existing plasticity
  - Two-phase experiment: evolve populations (sensors+) for X generations with no reward for EQU. 'Freeze' plastic genotypes.
  - Seed populations with plastic ancestors. Seed equal number of populations with non-plastic ancestors (evolved w/out sensors).

## TODO

- Data collection
  - mutation accumulation data
