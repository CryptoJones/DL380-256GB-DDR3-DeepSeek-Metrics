#!/usr/bin/env python3
"""
Context Scaling Benchmark for DeepSeek-V4-Flash 144GB on DL380.
Measures TTFT, prefill throughput, generation speed, and prompt caching across context lengths.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CONTEXT_SIZES = [64, 128, 256, 512, 1024, 2048]

PROMPT_BASE = (
    "The HP ProLiant DL380p Gen8 server features dual Intel Xeon E5-2640 v2 processors "
    "operating on an Ivy Bridge microarchitecture with 16 physical cores and 32 threads. "
    "It is equipped with 256 gigabytes of DDR3 registered ECC memory distributed across eight channels. "
    "Inference is performed purely on CPU across both NUMA sockets using hardware page interleaving. "
)

def build_prompt(target_tokens: int) -> str:
    # Approximate 1 token ~ 4 chars / 0.75 words
    # Build a coherent repeating factual prompt to reach target tokens
    words_needed = int(target_tokens * 0.75)
    base_words = PROMPT_BASE.split()
    repeats = (words_needed // len(base_words)) + 1
    text = " ".join((base_words * repeats)[:words_needed])
    return text + "\n\nSummarize the key architectural specifications described above in 2 bullet points."

def get_token_count(endpoint: str, text: str) -> int:
    try:
        url = endpoint.replace("/v1", "/tokenize")
        req = urllib.request.Request(
            url,
            data=json.dumps({"content": text}).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return len(data.get("tokens", []))
    except Exception:
        return int(len(text.split()) / 0.75)

def run_stream_query(endpoint: str, prompt: str, max_tokens: int = 16):
    url = f"{endpoint.rstrip('/')}/chat/completions"
    payload = {
        "model": "deepseek-v4-flash-144gb",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "stream": True,
        "stream_options": {"include_usage": True}
    }
    data = json.dumps(payload).encode('utf-8')
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers)

    start_time = time.time()
    first_token_time = None
    chunks_count = 0
    prompt_tokens = 0
    completion_tokens = 0

    with urllib.request.urlopen(req, timeout=1200) as resp:
        for line in resp:
            line = line.decode('utf-8').strip()
            if not line or not line.startswith("data: "):
                continue
            data_str = line[6:]
            if data_str == "[DONE]":
                break
            try:
                chunk = json.loads(data_str)
                choices = chunk.get("choices", [])
                if choices and "delta" in choices[0] and choices[0]["delta"].get("content"):
                    if first_token_time is None:
                        first_token_time = time.time()
                    chunks_count += 1
                usage = chunk.get("usage")
                if usage:
                    prompt_tokens = usage.get("prompt_tokens", 0)
                    completion_tokens = usage.get("completion_tokens", 0)
            except Exception:
                pass

    end_time = time.time()
    if first_token_time is None:
        first_token_time = end_time

    if prompt_tokens == 0:
        prompt_tokens = get_token_count(endpoint, prompt)

    ttft = first_token_time - start_time
    gen_time = end_time - first_token_time
    total_time = end_time - start_time
    actual_gen_tokens = completion_tokens if completion_tokens > 0 else chunks_count

    prefill_tok_s = prompt_tokens / ttft if ttft > 0 else 0
    gen_tok_s = actual_gen_tokens / gen_time if gen_time > 0 and actual_gen_tokens > 0 else 0

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": actual_gen_tokens,
        "ttft_sec": ttft,
        "prefill_tok_s": prefill_tok_s,
        "gen_time_sec": gen_time,
        "gen_tok_s": gen_tok_s,
        "total_time_sec": total_time
    }

def main():
    parser = argparse.ArgumentParser(description="Context scaling benchmark against llama-server")
    parser.add_argument("--endpoint", default="http://172.16.28.113:8084/v1", help="llama-server endpoint")
    parser.add_argument("--output", default="benchmarks/context_scaling_results.md", help="Output markdown results")
    args = parser.parse_args()

    print(f"[*] Checking server health at {args.endpoint}...")
    health_url = args.endpoint.replace("/v1", "/health")
    for _ in range(60):
        try:
            with urllib.request.urlopen(health_url, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get("status") == "ok":
                    print("[+] Server is online and ready!")
                    break
        except Exception:
            pass
        print("    Waiting for server model to load...")
        time.sleep(5)
    else:
        print("[!] Server failed to report healthy status.")
        sys.exit(1)

    results = []
    print("\n[+] Starting Context Length Benchmark Matrix:")
    print("| Target Ctx | Actual Prompt Tokens | TTFT (s) | Prefill (tok/s) | Gen Speed (tok/s) | Cached TTFT (s) | Cache Speedup |")
    print("| :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    for target_ctx in CONTEXT_SIZES:
        prompt = build_prompt(target_ctx)
        
        # Cold run
        cold = run_stream_query(args.endpoint, prompt, max_tokens=16)
        
        # Warm run (Prompt Caching test)
        warm = run_stream_query(args.endpoint, prompt, max_tokens=16)
        
        speedup = (cold["ttft_sec"] / warm["ttft_sec"]) if warm["ttft_sec"] > 0 else 1.0

        print(f"| {target_ctx} | {cold['prompt_tokens']} | {cold['ttft_sec']:.2f}s | {cold['prefill_tok_s']:.2f} | {cold['gen_tok_s']:.2f} | {warm['ttft_sec']:.2f}s | {speedup:.1f}x |")
        
        results.append({
            "target_ctx": target_ctx,
            "actual_prompt_tokens": cold["prompt_tokens"],
            "cold_ttft": cold["ttft_sec"],
            "prefill_tok_s": cold["prefill_tok_s"],
            "gen_tok_s": cold["gen_tok_s"],
            "warm_ttft": warm["ttft_sec"],
            "cache_speedup": speedup
        })

    # Save Markdown Report
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        f.write("# DeepSeek-V4-Flash 144GB Context Length Scaling & Prompt Caching Benchmark\n\n")
        f.write("Generated on physical dual Xeon E5-2640 v2 hardware (DL380 256GB DDR3-1600).\n\n")
        f.write("| Target Context | Measured Prompt Tokens | Cold TTFT (s) | Prefill Speed (tok/s) | Generation Speed (tok/s) | Cached TTFT (s) | Prompt Cache Speedup |\n")
        f.write("| :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for r in results:
            f.write(f"| {r['target_ctx']} | {r['actual_prompt_tokens']} | {r['cold_ttft']:.2f}s | {r['prefill_tok_s']:.2f} | {r['gen_tok_s']:.2f} | {r['warm_ttft']:.2f}s | {r['cache_speedup']:.1f}x |\n")

    # Generate Charts
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets_dir, exist_ok=True)

    BG_COLOR = "#0d1117"
    PANEL_COLOR = "#161b22"
    TEXT_COLOR = "#c9d1d9"
    GRID_COLOR = "#30363d"
    ACCENT_CYAN = "#58a6ff"
    ACCENT_GREEN = "#3fb950"
    ACCENT_ORANGE = "#d29922"
    ACCENT_PURPLE = "#bc8cff"

    plt.rcParams.update({
        "figure.facecolor": BG_COLOR,
        "axes.facecolor": PANEL_COLOR,
        "axes.edgecolor": GRID_COLOR,
        "axes.labelcolor": TEXT_COLOR,
        "xtick.color": TEXT_COLOR,
        "ytick.color": TEXT_COLOR,
        "grid.color": GRID_COLOR,
        "text.color": TEXT_COLOR,
        "font.family": "sans-serif",
        "font.size": 11,
    })

    ctx_labels = [f"{r['actual_prompt_tokens']} tok" for r in results]
    cold_ttfts = [r["cold_ttft"] for r in results]
    warm_ttfts = [r["warm_ttft"] for r in results]
    gen_speeds = [r["gen_tok_s"] for r in results]

    # Chart 1: Context Length vs Generation Speed
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    bars = ax.bar(ctx_labels, gen_speeds, color=ACCENT_CYAN, width=0.45, alpha=0.9)
    ax.set_ylabel("Measured Generation Speed (tok/s)", color=ACCENT_CYAN, fontweight="bold")
    ax.set_xlabel("Context Length (Prompt Tokens)", color=TEXT_COLOR, fontweight="bold")
    ax.set_title("DL380 E5-2640 v2: Context Length vs. Token Generation Speed\n(Empirical Hardware Measurement)", fontweight="bold", pad=15)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    for b, v in zip(bars, gen_speeds):
        ax.text(b.get_x() + b.get_width()/2, v + (max(gen_speeds)*0.02), f"{v:.2f} t/s",
                ha="center", va="bottom", fontweight="bold", color=ACCENT_CYAN)
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "empirical_context_generation_scaling.png"))
    plt.savefig(os.path.join(assets_dir, "empirical_context_generation_scaling.svg"))
    plt.close()

    # Chart 2: Cold vs Cached TTFT
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    import numpy as np
    x = np.arange(len(ctx_labels))
    width = 0.35
    ax.bar(x - width/2, cold_ttfts, width, label="Cold Ingestion (TTFT)", color=ACCENT_ORANGE, alpha=0.9)
    ax.bar(x + width/2, warm_ttfts, width, label="Warm Prompt Cache Hit (TTFT)", color=ACCENT_GREEN, alpha=0.9)
    ax.set_ylabel("Latency (Seconds)", color=TEXT_COLOR, fontweight="bold")
    ax.set_xlabel("Context Length (Tokens)", color=TEXT_COLOR, fontweight="bold")
    ax.set_title("DL380 E5-2640 v2: Prompt Ingestion vs. Cache Hit Latency\n(Empirical Hardware Measurement)", fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(ctx_labels)
    ax.legend(facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(assets_dir, "empirical_prompt_caching_speedup.png"))
    plt.savefig(os.path.join(assets_dir, "empirical_prompt_caching_speedup.svg"))
    plt.close()

    print(f"\n[+] Successfully saved results to {args.output} and updated charts in assets/")

if __name__ == "__main__":
    main()
