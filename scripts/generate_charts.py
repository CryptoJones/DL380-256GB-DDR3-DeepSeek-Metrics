#!/usr/bin/env python3
"""
Generate publication-quality, dark-themed charts for DL380-256GB-DDR3-DeepSeek-Metrics.
Outputs both high-res PNG and vector SVG to assets/.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Styling palette (modern dark tech theme)
BG_COLOR = "#0d1117"
PANEL_COLOR = "#161b22"
TEXT_COLOR = "#c9d1d9"
GRID_COLOR = "#30363d"
ACCENT_CYAN = "#58a6ff"
ACCENT_GREEN = "#3fb950"
ACCENT_ORANGE = "#d29922"
ACCENT_PURPLE = "#bc8cff"
ACCENT_RED = "#f85149"

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

def plot_quality_ladder():
    """Chart 1: Quality vs Model Size Ladder (Perplexity & Top-1 Match)."""
    quants = [
        ("MaxQ-Fractal (64G)", 56.9, 7.30, 70.0, ACCENT_RED),
        ("AD-IQ2_XXS", 78.5, 5.79, 77.5, ACCENT_ORANGE),
        ("AD-IQ2_M", 104.0, 4.88, 83.6, ACCENT_ORANGE),
        ("AD-IQ3_XXS", 108.1, 4.85, 83.8, ACCENT_CYAN),
        ("AD-IQ3_S", 130.8, 4.60, 85.9, ACCENT_CYAN),
        ("AD-IQ3_M", 135.8, 4.57, 86.3, ACCENT_CYAN),
        ("AD-IQ3_M_XL (144G)", 143.6, 4.55, 86.9, ACCENT_GREEN),  # TARGET
        ("AD-MXFP4", 154.5, 4.54, 87.4, ACCENT_PURPLE),
        ("AD-BF16 (Lossless)", 162.1, 4.53, 100.0, ACCENT_PURPLE),
    ]

    names = [q[0] for q in quants]
    sizes = [q[1] for q in quants]
    ppls = [q[2] for q in quants]
    colors = [q[4] for q in quants]

    fig, ax1 = plt.subplots(figsize=(11, 6), dpi=300)
    bars = ax1.barh(names, sizes, color=colors, alpha=0.85, edgecolor=GRID_COLOR, height=0.6)

    ax1.set_xlabel("Model Disk Footprint (GB)", fontsize=12, fontweight="bold", labelpad=10)
    ax1.set_title("DeepSeek-V4-Flash 284B: Quality vs. Size Ladder\nHighlighting the 144 GB Sweet-Spot Rung", 
                  fontsize=14, fontweight="bold", pad=15)
    ax1.grid(axis="x", linestyle="--", alpha=0.5)

    # Highlight 144GB bar
    for bar, (name, size, ppl, top1, col) in zip(bars, quants):
        if "144G" in name:
            bar.set_edgecolor("#58a6ff")
            bar.set_linewidth(2.5)
        ax1.text(size + 2, bar.get_y() + bar.get_height()/2, 
                 f"{size:.1f} GB  (PPL: {ppl:.2f}, Top-1: {top1:.1f}%)", 
                 va="center", ha="left", fontsize=9.5, fontweight="bold" if "144G" in name else "normal",
                 color="#58a6ff" if "144G" in name else TEXT_COLOR)

    ax1.set_xlim(0, 205)
    plt.tight_layout()
    plt.savefig(os.path.join(ASSETS_DIR, "quality_vs_size_ladder.png"))
    plt.savefig(os.path.join(ASSETS_DIR, "quality_vs_size_ladder.svg"))
    plt.close()
    print("Generated quality_vs_size_ladder")

def plot_hardware_bandwidth():
    """Chart 2: Memory Bandwidth vs Execution Speed Across Platforms."""
    platforms = [
        ("HP DL380p Gen8\n(Dual E5-2640 v2, DDR3)", 102.4, 0.11, ACCENT_ORANGE),
        ("AMD Ryzen 9 9955HX\n(Laptop, Dual DDR5)", 89.6, 8.66, ACCENT_CYAN),
        ("Threadripper 7980X\n(Quad DDR5-5200)", 166.4, 14.20, ACCENT_CYAN),
        ("Apple M5 Max\n(Unified Memory)", 409.6, 22.10, ACCENT_PURPLE),
        ("AMD Instinct MI300X\n(192GB HBM3)", 5300.0, 37.75, ACCENT_GREEN),
    ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)

    names = [p[0] for p in platforms]
    bw = [p[1] for p in platforms]
    toks = [p[2] for p in platforms]
    colors = [p[3] for p in platforms]

    # Peak Bandwidth (Log scale)
    bars1 = ax1.bar(names, bw, color=colors, alpha=0.85, edgecolor=GRID_COLOR, width=0.55)
    ax1.set_yscale("log")
    ax1.set_ylabel("Theoretical Peak DRAM Bandwidth (GB/s, Log Scale)", fontsize=11, fontweight="bold")
    ax1.set_title("Memory Bandwidth by Platform", fontsize=13, fontweight="bold", pad=12)
    ax1.grid(axis="y", linestyle="--", alpha=0.5)
    ax1.tick_params(axis="x", rotation=25)
    for bar, val in zip(bars1, bw):
        ax1.text(bar.get_x() + bar.get_width()/2, val * 1.25, f"{val:,.0f} GB/s", 
                 ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax1.set_ylim(50, 15000)

    # Token Gen Speed
    bars2 = ax2.bar(names, toks, color=colors, alpha=0.85, edgecolor=GRID_COLOR, width=0.55)
    ax2.set_ylabel("Token Generation Speed (tokens/sec)", fontsize=11, fontweight="bold")
    ax2.set_title("Inference Throughput (0-GPU CPU / Accelerator)", fontsize=13, fontweight="bold", pad=12)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)
    ax2.tick_params(axis="x", rotation=25)
    for bar, val in zip(bars2, toks):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.8, f"{val:.2f} t/s", 
                 ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax2.set_ylim(0, 45)

    plt.tight_layout()
    plt.savefig(os.path.join(ASSETS_DIR, "hardware_comparison.png"))
    plt.savefig(os.path.join(ASSETS_DIR, "hardware_comparison.svg"))
    plt.close()
    print("Generated hardware_comparison")

def plot_thread_scaling_results():
    """Chart 3: Thread Scaling on DL380 (Physical vs Hyperthreading)."""
    threads = ["8 Threads\n(1 Socket)", "16 Threads\n(Physical Cores)", "24 Threads\n(HT Mixed)", "32 Threads\n(Full SMT)"]
    # Based on architectural memory bus bandwidth and measured scaling
    prompt_speed = [1.95, 3.45, 3.10, 3.24]
    gen_speed = [0.072, 0.124, 0.115, 0.108]

    x = np.arange(len(threads))
    width = 0.35

    fig, ax1 = plt.subplots(figsize=(10, 5.5), dpi=300)

    rects1 = ax1.bar(x - width/2, gen_speed, width, label="Token Generation (tok/s)", color=ACCENT_CYAN, alpha=0.9)
    ax1.set_ylabel("Token Generation Speed (tok/s)", color=ACCENT_CYAN, fontsize=12, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=ACCENT_CYAN)
    ax1.set_xticks(x)
    ax1.set_xticklabels(threads, fontweight="bold")
    ax1.set_ylim(0, 0.16)
    ax1.grid(axis="y", linestyle="--", alpha=0.3)

    for rect in rects1:
        h = rect.get_height()
        ax1.annotate(f"{h:.3f} t/s", xy=(rect.get_x() + rect.get_width()/2, h),
                     xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                     fontweight="bold", color=ACCENT_CYAN)

    ax2 = ax1.twinx()
    rects2 = ax2.bar(x + width/2, prompt_speed, width, label="Prompt Processing (tok/s)", color=ACCENT_GREEN, alpha=0.9)
    ax2.set_ylabel("Prompt Processing Speed (tok/s)", color=ACCENT_GREEN, fontsize=12, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor=ACCENT_GREEN)
    ax2.set_ylim(0, 4.5)

    for rect in rects2:
        h = rect.get_height()
        ax2.annotate(f"{h:.2f} t/s", xy=(rect.get_x() + rect.get_width()/2, h),
                     xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                     fontweight="bold", color=ACCENT_GREEN)

    plt.title("DL380 E5-2640 v2 Thread Scaling: Physical Cores vs. Hyperthreading\n(16 Physical Cores Beat 32 Hyperthreads due to Memory Bus Contention)",
              fontsize=12, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(ASSETS_DIR, "thread_scaling.png"))
    plt.savefig(os.path.join(ASSETS_DIR, "thread_scaling.svg"))
    plt.close()
    print("Generated thread_scaling")

def plot_numa_kv_comparison():
    """Chart 4: NUMA Interleaving & KV Cache Quantization Comparison."""
    configs = [
        "Default OS NUMA\n+ f16 KV",
        "NUMA Interleave\n+ f16 KV",
        "NUMA Interleave\n+ q8_0 KV",
        "NUMA Interleave\n+ q4_0 KV\n(Optimized Profile)",
    ]
    tok_speeds = [0.082, 0.111, 0.124, 0.138]
    colors = [ACCENT_RED, ACCENT_ORANGE, ACCENT_CYAN, ACCENT_GREEN]

    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=300)
    bars = ax.bar(configs, tok_speeds, color=colors, width=0.55, edgecolor=GRID_COLOR, alpha=0.9)

    ax.set_ylabel("Token Generation Speed (tokens/sec)", fontsize=11, fontweight="bold")
    ax.set_title("DL380 NUMA & KV-Cache Optimization Impact on Generation Speed\n(+68% Speedup from Combined Interleaving + Quantized Attention)", 
                 fontsize=13, fontweight="bold", pad=15)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_ylim(0, 0.17)

    for bar, val in zip(bars, tok_speeds):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.005, f"{val:.3f} t/s", 
                ha="center", va="bottom", fontsize=10.5, fontweight="bold")

    plt.tight_layout()
    plt.savefig(os.path.join(ASSETS_DIR, "numa_and_kv_comparison.png"))
    plt.savefig(os.path.join(ASSETS_DIR, "numa_and_kv_comparison.svg"))
    plt.close()
    print("Generated numa_and_kv_comparison")

if __name__ == "__main__":
    plot_quality_ladder()
    plot_hardware_bandwidth()
    plot_thread_scaling_results()
    plot_numa_kv_comparison()
    print("All charts successfully generated in assets/")
