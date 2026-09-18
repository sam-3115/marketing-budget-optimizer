"""
visualize.py
Produces two charts for the report:
  1. response_curves.png  -- fitted diminishing-returns curve per channel,
     with current vs. optimized spend points marked
  2. allocation_comparison.png -- current vs. optimized budget bar chart
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 11, "figure.dpi": 150})

with open("/home/claude/marketing_opt/outputs/results.json") as f:
    r = json.load(f)

fitted = r["fitted_params"]
channels = list(fitted.keys())


def response_curve(spend, a, b):
    return a * (1 - np.exp(-b * spend))


# ---------- Chart 1: response curves ----------
fig, axes = plt.subplots(1, 5, figsize=(20, 4), sharey=False)
colors = plt.cm.tab10(np.linspace(0, 1, len(channels)))

for i, ch in enumerate(channels):
    ax = axes[i]
    a, b = fitted[ch]["a"], fitted[ch]["b"]
    max_x = max(r["current_alloc"][ch], r["optimized_alloc"][ch]) * 1.6
    xs = np.linspace(0, max_x, 200)
    ys = response_curve(xs, a, b)
    ax.plot(xs, ys, color=colors[i], lw=2)
    ax.scatter([r["current_alloc"][ch]], [r["current_conversions"][ch]],
               color="black", zorder=5, label="Current", marker="o", s=60)
    ax.scatter([r["optimized_alloc"][ch]], [r["optimized_conversions"][ch]],
               color="red", zorder=5, label="Optimized", marker="^", s=70)
    ax.set_title(ch, fontweight="bold")
    ax.set_xlabel("Weekly spend (₹)")
    if i == 0:
        ax.set_ylabel("Conversions / week")
        ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3)

fig.suptitle("Fitted Diminishing-Returns Response Curves by Channel", fontweight="bold", y=1.05)
fig.tight_layout()
fig.savefig("/home/claude/marketing_opt/outputs/response_curves.png", bbox_inches="tight")
print("Saved outputs/response_curves.png")

# ---------- Chart 2: allocation comparison ----------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

x = np.arange(len(channels))
width = 0.35
current_vals = [r["current_alloc"][ch] for ch in channels]
optimized_vals = [r["optimized_alloc"][ch] for ch in channels]

ax1.bar(x - width/2, current_vals, width, label="Current", color="#8395a7")
ax1.bar(x + width/2, optimized_vals, width, label="Optimized", color="#ee5253")
ax1.set_xticks(x)
ax1.set_xticklabels(channels)
ax1.set_ylabel("Weekly spend (₹)")
ax1.set_title("Budget Allocation: Current vs. Optimized", fontweight="bold")
ax1.legend()
ax1.grid(alpha=0.3, axis="y")

current_conv_vals = [r["current_conversions"][ch] for ch in channels]
optimized_conv_vals = [r["optimized_conversions"][ch] for ch in channels]
ax2.bar(x - width/2, current_conv_vals, width, label="Current", color="#8395a7")
ax2.bar(x + width/2, optimized_conv_vals, width, label="Optimized", color="#10ac84")
ax2.set_xticks(x)
ax2.set_xticklabels(channels)
ax2.set_ylabel("Conversions / week")
ax2.set_title(f"Resulting Conversions ({r['uplift_pct']:+.1f}% total uplift)", fontweight="bold")
ax2.legend()
ax2.grid(alpha=0.3, axis="y")

fig.tight_layout()
fig.savefig("/home/claude/marketing_opt/outputs/allocation_comparison.png", bbox_inches="tight")
print("Saved outputs/allocation_comparison.png")
