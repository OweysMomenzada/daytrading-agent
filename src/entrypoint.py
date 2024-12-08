import json
import time
import re
import os
import streamlit as st
from dotenv import load_dotenv
from agents.day_trader import DayTraderAgent
from connector.email_bot import send_email

# Load environment variables
load_dotenv()

admin = os.getenv("ADMIN_NAME")
password = os.getenv("ADMIN_PW")

day_trader = DayTraderAgent()
VALID_CREDENTIALS = {
    admin: password,
}

def authenticate(username, password):
    """Simple authentication function."""
    return VALID_CREDENTIALS.get(username) == password

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "login_attempted" not in st.session_state:
    st.session_state.login_attempted = False

def handle_login():
    """Handle the login process."""
    if authenticate(st.session_state.username, st.session_state.password):
        st.session_state.authenticated = True
        st.success("Successfully logged in!")
        time.sleep(1)
        st.experimental_rerun()
    else:
        st.error("Invalid username or password.")
        st.session_state.login_attempted = True

if not st.session_state.authenticated:
    # Show login screen
    st.title("Login")
    st.text_input("Username", key="username", on_change=handle_login)
    st.text_input("Password", type="password", key="password", on_change=handle_login)
    
    if st.button("Login"):
        handle_login()

else:
    # Main app content
    st.title("Day Trading Agent")

    with open('ticker_db.json') as f:
        ticker_db = json.load(f)
    tickers = ticker_db.keys()

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

    selected_tickers = st.multiselect('Select tickers', tickers)

    if st.button('Submit'):
        for ticker in selected_tickers:
            action, context = day_trader.generate_day_trading_action(ticker)
            try:
                proposal, formatted_action = extract_json_from_string(action)
                output_text = f"{formatted_action} \n\n\n Here is the data I used to support my decision: \n {context}"
                send_email(body=output_text, ticker=ticker, proposal=proposal)
            except:
                output_text = f"{action} \n\n\n Here is the data I used to support my decision: \n‚{context}"
                send_email(body=output_text, ticker=ticker, proposal="Unknown")

            time.sleep(10)
            st.write(f"Day trading action for {ticker}: {action}")

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.login_attempted = False
        st.experimental_rerun()