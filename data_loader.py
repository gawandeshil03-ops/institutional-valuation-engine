import pandas as pd
import yfinance as yf
from pathlib import Path


# =========================
# CONFIGURATION
# =========================

REQUIRED_SHEETS = {
    "Income_Statement": ["Year", "Revenue", "EBITDA", "D&A", "EBIT", "Taxes"],
    "Cash_Flow": ["Year", "CapEx", "Change_NWC"],
    "Balance_Sheet": ["Year", "Debt", "Cash", "Shares"],
    "Assumptions": ["Metric", "Value_Bear", "Value_Base", "Value_Bull"]
}


# =========================
# EXCEL LOADER
# =========================

def load_excel_financials(file_path: str, case: str = "base") -> dict:
    """
   Load financial inputs with scenario support.
    case: 'base', 'bull', or 'bear'

    Returns a dictionary containing:
    - income_statement (DataFrame)
    - cash_flow (DataFrame)
    - balance_sheet (DataFrame)
    - assumptions (dict)
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    excel = pd.ExcelFile(file_path)

    # Check required sheets 
    for sheet in REQUIRED_SHEETS:
        if sheet not in excel.sheet_names:
            raise ValueError(f"Missing required sheet: '{sheet}'")

    # Load sheets
    income_stmt = pd.read_excel(excel, "Income_Statement")
    cash_flow = pd.read_excel(excel, "Cash_Flow")
    balance_sheet = pd.read_excel(excel, "Balance_Sheet")
    assumptions_df = pd.read_excel(excel, "Assumptions")

    # Validate columns
    _validate_columns(income_stmt, "Income_Statement")
    _validate_columns(cash_flow, "Cash_Flow")
    _validate_columns(balance_sheet, "Balance_Sheet")
    _validate_columns(assumptions_df, "Assumptions")

    # Clean & format
    income_stmt = _clean_financial_df(income_stmt)
    cash_flow = _clean_financial_df(cash_flow)
    balance_sheet = _clean_financial_df(balance_sheet)

    # Validate historical depth 
    if income_stmt.shape[0] < 3:
        raise ValueError("Income Statement must contain at least 3 historical years.")

    # =========================
    #   SCENARIO SELECTION 
    # =========================

    # Construct column name, e.g., "Value_Base"
    target_col = f"Value_{case.title()}"
    
    if target_col not in assumptions_df.columns:
        # Fallback for backward compatibility
        if "Value" in assumptions_df.columns:
            print(f"⚠️ Warning: Column '{target_col}' not found. Using 'Value' column.")
            target_col = "Value"
        else:
            raise ValueError(f"Missing assumption column: '{target_col}'")

    # Convert to dict using the selected column
    assumptions = (
        assumptions_df
        .set_index("Metric")[target_col]
        .to_dict()
    )

    return {
        "income_statement": income_stmt,
        "cash_flow": cash_flow,
        "balance_sheet": balance_sheet,
        "assumptions": assumptions
    }


# =========================
# API MARKET DATA
# =========================

def load_market_data(ticker: str) -> dict:
    """
    Pull basic market data using yfinance.
    """

    stock = yf.Ticker(ticker)
    info = stock.info

    market_data = {
        "ticker": ticker,
        "share_price": info.get("currentPrice"),
        "market_cap": info.get("marketCap") / 1e6,
        "beta": info.get("beta"),
        "shares_outstanding": info.get("sharesOutstanding") / 1e6
    }

    if market_data["share_price"] is None:
        raise ValueError(f"Unable to retrieve market data for ticker: {ticker}")

    return market_data


# =========================
# INTERNAL HELPERS
# =========================

def _validate_columns(df: pd.DataFrame, sheet_name: str) -> None:
    """
    Ensure required columns exist.
    """
    required_cols = REQUIRED_SHEETS[sheet_name]
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        raise ValueError(
            f"Sheet '{sheet_name}' is missing columns: {missing}"
        )


def _clean_financial_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean financial DataFrame:
    - Drop empty rows
    - Ensure Year is int
    - Sort by Year
    """

    df = df.dropna(how="all")
    df["Year"] = df["Year"].astype(int)
    df = df.sort_values("Year").reset_index(drop=True)

    return df