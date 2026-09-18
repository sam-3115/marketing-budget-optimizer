"""
generate_data.py
Simulates 52 weeks of marketing spend and conversions across 5 channels.
Each channel has a hidden diminishing-returns response curve:
    conversions = a * (1 - exp(-b * spend))
Real spend decisions (by a hypothetical past marketing team) are randomized
around a baseline allocation, so the resulting dataset lets us RECOVER each
channel's response curve via curve fitting -- this mimics what you'd get
from a real company's historical spend/conversion log.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

N_WEEKS = 52

# Hidden "true" response-curve parameters per channel (unknown to the analyst
# in real life -- we back them out from data, same as a real MMM exercise)
CHANNELS = {
    # channel: (a = max achievable conversions/week, b = efficiency/saturation rate)
    # TV is deliberately over-invested (deep into saturation -> low marginal ROI);
    # Search/Email are under-invested (steep part of curve -> high marginal ROI).
    # This is what creates a real reallocation opportunity for the optimizer to find.
    "TV":       {"a": 489, "b": 0.0000727, "base_spend": 55000, "cost_per_unit_noise": 0.10},
    "Digital":  {"a": 901, "b": 0.0000500, "base_spend": 30000, "cost_per_unit_noise": 0.12},
    "Social":   {"a": 635, "b": 0.0000400, "base_spend": 20000, "cost_per_unit_noise": 0.15},
    "Search":   {"a": 699, "b": 0.0000278, "base_spend": 18000, "cost_per_unit_noise": 0.10},
    "Email":    {"a": 301, "b": 0.0000500, "base_spend": 6000,  "cost_per_unit_noise": 0.08},
}

rows = []
for week in range(1, N_WEEKS + 1):
    for ch, p in CHANNELS.items():
        # weekly spend fluctuates around a baseline (simulating a real, imperfectly
        # planned budget schedule -- this variation is what lets us fit the curve)
        spend = max(500, np.random.normal(p["base_spend"], p["base_spend"] * 0.35))

        true_conversions = p["a"] * (1 - np.exp(-p["b"] * spend))
        noisy_conversions = max(
            0, np.random.normal(true_conversions, true_conversions * p["cost_per_unit_noise"] + 2)
        )

        rows.append({
            "week": week,
            "channel": ch,
            "spend": round(spend, 2),
            "conversions": round(noisy_conversions, 1),
        })

df = pd.DataFrame(rows)
df.to_csv("/home/claude/marketing_opt/data/marketing_history.csv", index=False)
print(df.head(10))
print("\nSaved", len(df), "rows to data/marketing_history.csv")
print("\nTotals by channel (52 weeks):")
print(df.groupby("channel")[["spend", "conversions"]].sum().round(0))
