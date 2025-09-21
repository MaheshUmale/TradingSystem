import pandas as pd
from trading_system.main import run_system_for_ticker

# For development, we'll use a small, hardcoded list of F&O stocks.
F_AND_O_STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'SBIN.NS', 'BAJFINANCE.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS'
]

def run_scanner(tickers: list):
    """
    Runs the trading system analysis for a list of tickers and returns the results.
    """
    all_results = []
    print(f"--- Starting Scanner for {len(tickers)} stocks ---")
    for ticker in tickers:
        try:
            print(f"\n...Scanning {ticker}...")
            result = run_system_for_ticker(ticker)
            if result:
                all_results.append(result)
        except Exception as e:
            print(f"!!! Error processing {ticker}: {e} !!!")

    print(f"\n--- Scanner finished. Analyzed {len(all_results)} stocks successfully. ---")
    return all_results

def generate_report(results: list):
    """
    Filters, ranks, and prints a report of the top trading opportunities.
    """
    if not results:
        print("No successful analyses to report.")
        return

    df = pd.DataFrame(results)

    # Filter for actionable trades (where target_position is not 0)
    trade_candidates = df[df['target_position'] != 0].copy()

    # Separate into long and short candidates
    long_candidates = trade_candidates[trade_candidates['target_position'] > 0].sort_values(by='P_up', ascending=False)
    short_candidates = trade_candidates[trade_candidates['target_position'] < 0].sort_values(by='P_down', ascending=False)

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 80)

    print("\n--- Trading Opportunities Report ---")

    print("\n--- Top Long Candidates ---")
    if not long_candidates.empty:
        cols_to_show = ['ticker', 'instrument_price', 'target_position', 'stop_loss', 'take_profit', 'P_up', 'reasoning']
        print(long_candidates[cols_to_show].to_string())
    else:
        print("No strong long candidates found.")

    print("\n--- Top Short Candidates ---")
    if not short_candidates.empty:
        cols_to_show = ['ticker', 'instrument_price', 'target_position', 'stop_loss', 'take_profit', 'P_down', 'reasoning']
        print(short_candidates[cols_to_show].to_string())
    else:
        print("No strong short candidates found.")

if __name__ == "__main__":
    # In a real scenario, you might not want to run the full list every time.
    # For this test, we run the scanner on the dev list.
    results = run_scanner(F_AND_O_STOCKS)
    generate_report(results)
