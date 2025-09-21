# AI-Powered Systematic Trading System

## Overview

This project is a sophisticated, multi-phase systematic trading system designed to identify and evaluate trading opportunities in the stock market. It integrates the objective, risk-focused framework defined by Robert Carver with an advanced, AI-powered analysis and forecasting system inspired by the "TradingGroup" multi-agent system concept.

The system is capable of:
- Analyzing individual stocks based on a variety of technical indicators.
- Using a generative AI model (Google's Gemini) to forecast future price trends.
- Scanning a list of stocks to identify the most promising trading opportunities.
- Backtesting the trading strategy on historical data to evaluate its performance.

## Core Features

- **4-Phase Analysis Pipeline:** The system follows a structured, four-phase process for each stock:
    1.  **Foundational Intelligence:** Calculates a comprehensive set of systematic parameters and technical indicators.
    2.  **Forecasting:** Uses an AI agent to analyze the parameters and forecast the next day's trend.
    3.  **Execution & Sizing:** Translates the forecast into a risk-adjusted position size based on volatility targeting.
    4.  **Risk Management:** Calculates dynamic stop-loss and take-profit levels for the potential trade.
- **AI-Powered Forecasting:** The `Stock-Forecasting Agent` leverages the Gemini generative AI model to provide a trend prediction (`uptrend`, `downtrend`, `sideways`), a probability distribution, and a detailed text-based reasoning for its forecast.
- **Stock Scanner:** The scanner can iterate through a list of stocks, run the full analysis pipeline on each, and produce a ranked report of the top long and short trading opportunities.
- **Historical Backtester:** The backtester can simulate the trading strategy on historical data for a given stock. It generates a performance report, including the AI agent's forecast accuracy, and saves detailed, labeled records for each day of the backtest. This "high-quality post-training data" is essential for future strategy improvements and agent self-reflection.

## Project Structure

The project is organized into a Python package `trading_system` with a modular structure:

-   `trading_system/`: The main Python package.
    -   `scanner.py`: **Main entry point for scanning multiple stocks.**
    -   `backtester.py`: **Main entry point for running a historical backtest.**
    -   `main.py`: Contains the core orchestration logic for running the 4-phase analysis on a *single* stock.
    -   `agents.py`: Houses all agents, including the AI-powered `stock_forecasting_agent` and placeholders for other agents.
    -   `execution.py`: Contains the logic for Phase 3 (Position Sizing).
    -   `risk_management.py`: Contains the logic for Phase 4 (Active Trade Management).
-   `learnings/`: Directory where the live scanner saves its analysis output.
-   `backtest_learnings/`: Directory where the backtester saves its detailed, labeled output.
-   `.gitignore`: Configured to exclude generated files and caches.

## How to Run

### 1. Setup

**Dependencies:**
Install all required Python libraries. It is recommended to use a virtual environment.
```bash
pip install yfinance pandas numpy TA-Lib google-generativeai tqdm
```

**API Key:**
The system uses the Google Gemini API for its forecasting agent. You must set your API key as an environment variable.
```bash
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

### 2. Running the Scanner

To scan a list of stocks and get a report of current trading opportunities, run the `scanner.py` module.

```bash
python3 -m trading_system.scanner
```
The list of stocks to be scanned is currently hardcoded in `trading_system/scanner.py`.

### 3. Running the Backtester

To run a historical backtest for a single stock and evaluate the strategy's performance, run the `backtester.py` module.

```bash
python3 -m trading_system.backtester
```
The ticker and date range for the backtest are currently hardcoded in `trading_system/backtester.py`.
