from typing import Dict, List
import pandas as pd

def run_sanity_checks(
    financials: pd.DataFrame, 
    assumptions: Dict[str, any]
) -> None:

    print("\n🔍 Running Sanity Checks...")
    flags = 0
    
    # 1. Margin Check
    avg_hist_margin = (financials["EBITDA"].sum() / financials["Revenue"].sum())
    
    # Handle vectorized (list) or scalar inputs
    if isinstance(assumptions["ebitda_margin"], str): 
        # simplistic check for list strings, taking the first value
        forecast_margin = float(assumptions["ebitda_margin"].split(",")[0])
    else:
        forecast_margin = float(assumptions["ebitda_margin"])

    # Threshold: If forecast is >20% higher than history (relative)
    if forecast_margin > avg_hist_margin * 1.2:
        print(f"   ⚠️ CAUTION: Forecast margin ({forecast_margin:.1%}) significantly exceeds historical avg ({avg_hist_margin:.1%}).")
        flags += 1
        
    # 2. Revenue Growth Check
    # Compare last historical year growth vs forecast year 1
    last_rev = financials["Revenue"].iloc[-1]
    prev_rev = financials["Revenue"].iloc[-2]
    last_growth = (last_rev / prev_rev) - 1
    
    if isinstance(assumptions["revenue_growth"], str):
        forecast_growth = float(assumptions["revenue_growth"].split(",")[0])
    else:
        forecast_growth = float(assumptions["revenue_growth"])
        
    if forecast_growth > last_growth + 0.10: # If jumping more than 10%
        print(f"   ⚠️ CAUTION: Growth jumps from {last_growth:.1%} (last actual) to {forecast_growth:.1%} (forecast).")
        flags += 1

    if flags == 0:
        print("   ✅ Assumptions look reasonable based on history.")
    else:
        print("   👀 Review above warnings before finalizing.")