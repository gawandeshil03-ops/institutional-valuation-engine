from typing import Dict, List
from datetime import date

# -------------------------------------------------
# Forecast Operating Performance
# -------------------------------------------------

def forecast_financials(
    base_revenue: float,
    financials: Dict[str, float],
    assumptions: Dict[str, any]
) -> List[Dict[str, float]]:
    """
    Forecast operating metrics and FCFF for each year.
    Supports 'Vectorized Inputs' (lists of values) for growth and margins.
    """

    years = int(assumptions["forecast_years"])
    
    # Helper: Parse scalar or list inputs
    def _parse_input(key: str, default_val: float = 0.0) -> List[float]:
        val = assumptions.get(key, default_val)
        
        # Case A: Input is a string like "0.10, 0.08, 0.05" (from Excel)
        if isinstance(val, str) and "," in val:
            try:
                return [float(x.strip()) for x in val.split(",")]
            except ValueError:
                print(f"⚠️ Warning: Could not parse list for {key}. Using first value.")
                return [float(val.split(",")[0])] * years
        
        # Case B: Input is a single number (float/int)
        try:
            return [float(val)] * years
        except (ValueError, TypeError):
             return [default_val] * years

    # Parse Key Drivers
    rev_growth_rates = _parse_input("revenue_growth")
    ebitda_margins = _parse_input("ebitda_margin")
    depreciation_pcts = _parse_input("depreciation_pct_revenue")
    capex_pcts = _parse_input("capex_pct_revenue")
    nwc_pcts = _parse_input("nwc_pct_revenue")
    tax_rate = float(assumptions.get("tax_rate", 0.21)) 

    forecast = []
    revenue = base_revenue
    
    # Calculate initial NWC based on the first year's assumption or base year logic
    # (Simplification: Use base revenue * first year NWC % for previous NWC baseline)
    prev_nwc = revenue * nwc_pcts[0]

    for i in range(years):
        year_num = i + 1
        
        # Select Rate for Current Year
        # If list is shorter than years, extend the last value (Step-down logic)
        growth = rev_growth_rates[i] if i < len(rev_growth_rates) else rev_growth_rates[-1]
        margin = ebitda_margins[i] if i < len(ebitda_margins) else ebitda_margins[-1]
        dep_pct = depreciation_pcts[i] if i < len(depreciation_pcts) else depreciation_pcts[-1]
        cap_pct = capex_pcts[i] if i < len(capex_pcts) else capex_pcts[-1]
        nwc_pct = nwc_pcts[i] if i < len(nwc_pcts) else nwc_pcts[-1]

        # Calculate Metrics
        revenue *= (1 + growth)
        ebitda = revenue * margin
        depreciation = revenue * dep_pct
        ebit = ebitda - depreciation
        
        # Taxes
        taxes = ebit * tax_rate if ebit > 0 else 0

        # Cash Flow Items
        capex = revenue * cap_pct
        nwc = revenue * nwc_pct
        delta_nwc = nwc - prev_nwc

        fcff = (
            ebit
            - taxes
            + depreciation
            - capex
            - delta_nwc
        )

        forecast.append({
            "year": year_num,
            "revenue": revenue,
            "ebitda": ebitda,
            "taxes": taxes,
            "capex": capex,
            "delta_nwc": delta_nwc,
            "fcff": fcff,
            "active_growth": growth,
            "active_margin": margin
        })

        prev_nwc = nwc

    return forecast


# -------------------------------------------------
# Discount Cash Flows
# -------------------------------------------------

def discount_fcff(
    forecast: List[Dict[str, float]],
    wacc: float,
    valuation_date: date = None
) -> List[Dict[str, float]]:
    """
    Discount FCFF to present value using Stub Period + Mid-Year Convention.
    """

    # If no date provided, assume start of year (Standard Mid-Year: 0.5, 1.5...)
    if valuation_date is None:
        stub_fraction = 1.0
    else:
        # Calculate fraction of year remaining (Stub)
        # Assuming Fiscal Year End is Dec 31
        fye = date(valuation_date.year, 12, 31)
        days_in_year = 366 if (valuation_date.year % 4 == 0) else 365
        days_remaining = (fye - valuation_date).days
        
        # Avoid division by zero or negative days
        if days_remaining < 0: 
             # Fallback if we are past FYE (should move to next year)
             days_remaining = 0 
        
        stub_fraction = days_remaining / days_in_year

    discounted = []

    for i, row in enumerate(forecast):
        # row["year"] is 1, 2, 3...
        
        if i == 0:
            # Year 1 (Stub Year)
            # Discount period is half of the remaining time
            time_period = stub_fraction / 2
        else:
            # Future Years
            # Time = Stub Period + (Full Years passed) - 0.5 (mid-year adj)
            # Example Year 2: Stub + 0.5
            # Example Year 3: Stub + 1.5
            time_period = stub_fraction + (i - 0.5)

        discount_factor = 1 / ((1 + wacc) ** time_period)
        pv_fcff = row["fcff"] * discount_factor

        discounted.append({
            **row,
            "discount_factor": discount_factor,
            "pv_fcff": pv_fcff,
            "stub_fraction_used": stub_fraction if i == 0 else 0 # Just for tracking
        })

    return discounted


# -------------------------------------------------
# Terminal Value
# -------------------------------------------------

def compute_terminal_value(
    last_year_fcff: float,
    last_year_ebitda: float,
    wacc: float,
    assumptions: Dict[str, float]
) -> float:
    """
    Compute terminal value using Gordon Growth or Exit Multiple.
    """

    method = assumptions["terminal_method"]

    if method == "gordon":
        g = assumptions["terminal_growth_rate"]
        if g >= wacc:
            raise ValueError("Terminal growth rate must be < WACC.")
        terminal_value = last_year_fcff * (1 + g) / (wacc - g)

    elif method == "exit_multiple":
        multiple = assumptions["exit_ebitda_multiple"]
        terminal_value = last_year_ebitda * multiple

    else:
        raise ValueError("Invalid terminal value method.")

    return terminal_value


# -------------------------------------------------
# Equity Valuation
# -------------------------------------------------

def run_dcf(
    market_data: Dict[str, float],
    financials: Dict[str, float],
    assumptions: Dict[str, float],
    wacc: float,
    valuation_date: date = None 
) -> Dict[str, float]:
    """
    Full DCF valuation pipeline.
    """

    # Base inputs
    base_revenue = financials["revenue"]
    net_debt = financials["total_debt"] - financials.get("cash", 0.0)
    shares_outstanding = market_data["shares_outstanding"]

    # Forecast
    forecast = forecast_financials(
        base_revenue,
        financials,
        assumptions
    )

    # Discounting
    discounted_fcff = discount_fcff(forecast, wacc, valuation_date)

    pv_fcff_sum = sum(row["pv_fcff"] for row in discounted_fcff)

    # Terminal Value
    terminal_value = compute_terminal_value(
        last_year_fcff=forecast[-1]["fcff"],
        last_year_ebitda=forecast[-1]["ebitda"],
        wacc=wacc,
        assumptions=assumptions
    )

    # Calculate Time to Terminal Value
    # This is the end of the forecast period.
    # Time = Stub Fraction + (Forecast Years - 1)
    if valuation_date:
        fye = date(valuation_date.year, 12, 31)
        days_in_year = 366 if (valuation_date.year % 4 == 0) else 365
        stub_fraction = (fye - valuation_date).days / days_in_year
    else:
        stub_fraction = 1.0

    terminal_time = stub_fraction + (forecast[-1]["year"] - 1)
    
    terminal_discount_factor = 1 / ((1 + wacc) ** terminal_time)
    pv_terminal_value = terminal_value * terminal_discount_factor

    # Enterprise & Equity Value
    enterprise_value = pv_fcff_sum + pv_terminal_value
    equity_value = enterprise_value - net_debt
    implied_share_price = equity_value / shares_outstanding

    return {
        "enterprise_value": round(enterprise_value, 2),
        "equity_value": round(equity_value, 2),
        "implied_share_price": round(implied_share_price, 2),
        "pv_fcff": round(pv_fcff_sum, 2),
        "pv_terminal_value": round(pv_terminal_value, 2),
        "net_debt": round(net_debt, 2),
        "discounted_fcff": discounted_fcff
    }