import argparse
import json
import sys
from datetime import date
from pathlib import Path
import pandas as pd

# =========================
# Imports
# =========================
from src.data_loader import load_excel_financials, load_market_data
from src.wacc import calculate_wacc
from src.dcf_model import run_dcf
from src.comps_model import run_trading_comps_from_excel
from src.sensitivity_analysis import generate_sensitivity_table
from src.excel_export import export_to_excel
from src.sanity_check import run_sanity_checks
from src.plotting import plot_football_field

# =========================
# Helpers
# =========================

def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {}

def parse_arguments():
    config = load_config("config.json")
    parser = argparse.ArgumentParser(description="Valuation Engine")
    
    parser.add_argument("--ticker", type=str, default=config.get("ticker", "AMZN"))
    parser.add_argument("--excel", type=str, default=config.get("excel_path", "Valuation Engine/inputs/company_financials.xlsx"))
    parser.add_argument("--peers", type=str, default=config.get("peers_path", "Valuation Engine/inputs/peers.xlsx"))
    parser.add_argument("--output", type=str, default=config.get("output_file", "valuation_output.xlsx"))
    parser.add_argument("--case", type=str, default="base", choices=["base", "bull", "bear"],
                        help="Primary scenario to run for detailed forecast")

    return parser.parse_args()

def _safe_float(val):
    if isinstance(val, str):
        val = val.replace("%", "").strip()
    return float(val)

def run_valuation_for_case(case_name, excel_path, market_data):
    """
    Helper to run the full valuation logic for a single case (bear/base/bull).
    Returns (dcf_results, wacc, assumptions).
    """
    # Load Data
    data = load_excel_financials(excel_path, case=case_name)
    
    # Parse Assumptions
    raw_assumptions = data["assumptions"]
    assumptions = {
        "revenue_growth": raw_assumptions["Revenue growth"],
        "ebitda_margin": raw_assumptions["EBITDA margin"],
        "depreciation_pct_revenue": raw_assumptions["Depreciation % revenue"],
        "capex_pct_revenue": raw_assumptions["CapEx % revenue"],
        "nwc_pct_revenue": raw_assumptions["NWC % revenue"],
        
        "tax_rate": _safe_float(raw_assumptions["Tax rate"]),
        "forecast_years": int(raw_assumptions["Forecast years"]),
        "risk_free_rate": _safe_float(raw_assumptions["Risk-free rate"]),
        "adjusted_beta": _safe_float(raw_assumptions["Adjusted beta"]),
        "market_risk_premium": _safe_float(raw_assumptions["Market risk premium"]),
        "cost_of_debt": _safe_float(raw_assumptions["Cost of debt"]),

        "terminal_method": raw_assumptions["Terminal Method"].strip().lower(),
        "terminal_growth_rate": _safe_float(raw_assumptions["Terminal growth rate"]),
        "exit_ebitda_multiple": _safe_float(raw_assumptions["Exit EBITDA multiple"]),
    }
    
    # Prepare Financials
    latest_financials = {
        "revenue": data["income_statement"]["Revenue"].iloc[-1],
        "ebitda": data["income_statement"]["EBITDA"].iloc[-1],
        "depreciation": data["income_statement"]["D&A"].iloc[-1],
        "capex": data["cash_flow"]["CapEx"].iloc[-1],
        "nwc": data["cash_flow"]["Change_NWC"].iloc[-1],
        "total_debt": data["balance_sheet"]["Debt"].iloc[-1],
        "cash": data["balance_sheet"]["Cash"].iloc[-1],
        "net_income": data["income_statement"]["Net Income"].iloc[-1],
    }
    
    # Compute WACC
    wacc_output = calculate_wacc(
        market_data=market_data,
        financials={"total_debt": latest_financials["total_debt"]},
        assumptions={
            "risk_free_rate": assumptions["risk_free_rate"],
            "market_risk_premium": assumptions["market_risk_premium"],
            "cost_of_debt": assumptions["cost_of_debt"],
            "tax_rate": assumptions["tax_rate"],
            "adjusted_beta": assumptions["adjusted_beta"]
        }
    )
    
    # Run DCF
    dcf_results = run_dcf(
        financials=latest_financials,
        market_data=market_data,
        assumptions=assumptions,
        wacc=wacc_output["wacc"],
        valuation_date=date.today()
    )
    
    return dcf_results, wacc_output, assumptions, latest_financials, data

# =========================
# Main Execution
# =========================

def main():
    args = parse_arguments()
    
    if not Path(args.excel).exists():
        print(f"❌ Error: Input file '{args.excel}' not found.")
        sys.exit(1)

    print(f"\n🚀 Starting Valuation for {args.ticker}...")
    print(f"📅 Valuation Date: {date.today()}")

    try:
        market_data = load_market_data(args.ticker)
    except Exception as e:
        print(f"❌ Market Data Error: {e}")
        sys.exit(1)

    # ==========================================
    # Run All 3 Scenarios (Bear, Base, Bull)
    # ==========================================
    print("\n🔄 Running Scenario Analysis...")
    scenario_results = {}
    
    # Placeholders for the "Primary" selected case data (to be used in plotting/export)
    primary_dcf = None
    primary_wacc = None
    primary_assump = None
    primary_fin = None
    primary_data_raw = None

    for case in ["bear", "base", "bull"]:
        print(f"   ... calculating {case.upper()} case")
        try:
            dcf, wacc, assump, fin, raw_data = run_valuation_for_case(case, args.excel, market_data)
            
            # Store summary metrics for the Excel "Scenarios" tab
            scenario_results[case] = {
                "Implied Share Price": dcf["implied_share_price"],
                "Equity Value": dcf["equity_value"],
                "Enterprise Value": dcf["enterprise_value"],
                "WACC": wacc["wacc"],
                "Terminal Growth Rate": assump["terminal_growth_rate"],
                "Exit Multiple": assump["exit_ebitda_multiple"]
            }
            
            # If this is the user-selected case, capture the full details
            if case == args.case:
                primary_dcf = dcf
                primary_wacc = wacc
                primary_assump = assump
                primary_fin = fin
                primary_data_raw = raw_data

        except Exception as e:
            print(f"   ⚠️ Could not run {case} case: {e}")
            scenario_results[case] = {}

    if not primary_dcf:
        print("❌ Critical Error: The selected primary case failed to run.")
        sys.exit(1)

    # =========================
    # Sanity Checks (Primary Case)
    # =========================
    run_sanity_checks(primary_data_raw["income_statement"], primary_assump)

    print(f"\n💰 {args.case.upper()} Case Share Price: ${primary_dcf['implied_share_price']:.2f}")

    # =========================
    # Run Trading Comps
    # =========================
    comps_results = {}
    if Path(args.peers).exists():
        comps_results = run_trading_comps_from_excel(
            peer_xlsx_path=args.peers,
            company_financials={
                "revenue": primary_fin["revenue"],
                "ebitda": primary_fin["ebitda"],
                "net_income": primary_fin["net_income"],
                "total_debt": primary_fin["total_debt"],
                "cash": primary_fin["cash"]
            }
        )
    else:
        print(f"⚠️ Warning: Peers file '{args.peers}' not found. Skipping Comps.")

    # =========================
    # Sensitivity Analysis (Primary Case)
    # =========================
    print("\n🎲 Running Sensitivity Analysis...")
    sensitivity_df = generate_sensitivity_table(
        market_data=market_data,
        financials=primary_fin,
        base_assumptions=primary_assump,
        base_wacc=primary_wacc["wacc"],
        run_dcf_func=run_dcf
    )

    # =========================
    # Generate Football Field
    # =========================
    dcf_min = sensitivity_df.min().min()
    dcf_max = sensitivity_df.max().max()
    r_low = market_data.get("fiftyTwoWeekLow", market_data["share_price"] * 0.8)
    r_high = market_data.get("fiftyTwoWeekHigh", market_data["share_price"] * 1.2)

    valuation_ranges = {
        "52-Week Range": [r_low, r_high],
        f"DCF ({args.case.title()})": [dcf_min, dcf_max],
        "Scenario Range": [
            min(s["Implied Share Price"] for s in scenario_results.values() if "Implied Share Price" in s),
            max(s["Implied Share Price"] for s in scenario_results.values() if "Implied Share Price" in s)
        ]
    }
    
    if comps_results:
        implied_p = comps_results["implied_valuation"]["EV_EBITDA"]["equity_value"] / market_data["shares_outstanding"]
        valuation_ranges["Trading Comps"] = [implied_p * 0.9, implied_p * 1.1]

    plot_football_field(
        valuation_ranges=valuation_ranges,
        current_share_price=market_data["share_price"],
        ticker=args.ticker,
        filename=args.output.replace(".xlsx", ".png")
    )

    # =========================
    # Export to Excel
    # =========================
    summary_payload = {
        "Ticker": args.ticker,
        "Valuation Date": str(date.today()),
        "Current Share Price": market_data["share_price"],
        "Selected Case": args.case.title(),
        "Implied DCF Price": primary_dcf["implied_share_price"],
        "WACC": primary_wacc["wacc"],
        "Enterprise Value": primary_dcf["enterprise_value"],
        "Equity Value": primary_dcf["equity_value"]
    }

    export_to_excel(
        summary_data=summary_payload,
        forecast_data=primary_dcf["discounted_fcff"],
        dcf_data=primary_dcf,
        comps_data=comps_results,
        sensitivity_df=sensitivity_df,
        scenario_data=scenario_results,
        filename=args.output
    )

if __name__ == "__main__":
    main()