import yfinance as yf
import pandas as pd
import numpy as np
import math
import json
from datetime import datetime
from typing import Dict, Any, List

# --- Phase 1: Foundational Intelligence and Learning ---

# --- Step 1.1: Instrument Selection & Data Acquisition ---

def select_instruments(tickers: List[str]) -> List[str]:
    """
    Selects instruments based on data availability.
    In a real system, this would include checks for liquidity, trading costs, etc.
    """
    selected = []
    for ticker in tickers:
        # A simple check for data availability for the last year.
        data = yf.download(ticker, period="1y", progress=False)
        if not data.empty:
            print(f"Data available for {ticker}. Selected.")
            selected.append(ticker)
        else:
            print(f"Data not available for {ticker}. Skipped.")
    return selected

# Data acquisition is performed within step 1.3.

# --- Step 1.2: Multi-modal Data Processing ---

def news_sentiment_agent(ticker: str) -> float:
    """
    Placeholder for the News-Sentiment Agent.
    This agent would filter real-time news, dedupe, and output a sentiment score.
    Returns a mock sentiment score between -1 (very negative) and 1 (very positive).
    """
    print(f"[{ticker}] News-Sentiment Agent: Analyzing news... (mock)")
    return np.random.uniform(-1, 1)

def financial_report_agent(ticker: str) -> Dict[str, Any]:
    """
    Placeholder for the Financial-Report Agent.
    This agent would use RAG to analyze financial reports.
    Returns mock key indicators.
    """
    print(f"[{ticker}] Financial-Report Agent: Analyzing reports... (mock)")
    return {
        "revenue_growth_qoq": np.random.uniform(-0.1, 0.2),
        "net_profit_margin": np.random.uniform(0.05, 0.25),
        "debt_to_equity": np.random.uniform(0.1, 1.5),
        "potential_risks": ["Market competition", "Regulatory changes"] # Mock risks
    }


# --- Step 1.3: Systematic Parameter Learning (Backtesting) ---
# This is the code provided by the user. I'll make sure it's integrated.

def calculate_systematic_parameters(ticker: str, lookback_L: int = 20, rsi_L: int = 14) -> pd.DataFrame:
    """
    Calculates essential systematic and technical parameters for a given stock,
    based on the principles of volatility standardisation and objective technical analysis.

    Parameters:
    - ticker (str): Stock ticker (e.g., 'RELIANCE.NS' for NSE:RELIANCE in yfinance).
    - lookback_L (int): Default lookback period for SMA and ATR (20 days).
    - rsi_L (int): Lookback period for RSI (14 days).

    Returns:
    - pd.DataFrame: DataFrame containing calculated technical parameters.
    """

    # --- 1. Data Retrieval (Source: yfinance) ---
    print(f"[{ticker}] Retrieving data for systematic parameter calculation...")
    df = yf.download(ticker, period="1y", progress=False)

    if df.empty:
        print(f"Error: Could not retrieve data for {ticker}.")
        return pd.DataFrame()

    # Calculate Daily Log Returns
    df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))

    # --- 2. Volatility and Range Metrics (Carver's Objective Risk Measurement) ---
    HV_L = 10
    annualization_factor = math.sqrt(256)
    df[f'HV_{HV_L}_pct'] = df['Log_Returns'].rolling(window=HV_L).std() * annualization_factor * 100

    df[f'Simplified_ATR_{lookback_L}_pct'] = df['Log_Returns'].rolling(window=lookback_L).std() * 100

    df['Breakout_Threshold_pct'] = df[f'Simplified_ATR_{lookback_L}_pct'].apply(lambda x: max(1.0, 0.5 * x))

    # --- 3. Momentum and Condition Metrics (TradingGroup Inputs) ---
    df[f'SMA_{lookback_L}'] = df['Close'].rolling(window=lookback_L).mean()

    df[f'Distance_to_SMA_{lookback_L}_pct'] = ((df['Close'] - df[f'SMA_{lookback_L}']) / df[f'SMA_{lookback_L}']) * 100

    df[f'High_{lookback_L}'] = df['Close'].rolling(window=lookback_L).max()
    df[f'Low_{lookback_L}'] = df['Close'].rolling(window=lookback_L).min()
    df[f'High_Low_Flag_{lookback_L}'] = (df['Close'] == df[f'High_{lookback_L}']) | (df['Close'] == df[f'Low_{lookback_L}'])

    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_L).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_L).mean()
    RS = gain / loss
    df[f'RSI_{rsi_L}'] = 100 - (100 / (1 + RS))

    # --- 4. Final Cleanup and Output ---
    output_columns = [
        'Close',
        'Log_Returns',
        f'HV_{HV_L}_pct',
        f'Simplified_ATR_{lookback_L}_pct',
        'Breakout_Threshold_pct',
        f'SMA_{lookback_L}',
        f'Distance_to_SMA_{lookback_L}_pct',
        f'High_Low_Flag_{lookback_L}',
        f'RSI_{rsi_L}'
    ]

    result_df = df[output_columns].dropna()

    return result_df

# --- Step 1.4: Storing Stock Learnings ---
# This is also from the user's provided text.
# I'll modify it slightly to be more usable as a class or a set of functions.
# I will create a directory for learnings.

class LearningStore:
    def __init__(self, storage_path="learnings/"):
        self.storage_path = storage_path
        # Create directory if it doesn't exist
        import os
        os.makedirs(self.storage_path, exist_ok=True)
        self.lookback_days = 20
        self.alpha = 0.5
        self.e_min = 0.005

    def _calculate_reward_threshold(self, log_returns: pd.Series) -> float:
        if len(log_returns) < self.lookback_days:
            return self.e_min

        avg_daily_volatility = log_returns.abs().rolling(window=self.lookback_days).mean().iloc[-1]
        epsilon = max(self.alpha * avg_daily_volatility, self.e_min)
        return epsilon

    def _evaluate_forecast_outcome(
        self,
        daily_log_return: float,
        predicted_trend: str,
        log_returns_series: pd.Series
    ) -> Dict[str, Any]:
        if not daily_log_return or not predicted_trend:
            return {"sign_ok": False, "label_3cls": "N/A", "success": False}

        epsilon = self._calculate_reward_threshold(log_returns_series)

        if daily_log_return > epsilon:
            true_label = "uptrend"
        elif daily_log_return < -epsilon:
            true_label = "downtrend"
        else:
            true_label = "sideways"

        sign_ok = False
        if predicted_trend == true_label:
            sign_ok = True
        elif predicted_trend == "sideways" and abs(daily_log_return) <= epsilon:
            sign_ok = True

        success = sign_ok and (true_label != "sideways")

        return {
            "true_log_return": daily_log_return,
            "epsilon_threshold": epsilon,
            "true_label_3cls": true_label,
            "predicted_trend": predicted_trend,
            "sign_ok": sign_ok,
            "success": success
        }

    def store_learning(
        self,
        ticker: str,
        date: datetime,
        technical_metrics: Dict[str, float],
        agent_forecast: Dict[str, Any],
        trade_outcome: Dict[str, Any],
        historical_log_returns: pd.Series
    ) -> None:

        quant_features = {
            k: v for k, v in technical_metrics.items()
            if k in ['Simplified_ATR_20_pct', 'RSI_14', 'Distance_to_SMA_20_pct', 'Breakout_Threshold_pct']
        }

        forecast_data = {
            "P_up": agent_forecast.get('P_up', 0.0),
            "P_down": agent_forecast.get('P_down', 0.0),
            "P_side": agent_forecast.get('P_side', 0.0),
            "trend": agent_forecast.get('trend', 'sideways'),
            "reasoning": "CoT trajectory placeholder..."
        }

        evaluation_metrics = self._evaluate_forecast_outcome(
            daily_log_return=trade_outcome.get('realized_log_return_next_day', 0.0),
            predicted_trend=forecast_data['trend'],
            log_returns_series=historical_log_returns
        )

        learning_record = {
            "ticker": ticker,
            "date": date.strftime("%Y-%m-%d"),
            "quant_features_input": quant_features,
            "agent_forecast_output": forecast_data,
            "evaluation": evaluation_metrics,
            "reward_signals": {
                "good_or_bad": "good" if evaluation_metrics["success"] else "bad",
                "DA_reward": trade_outcome.get('DA_reward', 0.0)
            }
        }

        file_path = f"{self.storage_path}/{ticker}_{date.strftime('%Y%m%d')}_learning.json"
        with open(file_path, 'w') as f:
            json.dump(learning_record, f, indent=4)

        print(f"[{ticker}] Learning record saved to {file_path}")
        print(f"[{ticker}] Evaluation outcome: {'Success' if evaluation_metrics['success'] else 'Failure'} (True Label: {evaluation_metrics['true_label_3cls']})")

def run_phase1_for_ticker(ticker: str):
    """
    Runs all steps of Phase 1 for a given ticker.
    """
    print(f"\n--- Running Phase 1 for {ticker} ---")

    # Step 1.2 (mocked)
    sentiment = news_sentiment_agent(ticker)
    financials = financial_report_agent(ticker)
    print(f"[{ticker}] Mock Sentiment Score: {sentiment:.2f}")
    print(f"[{ticker}] Mock Financials: {financials}")

    # Step 1.3
    params_df = calculate_systematic_parameters(ticker)
    if params_df.empty:
        print(f"[{ticker}] Could not proceed without systematic parameters.")
        return
    print(f"\n[{ticker}] Calculated Systematic Parameters (Last 5 days):")
    print(params_df.tail())

    # Step 1.4 (simulation)
    # We'll simulate a forecast and outcome for the last day in our data.
    last_day_metrics = params_df.iloc[-1].to_dict()

    # Mock Stock-Forecasting Agent output
    mock_forecast = {
        'P_up': 0.65,
        'P_down': 0.15,
        'P_side': 0.20,
        'trend': 'uptrend',
    }

    # Mock next day outcome
    mock_outcome = {
        'realized_log_return_next_day': 0.007, # 0.7% gain
        'DA_reward': 0.015
    }

    # Run the storage function
    learning_store = LearningStore()
    learning_store.store_learning(
        ticker=ticker,
        date=params_df.index[-1],
        technical_metrics=last_day_metrics,
        agent_forecast=mock_forecast,
        trade_outcome=mock_outcome,
        historical_log_returns=params_df['Log_Returns']
    )


# --- Main Execution ---
if __name__ == "__main__":
    # Step 1.1
    candidate_tickers = ['RELIANCE.NS', 'TCS.NS', 'INVALIDTICKER']
    print("--- Step 1.1: Instrument Selection ---")
    selected_tickers = select_instruments(candidate_tickers)

    if 'RELIANCE.NS' in selected_tickers:
        run_phase1_for_ticker('RELIANCE.NS')
