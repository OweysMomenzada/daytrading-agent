from datetime import datetime, time, timedelta
from pytz import timezone
import json

def check_market_status():
    """
    Check the status of the US and German stock markets.

    Returns:
        tuple: A tuple containing the status of the US market and the overall market status.
               ("open" or "closed") and the time until they open in minutes if they are closed.
    """
    # Set MEZ timezone
    mez_tz = timezone('Europe/Berlin')
    current_time = datetime.now(mez_tz)
    
    us_market_opening_time = time(hour=15, minute=30)  # US market opens at 15:30 MEZ
    us_market_closing_time = time(hour=22, minute=0)   # US market closes at 22:00 MEZ
    german_market_opening_time = time(hour=9, minute=0)  # German market opens at 9:00 MEZ

    # Check if US market is open while considering day (Saturday and Sunday closed)
    if current_time.weekday() in [5, 6] or current_time.time() < us_market_opening_time or current_time.time() > us_market_closing_time:
        time_until_us_open = 0
        if current_time.time() < us_market_opening_time:
            time_until_us_open = (datetime.combine(current_time.date(), us_market_opening_time, mez_tz) - current_time).total_seconds() // 60
        else:
            time_until_us_open = ((datetime.combine(current_time.date() + timedelta(days=1), us_market_opening_time, mez_tz) - current_time).total_seconds() // 60)
        is_us_market_open = f"opens in {int(time_until_us_open)} minutes"
    else:
        is_us_market_open = "open (now)"

    # Check if user can trade in the market (either German or US)
    if current_time.weekday() in [5, 6] or current_time.time() < german_market_opening_time or current_time.time() > us_market_closing_time:
        time_until_market_open = 0
        if current_time.time() < german_market_opening_time:
            time_until_market_open = (datetime.combine(current_time.date(), german_market_opening_time, mez_tz) - current_time).total_seconds() // 60
        else:
            time_until_market_open = ((datetime.combine(current_time.date() + timedelta(days=1), german_market_opening_time, mez_tz) - current_time).total_seconds() // 60)
        is_market_open = f"closed (opens in {int(time_until_market_open)} minutes)"
    else:
        is_market_open = "open (USER CAN TRADE NOW!)"

    return is_us_market_open, is_market_open

def get_user_data():
    """
    Get user data from the database.

    Returns:
        dict: A dictionary containing user information.
    """
    # get market status
    us_market_status, market_status = check_market_status()
    with open('user_information.json') as f:
        user_data = json.load(f)

    mez_tz = timezone('Europe/Berlin')
    current_time_mez = datetime.now(mez_tz).strftime('%Y-%m-%d %H:%M:%S %Z')

    output_text = f"""
User Location: {user_data['user_location']}
Available Budget: {user_data['available_budget']} {user_data['trading_currency']}
Trading Market Location: {user_data['trading_market_location']}
Risk Tolerance: {user_data['risk_tolerance_description']}
Current Time of the User (MEZ): {current_time_mez}
US Market Status: {us_market_status}
Overall Market Status (User can actively trade): {market_status}
    """
    return output_text

if __name__ == "__main__":
    print(get_user_data())