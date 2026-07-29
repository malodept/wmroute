# Frozen audit comparisons

Negative candidate-minus-reference decision cost favours the
prediction-interface router.

| Evaluation | Reference | Difference | 95% interval | Gate |
|---|---|---:|---:|:---:|
| PushT V107 | Current-DINO + actions | -0.002549 | [-0.002867, -0.002238] | Pass |
| PyBullet V104E | Fixed Medium | -0.003677 | [-0.003805, -0.003553] | Pass |
| PyBullet V104E | Fixed Full | -0.003746 | [-0.003880, -0.003613] | Pass |
| PyBullet V104E | Margin sequential matched-rate | -0.002800 | [-0.002902, -0.002698] | Pass |
| PyBullet V104E | Random input matched-rate | -0.003668 | [-0.003773, -0.003565] | Pass |
| PushT V106 | Fixed Medium | -0.004308 | [-0.004759, -0.003857] | Pass |
| PushT V106 | Fixed Full | -0.002577 | [-0.003001, -0.002159] | Pass |
| PushT V106 | Task-only input router | -0.002620 | [-0.003037, -0.002213] | Pass |
| PushT V106 | Margin sequential matched-rate | -0.003294 | [-0.003700, -0.002891] | Pass |
| PushT V106 | Expected random input matched-rate | -0.003591 | [-0.003949, -0.003239] | Pass |
