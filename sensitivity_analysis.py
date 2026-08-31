import pandas as pd
import numpy as np
from typing import Dict, List, Callable

def generate_sensitivity_table(
    market_data: Dict[str, float],
    financials: Dict[str, float],
    base_assumptions: Dict[str, float],
    base_wacc: float,
    run_dcf_func: Callable,
    wacc_range: List[float] = None,
    growth_range: List[float] = None
) -> pd.DataFrame:

    # Defaults: +/- 1.0% spread with 0.5% steps
    if wacc_range is None:
        wacc_range = [base_wacc - 0.01, base_wacc - 0.005, base_wacc, base_wacc + 0.005, base_wacc + 0.01]
    
    # Use the base growth from assumptions if available
    base_g = base_assumptions.get("terminal_growth_rate", 0.02)
    
    if growth_range is None:
        growth_range = [base_g - 0.005, base_g - 0.0025, base_g, base_g + 0.0025, base_g + 0.005]

    results = {}

    # Iterate through WACC (Columns)
    for w in wacc_range:
        col_name = f"WACC {w:.1%}"
        column_values = []
        
        # Iterate through Growth Rates (Rows)
        for g in growth_range:
            # Create a temporary assumptions dict copy to not mutate the original
            scenario_assumptions = base_assumptions.copy()
            scenario_assumptions["terminal_growth_rate"] = g
            
            # Run DCF for this specific scenario
            try:
                dcf_output = run_dcf_func(
                    market_data=market_data,
                    financials=financials,
                    assumptions=scenario_assumptions,
                    wacc=w
                )
                share_price = dcf_output["implied_share_price"]
            except ValueError:
                # Handle cases where Growth >= WACC (Gordon Growth invalid)
                share_price = np.nan
            
            column_values.append(share_price)
        
        results[col_name] = column_values

    # Format DataFrame
    index_labels = [f"Growth {g:.2%}" for g in growth_range]
    df = pd.DataFrame(results, index=index_labels)
    
    return df

def format_sensitivity_output(df: pd.DataFrame, base_price: float) -> pd.DataFrame:

    return df.applymap(lambda x: (x / base_price) - 1 if pd.notnull(x) else pd.NA)