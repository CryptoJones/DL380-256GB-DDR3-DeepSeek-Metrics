# DeepSeek-V4-Flash 144GB (AD-IQ3_M_XL) DL380 Benchmark Matrix
Generated at 2026-11-14T05:24:58-06:00 on DL380 (Dual Xeon E5-2640 v2, 256GB RAM)

### Test 1: Thread Scaling with NUMA Interleave
```
| model                          |       size |     params | backend    | threads | type_k | type_v |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | -----: | -----: | --------------: | -------------------: |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |       8 |   q8_0 |   q8_0 |            pp64 |          3.44 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |       8 |   q8_0 |   q8_0 |            tg16 |          1.89 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      16 |   q8_0 |   q8_0 |            pp64 |          6.46 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      16 |   q8_0 |   q8_0 |            tg16 |          2.44 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      24 |   q8_0 |   q8_0 |            pp64 |          6.29 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      24 |   q8_0 |   q8_0 |            tg16 |          2.42 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      32 |   q8_0 |   q8_0 |            pp64 |          7.18 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      32 |   q8_0 |   q8_0 |            tg16 |          2.06 ± 0.00 |

build: f1a7dea (1)
```

### Test 2: NUMA Policy (Best Thread Count)
```
| model                          |       size |     params | backend    | threads | type_k | type_v |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | -----: | -----: | --------------: | -------------------: |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      16 |   q8_0 |   q8_0 |            pp64 |          6.50 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      16 |   q8_0 |   q8_0 |            tg16 |          2.30 ± 0.00 |

build: f1a7dea (1)
```

### Test 3: KV Cache Quantization
```
| model                          |       size |     params | backend    | threads | type_k | type_v |            test |                  t/s |
| ------------------------------ | ---------: | ---------: | ---------- | ------: | -----: | -----: | --------------: | -------------------: |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      16 |   q4_0 |   q4_0 |            pp64 |          6.60 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      16 |   q4_0 |   q4_0 |            tg16 |          2.49 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      16 |   q8_0 |   q8_0 |            pp64 |          6.42 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      16 |   q8_0 |   q8_0 |            tg16 |          2.33 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      16 |            pp64 |          6.54 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      16 |            tg16 |          2.27 ± 0.00 |
```

### Test 4: Memory Residency Mode
```
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      16 |   q8_0 |   q8_0 |       mmap |            pp64 |          6.66 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      16 |   q8_0 |   q8_0 |       mmap |            tg16 |          2.32 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      16 |   q8_0 |   q8_0 |      mlock |            pp64 |          6.26 ± 0.00 |
| deepseek4 ?B IQ3_XXS - 3.0625 bpw | 133.77 GiB |   284.33 B | CPU        |      16 |   q8_0 |   q8_0 |      mlock |            tg16 |          2.42 ± 0.00 |
```

