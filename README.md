# DL380 256GB DDR3 DeepSeek-V4-Flash 144GB Benchmark & Metrics

<div align="center">

[![Model](https://img.shields.io/badge/Model-DeepSeek--V4--Flash--0731--AD--IQ3__M__XL-58a6ff?style=for-the-badge&logo=huggingface)](https://huggingface.co/AtomicChat/DeepSeek-V4-Flash-0731-GGUF)
[![Hardware](https://img.shields.io/badge/Server-HP%20ProLiant%20DL380p%20Gen8-3fb950?style=for-the-badge&logo=hewlettpackardenterprise)](https://www.hpe.com)
[![RAM](https://img.shields.io/badge/RAM-256%20GB%20DDR3--1600%20ECC%20Reg-d29922?style=for-the-badge)](https://en.wikipedia.org/wiki/DDR3_SDRAM)
[![CPUs](https://img.shields.io/badge/CPU-2x%20Intel%20Xeon%20E5--2640%20v2-bc8cff?style=for-the-badge&logo=intel)](https://www.intel.com)
[![Engine](https://img.shields.io/badge/Engine-llama.cpp%20(f1a7dea)-f85149?style=for-the-badge&logo=cplusplus)](https://github.com/ggml-org/llama.cpp)

<p align="center">
  <b>Empirical Benchmarking, NUMA Optimization, and Memory-Bandwidth Profiling for 284B Sparse MoE Inference on Dual Xeon E5-2640 v2 Hardware</b>
</p>

</div>

---

## 📌 Status: Benchmark In Progress

The 144 GB weights (`DeepSeek-V4-Flash-0731 AD-IQ3_M_XL`) are currently being staged on the DL380's local SSD array. The automated `llama-bench` test harness (`benchmarks/stage_and_bench.sh`) will execute the full A/B/C empirical test matrix immediately upon transfer completion.

**All metrics and charts in this repository will be generated exclusively from actual measured runs on the physical hardware.**

---

## 🖥️ Physical Hardware Specifications

* **Server:** HP ProLiant DL380p Gen8 (2U Rackmount)
* **CPUs:** 2x Intel(R) Xeon(R) CPU E5-2640 v2 @ 2.00GHz
  * Total Physical Cores: 16 (8 cores / socket)
  * Total Logical Threads: 32 (2 threads / core)
  * Instruction Sets: **AVX**, SSE4.2 *(No AVX2, No AVX-512)*
  * L3 Cache: 20 MB per socket (40 MB total)
* **Memory:** **247 GiB Usable Physical RAM** (256 GB Installed)
  * Topology: 2 NUMA Nodes (8 memory channels across 2 sockets)
  * Speed: DDR3-1600 MHz Registered ECC
* **Storage:** 683.5 GB Hardware RAID Array (Smart Array Gen8 P420i)
* **Inference Runtime:** `llama.cpp` build `f1a7dea`

---

## 🔬 Empirical Test Matrix Under Test

The automated harness runs `llama-bench` across four primary control axes to measure empirical tokens/second (`tg` generation and `pp` prompt ingestion):

1. **Thread Scaling (`-t`):**
   * Physical cores only (`-t 8`, `-t 16`) vs. SMT hyperthreads (`-t 24`, `-t 32`).
2. **NUMA Interleaving Policy:**
   * Hardware memory striping (`numactl --interleave=all`) vs. application-level node distribution (`--numa distribute`).
3. **KV Cache Quantization:**
   * Evaluating `-ctk` and `-ctv` across `q4_0`, `q8_0`, and `f16`.
4. **Memory Residency:**
   * Physical memory pre-faulting and locking (`-lm mlock`) vs. demand-paged mapping (`-lm mmap`).

---

## 📂 Repository Structure

```
.
├── README.md                          # Empirical benchmark report and analysis
├── assets/                            # Generated charts from actual test runs
├── benchmarks/
│   └── stage_and_bench.sh             # Live staging and llama-bench harness
└── scripts/
    └── generate_charts.py             # Parser & chart generator for llama-bench output
```

*Results will be published here as soon as the live benchmark run concludes.*
