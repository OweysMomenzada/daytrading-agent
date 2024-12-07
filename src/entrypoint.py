import time
from agents.day_trader import DayTraderAgent

day_trader = DayTraderAgent()

def generate_day_trading_action(ticker):
    return day_trader.generate_day_trading_action(ticker)

if __name__ == '__main__':
    start_time = time.time()
    print(generate_day_trading_action('AAPL'))
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds.")