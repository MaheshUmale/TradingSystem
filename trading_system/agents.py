import os
import json
import numpy as np
import google.generativeai as genai
from typing import Dict, Any

# Configure the Gemini API key
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    GEMINI_API_KEY_CONFIGURED = True
except KeyError:
    print("Warning: GEMINI_API_KEY not found in environment variables. Agents will use mock data.")
    GEMINI_API_KEY_CONFIGURED = False

def news_sentiment_agent(ticker: str) -> float:
    """
    Placeholder for the News-Sentiment Agent.
    """
    print(f"[{ticker}] News-Sentiment Agent: Analyzing news... (mock)")
    return np.random.uniform(-1, 1)

def financial_report_agent(ticker: str) -> Dict[str, Any]:
    """
    Placeholder for the Financial-Report Agent.
    """
    print(f"[{ticker}] Financial-Report Agent: Analyzing reports... (mock)")
    return {
        "revenue_growth_qoq": np.random.uniform(-0.1, 0.2),
        "net_profit_margin": np.random.uniform(0.05, 0.25),
        "debt_to_equity": np.random.uniform(0.1, 1.5),
        "potential_risks": ["Market competition", "Regulatory changes"]
    }

def stock_forecasting_agent(ticker: str, technical_metrics: Dict[str, float]) -> Dict[str, Any]:
    """
    Analyzes stock data using a generative AI model to forecast the next day's trend.
    """
    if not GEMINI_API_KEY_CONFIGURED:
        return {
            'P_up': 0.33, 'P_down': 0.33, 'P_side': 0.34, 'trend': 'sideways',
            'reasoning': "Mock forecast due to missing Gemini API key."
        }

    model = genai.GenerativeModel('gemini-1.5-flash')

    metrics_for_json = {str(k): v for k, v in technical_metrics.items()}
    metrics_json = json.dumps(metrics_for_json, indent=2)

    prompt = f"""
You are a sophisticated Stock-Forecasting Agent. Your role is to analyze a set of technical indicators for a given stock and predict the most likely trend for the next trading day.

Based on the following technical metrics for the stock {ticker}:
{metrics_json}

Please provide your forecast in the following JSON format:
{{
  "P_up": <probability of uptrend, float between 0.0 and 1.0>,
  "P_down": <probability of downtrend, float between 0.0 and 1.0>,
  "P_side": <probability of sideways movement, float between 0.0 and 1.0>,
  "trend": "<'uptrend', 'downtrend', or 'sideways'>",
  "reasoning": "<a brief explanation of your reasoning for the forecast>"
}}

The probabilities (P_up, P_down, P_side) must sum to 1.0. The 'trend' should be the one with the highest probability.
The output must be only the JSON object, without any markdown formatting like ```json ... ```.
"""

    try:
        print(f"[{ticker}] Stock-Forecasting Agent: Querying Gemini API for forecast...")
        response = model.generate_content(prompt)

        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        forecast = json.loads(response_text)

        required_keys = ["P_up", "P_down", "P_side", "trend", "reasoning"]
        if not all(key in forecast for key in required_keys):
            raise ValueError("Forecast JSON is missing required keys.")

        print(f"[{ticker}] Stock-Forecasting Agent: Forecast received - Trend: {forecast['trend']}")
        return forecast

    except Exception as e:
        print(f"[{ticker}] Stock-Forecasting Agent: Error during generation: {e}")
        return {
            'P_up': 0.33, 'P_down': 0.33, 'P_side': 0.34, 'trend': 'sideways',
            'reasoning': f"Error during generation: {e}"
        }

def style_preference_agent() -> str:
    """
    Placeholder for the Style-Preference Agent.
    """
    print("Style-Preference Agent: Determining style... (mock)")
    return "conservative"

def trading_decision_agent(signals: Dict[str, Any], style: str) -> str:
    """
    Placeholder for the Trading-Decision Agent.
    """
    print("Trading-Decision Agent: Making final decision... (mock)")
    if signals.get('trend') == 'uptrend':
        return "Buy"
    elif signals.get('trend') == 'downtrend':
        return "Sell"
    else:
        return "Hold"
