import os
import json
import numpy as np
import google.generativeai as genai
from typing import Dict, Any
import time

import curl_request
# No longer configure API key at the module level

def news_sentiment_agent(ticker: str) -> float:
    return curl_request.make_curl_requestForSentimentAnalysis(ticker)

def financial_report_agent(ticker: str) -> Dict[str, Any]:
    """
    Placeholder for the Financial-Report Agent.
    """
    return curl_request.make_curl_requestForFinancialReportAnalysis(ticker)

def stock_forecasting_agent(ticker: str, technical_metrics: Dict[str, float], date_str: str) -> Dict[str, Any]:
    """
    Analyzes stock data using a generative AI model to forecast the next day's trend.
    Includes file-based caching to avoid redundant API calls.
    """
    # Caching setup
    cache_dir = "forecast_cache"
    os.makedirs(cache_dir, exist_ok=True)
    analysis_cache_file = os.path.join(cache_dir, f"{ticker}_{date_str}_analysis.json")
    matrix_cache_file = os.path.join(cache_dir, f"{ticker}_{date_str}_matrix.json")

    # Check if forecast is in cache
    if os.path.exists(analysis_cache_file):
        with open(analysis_cache_file, 'r') as f:
            return json.load(f)

#     # Configure the Gemini API key, checking each time
#     try:
#         genai.configure(api_key=os.environ["GEMINI_API_KEY"])
#         gemini_api_key_configured = True
#     except KeyError:
#         gemini_api_key_configured = False


#     if not gemini_api_key_configured:
#         # Improved mock agent for testing: returns a random trend
#         trends = ['uptrend', 'downtrend', 'sideways']
#         mock_trend = np.random.choice(trends)
#         forecast = {
#             'P_up': 0.8 if mock_trend == 'uptrend' else 0.1,
#             'P_down': 0.8 if mock_trend == 'downtrend' else 0.1,
#             'P_side': 0.8 if mock_trend == 'sideways' else 0.1,
#             'trend': mock_trend,
#             'reasoning': f"Mock forecast ({mock_trend}) due to missing Gemini API key."
#         }
#         # Save mock forecast to cache for consistency in testing
#         with open(cache_file, 'w') as f:
#             json.dump(forecast, f)
#         return forecast

#     model = genai.GenerativeModel('gemini-1.5-flash')

    metrics_for_json = {str(k): v for k, v in technical_metrics.items()}
    # print(f"[{ticker}] Technical Metrics for JSON: {metrics_for_json}")
    
    
    metrics_json = json.dumps(metrics_for_json, indent=2)
    print(f"[{ticker}] Technical Metrics JSON:\n{metrics_json}")
    
    with open(matrix_cache_file, 'w') as f:
        json.dump(metrics_json, f)
        print(f"[{ticker}] Technical Metrics JSON saved to cache file {matrix_cache_file}.")

#     prompt = f"""
# You are a sophisticated Stock-Forecasting Agent. Your role is to analyze a set of technical indicators for a given stock and predict the most likely trend for the next trading day.

# Based on the following technical metrics for the stock {ticker}:
# {metrics_json}

# Please provide your forecast in the following JSON format:
# {{
#   "P_up": <probability of uptrend, float between 0.0 and 1.0>,
#   "P_down": <probability of downtrend, float between 0.0 and 1.0>,
#   "P_side": <probability of sideways movement, float between 0.0 and 1.0>,
#   "trend": "<'uptrend', 'downtrend', or 'sideways'>",
#   "reasoning": "<a brief explanation of your reasoning for the forecast>"
# }}

# The probabilities (P_up, P_down, P_side) must sum to 1.0. The 'trend' should be the one with the highest probability.
# The output must be only the JSON object, without any markdown formatting like ```json ... ```.
# """

    try:
#         response = model.generate_content(prompt)
#         response_text = response.text.strip()

#         # Clean the response to ensure it's valid JSON
#         if response_text.startswith("```json"):
#             response_text = response_text[7:-3].strip()

#         forecast = json.loads(response_text)

#         required_keys = ["P_up", "P_down", "P_side", "trend", "reasoning"]
#         if not all(key in forecast for key in required_keys):
#             raise ValueError("Forecast JSON is missing required keys.")

#         # Save the successful forecast to cache
#         with open(cache_file, 'w') as f:
#             json.dump(forecast, f, indent=4)
#         return forecast
        time.sleep(7)
        forecast = curl_request.make_curl_request(ticker, metrics_json)
        print(f"[{ticker}] Stock-Forecasting Agent: Forecast received: {forecast}")
        # Save the successful forecast to cache
        with open(analysis_cache_file, 'w') as f:
            json.dump(forecast, f, indent=4)
        return forecast

    except Exception as e:
        print(f"[{ticker}] Stock-Forecasting Agent: Error during generation: {e}")
        return {
            'P_up': 0.33, 'P_down': 0.33, 'P_side': 0.34, 'trend': 'sideways',
            'reasoning': f"Error during generation: {e}"
        }
    #finally:
        # Add a delay to respect the API rate limit (15 requests per minute for free tier)
        


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
