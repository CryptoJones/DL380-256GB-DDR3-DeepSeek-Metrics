# DeepSeek-V4-Flash 144GB Context Length Scaling & Prompt Caching Benchmark

Generated on physical dual Xeon E5-2640 v2 hardware (DL380 256GB DDR3-1600).

| Target Context | Measured Prompt Tokens | Cold TTFT (s) | Prefill Speed (tok/s) | Generation Speed (tok/s) | Cached TTFT (s) | Prompt Cache Speedup |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 64 | 86 | 13.99s | 6.15 | 2.26 | 0.88s | 15.8x |
| 256 | 295 | 42.22s | 6.96 | 2.36 | 0.93s | 45.6x |
| 512 | 561 | 80.50s | 6.96 | 2.36 | 0.92s | 87.7x |
| 1024 | 1106 | 153.05s | 6.93 | 2.28 | 0.95s | 161.9x |
| 2048 | 2196 | 247.29s | 6.49 | 2.25 | 0.98s | 252.6x |
