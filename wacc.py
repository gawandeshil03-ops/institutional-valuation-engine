from typing import Dict


def calculate_cost_of_equity(
    risk_free_rate: float,
    beta: float,
    market_risk_premium: float
) -> float:
    """
    CAPM formula:
    Cost of Equity = Rf + Beta * (Rm - Rf)
    """
    if beta is None:
        raise ValueError("Beta is required to compute cost of equity.")

    return risk_free_rate + beta * market_risk_premium


def calculate_cost_of_debt_after_tax(
    pre_tax_cost_of_debt: float,
    tax_rate: float
) -> float:
    """
    After-tax cost of debt:
    Rd * (1 - Tax Rate)
    """
    if not (0 <= tax_rate <= 1):
        raise ValueError("Tax rate must be between 0 and 1.")

    return pre_tax_cost_of_debt * (1 - tax_rate)


def calculate_capital_weights(
    market_value_equity: float,
    total_debt: float
) -> Dict[str, float]:
    """
    Compute capital structure weights using market values.
    """
    if market_value_equity <= 0:
        raise ValueError("Market value of equity must be positive.")

    if total_debt < 0:
        raise ValueError("Total debt cannot be negative.")

    total_capital = (market_value_equity) + total_debt

    equity_weight = (market_value_equity) / total_capital
    debt_weight = total_debt / total_capital

    return {
        "equity_weight": equity_weight,
        "debt_weight": debt_weight
    }


def calculate_wacc(
    market_data: Dict[str, float],
    financials: Dict[str, float],
    assumptions: Dict[str, float]
) -> Dict[str, float]:
    """
    Master WACC function.

    Parameters
    
    market_data : dict
        Expected keys:
        - market_cap
        - beta

    financials : dict
        Expected keys:
        - total_debt

    assumptions : dict
        Expected keys:
        - risk_free_rate
        - market_risk_premium
        - cost_of_debt
        - tax_rate
    """

    # Extract inputs
    market_cap = market_data.get("market_cap")

    adjusted_beta = assumptions["adjusted_beta"]
    
    if adjusted_beta > 0:
        beta = adjusted_beta
        print(f"⚠️ Using Adjusted Beta from Excel: {beta}")
    else: 
        beta = market_data.get("beta")
        print(f"ℹ️ Using Market Beta from Yahoo: {beta}")

    total_debt = financials.get("total_debt")

    risk_free_rate = assumptions["risk_free_rate"]
    market_risk_premium = assumptions["market_risk_premium"]
    pre_tax_cost_of_debt = assumptions["cost_of_debt"]
    tax_rate = assumptions["tax_rate"]


    # Input validation
    for name in ["risk_free_rate", "market_risk_premium", "cost_of_debt", "tax_rate"]:
        if name not in assumptions or assumptions[name] is None:
            raise ValueError(f"Missing WACC input: {name}")


    # Compute components
    cost_of_equity = calculate_cost_of_equity(
        risk_free_rate,
        beta,
        market_risk_premium
    )

    cost_of_debt_after_tax = calculate_cost_of_debt_after_tax(
        pre_tax_cost_of_debt,
        tax_rate
    )

    weights = calculate_capital_weights(
        market_value_equity=market_cap,
        total_debt=total_debt
    )

    # Compute WACC
    wacc = (
        weights["equity_weight"] * cost_of_equity +
        weights["debt_weight"] * cost_of_debt_after_tax
    )

    # Sanity checks
    if wacc <= 0:
        raise ValueError("Computed WACC is non-positive. Check inputs.")

    if wacc < 0.05 or wacc > 0.20:
        print("⚠️ Warning: WACC outside typical range (5% - 20%).")

    return {
        "cost_of_equity": round(cost_of_equity, 4),
        "cost_of_debt_after_tax": round(cost_of_debt_after_tax, 4),
        "equity_weight": round(weights["equity_weight"], 4),
        "debt_weight": round(weights["debt_weight"], 4),
        "wacc": round(wacc, 4)
    }