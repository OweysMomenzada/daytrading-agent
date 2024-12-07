import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple

def get_stock_data(ticker: str) -> Tuple[str, str]:
    """
    Fetch both 3-day historical and current day intraday stock data for given ticker.
    
    Args:
        ticker (str): Stock ticker symbol (e.g. 'AAPL')
    
    Returns:
        Tuple[str, str]: (3-day historical data, current day intraday data) in markdown format
    """
    try:
        # Calculate dates
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=3)

        # Get historical data
        stock_data = yf.download(ticker, start=start_date, end=end_date, interval="1d")
        stock_data = stock_data.to_markdown(index=False)

        # Fetch detailed data for current day
        current_day_data = yf.download(ticker, period="1d", interval="2m")
        current_day_data = current_day_data.to_markdown(index=False)

        return stock_data, current_day_data
    
    except Exception as e:
        return f"Error fetching data: {str(e)}", ""

if __name__ == "__main__":
    historical, intraday = get_stock_data("AAPL")
    print("Last 3 Days (Daily Data):")
    print(historical)
    print("\nCurrent Day (Intraday Data):")
    print(intraday)