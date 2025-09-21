import math
from typing import Dict

def calculate_volatility_scalar(
    daily_cash_volatility_target: float,
    instrument_value_volatility: float
) -> float:
    """
    Calculates the volatility scalar.
    """
    if instrument_value_volatility == 0:
        return 0.0
    return daily_cash_volatility_target / instrument_value_volatility

def calculate_subsystem_position(
    volatility_scalar: float,
    forecast: float
) -> float:
    """
    Calculates the unrounded subsystem position.
    """
    return (volatility_scalar * forecast) / 10.0

def get_execution_decision(
    target_position: float,
    current_position: int,
    position_inertia: float = 0.1
) -> str:
    """
    Determines whether to issue a trade based on position inertia.
    """
    rounded_target_position = round(target_position)

    if abs(rounded_target_position - current_position) > position_inertia:
        return f"Trade to new position: {rounded_target_position}"
    else:
        return f"Hold current position: {current_position}"

def run_phase3_execution(
    forecast: float,
    ewma_volatility: float,
    instrument_price: float,
    total_capital: float,
    annual_risk_target: float = 0.20, # e.g., 20%
    current_position: int = 0
):
    """
    Runs the full Phase 3 execution and position sizing logic.
    """
    print("\n--- Phase 3: Execution and Position Sizing ---")

    # 2.4 Risk Profiling and Volatility Targeting
    daily_risk_target = (total_capital * annual_risk_target) / 16 # Carver's sqrt of time rule

    # Instrument Value Volatility (risk of one block in account currency)
    # Assuming one block is one share for simplicity
    instrument_value_volatility = instrument_price * ewma_volatility / 100 # ewma_volatility is in %

    # 3.1 Volatility Scalar Calculation
    volatility_scalar = calculate_volatility_scalar(daily_risk_target, instrument_value_volatility)

    # 3.2 Subsystem Position Sizing
    target_position = calculate_subsystem_position(volatility_scalar, forecast)

    # 3.4 Execution Decision
    decision = get_execution_decision(target_position, current_position)

    print(f"Daily Risk Target: ${daily_risk_target:,.2f}")
    print(f"Instrument Value Volatility: ${instrument_value_volatility:,.2f}")
    print(f"Volatility Scalar: {volatility_scalar:.4f}")
    print(f"Target Position (unrounded): {target_position:.4f}")
    print(f"Execution Decision: {decision}")

    return round(target_position)
