# 2021-01-20 - Evolution of complex features experiment - fixed genome length

In these runs, we repeat our 2021-01-14 experiments, except we fix genome lengths of digital organisms. Additionally, we reduce the number of replicates due to constraints on computational resources.

Conditions

- Non-plastic (no-sensors), fluctuating environment
- Plastic (sensors), fluctuating environment
- Non-plastic (no-sensors), constant environment

Extra task values

- x1 (no selection)
- x1.03
- x1.10
- x1.30

Setting changes for controlling genome length:

- DIVIDE_INS_PROB 0.0
- DIVIDE_DEL_PROB 0.0
- OFFSPRING_SIZE_RANGE 1.0