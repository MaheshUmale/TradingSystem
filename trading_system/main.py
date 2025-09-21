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

def calculate_systematic_parameters(ticker: str, lookback_L: int = 20, rsi_L: int = 14) -> pd.DataFrame:
    """
    Calculates essential systematic and technical parameters for a given stock.
    Handles yfinance multi-level columns by default.
    """
    df = yf.download(ticker, period="1y", progress=False, auto_adjust=True)
    if df.empty:
        return pd.DataFrame()

    # Define column tuples for consistent access
    close_col = ('Close', ticker)
    high_col = ('High', ticker)
    low_col = ('Low', ticker)
    log_returns_col = ('Log_Returns', '')

    # Calculate indicators using tuple-based column access
    df[log_returns_col] = np.log(df[close_col] / df[close_col].shift(1))

    HV_L = 10
    df[(f'HV_{HV_L}_pct', '')] = df[log_returns_col].rolling(window=HV_L).std() * math.sqrt(256) * 100
    df[(f'Simplified_ATR_{lookback_L}_pct', '')] = df[log_returns_col].rolling(window=lookback_L).std() * 100
    df[('Breakout_Threshold_pct', '')] = df[(f'Simplified_ATR_{lookback_L}_pct', '')].apply(lambda x: max(1.0, 0.5 * x))

    ewma_span = 36
    df[(f'EWMA_Volatility_{ewma_span}_pct', '')] = df[log_returns_col].ewm(span=ewma_span, adjust=False).std() * 100
    df[(f'EWMA_Volatility_{ewma_span}_annualized_pct', '')] = df[(f'EWMA_Volatility_{ewma_span}_pct', '')] * math.sqrt(256)

    df[(f'SMA_{lookback_L}', '')] = df[close_col].rolling(window=lookback_L).mean()
    df[(f'Distance_to_SMA_{lookback_L}_pct', '')] = ((df[close_col] - df[(f'SMA_{lookback_L}', '')]) / df[(f'SMA_{lookback_L}', '')]) * 100

    df[(f'High_{lookback_L}', '')] = df[high_col].rolling(window=lookback_L).max()
    df[(f'Low_{lookback_L}', '')] = df[low_col].rolling(window=lookback_L).min()
    df[(f'High_Low_Flag_{lookback_L}', '')] = (df[close_col] == df[(f'High_{lookback_L}', '')]) | (df[close_col] == df[(f'Low_{lookback_L}', '')])

    df[(f'RSI_{rsi_L}', '')] = talib.RSI(df[close_col], timeperiod=rsi_L)

    return df.dropna()

class LearningStore:
    def __init__(self, storage_path="learnings"):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)

    def store_learning(self, ticker: str, date: datetime, result_data: Dict):
        file_path = f"{self.storage_path}/{ticker}_{date.strftime('%Y%m%d')}_analysis.json"
        with open(file_path, 'w') as f:
            json.dump(result_data, f, indent=4)

def run_system_for_ticker(ticker: str) -> Dict[str, Any]:
    """
    Runs the full trading system for a single ticker and returns the results.
    """
    # Phase 1
    params_df = calculate_systematic_parameters(ticker)
    if params_df.empty:
        return None

    # Phase 2
    last_day_metrics = params_df.iloc[-1].to_dict()
    agent_forecast = stock_forecasting_agent(ticker, last_day_metrics)
    trading_style = style_preference_agent()

    trend_map = {'uptrend': 10.0, 'downtrend': -10.0, 'sideways': 0.0}
    scaled_forecast = trend_map.get(agent_forecast.get('trend'), 0.0)

    # Phase 3
    target_position = run_phase3_execution(
        forecast=scaled_forecast,
        ewma_volatility=last_day_metrics.get((f'EWMA_Volatility_36_pct', '')),
        instrument_price=last_day_metrics.get(('Close', ticker)),
        total_capital=100000,
        current_position=0
    )

    # Phase 4
    risk_thresholds = None
    if target_position != 0:
        risk_thresholds = run_phase4_risk_management(
            instrument_price=last_day_metrics.get(('Close', ticker)),
            volatility=last_day_metrics.get((f'EWMA_Volatility_36_pct', '')),
            style=trading_style
        )

    # Consolidate results
    result = {
        'ticker': ticker,
        'date': params_df.index[-1].strftime("%Y-%m-%d"),
        'instrument_price': last_day_metrics.get(('Close', ticker)),
        'trend': agent_forecast.get('trend'),
        'P_up': agent_forecast.get('P_up'),
        'P_down': agent_forecast.get('P_down'),
        'reasoning': agent_forecast.get('reasoning'),
        'target_position': target_position,
        'stop_loss': risk_thresholds.get('stop_loss') if risk_thresholds else None,
        'take_profit': risk_thresholds.get('take_profit') if risk_thresholds else None,
    }

    # Store result for learning/auditing
    learning_store = LearningStore()
    learning_store.store_learning(ticker, params_df.index[-1], result)

    return result
