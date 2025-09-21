import yfinance as yf
import pandas as pd
import numpy as np
import math
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import talib
from trading_system.agents import (
    news_sentiment_agent,
    financial_report_agent,
    stock_forecasting_agent,
    style_preference_agent
)
from trading_system.execution import run_phase3_execution
from trading_system.risk_management import run_phase4_risk_management

# --- Phase 1: Foundational Intelligence and Learning ---

def select_instruments(tickers: List[str]) -> List[str]:
    """
    Selects instruments based on data availability.
    """
    selected = []
    for ticker in tickers:
        data = yf.download(ticker, period="1y", progress=False, auto_adjust=True)
        if not data.empty:
            print(f"Data available for {ticker}. Selected.")
            selected.append(ticker)
        else:
            print(f"Data not available for {ticker}. Skipped.")
    return selected

def calculate_systematic_parameters(ticker: str, lookback_L: int = 20, rsi_L: int = 14) -> pd.DataFrame:
    """
    Calculates essential systematic and technical parameters for a given stock.
    """
    print(f"[{ticker}] Retrieving data for systematic parameter calculation...")
    df = yf.download(ticker, period="1y", progress=False, auto_adjust=True)

    if df.empty:
        print(f"Error: Could not retrieve data for {ticker}.")
        return pd.DataFrame()

    # Calculate indicators on the multi-level column DataFrame
    df[('Log_Returns', '')] = np.log(df[('Close', ticker)] / df[('Close', ticker)].shift(1))
    HV_L = 10
    df[(f'HV_{HV_L}_pct', '')] = df[('Log_Returns', '')].rolling(window=HV_L).std() * math.sqrt(256) * 100
    df[(f'Simplified_ATR_{lookback_L}_pct', '')] = df[('Log_Returns', '')].rolling(window=lookback_L).std() * 100
    df[('Breakout_Threshold_pct', '')] = df[(f'Simplified_ATR_{lookback_L}_pct', '')].apply(lambda x: max(1.0, 0.5 * x))
    ewma_span = 36
    df[(f'EWMA_Volatility_{ewma_span}_pct', '')] = df[('Log_Returns', '')].ewm(span=ewma_span, adjust=False).std() * 100
    df[(f'EWMA_Volatility_{ewma_span}_annualized_pct', '')] = df[(f'EWMA_Volatility_{ewma_span}_pct', '')] * math.sqrt(256)
    df[(f'SMA_{lookback_L}', '')] = df[('Close', ticker)].rolling(window=lookback_L).mean()
    df[(f'Distance_to_SMA_{lookback_L}_pct', '')] = ((df[('Close', ticker)] - df[(f'SMA_{lookback_L}', '')]) / df[(f'SMA_{lookback_L}', '')]) * 100
    df[(f'High_{lookback_L}', '')] = df[('High', ticker)].rolling(window=lookback_L).max()
    df[(f'Low_{lookback_L}', '')] = df[('Low', ticker)].rolling(window=lookback_L).min()
    df[(f'High_Low_Flag_{lookback_L}', '')] = (df[('Close', ticker)] == df[(f'High_{lookback_L}', '')]) | (df[('Close', ticker)] == df[(f'Low_{lookback_L}', '')])
    df[(f'RSI_{rsi_L}', '')] = talib.RSI(df[('Close', ticker)], timeperiod=rsi_L)

    return df.dropna()

class LearningStore:
    def __init__(self, storage_path="learnings"):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        self.lookback_days = 20
        self.alpha = 0.5
        self.e_min = 0.005

    def _calculate_reward_threshold(self, log_returns: pd.Series) -> float:
        if len(log_returns) < self.lookback_days: return self.e_min
        avg_daily_volatility = log_returns.abs().rolling(window=self.lookback_days).mean().iloc[-1]
        return max(self.alpha * avg_daily_volatility, self.e_min)

    def _evaluate_forecast_outcome(self, daily_log_return: float, predicted_trend: str, log_returns_series: pd.Series) -> Dict[str, Any]:
        if not daily_log_return or not predicted_trend:
            return {"sign_ok": False, "label_3cls": "N/A", "success": False}
        epsilon = self._calculate_reward_threshold(log_returns_series)
        true_label = "uptrend" if daily_log_return > epsilon else "downtrend" if daily_log_return < -epsilon else "sideways"
        sign_ok = (predicted_trend == true_label) or (predicted_trend == "sideways" and abs(daily_log_return) <= epsilon)
        success = sign_ok and (true_label != "sideways")
        return {"true_log_return": daily_log_return, "epsilon_threshold": epsilon, "true_label_3cls": true_label, "predicted_trend": predicted_trend, "sign_ok": sign_ok, "success": success}

    def store_learning(self, ticker: str, date: datetime, technical_metrics: Dict[str, float], agent_forecast: Dict[str, Any], trade_outcome: Dict[str, Any], historical_log_returns: pd.Series):
        quant_features = {k[0]: v for k, v in technical_metrics.items() if k[0] in ['Simplified_ATR_20_pct', 'RSI_14', 'Distance_to_SMA_20_pct', 'Breakout_Threshold_pct']}
        evaluation_metrics = self._evaluate_forecast_outcome(trade_outcome.get('realized_log_return_next_day', 0.0), agent_forecast.get('trend'), historical_log_returns)
        learning_record = {
            "ticker": ticker, "date": date.strftime("%Y-%m-%d"),
            "quant_features_input": quant_features,
            "agent_forecast_output": agent_forecast,
            "evaluation": evaluation_metrics,
            "reward_signals": {"good_or_bad": "good" if evaluation_metrics["success"] else "bad", "DA_reward": trade_outcome.get('DA_reward', 0.0)}
        }
        file_path = f"{self.storage_path}/{ticker}_{date.strftime('%Y%m%d')}_learning.json"
        with open(file_path, 'w') as f:
            json.dump(learning_record, f, indent=4)
        print(f"[{ticker}] Learning record saved to {file_path}")
        print(f"[{ticker}] Evaluation outcome: {'Success' if evaluation_metrics['success'] else 'Failure'} (True Label: {evaluation_metrics['true_label_3cls']})")

# --- Orchestration ---

def run_system_for_ticker(ticker: str):
    """
    Runs the full trading system for a given ticker.
    """
    print(f"\n--- Running Trading System for {ticker} ---")

    # Phase 1: Foundational Intelligence & Learning
    print("\n--- Phase 1: Foundational Intelligence & Learning ---")
    sentiment = news_sentiment_agent(ticker)
    financials = financial_report_agent(ticker)
    params_df = calculate_systematic_parameters(ticker)
    if params_df.empty:
        print(f"[{ticker}] Could not proceed without systematic parameters.")
        return
    print(f"\n[{ticker}] Calculated Systematic Parameters (Last 5 days):")
    print(params_df.tail())

    # Phase 2: Opportunity Scanning & Forecasting
    print("\n--- Phase 2: Opportunity Scanning & Forecasting ---")
    last_day_metrics = params_df.iloc[-1].to_dict()
    agent_forecast = stock_forecasting_agent(ticker, last_day_metrics)
    trading_style = style_preference_agent()

    trend_map = {'uptrend': 10.0, 'downtrend': -10.0, 'sideways': 0.0}
    scaled_forecast = trend_map.get(agent_forecast.get('trend'), 0.0)

    # Phase 3: Execution and Position Sizing
    target_position = run_phase3_execution(
        forecast=scaled_forecast,
        ewma_volatility=last_day_metrics[('EWMA_Volatility_36_pct', '')],
        instrument_price=last_day_metrics[('Close', ticker)],
        total_capital=100000,
        current_position=0
    )

    # Phase 4: Active Trade Management
    if target_position != 0:
        run_phase4_risk_management(
            instrument_price=last_day_metrics[('Close', ticker)],
            volatility=last_day_metrics[('EWMA_Volatility_36_pct', '')],
            style=trading_style
        )

    # --- Learning Simulation ---
    mock_outcome = {'realized_log_return_next_day': 0.007, 'DA_reward': 0.015}
    learning_store = LearningStore()
    learning_store.store_learning(
        ticker=ticker,
        date=params_df.index[-1],
        technical_metrics=last_day_metrics,
        agent_forecast=agent_forecast,
        trade_outcome=mock_outcome,
        historical_log_returns=params_df[('Log_Returns', '')]
    )

# --- Main Execution ---
if __name__ == "__main__":
    candidate_tickers = ['RELIANCE.NS', 'TCS.NS', 'INVALIDTICKER']
    print("--- Instrument Selection ---")
    selected_tickers = select_instruments(candidate_tickers)

    if 'RELIANCE.NS' in selected_tickers:
        run_system_for_ticker('RELIANCE.NS')
