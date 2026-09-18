# Marketing Budget Allocation Optimizer

**A decision-analytics project: given a fixed marketing budget, which channel should get more money — and which should get less?**

## Business Problem
A company spends a fixed weekly budget across 5 marketing channels (TV, Digital, Social, Search, Email). Historical spend was set by habit, not by measuring each channel's *marginal* return. This project asks: **without spending a rupee more, can we reallocate the existing budget to get more conversions?**

## Approach
1. **Response curve modeling** — Using 52 weeks of historical spend/conversion data per channel, fit a diminishing-returns curve to each channel:
   `conversions = a · (1 − e^(−b·spend))`
   fitted via non-linear least squares (`scipy.optimize.curve_fit`).
2. **Constrained optimization** — Using the fitted curves, solve for the spend allocation across channels that **maximizes total conversions subject to the total budget staying fixed** (`scipy.optimize.minimize`, SLSQP, budget-equality constraint + per-channel bounds).
3. **Visualization** — Response curves (with current vs. optimized spend marked) and a before/after allocation comparison.
4. **Plain-English summary** — a short script turns the raw numbers into a one-paragraph recommendation.

## Key Result
| | Current | Optimized |
|---|---|---|
| Total weekly conversions | ~1,888 | ~2,094 |
| **Uplift** | | **+10.9%**, same budget |
| Projected annual revenue impact | | **+₹1.29 crore/year** *(at an assumed ₹1,200/conversion)* |

**Why it works:** TV spend was deep into diminishing returns (flat part of the curve) — extra rupees there barely move the needle. Search, Social, and Email were still on the steep part of their curves — the same rupee produces more conversions there. Reallocating from a saturated channel to underinvested ones raises total output at zero extra cost.

## Files
- `generate_data.py` — simulates realistic weekly spend/conversion history per channel
- `fit_and_optimize.py` — curve fitting + constrained optimization
- `visualize.py` — response curve and allocation comparison charts
- `generate_report.py` — plain-English summary of the recommendation
- `outputs/` — results.json, charts, executive_summary.md

## Tech Stack
Python, NumPy, Pandas, SciPy (`curve_fit`, `minimize`), Matplotlib

## Suggested Resume Bullet
> **Marketing Budget Allocation Optimizer** *(Python, SciPy)*
> - Modeled diminishing-returns response curves for 5 marketing channels from 52 weeks of spend/conversion data using non-linear curve fitting
> - Formulated and solved a constrained optimization problem (SciPy SLSQP) to reallocate a fixed budget across channels, achieving a projected **+10.9% conversion uplift** (~₹1.29 Cr/year) with no budget increase
