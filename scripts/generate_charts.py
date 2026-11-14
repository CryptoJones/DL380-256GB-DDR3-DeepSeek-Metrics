#!/usr/bin/env python3
"""
Empirical Chart Generator for DL380-256GB-DDR3-DeepSeek-Metrics.
Parses actual measured output from benchmark_results.md.
Does NOT generate charts if empirical data is missing.
"""

import os
import re
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS_FILE = sys.argv[1] if len(sys.argv) > 1 else "/home/akclark/models/benchmark_results.md"
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

if not os.path.exists(RESULTS_FILE):
    print(f"[!] Empirical results file '{RESULTS_FILE}' not found. Benchmark has not finished yet.")
    sys.exit(1)

# Read results
with open(RESULTS_FILE, "r") as f:
    content = f.read()

# Parse markdown table rows
# Format typically: | model | size | params | backend | threads | ... | test | t/s |
rows = []
for line in content.splitlines():
    line = line.strip()
    if line.startswith("|") and not line.startswith("| model") and not line.startswith("|---"):
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) >= 6:
            rows.append(parts)

if not rows:
    print("[!] No benchmark table rows found in results file.")
    sys.exit(1)

print(f"[+] Successfully parsed {len(rows)} empirical benchmark measurements.")

# Dark theme palette
BG_COLOR = "#0d1117"
PANEL_COLOR = "#161b22"
TEXT_COLOR = "#c9d1d9"
GRID_COLOR = "#30363d"
ACCENT_CYAN = "#58a6ff"
ACCENT_GREEN = "#3fb950"

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

# Filter thread scaling results
threads = []
tg_vals = []
pp_vals = []

for r in rows:
    # Check if thread row
    # Identify test type from columns
    test_type = None
    ts_val = None
    thread_num = None
    
    for item in r:
        if item.isdigit() and int(item) in [8, 16, 24, 32]:
            thread_num = int(item)
        if item.startswith("pp") or item.startswith("tg"):
            test_type = item
        if "±" in item or re.match(r"^\d+\.\d+$", item):
            try:
                ts_val = float(item.split("±")[0].strip())
            except ValueError:
                pass
                
    if thread_num is not None and ts_val is not None:
        if test_type and test_type.startswith("tg"):
            threads.append(f"{thread_num} Threads")
            tg_vals.append(ts_val)
        elif test_type and test_type.startswith("pp"):
            pp_vals.append(ts_val)

if tg_vals:
    fig, ax1 = plt.subplots(figsize=(10, 5.5), dpi=300)
    bars = ax1.bar(threads, tg_vals, color=ACCENT_CYAN, alpha=0.9, width=0.45)
    ax1.set_ylabel("Measured Token Generation Speed (tok/s)", color=ACCENT_CYAN, fontsize=12, fontweight="bold")
    ax1.set_title("DL380 E5-2640 v2: Empirical Generation Speed vs. Thread Count\n(Measured on Physical Hardware)", fontsize=13, fontweight="bold", pad=15)
    ax1.grid(axis="y", linestyle="--", alpha=0.3)
    
    for b, val in zip(bars, tg_vals):
        ax1.text(b.get_x() + b.get_width()/2, val + (max(tg_vals)*0.02), f"{val:.3f} t/s",
                 ha="center", va="bottom", fontweight="bold", color=ACCENT_CYAN)
                 
    plt.tight_layout()
    out_png = os.path.join(ASSETS_DIR, "empirical_thread_scaling.png")
    out_svg = os.path.join(ASSETS_DIR, "empirical_thread_scaling.svg")
    plt.savefig(out_png)
    plt.savefig(out_svg)
    plt.close()
    print(f"[+] Saved empirical thread scaling chart to {out_png}")
