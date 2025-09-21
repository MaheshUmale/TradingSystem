from typing import Dict

def calculate_dynamic_thresholds(
    instrument_price: float,
    volatility: float,
    style: str = 'conservative'
) -> Dict[str, float]:
    """
    Calculates dynamic stop-loss and take-profit thresholds.
    """

    # Multipliers tied to trading style (mock values)
    style_multipliers = {
        'conservative': {'sl': 1.5, 'tp': 2.0},
        'aggressive': {'sl': 2.5, 'tp': 4.0}
    }

    multipliers = style_multipliers.get(style, style_multipliers['conservative'])

    sl_distance = instrument_price * volatility / 100 * multipliers['sl']
    tp_distance = instrument_price * volatility / 100 * multipliers['tp']

    stop_loss_price = instrument_price - sl_distance
    take_profit_price = instrument_price + tp_distance

    return {
        "stop_loss": stop_loss_price,
        "take_profit": take_profit_price
    }

def run_phase4_risk_management(
    instrument_price: float,
    volatility: float, # Unannualized standard deviation of returns
    style: str
):
    """
    Runs the full Phase 4 risk management logic.
    """
    print("\n--- Phase 4: Active Trade Management ---")

    thresholds = calculate_dynamic_thresholds(instrument_price, volatility, style)

    print(f"Dynamic Stop-Loss Price: ${thresholds['stop_loss']:,.2f}")
    print(f"Dynamic Take-Profit Price: ${thresholds['take_profit']:,.2f}")

    return thresholds
