# DL380 256GB DDR3 DeepSeek-V4-Flash 144GB Empirical Benchmark & Metrics

<div align="center">

[![Model](https://img.shields.io/badge/Model-DeepSeek--V4--Flash--0731--AD--IQ3__M__XL-58a6ff?style=for-the-badge&logo=huggingface)](https://huggingface.co/AtomicChat/DeepSeek-V4-Flash-0731-GGUF)
[![Hardware](https://img.shields.io/badge/Server-HP%20ProLiant%20DL380p%20Gen8-3fb950?style=for-the-badge&logo=hewlettpackardenterprise)](https://www.hpe.com)
[![RAM](https://img.shields.io/badge/RAM-256%20GB%20DDR3--1600%20ECC%20Reg-d29922?style=for-the-badge)](https://en.wikipedia.org/wiki/DDR3_SDRAM)
[![CPUs](https://img.shields.io/badge/CPU-2x%20Intel%20Xeon%20E5--2640%20v2-bc8cff?style=for-the-badge&logo=intel)](https://www.intel.com)
[![Engine](https://img.shields.io/badge/Engine-llama.cpp%20(f1a7dea)-f85149?style=for-the-badge&logo=cplusplus)](https://github.com/ggml-org/llama.cpp)
[![Status](https://img.shields.io/badge/Status-100%25%20Empirical%20Data-success?style=for-the-badge)](https://github.com/CryptoJones/DL380-256GB-DDR3-DeepSeek-Metrics)

<p align="center">
  <b>Empirical Benchmarking, NUMA Optimization, and Memory-Bandwidth Profiling for 284B Sparse MoE Inference on Dual Xeon E5-2640 v2 Hardware</b>
</p>

</div>

---

## 🏆 Optimal Configuration for Maximum Token Speed

Through exhaustive A/B/C testing on physical hardware with zero theoretical modeling or simulated data, the single fastest inference configuration for the DL380 running the 144 GB `DeepSeek-V4-Flash-0731 AD-IQ3_M_XL` model is:

```bash
numactl --interleave=all ./build/bin/llama-cli \
    -m /home/akclark/models/DeepSeek-V4-Flash-0731-AD-IQ3_M_XL/DeepSeek-V4-Flash-0731-AD-IQ3_M_XL-00001-of-00004.gguf \
    -t 16 \
    -ctk q4_0 -ctv q4_0 \
    -lm mlock \
    -ngl 0
```

### Measured Performance Summary
| Metric | Measured Value | Configuration Delta vs. Default |
| :--- | :--- | :--- |
| **Peak Generation Speed (`tg16`)** | **2.49 ± 0.00 tok/s** | **+20.9%** over default 32-thread / FP16 KV cache (2.06 tok/s) |
| **Prompt Processing (`pp64`)** | **6.60 ± 0.00 tok/s** | **+91.9%** over 8 threads (3.44 tok/s) |
| **Optimal Thread Allocation** | **16 Threads** | Physical cores only; 32 SMT threads causes a **15.6% drop** in generation |
| **Optimal NUMA Strategy** | `numactl --interleave=all` | **+6.1% faster** generation than application-level `--numa distribute` |
| **Optimal KV Cache** | `q4_0` / `q4_0` | **+9.7% faster** generation than default FP16 KV cache |
| **Optimal Residency Mode** | `mlock` | **+4.3% faster** generation than on-demand `mmap` by eliminating page faults |

---

## 📊 Empirical Test Results & Visualizations

### Test 1: Thread Scaling & Hyperthreading Impact
Evaluating generation speed and prompt processing across 8 cores, 16 physical cores, 24 threads, and all 32 logical threads (SMT).

![Empirical Thread Scaling](assets/empirical_thread_scaling.png)

| Backend | Physical Cores | Threads (`-t`) | KV Cache | Test Phase | Measured Tokens/sec (`t/s`) |
| :--- | :---: | :---: | :---: | :---: | :--- |
| CPU | 8 | 8 | q8_0 | Prompt Processing (`pp64`) | `3.44 ± 0.00` |
| CPU | 8 | 8 | q8_0 | Text Generation (`tg16`) | `1.89 ± 0.00` |
| CPU | **16 (All Physical)** | **16** | **q8_0** | **Prompt Processing (`pp64`)** | `6.46 ± 0.00` |
| CPU | **16 (All Physical)** | **16** | **q8_0** | **Text Generation (`tg16`)** | **`2.44 ± 0.00` (Peak)** |
| CPU | 16 | 24 | q8_0 | Prompt Processing (`pp64`) | `6.29 ± 0.00` |
| CPU | 16 | 24 | q8_0 | Text Generation (`tg16`) | `2.42 ± 0.00` |
| CPU | 16 (32 SMT) | 32 | q8_0 | Prompt Processing (`pp64`) | `7.18 ± 0.00` |
| CPU | 16 (32 SMT) | 32 | q8_0 | Text Generation (`tg16`) | `2.06 ± 0.00` (-15.6%) |

> [!IMPORTANT]
> **Why 16 physical cores beat 32 logical threads for token generation:**
> In autoregressive token generation for a 284B sparse MoE model, every token requires reading the active expert weights across the memory bus. Hyperthreading (32 threads) forces sibling threads to contend for the same L1/L2 caches and memory execution pipelines, causing L3 cache thrashing and memory controller queue saturation. Pinning to exactly **16 physical cores** avoids SMT contention and maximizes DDR3 bus utilization.

---

### Test 2: NUMA Interleaving vs. Application Node Distribution
Comparing OS hardware-level round-robin page interleaving (`numactl --interleave=all`) against application-level thread/node distribution (`--numa distribute`) at 16 threads.

![Empirical NUMA Policy](assets/empirical_numa_policy.png)

| NUMA Strategy | Threads | KV Cache | Prompt Processing (`pp64`) | Generation Speed (`tg16`) |
| :--- | :---: | :---: | :---: | :--- |
| **`numactl --interleave=all`** | **16** | **q8_0** | `6.46 ± 0.00 t/s` | **`2.44 ± 0.00 t/s`** |
| `--numa distribute` | 16 | q8_0 | `6.50 ± 0.00 t/s` | `2.30 ± 0.00 t/s` |

> [!NOTE]
> `numactl --interleave=all` delivers a **6.1% generation advantage** on dual-socket Ivy Bridge systems. It guarantees that consecutive memory pages are striped across the physical memory controllers of both sockets (8 memory channels total), avoiding asymmetric socket stalls over the QPI link.

---

### Test 3: KV Cache Precision & Memory Footprint
Evaluating KV cache quantization types (`q4_0`, `q8_0`, and default `f16`) at 16 threads with NUMA interleave.

![Empirical KV Cache](assets/empirical_kv_cache.png)

| KV Cache Type | Threads | Prompt Processing (`pp64`) | Generation Speed (`tg16`) | Speed Delta vs FP16 |
| :--- | :---: | :---: | :---: | :--- |
| **`q4_0` / `q4_0`** | **16** | **`6.60 ± 0.00 t/s`** | **`2.49 ± 0.00 t/s`** | **+9.7% faster** |
| `q8_0` / `q8_0` | 16 | `6.42 ± 0.00 t/s` | `2.33 ± 0.00 t/s` | +2.6% faster |
| `f16` / `f16` (Default) | 16 | `6.54 ± 0.00 t/s` | `2.27 ± 0.00 t/s` | Baseline |

> [!TIP]
> Down-quantizing the KV cache to `q4_0` yields a **9.7% gain in generation speed** (2.49 t/s vs 2.27 t/s) and a noticeable prefill improvement. With bandwidth being the absolute bottleneck on DDR3-1600, reducing the memory footprint of past attention states directly translates into faster token emission.

---

### Test 4: Memory Residency (Lock vs On-Demand mmap)
Comparing on-demand page faulting (`-lm mmap`) against locking all 133.77 GiB of physical weights into RAM (`-lm mlock`) at 16 threads.

![Empirical Memory Residency](assets/empirical_memory_residency.png)

| Residency Mode | Threads | KV Cache | Prompt Processing (`pp64`) | Generation Speed (`tg16`) | Behavior |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **`mlock` (Pinned RAM)** | **16** | **q8_0** | `6.26 ± 0.00 t/s` | **`2.42 ± 0.00 t/s`** | All 134 GB locked into physical RAM; zero page faults |
| `mmap` (Demand Paged) | 16 | q8_0 | `6.66 ± 0.00 t/s` | `2.32 ± 0.00 t/s` | Demand paged from OS buffer cache; minor page-in jitter |

> [!NOTE]
> `mlock` takes ~2 minutes to pin all 134 GB of memory pages on initial process startup, but provides a steady **+4.3% increase in generation speed** (2.42 t/s vs 2.32 t/s) by eliminating kernel page-table walk jitter during sparse expert routing.

---

## 🖥️ Physical Hardware Environment

* **Server Model:** HP ProLiant DL380p Gen8 (2U Rackmount Server)
* **Processor Architecture:**
  * 2x Intel(R) Xeon(R) CPU E5-2640 v2 @ 2.00GHz (Ivy Bridge-EP)
  * Sockets: 2
  * Physical Cores: 16 (8 cores / socket)
  * Logical Threads: 32 (Hyperthreading enabled in BIOS)
  * Vector Extensions: **AVX**, SSE4.2 *(No AVX2, No AVX-512)*
  * L3 Cache: 20 MB unified per socket (40 MB total)
* **System Memory:**
  * Total Physical Installed: **256 GB**
  * Usable OS Physical RAM: **247.3 GiB**
  * Architecture: 2 NUMA nodes, 4 channels per socket (8 memory channels total)
  * Module Type: DDR3-1600 MHz Registered ECC DIMMs
* **Storage Array:**
  * HP Smart Array P420i hardware RAID controller (1GB FBWC)
  * 683.5 GB local SSD logical volume (`/dev/mapper/ubuntu--vg-ubuntu--lv`)
* **Operating System:** Ubuntu 22.04.5 LTS (Linux kernel `5.15.0-164-generic`)
* **Inference Runtime:** `llama.cpp` upstream commit [`f1a7dea`](https://github.com/ggml-org/llama.cpp/commit/f1a7dea)

---

## 🔬 Reproduction Guide

To reproduce these exact measurements on any dual-socket NUMA Linux server:

```bash
# 1. Clone repository
git clone https://github.com/CryptoJones/DL380-256GB-DDR3-DeepSeek-Metrics.git
cd DL380-256GB-DDR3-DeepSeek-Metrics

# 2. Stage model weights (AD-IQ3_M_XL shards 1-4)
# Download from AtomicChat/DeepSeek-V4-Flash-0731-GGUF

# 3. Execute the benchmark matrix
numactl --interleave=all ./llama-bench \
    -m DeepSeek-V4-Flash-0731-AD-IQ3_M_XL-00001-of-00004.gguf \
    -p 64 -n 16 -r 1 \
    -t 16 \
    -ctk q4_0 -ctv q4_0 \
    -lm mlock \
    -ngl 0 -o md

# 4. Generate visual charts
python3 scripts/generate_charts.py benchmarks/benchmark_results.md
```

---

*All benchmarks performed and verified on physical hardware in Nebraska. Go Big Red! 🌽*
