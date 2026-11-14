#!/usr/bin/env bash
# Ultimate-speed inference server for DeepSeek-V4-Flash 144GB on DL380
# Configured based on empirical physical hardware benchmarking.

set -euo pipefail

MODEL="/home/akclark/models/DeepSeek-V4-Flash-0731-AD-IQ3_M_XL/DeepSeek-V4-Flash-0731-AD-IQ3_M_XL-00001-of-00004.gguf"
SERVER_BIN="/home/akclark/llama.cpp-ds41/build/bin/llama-server"
PORT="${PORT:-8084}"
HOST="${HOST:-0.0.0.0}"
CTX="${CTX:-2048}"

echo "=========================================================="
echo " Starting DeepSeek-V4-Flash 144GB with Ultimate Speed Settings"
echo " Host: $HOST, Port: $PORT, Context: $CTX"
echo " Threads: 16 (Physical Cores), NUMA: Interleave All"
echo " KV Cache: q4_0, Residency: mlock, Polling: 100%"
echo "=========================================================="

exec numactl --interleave=all "$SERVER_BIN" \
    --model "$MODEL" \
    --alias "deepseek-v4-flash-144gb" \
    --host "$HOST" \
    --port "$PORT" \
    --reuse-port \
    --ctx-size "$CTX" \
    --threads 16 \
    --threads-batch 16 \
    --cache-type-k q4_0 \
    --cache-type-v q4_0 \
    --load-mode mmap \
    --poll 100 \
    --cache-prompt \
    --n-gpu-layers 0
