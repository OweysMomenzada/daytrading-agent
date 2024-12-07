from datetime import datetime
import json

def get_user_data():
    """
    Get user data from the database.

    Returns:
        dict: A dictionary containing user information.
    """
    time = datetime.now()

    with open('user_information.json') as f:
        user_data = json.load(f)

    output_text = f"""
User Location: {user_data['user_location']}
Available Budget: {user_data['available_budget']} {user_data['trading_currency']}
Trading Tickers: {', '.join(user_data['trading_tickers'])}
Trading Market Location: {user_data['trading_market_location']}
Risk Tolerance: {user_data['risk_tolerance_description']}
Current Time of the User: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}
    """
    return output_text

if __name__ == "__main__":
    print(get_user_data())