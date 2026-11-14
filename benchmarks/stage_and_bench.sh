#!/usr/bin/env bash
# Stage 144GB DeepSeek-V4-Flash from Telesto and execute A/B/C benchmark matrix on DL380
set -euo pipefail

MODEL_DIR="/home/akclark/models/DeepSeek-V4-Flash-0731-AD-IQ3_M_XL"
BENCH_BIN="/home/akclark/llama.cpp-ds41/build/bin/llama-bench"
LOG="/home/akclark/models/stage_and_bench.log"
RESULTS="/home/akclark/models/benchmark_results.md"
FIRST_SHARD="$MODEL_DIR/DeepSeek-V4-Flash-0731-AD-IQ3_M_XL-00001-of-00004.gguf"

mkdir -p "$MODEL_DIR"
exec >>"$LOG" 2>&1

log() {
    echo "[$(date -Is)] $*"
}

log "================ STEP 1: PULLING 144GB WEIGHTS FROM TELESTO ================"
rsync -av --progress telesto:/NAS/models-telesto/DeepSeek-V4-Flash-0731-AD-IQ3_M_XL/ "$MODEL_DIR/"

log "================ STEP 2: VERIFYING STAGED LOCAL FILES ================"
ls -lh "$MODEL_DIR"
df -h /

log "================ STEP 3: RUNNING A/B/C BENCHMARK MATRIX ================"
echo "# DeepSeek-V4-Flash 144GB (AD-IQ3_M_XL) DL380 Benchmark Matrix" > "$RESULTS"
echo "Generated at $(date -Is) on DL380 (Dual Xeon E5-2640 v2, 256GB RAM)" >> "$RESULTS"
echo "" >> "$RESULTS"

# Test 1: Thread scaling with NUMA Interleave (Physical 16 cores vs Hyperthreaded 32 cores vs 24 cores vs 8 cores)
log "--- Running Test 1: Thread Scaling (-t 8, 16, 24, 32) ---"
echo "### Test 1: Thread Scaling with NUMA Interleave" >> "$RESULTS"
echo "\`\`\`" >> "$RESULTS"
numactl --interleave=all "$BENCH_BIN" \
    -m "$FIRST_SHARD" \
    -p 64 -n 16 -r 1 \
    -t 8,16,24,32 \
    -ctk q8_0 -ctv q8_0 \
    -ngl 0 -o md | tee -a "$RESULTS"
echo "\`\`\`" >> "$RESULTS"
echo "" >> "$RESULTS"

# Test 2: NUMA Policy Comparison (numactl interleave vs internal distribute vs default)
log "--- Running Test 2: NUMA Policy Comparison ---"
echo "### Test 2: NUMA Policy (Best Thread Count)" >> "$RESULTS"
echo "\`\`\`" >> "$RESULTS"
"$BENCH_BIN" \
    -m "$FIRST_SHARD" \
    -p 64 -n 16 -r 1 \
    -t 16 \
    --numa distribute \
    -ctk q8_0 -ctv q8_0 \
    -ngl 0 -o md | tee -a "$RESULTS"
echo "\`\`\`" >> "$RESULTS"
echo "" >> "$RESULTS"

# Test 3: KV Cache Precision (q8_0 vs f16 vs q4_0)
log "--- Running Test 3: KV Cache Precision (q4_0 vs q8_0 vs f16) ---"
echo "### Test 3: KV Cache Quantization" >> "$RESULTS"
echo "\`\`\`" >> "$RESULTS"
numactl --interleave=all "$BENCH_BIN" \
    -m "$FIRST_SHARD" \
    -p 64 -n 16 -r 1 \
    -t 16 \
    -ctk q4_0,q8_0,f16 -ctv q4_0,q8_0,f16 \
    -ngl 0 -o md | tee -a "$RESULTS"
echo "\`\`\`" >> "$RESULTS"
echo "" >> "$RESULTS"

# Test 4: Memory Lock vs On-demand mmap
log "--- Running Test 4: Memory Lock (-lm mlock vs mmap) ---"
echo "### Test 4: Memory Residency Mode" >> "$RESULTS"
echo "\`\`\`" >> "$RESULTS"
numactl --interleave=all "$BENCH_BIN" \
    -m "$FIRST_SHARD" \
    -p 64 -n 16 -r 1 \
    -t 16 \
    -lm mmap,mlock \
    -ctk q8_0 -ctv q8_0 \
    -ngl 0 -o md | tee -a "$RESULTS"
echo "\`\`\`" >> "$RESULTS"
echo "" >> "$RESULTS"

log "================ ALL BENCHMARKS COMPLETED ================"
cat "$RESULTS"
