import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta

from trading_system.main import calculate_systematic_parameters, run_system_for_ticker
from trading_system.agents import stock_forecasting_agent
from trading_system.execution import run_phase3_execution
from trading_system.risk_management import run_phase4_risk_management
from trading_system.nifty50 import NIFTY_50_SYMBOLS

from tqdm import tqdm

def run_trading_backtest(ticker: str, start_date: str, end_date: str, initial_capital: float = 100000.0):
    """
    Runs a comprehensive trading backtest for a single ticker, simulating trades and tracking P&L.
    """
    print(f"\n--- Running Trading Backtest for {ticker} ---")

    # 1. Data Fetching
    # We need extra data before the start date for initial calculations
    extended_start_date = (datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=60)).strftime("%Y-%m-%d")
    full_data = yf.download(ticker, start=extended_start_date, end=end_date, progress=False, auto_adjust=True)
    if full_data.empty:
        print(f"Could not download data for {ticker}.")
        return None

    # Ensure columns are MultiIndex for consistency with other modules
    if not isinstance(full_data.columns, pd.MultiIndex):
        full_data.columns = pd.MultiIndex.from_product([full_data.columns, [ticker]])

    # 2. Initialization
    capital = initial_capital
    position = 0
    open_trade = None
    trades = []
    equity_curve = []
    peak_equity = initial_capital
    max_drawdown = 0

    # 3. Main Backtesting Loop
    # We iterate from the requested start_date, using the earlier data for indicators
    backtest_data = full_data[full_data.index >= pd.to_datetime(start_date)]

    for i in tqdm(range(1, len(backtest_data)), desc=f"Backtesting {ticker}"):
        # Define current and previous day's data for analysis
        current_date = backtest_data.index[i]

        # The historical slice should include all data up to the day *before* the current day
        # to prevent lookahead bias.
        historical_slice = full_data[full_data.index < current_date]

        if len(historical_slice) < 50: # Ensure enough data for indicators
            equity_curve.append({'date': current_date, 'equity': capital})
            continue

        # --- Core Trading Logic ---

        # Get prices for the current day
        open_price = backtest_data.iloc[i][('Open', ticker)]
        low_price = backtest_data.iloc[i][('Low', ticker)]
        high_price = backtest_data.iloc[i][('High', ticker)]
        close_price = backtest_data.iloc[i][('Close', ticker)]

        # a. Check for exits on the open position
        if position != 0:
            trade_closed = False
            exit_price = 0

            # Check for Stop Loss
            if (position > 0 and low_price <= open_trade['stop_loss']) or \
               (position < 0 and high_price >= open_trade['stop_loss']):
                exit_price = open_trade['stop_loss']
                trade_closed = True
                exit_reason = "Stop-Loss"

            # Check for Take Profit
            elif (position > 0 and high_price >= open_trade['take_profit']) or \
                 (position < 0 and low_price <= open_trade['take_profit']):
                exit_price = open_trade['take_profit']
                trade_closed = True
                exit_reason = "Take-Profit"

            if trade_closed:
                # Close position and record trade
                capital += position * exit_price

                trade = open_trade
                trade.update({
                    "exit_date": current_date.strftime("%Y-%m-%d"),
                    "exit_price": exit_price,
                    "pnl": position * (exit_price - trade['entry_price']),
                    "exit_reason": exit_reason
                })
                trades.append(trade)

                position = 0
                open_trade = None

        # b. Get new trade signal if no position is open
        if position == 0:
            # Get the signal, passing the date for caching purposes
            date_str = current_date.strftime("%Y-%m-%d")
            signal = run_system_for_ticker(ticker, data=historical_slice, date_str=date_str)

            if signal and signal.get('target_position') != 0 and signal.get('stop_loss') is not None and signal.get('take_profit') is not None:
                target_pos = signal['target_position']

                # Simple execution: trade at open price of the current day
                entry_price = open_price
                position = target_pos # Assume full position is taken

                # Update capital
                capital -= position * entry_price

                # Store the open trade
                open_trade = {
                    "entry_date": current_date.strftime("%Y-%m-%d"),
                    "ticker": ticker,
                    "direction": "long" if position > 0 else "short",
                    "entry_price": entry_price,
                    "size": position,
                    "stop_loss": signal['stop_loss'],
                    "take_profit": signal['take_profit']
                }

        # c. Update daily equity and drawdown
        current_equity = capital
        if position != 0:
            current_equity += position * close_price

        equity_curve.append({'date': current_date, 'equity': current_equity})

        # Update peak equity and max drawdown
        if current_equity > peak_equity:
            peak_equity = current_equity

        drawdown = (peak_equity - current_equity) / peak_equity
        if drawdown > max_drawdown:
            max_drawdown = drawdown


    # 4. Performance Calculation
    report = {
        "ticker": ticker,
        "initial_capital": initial_capital,
        "final_equity": current_equity, # Use the last calculated equity
        "max_drawdown": max_drawdown,
        "trades": trades,
        "equity_curve": equity_curve
    }

    return report


def generate_full_report(results: dict):
    """
    Generates and prints a comprehensive report from the backtest results.
    """
    print("\n--- Backtest Performance Report ---")
    if not results or not results.get('trades'):
        print("No trades were made during the backtest.")
        print(f"Ticker: {results.get('ticker', 'N/A')}")
        print(f"Initial Capital: ${results.get('initial_capital', 0):,.2f}")
        print(f"Final Equity: ${results.get('final_equity', 0):,.2f}")
        return

    trades = results['trades']
    initial_capital = results['initial_capital']
    final_equity = results['final_equity']
    max_drawdown = results['max_drawdown']

    # Key Metrics
    total_trades = len(trades)
    winning_trades = [t for t in trades if t['pnl'] > 0]
    losing_trades = [t for t in trades if t['pnl'] <= 0]

    win_rate = (len(winning_trades) / total_trades) * 100 if total_trades > 0 else 0
    total_pnl = final_equity - initial_capital

    avg_win_pnl = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss_pnl = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0

    # Sharpe Ratio Calculation
    equity_df = pd.DataFrame(results['equity_curve'])
    equity_df['date'] = pd.to_datetime(equity_df['date'])
    equity_df.set_index('date', inplace=True)
    equity_df['daily_return'] = equity_df['equity'].pct_change().fillna(0)

    if equity_df['daily_return'].std() > 0:
        sharpe_ratio = (equity_df['daily_return'].mean() / equity_df['daily_return'].std()) * np.sqrt(252)
    else:
        sharpe_ratio = 0.0

    # Print Report
    print(f"Stock:                  {results['ticker']}")
    print("--- P&L ---")
    print(f"Starting Capital:       ${initial_capital:,.2f}")
    print(f"Ending Equity:          ${final_equity:,.2f}")
    print(f"Total P&L:              ${total_pnl:,.2f}")
    print(f"Max Drawdown:           {max_drawdown:.2%}")
    print("\n--- Trades ---")
    print(f"Total Trades:           {total_trades}")
    print(f"Win Rate:               {win_rate:.2f}%")
    print(f"Avg. Win P&L:           ${avg_win_pnl:,.2f}")
    print(f"Avg. Loss P&L:          ${avg_loss_pnl:,.2f}")
    print("\n--- Risk ---")
    print(f"Annualized Sharpe Ratio:{sharpe_ratio:.2f}")


def generate_summary_report(all_results: list):
    """
    Generates a summary report from a list of backtest results.
    """
    if not all_results:
        print("No results to summarize.")
        return

    summary_data = []
    for results in all_results:
        trades = results['trades']
        total_trades = len(trades)
        winning_trades = [t for t in trades if t['pnl'] > 0]
        win_rate = (len(winning_trades) / total_trades) * 100 if total_trades > 0 else 0
        total_pnl = results['final_equity'] - results['initial_capital']

        equity_df = pd.DataFrame(results['equity_curve'])
        if not equity_df.empty:
            equity_df['date'] = pd.to_datetime(equity_df['date'])
            equity_df.set_index('date', inplace=True)
            equity_df['daily_return'] = equity_df['equity'].pct_change().fillna(0)
            sharpe_ratio = (equity_df['daily_return'].mean() / equity_df['daily_return'].std()) * np.sqrt(252) if equity_df['daily_return'].std() > 0 else 0.0
        else:
            sharpe_ratio = 0.0

        summary_data.append({
            "Ticker": results['ticker'],
            "Total P&L": total_pnl,
            "Win Rate (%)": win_rate,
            "Max Drawdown (%)": results['max_drawdown'] * 100,
            "Sharpe Ratio": sharpe_ratio,
            "Total Trades": total_trades,
        })

    summary_df = pd.DataFrame(summary_data)
    summary_df.sort_values(by="Sharpe Ratio", ascending=False, inplace=True)
    summary_df.set_index("Ticker", inplace=True)

    print("\n\n--- Full Backtest Summary Report ---")
    print(summary_df.to_string(float_format="%.2f"))

    # Save summary report
    output_dir = "backtest_results"
    os.makedirs(output_dir, exist_ok=True)
    summary_df.to_csv(f"{output_dir}/summary_report.csv")
    print(f"\nSummary report saved to {output_dir}/summary_report.csv")


if __name__ == "__main__":
    # Ensure the API key is set, otherwise it will use mock data
    if "GEMINI_API_KEY" in os.environ:
        print("GEMINI_API_KEY found. Running with live agent.")
    else:
        print("Warning: GEMINI_API_KEY not found. Running with mock agent.")

    # Create directory for detailed logs
    output_dir = "backtest_results"
    os.makedirs(output_dir, exist_ok=True)

    all_results = []

    # Use a smaller list for testing the orchestration
    # symbols_to_run = NIFTY_50_SYMBOLS[:5]
    symbols_to_run = NIFTY_50_SYMBOLS

    START_DATE = "2023-01-01"
    END_DATE = "2023-12-31"

    for ticker in symbols_to_run:
        results = run_trading_backtest(ticker, START_DATE, END_DATE)
        if results:
            all_results.append(results)

            # Save detailed trade log for the ticker
            if results['trades']:
                trades_df = pd.DataFrame(results['trades'])
                trades_df.to_csv(f"{output_dir}/trade_log_{ticker}.csv", index=False)

    if all_results:
        generate_summary_report(all_results)
