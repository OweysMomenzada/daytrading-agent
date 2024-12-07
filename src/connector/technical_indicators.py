import yfinance as yf
import pandas_ta as ta

def fetch_stock_data(ticker, period="1mo", interval="1d"):
    """
    Fetch historical stock data for a given ticker.

    Parameters:
        ticker (str): The stock ticker symbol (e.g., "AAPL").
        period (str): The period of historical data to fetch (e.g., "1mo", "3mo", "1y").
        interval (str): The interval for the data (e.g., "1d", "1h").

    Returns:
        pandas.DataFrame: Historical stock data with datetime index.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    data.index = data.index.tz_localize(None)  # Ensure datetime index without timezone
    return data

def add_technical_indicators(data):
    """
    Add technical indicators to a stock data DataFrame.

    Parameters:
        data (pandas.DataFrame): Stock data containing columns like 'Close', 'High', 'Low', 'Volume'.

    Returns:
        pandas.DataFrame: The input DataFrame with additional columns for technical indicators:
            - RSI: Relative Strength Index
            - SMA_20: 20-period Simple Moving Average
            - EMA_20: 20-period Exponential Moving Average
            - Bollinger Bands (BBL_20_2.0, BBM_20_2.0, BBU_20_2.0)
            - VWAP: Volume-Weighted Average Price
            - ATR: Average True Range
    """
    # Relative Strength Index (RSI)
    data['RSI'] = ta.rsi(data['Close'], length=14)
    # Simple Moving Average (SMA)
    data['SMA_20'] = ta.sma(data['Close'], length=20)
    # Exponential Moving Average (EMA)
    data['EMA_20'] = ta.ema(data['Close'], length=20)
    # Bollinger Bands
    bb = ta.bbands(data['Close'], length=20, std=2)
    data = data.join(bb)
    # Volume-Weighted Average Price (VWAP)
    data['VWAP'] = ta.vwap(data['High'], data['Low'], data['Close'], data['Volume'])
    # Average True Range (ATR)
    data['ATR'] = ta.atr(data['High'], data['Low'], data['Close'], length=14)
    
    return data

# Function to format data into the desired text-based format
def format_as_text(data):
    """
    Format stock data with technical indicators into a structured text format.

    Parameters:
        data (pandas.DataFrame): Stock data with columns for indicators like 'Close', 'RSI', 'SMA_20', etc.

    Returns:
        str: A formatted string containing stock data and technical indicators for each row in the DataFrame.
            Example:
                Date: YYYY-MM-DD
                Close Price: $XXX.XX
                RSI: XX.X (Status)
                SMA (20): $XXX.XX
                EMA (20): $XXX.XX
                VWAP: $XXX.XX
                ATR: X.X (Status)
    """
    output = []
    for date, row in data.iterrows():
        rsi_status = "Overbought" if row['RSI'] > 70 else "Oversold" if row['RSI'] < 30 else "Neutral"
        atr_status = "High Volatility" if row['ATR'] > 2 else "Low Volatility"
        formatted = f"""
Date: {date.date()}
Close Price: ${row['Close']:.2f}
RSI: {row['RSI']:.1f} ({rsi_status})
SMA (20): ${row['SMA_20']:.2f}
EMA (20): ${row['EMA_20']:.2f}
VWAP: ${row['VWAP']:.2f}
ATR: {row['ATR']:.1f} ({atr_status})
"""
        output.append(formatted.strip())
    return "\n\n".join(output)


def fetch_technical_indicators_of_ticker(ticker):
    """
    Main function to fetch stock data, compute technical indicators, and prepare the output.

    Returns:
        str: Stock data with added technical indicators.
    """
    data = fetch_stock_data(ticker, period="1mo", interval="1h")
    data_with_indicators = add_technical_indicators(data)
    data_with_indicators_formatted = format_as_text(data_with_indicators.dropna())
    return data_with_indicators_formatted


if __name__ == "__main__":
    data_with_indicators_formatted = fetch_technical_indicators_of_ticker(ticker="AAPL")
    print(data_with_indicators_formatted)