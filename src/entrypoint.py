import json
import re
import logging
from dotenv import load_dotenv
from agents.day_trader import DayTraderAgent
from connector.email_bot import send_email
from datetime import datetime
import schedule
import time
import pytz

logging.basicConfig(level=logging.INFO)
load_dotenv()
day_trader = DayTraderAgent()
MEZ = pytz.timezone('Europe/Berlin')

def extract_json_from_string(string):
    json_pattern = re.compile(r'```json(.*?)```', re.DOTALL)
    json_match = json_pattern.search(string)
    if json_match:
        json_str = json_match.group(1).strip()
        json_ = json.loads(json_str)

        formatted_action = f"**Action:** {json_['action']} \n\n Certificate Type: {json_['buy_type']} \n\n **Amount**: {json_['amount']} \n\n **Rechecking process in seconds**: {json_['look_back_in_seconds']} \n\n **Reason of Decision:** {json_['reason_of_decision']}"
        if json_['buy_type'] == None:
            return "hold", formatted_action
        else:
            return json_['buy_type'], formatted_action
    return None, string

def perform_ticker_evaluation():
    """Perform ticker evaluation and send emails."""
    logging.info("Ticker evaluation job started.")
    with open('ticker_db.json') as f:
        ticker_db = json.load(f)
    tickers = ticker_db.keys()
    
    for ticker in tickers:
        print(ticker)
        action, context = day_trader.generate_day_trading_action(ticker)
        try:
            proposal, formatted_action = extract_json_from_string(action)
            output_text = f"{formatted_action} \n\n\n Here is the data I used to support my decision: \n {context}"
            send_email(body=output_text, ticker=ticker, proposal=proposal)
        except:
            output_text = f"{action} \n\n\n Here is the data I used to support my decision: \n‚{context}"
            send_email(body=output_text, ticker=ticker, proposal="Unknown")
    logging.info("Ticker evaluation job completed.")

def is_weekday():
    today = datetime.now(MEZ).weekday()  # Monday is 0, Sunday is 6
    return 0 <= today <= 4

def schedule_tasks():
    schedule.every().monday.at("07:50").do(lambda: perform_ticker_evaluation() if is_weekday() else None)
    schedule.every().monday.at("15:10").do(lambda: perform_ticker_evaluation() if is_weekday() else None)
    schedule.every().tuesday.at("07:50").do(lambda: perform_ticker_evaluation() if is_weekday() else None)
    schedule.every().tuesday.at("15:10").do(lambda: perform_ticker_evaluation() if is_weekday() else None)
    schedule.every().wednesday.at("07:50").do(lambda: perform_ticker_evaluation() if is_weekday() else None)
    schedule.every().wednesday.at("15:10").do(lambda: perform_ticker_evaluation() if is_weekday() else None)
    schedule.every().thursday.at("07:50").do(lambda: perform_ticker_evaluation() if is_weekday() else None)
    schedule.every().thursday.at("15:10").do(lambda: perform_ticker_evaluation() if is_weekday() else None)
    schedule.every().friday.at("07:50").do(lambda: perform_ticker_evaluation() if is_weekday() else None)
    schedule.every().friday.at("15:10").do(lambda: perform_ticker_evaluation() if is_weekday() else None)

def run_scheduler():
    schedule_tasks()
    logging.info("Scheduler started.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler()