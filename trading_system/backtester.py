import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
from trading_system.main import calculate_systematic_parameters
from trading_system.agents import stock_forecasting_agent
from tqdm import tqdm

# --- Data Storage ---
def store_backtest_record(ticker: str, date: str, record: dict, storage_path="backtest_learnings/"):
    """Saves a single labeled record from a backtest."""
    os.makedirs(storage_path, exist_ok=True)
    file_path = f"{storage_path}/{ticker}_{date.replace('-', '')}_record.json"
    with open(file_path, 'w') as f:
        json.dump(record, f, indent=4)

# --- Evaluation Logic ---
def evaluate_forecast(predicted_trend: str, actual_log_return: float, volatility: float) -> bool:
    """
    Evaluates if a forecast was successful based on the actual outcome.
    """
    epsilon = volatility * 0.5
    if actual_log_return > epsilon:
        true_label = "uptrend"
    elif actual_log_return < -epsilon:
        true_label = "downtrend"
    else:
        true_label = "sideways"
    return predicted_trend == true_label

# --- Backtesting Workflow ---
def run_backtest(ticker: str, start_date: str, end_date: str, backtest_days: int = 252):
    """
    Runs a backtest for a given ticker over a specified period.
    """
    print(f"--- Starting Backtest for {ticker} from {start_date} to {end_date} ---")

    full_data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
    if full_data.empty:
        print(f"Could not download data for {ticker}.")
        return []

    if not isinstance(full_data.columns, pd.MultiIndex):
        full_data.columns = pd.MultiIndex.from_product([full_data.columns, [ticker]])

    all_results = []
    start_index = max(0, len(full_data) - backtest_days)

    print(f"Backtesting over the last {len(full_data) - start_index} trading days...")
    for i in tqdm(range(start_index, len(full_data) - 1)):
        historical_slice = full_data.iloc[0:i+1]

        params_df = calculate_systematic_parameters(ticker, data=historical_slice)
        if params_df.empty:
            continue

        last_day_metrics = params_df.iloc[-1].to_dict()
        agent_forecast = stock_forecasting_agent(ticker, last_day_metrics)

        today_price = full_data.iloc[i][('Close', ticker)]
        tomorrow_price = full_data.iloc[i+1][('Close', ticker)]
        actual_log_return = np.log(tomorrow_price / today_price)

        daily_volatility = last_day_metrics.get(('EWMA_Volatility_36_pct', '')) / 100
        success = evaluate_forecast(agent_forecast.get('trend'), actual_log_return, daily_volatility)

        result = {
            "date": full_data.index[i].strftime("%Y-%m-%d"),
            "ticker": ticker,
            "inputs": {k[0]: v for k, v in last_day_metrics.items()}, # Store flattened inputs
            "predicted_trend": agent_forecast.get('trend'),
            "prediction_reasoning": agent_forecast.get('reasoning'),
            "actual_log_return": actual_log_return,
            "success": success
        }
        all_results.append(result)
        store_backtest_record(ticker, result["date"], result)

    return all_results

def generate_backtest_report(results: list):
    """
    Generates a report from the backtest results.
    """
    print("\n--- Backtest Performance Report ---")

    if not results:
        print("No backtest results to report.")
        return

    df = pd.DataFrame(results)

    total_forecasts = len(df)
    successful_forecasts = df['success'].sum()
    accuracy = (successful_forecasts / total_forecasts) * 100 if total_forecasts > 0 else 0

    print(f"Total Forecasts Made: {total_forecasts}")
    print(f"Successful Forecasts:  {successful_forecasts}")
    print(f"Overall Accuracy:      {accuracy:.2f}%")

    uptrend_df = df[df['predicted_trend'] == 'uptrend']
    downtrend_df = df[df['predicted_trend'] == 'downtrend']

    if not uptrend_df.empty:
        uptrend_accuracy = (uptrend_df['success'].sum() / len(uptrend_df)) * 100
        print(f"\nUptrend Forecasts ({len(uptrend_df)} total):")
        print(f"  - Accuracy: {uptrend_accuracy:.2f}%")

    if not downtrend_df.empty:
        downtrend_accuracy = (downtrend_df['success'].sum() / len(downtrend_df)) * 100
        print(f"\nDowntrend Forecasts ({len(downtrend_df)} total):")
        print(f"  - Accuracy: {downtrend_accuracy:.2f}%")

if __name__ == "__main__":
    TICKER_TO_TEST = "RELIANCE.NS"
    START_DATE = "2023-01-01"
    END_DATE = "2023-12-31" # Use a smaller range for faster testing

    backtest_results = run_backtest(TICKER_TO_TEST, START_DATE, END_DATE, backtest_days=60) # Test last 60 days
    generate_backtest_report(backtest_results)
