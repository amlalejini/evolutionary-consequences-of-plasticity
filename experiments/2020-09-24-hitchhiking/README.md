# 2020-09-24 - Hitchhiking Exploratory Experiments

Plasticity stabilizes the population's location in the fitness landscape. Does this stability affect the prevalence of hitchhiking?

Are plastic populations able to support low-payoff and more complex additional metabolic activity?

Two-phase experiment

- Phase 1
  - Fluctuate environment between envA and envB
    - envA: 3 of the first 6 logic-9 tasks
    - envB: 3 of the first 6 logic-9 tasks
- Phase 2
  - Fluctuate environment between envA and envB
    - (environments A and B are same as in phase 1)
  - Add extra 'hitchhiker' instructions.
    - Hitchhiker instructions
      - prob_die - chance of death on execution
      - poison - decrements merit on execution
      - nop-x - neutral control instruction (does nothing)

Relevant avida parameters

- KABOOM_PROB
- POISON_PENALTY
  - `double poison_multiplier = 1.0 - m_world->GetConfig().POISON_PENALTY.Get();`

Takeaways

- Need to control genome length!
- Poison and prob-die similar dynamics. Probably do subsequent experiments with poison instruction (simpler dynamics).
