"""
generate_report.py

Turns the optimizer's raw numbers into a short, plain-English summary
someone could hand to a manager -- no AI/LLM involved, just string
formatting based on the results.
"""

import json

with open("/home/claude/marketing_opt/outputs/results.json") as f:
    r = json.load(f)

channels = list(r["fitted_params"].keys())

# Channel that lost the most budget vs. the channel that gained the most
biggest_cut = min(channels, key=lambda c: r["optimized_alloc"][c] - r["current_alloc"][c])
biggest_gain = max(channels, key=lambda c: r["optimized_alloc"][c] - r["current_alloc"][c])

summary = (
    f"RECOMMENDATION\n"
    f"Move budget away from {biggest_cut} and into {biggest_gain} (and other "
    f"underinvested channels), keeping total weekly spend the same at "
    f"Rs.{r['total_budget']:,.0f}.\n\n"
    f"WHY\n"
    f"{biggest_cut} has hit diminishing returns -- extra spend there barely "
    f"increases conversions anymore. {biggest_gain} is still on the steep "
    f"part of its response curve, so the same rupee produces more "
    f"conversions there.\n\n"
    f"IMPACT\n"
    f"Projected uplift: {r['uplift_pct']:+.1f}% more conversions per week, "
    f"worth an estimated Rs.{r['extra_revenue_per_year']:,.0f} in extra "
    f"annual revenue (assuming Rs.{r['value_per_conversion']:,} value per "
    f"conversion)."
)

print(summary)

with open("/home/claude/marketing_opt/outputs/executive_summary.md", "w") as f:
    f.write("# Executive Summary\n\n" + summary.replace("\n", "  \n"))

print("\nSaved outputs/executive_summary.md")
