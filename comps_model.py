from typing import Dict
import pandas as pd


# =====================================================
# Load peer data from Excel
# =====================================================

def load_peer_data_from_excel(xlsx_path: str, sheet_name: str = "Peers") -> pd.DataFrame:
    """
    Load peer trading data from an Excel file.

    Expected columns:
    - Company
    - EV
    - Revenue
    - EBITDA
    - Net Income
    """

    df = pd.read_excel(xlsx_path, sheet_name=sheet_name)

    required_columns = [
        "Company",
        "EV",
        "Revenue",
        "EBITDA",
        "Net Income"
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in peer Excel file: {missing}")

    return df


# =====================================================
# Compute trading multiples
# =====================================================

def compute_trading_multiples(peers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute trading multiples:
    - EV / EBITDA
    - EV / Sales
    - P / E
    """

    df = peers_df.copy()

    df["EV_EBITDA"] = df["EV"] / df["EBITDA"]
    df["EV_Sales"] = df["EV"] / df["Revenue"]
    df["P_E"] = df["EV"] / df["Net Income"]

    # Remove invalid values
    df = df.replace([float("inf"), -float("inf")], pd.NA)
    df = df.dropna(subset=["EV_EBITDA", "EV_Sales", "P_E"])

    return df


# =====================================================
# Compute median multiples
# =====================================================

def compute_median_multiples(peers_df: pd.DataFrame) -> Dict[str, float]:
    """
    Compute median trading multiples across peers.
    """

    return {
        "EV_EBITDA": peers_df["EV_EBITDA"].median(),
        "EV_Sales": peers_df["EV_Sales"].median(),
        "P_E": peers_df["P_E"].median()
    }


# =====================================================
# Implied valuation
# =====================================================

def compute_implied_valuation(
    company_financials: Dict[str, float],
    median_multiples: Dict[str, float]
) -> Dict[str, Dict[str, float]]:
    """
    Compute implied Enterprise Value and Equity Value
    using median trading multiples.
    """

    revenue = company_financials["revenue"]
    ebitda = company_financials["ebitda"]
    net_income = company_financials["net_income"]
    net_debt = company_financials["total_debt"] - company_financials["cash"]

    valuations = {}

    # EV / EBITDA
    ev_ebitda = median_multiples["EV_EBITDA"] * ebitda
    valuations["EV_EBITDA"] = {
        "enterprise_value": round(ev_ebitda, 2),
        "equity_value": round(ev_ebitda - net_debt, 2)
    }

    # EV / Sales
    ev_sales = median_multiples["EV_Sales"] * revenue
    valuations["EV_Sales"] = {
        "enterprise_value": round(ev_sales, 2),
        "equity_value": round(ev_sales - net_debt, 2)
    }

    # P / E
    equity_pe = median_multiples["P_E"] * net_income
    valuations["P_E"] = {
        "enterprise_value": round(equity_pe + net_debt, 2),
        "equity_value": round(equity_pe, 2)
    }

    return valuations


# =====================================================
# High-level runner
# =====================================================

def run_trading_comps_from_excel(
    peer_xlsx_path: str,
    company_financials: Dict[str, float],
    sheet_name: str = "Peers"
) -> Dict[str, object]:
    """
    Full trading comparables pipeline (Excel-based).
    """

    peers_raw = load_peer_data_from_excel(peer_xlsx_path, sheet_name)
    peers_with_multiples = compute_trading_multiples(peers_raw)
    median_multiples = compute_median_multiples(peers_with_multiples)
    implied_valuation = compute_implied_valuation(
        company_financials,
        median_multiples
    )

    return {
        "median_multiples": median_multiples,
        "implied_valuation": implied_valuation
    }
