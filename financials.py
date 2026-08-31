import pandas as pd
import numpy as np


# =========================
# PUBLIC INTERFACE
# =========================

def build_normalized_financials(
    income_statement: pd.DataFrame,
    cash_flow: pd.DataFrame,
    balance_sheet: pd.DataFrame,
    assumptions: dict
) -> dict:
    """
    Normalize historical financials and prepare inputs for forecasting.

    Returns a dictionary containing:
    - historical metrics
    - normalized ratios
    - base-year financials
    """

    _validate_inputs(income_statement, cash_flow, balance_sheet)

    # Historical series
    revenue = income_statement["Revenue"]
    ebitda = income_statement["EBITDA"]
    ebit = income_statement["EBIT"]

    # Growth
    revenue_cagr = _calculate_cagr(revenue)
    ebitda_cagr = _calculate_cagr(ebitda)

    # Margins
    ebitda_margin = (ebitda / revenue).mean()
    ebit_margin = (ebit / revenue).mean()

    # Reinvestment ratios 
    capex_ratio = (cash_flow["CapEx"] / revenue).mean()
    nwc_ratio = (cash_flow["Change_NWC"] / revenue).mean()

    # Base year (last historical year) 
    base_year = income_statement.iloc[-1]

    normalized_financials = {
        "base_year": {
            "year": int(base_year["Year"]),
            "revenue": float(base_year["Revenue"]),
            "ebitda": float(base_year["EBITDA"]),
            "ebit": float(base_year["EBIT"]),
        },
        "growth": {
            "revenue_cagr": revenue_cagr,
            "ebitda_cagr": ebitda_cagr,
            "assumed_revenue_growth": assumptions.get("Revenue growth", revenue_cagr),
        },
        "margins": {
            "ebitda_margin": ebitda_margin,
            "ebit_margin": ebit_margin,
        },
        "reinvestment": {
            "capex_ratio": capex_ratio,
            "nwc_ratio": nwc_ratio,
        },
        "capital_structure": {
            "debt": float(balance_sheet.iloc[-1]["Debt"]),
            "cash": float(balance_sheet.iloc[-1]["Cash"]),
            "shares": float(balance_sheet.iloc[-1]["Shares"]),
        }
    }

    return normalized_financials


# =========================
# HELPERS
# =========================

def _calculate_cagr(series: pd.Series) -> float:
    """
    Calculate CAGR from a pandas Series.
    """
    start_value = series.iloc[0]
    end_value = series.iloc[-1]
    periods = len(series) - 1

    if start_value <= 0 or periods <= 0:
        return np.nan

    return (end_value / start_value) ** (1 / periods) - 1


def _validate_inputs(
    income_statement: pd.DataFrame,
    cash_flow: pd.DataFrame,
    balance_sheet: pd.DataFrame
) -> None:
    """
    Basic validation checks before normalization.
    """

    if income_statement.shape[0] < 3:
        raise ValueError("At least 3 years of income statement data required.")

    if cash_flow.shape[0] != income_statement.shape[0]:
        raise ValueError("Cash flow and income statement must have the same number of years.")

    if balance_sheet.empty:
        raise ValueError("Balance sheet data is missing.")

    # Logical consistency checks (soft warnings)
    if not (income_statement["EBITDA"] >= income_statement["EBIT"]).all():
        print("⚠️ Warning: EBITDA is lower than EBIT for some years.")

