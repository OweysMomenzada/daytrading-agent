import json, time, re
import streamlit as st
from agents.day_trader import DayTraderAgent
from connector.email_bot import send_email

day_trader = DayTraderAgent()

def generate_day_trading_action(ticker):
    return day_trader.generate_day_trading_action(ticker)
st.title('Day Trading Agent')

with open('ticker_db.json') as f:
    ticker_db = json.load(f)
tickers = ticker_db.keys()

def extract_json_from_string(string):
    json_pattern = re.compile(r'```json(.*?)```', re.DOTALL)
    json_match = json_pattern.search(string)
    if json_match:
        json_str = json_match.group(1).strip()
        json_ =json.loads(json_str)

        formatted_action = f"**Action:** {json_['action']} \n Certificate Type: {json_['buy_type']} \n **Amount**: {json_['amount']} \n **Rechecking process in seconds**: {json_['look_back_in_seconds']} \n **Reason of Decision:** {json_['reason_of_decision']}"
        if json_['buy_type'] == None:
            return "hold", formatted_action
        else:
            return json_['buy_type'], formatted_action
    return None, string

selected_tickers = st.multiselect('Select tickers', tickers)

if st.button('Submit'):
    for ticker in selected_tickers:
        action, context = generate_day_trading_action(ticker)
        try:
            proposal, formatted_action = extract_json_from_string(action)
            output_text = f"{formatted_action} \n\n\n Here is the data I used to support my decision: \n {context}"
            send_email(body=output_text, ticker=ticker, proposal=proposal)
        except:
            output_text = f"{action} \n\n\n Here is the data I used to support my decision: \n‚{context}"
            send_email(body=output_text, ticker=ticker, proposal="Unknown")

        time.sleep(10)
        st.write(f"Day trading action for {ticker}: {action}")