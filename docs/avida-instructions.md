# Avida instruction set

## Default instructions

We used the following default instructions in all of our experiments:

```
# No-ops
INST nop-A
INST nop-B
INST nop-C

# Flow control operations
INST if-n-equ
INST if-less
INST if-label
INST mov-head
INST jmp-head
INST get-head
INST set-flow

# Single Argument Math
INST shift-r
INST shift-l
INST inc
INST dec
INST push
INST pop
INST swap-stk
INST swap

# Double Argument Math
INST add
INST sub
INST nand

# Biological Operations
INST h-copy
INST h-alloc
INST h-divide

# I/O and Sensory
INST IO
INST h-search
```

Each of these instructions is described in the [Avida documentation](https://github.com/devosoft/avida/wiki/Instruction-Set).

## Custom instructions

We implemented several custom instructions for this work:

- `INST sense-react-NAND`
  - Provides sensory feedback on whether the NAND Boolean logic task is currently rewarded or punished by pushing a 1 to the organism's active stack if it is rewarded, a -1 if it is punished, and a 0 if it is neither rewarded nor punished.
- `INST sense-react-NOT`
  - Provides sensory feedback on whether the NOT Boolean logic task is currently rewarded or punished by pushing a 1 to the organism's active stack if it is rewarded, a -1 if it is punished, and a 0 if it is neither rewarded nor punished.
- `INST sense-react-AND`
  - Provides sensory feedback on whether the AND Boolean logic task is currently rewarded or punished by pushing a 1 to the organism's active stack if it is rewarded, a -1 if it is punished, and a 0 if it is neither rewarded nor punished.
- `INST sense-react-ORN`
  - Provides sensory feedback on whether the ORN Boolean logic task is currently rewarded or punished by pushing a 1 to the organism's active stack if it is rewarded, a -1 if it is punished, and a 0 if it is neither rewarded nor punished.
- `INST sense-react-OR`
  - Provides sensory feedback on whether the OR Boolean logic task is currently rewarded or punished by pushing a 1 to the organism's active stack if it is rewarded, a -1 if it is punished, and a 0 if it is neither rewarded nor punished.
- `INST sense-react-ANDN`
  - Provides sensory feedback on whether the ANDN Boolean logic task is currently rewarded or punished by pushing a 1 to the organism's active stack if it is rewarded, a -1 if it is punished, and a 0 if it is neither rewarded nor punished.
- `INST poison`
  - Each time `poison` is executed, the organism reduces the metabolic rate of the organism by a fixed rate (specified by `POISON_PENALTY` in `avida.cfg`).
