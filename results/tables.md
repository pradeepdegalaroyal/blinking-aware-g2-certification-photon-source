### Table 0 (E0): peak-area model against the pulse-level simulation

| quantity | observed | model or truth | 95% interval |
|---|---|---|---|
| side-peak envelope, mean abs. relative deviation | 0.0045 | 0.0000 | - |
| central peak / plateau | 0.2106 | 0.2040 | - |
| g2(0) estimate, naive_far | 0.1296 | 0.1000 | [0.116, 0.144] |
| g2(0) estimate, envelope | 0.1063 | 0.1000 | [0.095, 0.118] |

### Table 1 (E1): selected blinking cells, true g2(0) = 0.03, A = 400

| b | tau_b | estimator | bias | RMSE | 95% coverage |
|---|---|---|---|---|---|
| 0 | 30 | naive, all 40 side peaks | 0.0001 ± 0.0005 | 0.0208 ± 0.0020 | 0.944 ± 0.029 |
| 0 | 30 | naive, 20 outer side peaks | 0.0000 ± 0.0004 | 0.0208 ± 0.0019 | 0.941 ± 0.033 |
| 0 | 30 | envelope fit (proposed) | 0.0003 ± 0.0004 | 0.0203 ± 0.0018 | 0.939 ± 0.030 |
| 0.5 | 3 | naive, all 40 side peaks | 0.0120 ± 0.0014 | 0.0235 ± 0.0014 | 0.919 ± 0.015 |
| 0.5 | 3 | naive, 20 outer side peaks | 0.0163 ± 0.0015 | 0.0263 ± 0.0016 | 0.887 ± 0.021 |
| 0.5 | 3 | envelope fit (proposed) | 0.0007 ± 0.0010 | 0.0140 ± 0.0007 | 0.957 ± 0.020 |
| 0.5 | 30 | naive, all 40 side peaks | -0.0153 ± 0.0014 | 0.0234 ± 0.0008 | 0.853 ± 0.015 |
| 0.5 | 30 | naive, 20 outer side peaks | -0.0070 ± 0.0015 | 0.0199 ± 0.0007 | 0.935 ± 0.007 |
| 0.5 | 30 | envelope fit (proposed) | 0.0004 ± 0.0011 | 0.0148 ± 0.0007 | 0.943 ± 0.014 |
| 1 | 10 | naive, all 40 side peaks | 0.0003 ± 0.0016 | 0.0188 ± 0.0015 | 0.955 ± 0.011 |
| 1 | 10 | naive, 20 outer side peaks | 0.0214 ± 0.0017 | 0.0302 ± 0.0006 | 0.820 ± 0.019 |
| 1 | 10 | envelope fit (proposed) | 0.0002 ± 0.0009 | 0.0113 ± 0.0008 | 0.952 ± 0.014 |
| 1 | 30 | naive, all 40 side peaks | -0.0245 ± 0.0004 | 0.0291 ± 0.0009 | 0.680 ± 0.025 |
| 1 | 30 | naive, 20 outer side peaks | -0.0111 ± 0.0003 | 0.0205 ± 0.0013 | 0.897 ± 0.038 |
| 1 | 30 | envelope fit (proposed) | 0.0016 ± 0.0004 | 0.0119 ± 0.0011 | 0.957 ± 0.016 |
| 1 | 100 | naive, all 40 side peaks | -0.0418 ± 0.0018 | 0.0439 ± 0.0018 | 0.212 ± 0.044 |
| 1 | 100 | naive, 20 outer side peaks | -0.0375 ± 0.0019 | 0.0400 ± 0.0018 | 0.313 ± 0.051 |
| 1 | 100 | envelope fit (proposed) | -0.0248 ± 0.0016 | 0.0275 ± 0.0015 | 0.532 ± 0.051 |

### Table 2 (E2): counts for 90% certification power (good source 0.03, threshold 0.05)

| blinking | estimator | smallest A reaching 90% power | seeds reaching it (of 5) | power at A = 3200 | coverage at A = 3200 |
|---|---|---|---|---|---|
| none | naive, all 40 side peaks | 12800 | 3 | 0.725 ± 0.032 | 0.956 ± 0.014 |
| none | naive, 20 outer side peaks | 12800 | 3 | 0.724 ± 0.026 | 0.957 ± 0.009 |
| none | envelope fit (proposed) | 12800 | 4 | 0.732 ± 0.027 | 0.959 ± 0.011 |
| moderate | naive, all 40 side peaks | 12800 | 4 | 0.721 ± 0.044 | 0.948 ± 0.025 |
| moderate | naive, 20 outer side peaks | not reached up to 12800 | 0 | 0.481 ± 0.027 | 0.901 ± 0.025 |
| moderate | envelope fit (proposed) | 6400 | 5 | 0.836 ± 0.033 | 0.951 ± 0.023 |
| heavy | naive, all 40 side peaks | 800 | 5 | 1.000 ± 0.000 | 0.119 ± 0.025 |
| heavy | naive, 20 outer side peaks | 1600 | 5 | 0.984 ± 0.014 | 0.688 ± 0.026 |
| heavy | envelope fit (proposed) | 3200 | 5 | 0.976 ± 0.011 | 0.957 ± 0.008 |

### Table 3 (E3): ablation at A = 1600, true g2(0) = 0.03

| blinking | variant | bias | RMSE | 95% coverage | mean interval width |
|---|---|---|---|---|---|
| none | naive, 20 outer side peaks | 0.0002 ± 0.0009 | 0.0115 ± 0.0005 | 0.960 ± 0.012 | 0.0450 |
| none | ablation: no blinking-aware denominator | 0.0005 ± 0.0009 | 0.0115 ± 0.0005 | 0.953 ± 0.016 | 0.0454 |
| none | ablation: no averaging over tau | 0.0002 ± 0.0009 | 0.0115 ± 0.0005 | 0.956 ± 0.011 | 0.0448 |
| none | envelope fit (proposed) | 0.0000 ± 0.0009 | 0.0113 ± 0.0005 | 0.956 ± 0.013 | 0.0447 |
| moderate | naive, 20 outer side peaks | 0.0060 ± 0.0005 | 0.0129 ± 0.0006 | 0.919 ± 0.024 | 0.0455 |
| moderate | ablation: no blinking-aware denominator | 0.0081 ± 0.0004 | 0.0141 ± 0.0006 | 0.891 ± 0.026 | 0.0460 |
| moderate | ablation: no averaging over tau | 0.0003 ± 0.0005 | 0.0093 ± 0.0005 | 0.948 ± 0.016 | 0.0366 |
| moderate | envelope fit (proposed) | 0.0004 ± 0.0004 | 0.0093 ± 0.0005 | 0.951 ± 0.017 | 0.0369 |
| heavy | naive, 20 outer side peaks | -0.0115 ± 0.0011 | 0.0153 ± 0.0006 | 0.785 ± 0.039 | 0.0397 |
| heavy | ablation: no blinking-aware denominator | 0.0334 ± 0.0025 | 0.0371 ± 0.0027 | 0.332 ± 0.035 | 0.0620 |
| heavy | ablation: no averaging over tau | 0.0007 ± 0.0010 | 0.0074 ± 0.0004 | 0.900 ± 0.019 | 0.0242 |
| heavy | envelope fit (proposed) | 0.0011 ± 0.0009 | 0.0070 ± 0.0005 | 0.956 ± 0.027 | 0.0267 |

### Table 4 (E4): false-certification rate, source g2(0) = 0.06, threshold 0.05, A = 1600

| true rho | error in rho | naive, 20 outer side peaks | envelope fit (proposed) |
|---|---|---|---|
| 1 | -0.02 | 0.463 ± 0.046 | 0.872 ± 0.043 |
| 1 | -0.01 | 0.011 ± 0.010 | 0.149 ± 0.026 |
| 1 | +0.00 | 0.000 ± 0.000 | 0.003 ± 0.004 |
| 1 | +0.01 | 0.000 ± 0.000 | 0.000 ± 0.000 |
| 0.9 | -0.02 | 0.336 ± 0.026 | 0.525 ± 0.044 |
| 0.9 | -0.01 | 0.039 ± 0.014 | 0.124 ± 0.028 |
| 0.9 | +0.00 | 0.001 ± 0.003 | 0.007 ± 0.007 |
| 0.9 | +0.01 | 0.000 ± 0.000 | 0.000 ± 0.000 |

### Table 5 (E5): pre-registered window against window chosen to minimise the estimate

| true g2(0) | A | estimator | window | bias | 95% coverage | certification rate |
|---|---|---|---|---|---|---|
| 0.03 | 400 | envelope fit (proposed) | data-selected | -0.0078 ± 0.0009 | 0.951 ± 0.020 | 0.377 ± 0.042 |
| 0.03 | 400 | envelope fit (proposed) | pre-registered | 0.0013 ± 0.0004 | 0.944 ± 0.019 | 0.276 ± 0.032 |
| 0.03 | 400 | naive, 20 outer side peaks | data-selected | -0.0058 ± 0.0011 | 0.956 ± 0.017 | 0.239 ± 0.021 |
| 0.03 | 400 | naive, 20 outer side peaks | pre-registered | 0.0060 ± 0.0003 | 0.947 ± 0.011 | 0.155 ± 0.024 |
| 0.03 | 1600 | envelope fit (proposed) | data-selected | -0.0044 ± 0.0005 | 0.937 ± 0.022 | 0.760 ± 0.023 |
| 0.03 | 1600 | envelope fit (proposed) | pre-registered | 0.0003 ± 0.0003 | 0.945 ± 0.020 | 0.667 ± 0.008 |
| 0.03 | 1600 | naive, 20 outer side peaks | data-selected | -0.0002 ± 0.0007 | 0.952 ± 0.009 | 0.415 ± 0.034 |
| 0.03 | 1600 | naive, 20 outer side peaks | pre-registered | 0.0057 ± 0.0005 | 0.917 ± 0.009 | 0.332 ± 0.020 |
| 0.08 | 400 | envelope fit (proposed) | data-selected | -0.0111 ± 0.0015 | 0.936 ± 0.012 | 0.005 ± 0.009 |
| 0.08 | 400 | envelope fit (proposed) | pre-registered | 0.0001 ± 0.0014 | 0.944 ± 0.015 | 0.000 ± 0.000 |
| 0.08 | 400 | naive, 20 outer side peaks | data-selected | 0.0021 ± 0.0019 | 0.939 ± 0.026 | 0.001 ± 0.003 |
| 0.08 | 400 | naive, 20 outer side peaks | pre-registered | 0.0161 ± 0.0019 | 0.875 ± 0.031 | 0.000 ± 0.000 |
| 0.08 | 1600 | envelope fit (proposed) | data-selected | -0.0054 ± 0.0006 | 0.936 ± 0.030 | 0.001 ± 0.003 |
| 0.08 | 1600 | envelope fit (proposed) | pre-registered | 0.0005 ± 0.0008 | 0.944 ± 0.016 | 0.000 ± 0.000 |
| 0.08 | 1600 | naive, 20 outer side peaks | data-selected | 0.0104 ± 0.0009 | 0.845 ± 0.047 | 0.001 ± 0.003 |
| 0.08 | 1600 | naive, 20 outer side peaks | pre-registered | 0.0178 ± 0.0012 | 0.701 ± 0.057 | 0.000 ± 0.000 |
