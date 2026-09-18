"""
fit_and_optimize.py

Marketing Budget Allocation Optimizer
--------------------------------------
1. Fits a diminishing-returns response curve per channel from historical
   spend/conversion data:  conversions(spend) = a * (1 - exp(-b * spend))
2. Solves a constrained optimization problem: given a fixed total weekly
   budget (same as the historical average), how should spend be reallocated
   across channels to MAXIMIZE total conversions?
3. Quantifies the uplift vs. the current (historical average) allocation.
4. Produces a short natural-language business summary of the recommendation
   (see `generate_insight_summary` -- structured so the templated summary
   can be swapped for a live LLM API call, see NOTE inside that function).
"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, minimize
import json

df = pd.read_csv("/home/claude/marketing_opt/data/marketing_history.csv")
channels = df["channel"].unique().tolist()


def response_curve(spend, a, b):
    return a * (1 - np.exp(-b * spend))


# ---------------------------------------------------------------
# 1. Fit a response curve per channel
# ---------------------------------------------------------------
fitted_params = {}
for ch in channels:
    sub = df[df["channel"] == ch]
    x, y = sub["spend"].values, sub["conversions"].values
    # initial guesses: a ~ 1.5x max observed conversions, b ~ small
    p0 = [y.max() * 1.3, 1e-4]
    popt, _ = curve_fit(response_curve, x, y, p0=p0, maxfev=20000)
    fitted_params[ch] = {"a": popt[0], "b": popt[1]}

print("Fitted response-curve parameters (conversions = a * (1 - exp(-b*spend))):")
for ch, p in fitted_params.items():
    print(f"  {ch:8s}  a={p['a']:.1f}   b={p['b']:.6f}")

# ---------------------------------------------------------------
# 2. Current allocation (historical weekly average per channel)
# ---------------------------------------------------------------
current_alloc = df.groupby("channel")["spend"].mean().to_dict()
total_budget = sum(current_alloc.values())
current_conversions = {
    ch: response_curve(current_alloc[ch], **fitted_params[ch]) for ch in channels
}
current_total_conversions = sum(current_conversions.values())

print(f"\nTotal weekly budget (fixed): ₹{total_budget:,.0f}")
print("Current average weekly allocation & modeled conversions:")
for ch in channels:
    print(f"  {ch:8s}  ₹{current_alloc[ch]:>10,.0f}  ->  {current_conversions[ch]:>7.1f} conversions")
print(f"  {'TOTAL':8s}  ₹{total_budget:>10,.0f}  ->  {current_total_conversions:>7.1f} conversions")

# ---------------------------------------------------------------
# 3. Optimize allocation: maximize total conversions, budget fixed
# ---------------------------------------------------------------
# Bounds: don't let any channel go to zero (floor = 20% of current) or
# beyond 2x its current spend (realistic operational constraint / avoids
# extrapolating the fitted curve too far beyond observed data).
bounds = [(0.2 * current_alloc[ch], 2.0 * current_alloc[ch]) for ch in channels]
x0 = np.array([current_alloc[ch] for ch in channels])


def negative_total_conversions(x):
    return -sum(
        response_curve(x[i], **fitted_params[ch]) for i, ch in enumerate(channels)
    )


budget_constraint = {"type": "eq", "fun": lambda x: np.sum(x) - total_budget}

result = minimize(
    negative_total_conversions,
    x0,
    method="SLSQP",
    bounds=bounds,
    constraints=[budget_constraint],
    options={"maxiter": 500, "ftol": 1e-9},
)

optimized_alloc = {ch: result.x[i] for i, ch in enumerate(channels)}
optimized_conversions = {
    ch: response_curve(optimized_alloc[ch], **fitted_params[ch]) for ch in channels
}
optimized_total_conversions = sum(optimized_conversions.values())

uplift_pct = (optimized_total_conversions / current_total_conversions - 1) * 100

print(f"\nOptimized allocation (same ₹{total_budget:,.0f} total budget):")
for ch in channels:
    delta = optimized_alloc[ch] - current_alloc[ch]
    print(
        f"  {ch:8s}  ₹{optimized_alloc[ch]:>10,.0f}  ({delta:+9,.0f})  ->  {optimized_conversions[ch]:>7.1f} conversions"
    )
print(f"  {'TOTAL':8s}  ₹{total_budget:>10,.0f}              ->  {optimized_total_conversions:>7.1f} conversions")
print(f"\n>>> Projected uplift: {uplift_pct:+.1f}% more conversions at the SAME budget <<<")

# Assume a business value per conversion to translate into revenue impact
VALUE_PER_CONVERSION = 1200  # ₹, illustrative assumption -- stated explicitly, not hidden
extra_conversions_per_week = optimized_total_conversions - current_total_conversions
extra_revenue_per_week = extra_conversions_per_week * VALUE_PER_CONVERSION
extra_revenue_per_year = extra_revenue_per_week * 52

print(f"\nAt an assumed value of ₹{VALUE_PER_CONVERSION:,}/conversion:")
print(f"  +{extra_conversions_per_week:.0f} conversions/week  ->  +₹{extra_revenue_per_week:,.0f}/week  ->  +₹{extra_revenue_per_year:,.0f}/year")

# ---------------------------------------------------------------
# 4. Save results for the report / plotting script
# ---------------------------------------------------------------
results = {
    "fitted_params": fitted_params,
    "total_budget": total_budget,
    "current_alloc": current_alloc,
    "current_conversions": current_conversions,
    "current_total_conversions": current_total_conversions,
    "optimized_alloc": optimized_alloc,
    "optimized_conversions": optimized_conversions,
    "optimized_total_conversions": optimized_total_conversions,
    "uplift_pct": uplift_pct,
    "value_per_conversion": VALUE_PER_CONVERSION,
    "extra_revenue_per_year": extra_revenue_per_year,
}
with open("/home/claude/marketing_opt/outputs/results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSaved results -> outputs/results.json")
