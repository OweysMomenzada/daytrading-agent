import os
import json

from openai import OpenAI
from dotenv import load_dotenv

from agents.financial_analyst import FinancialAnalystAgent
from agents.utils.helpers import retry_request
from connector.user_information import get_user_data
from connector.stock_data import get_stock_data

load_dotenv()

class DayTraderAgent:
    def __init__(self):
        """Initializing OpenAI Client for the Day Trader Agent.
        """
        api_key = os.getenv('OPENAI_KEY')
        self.client = OpenAI(api_key=api_key)
        
        with open('ticker_db.json') as f:
            self.TICKER_OVERVIEW_DB = json.load(f)
        self.fin_agent = FinancialAnalystAgent()

    def _get_user_stock_position(self, ticker):
        """ Get the user's current stock position.

        Args:
            ticker (str): The stock ticker to evaluate.

        Returns:
            dict: The user's current stock position.
        """
        try:
            with open(f'pending_positions/{ticker}.json') as f:
                user_stock_position_input_text = ""
                user_stock_position = json.load(f)
                # the amount of the stock the user has in the stock
                if user_stock_position["amount"] == "0":
                    user_stock_position_input_text = "User is invested in the stock."
                else:
                    user_stock_position_input_text = "User is invested in the stock."
                    # user_stock_position_input_text += "Current Position Amount: " + user_stock_position["amount"] + "\n"
                    # user_stock_position_input_text += "Derivative type: " + user_stock_position["buy_type"] + "\n"
        except FileNotFoundError:
            user_stock_position = {
                "amount": "0",
                "buy_type": "none"
            }
            with open(f'pending_positions/{ticker}.json', 'w') as f:
                json.dump(user_stock_position, f)
            user_stock_position_input_text = "User is invested in the stock."
        
        return user_stock_position_input_text

    def generate_day_trading_action(self, ticker):
        """ Generate a day trading action for a given stock ticker.

        Args:
            ticker (str): The stock ticker to evaluate.

        Returns:    
            str: The generated financial evaluation.
        """
        company_name = self.TICKER_OVERVIEW_DB[ticker]
        # all financial agent evaluations
        bing_eval = self.fin_agent.generate_financial_evaluation_on_bing_search_engine(ticker=ticker)
        general_news_eval = self.fin_agent.generate_financial_evaluation_on_general_news()
        stock_news_eval = self.fin_agent.generate_financial_evaluation_on_stock_news(ticker=ticker)
        ### NOTE this (Sentiment Analysis on public opinion) confused the model. It relied too much on it.
        #sentiment_analysis_eval = self.fin_agent.generate_sentiment_analysis(ticker=ticker)
        techindicator_analysis_eval = self.fin_agent.generate_technical_indicator_analysis(ticker=ticker)

        # get relevant user data and stock data
        user_data = get_user_data()
        three_days_stock_data, current_stock_data = get_stock_data(ticker)
        user_stock_position = self._get_user_stock_position(ticker)

        context = f"""
General News About the Company: {bing_eval}
_____

General Financial Market Condition: {general_news_eval}
_____

Recent News About the Stock: {stock_news_eval}
_____

Technical Indicators: {techindicator_analysis_eval}
_____

User Data: {user_data}
_____

Three-Day Stock Data: {three_days_stock_data}
_____

Minute-by-Minute Stock Data: {current_stock_data}
_____

Current purchased derivative on {company_name} ({ticker}): {user_stock_position}
"""

        instruction = f"""
You are a **Day Trader Agent** tasked with deciding whether to take a **long** position on {company_name} ({ticker}) stock or to hold the current position. You must respond strictly in JSON format following the schema below. Your decisions must be based on the given inputs and adhere to the specified guidelines and day trading principles.

---

### **JSON Response Format**:
```json
{{
  "action": "buy",  // Options: "buy", "hold", "sell".
  "amount": "1000", // Amount in EUR to buy/sell. Use null if "hold" actions was chosen.
  "look_back_in_seconds": 1000, 
  "reason_of_decision": "Detailed explanation of why this action was chosen based on the input data and analysis and maybe the amount of seconds which was chosen."
}}
```

---

### **Examples**:

#### **Example 1: Buying with a Long Position**
```json
{{
  "action": "buy",
  "amount": "1000",
  "look_back_in_seconds": 600,
  "reason_of_decision": "The stock shows positive momentum based on recent technical indicators, increasing sentiment, and bullish market conditions."
}}
```

#### **Example 2: Holding**
```json
{{
  "action": "hold",
  "amount": null,
  "look_back_in_seconds": 1800,
  "reason_of_decision": "The market data and sentiment are inconclusive, and no strong signals to act are evident."
}}
```

#### **Example 3: Selling**
```json
{{
  "action": "sell",
  "amount": "500",
  "look_back_in_seconds": 1200,
  "reason_of_decision": "Technical indicators suggest a reversal, and risk mitigation is recommended based on declining market sentiment."
}}
```

---

### **Inputs**:
The Day Trader Agent must consider the following inputs for decision-making:

1. **General News About the Company**: Evaluation of the company’s news by a Financial Agent LLM. (Note: This information is not always accurate, recent, or relevant.)
2. **General Financial Market Condition**: Evaluation of recent global and market-specific financial conditions by a Financial Agent LLM.
3. **Recent News About the Stock**: Insights from the Financial Agent LLM regarding {company_name} ({ticker}) stock-specific news.
4. **Technical Indicators**: Analysis of recent technical indicators (e.g., RSI, moving averages, MACD) provided by the Financial Agent LLM.
5. **User Data**: Includes:
   - User’s available budget and maximum risk tolerance.
   - Geographic location and time zone to be considered when buying and considering opening hours of stock exchanges.
6. **Three-Day Stock Data**: A rough overview of the stock’s performance over the past three days.
7. **Minute-by-Minute Stock Data**: Current stock data updated in one-minute intervals.
8. **Current purchased derivative**: The current position of the user in the {company_name} ({ticker}) stock (if any).

---

### **Decision Guidelines**:
- The agent must analyze and integrate all inputs objectively while acknowledging potential inaccuracies in company-related news.
- Decisions must align with market and technical indicators, balancing a slight risk-taking approach with the goal of optimal results.
- You may also choose "Hold" even if the user has no current position or is invested in the stock. This is appropriate if market conditions are unclear, trends are inconclusive, or waiting, if you are not comfortable to make a decision between `sell` or `buy`.
- The **look_back_in_seconds** determines how frequently the agent reevaluates and adjusts its position:
  - Minimum: **2 minutes** (120 seconds).
  - Maximum: **1 day** (86,400 seconds).
- You should aim to **maximize winnings** or **minimize losses** based on the current market conditions.
- When markets are **closed**, decisions should account for the next trading session. In such cases:
  - Set `look_back_in_seconds` to the time remaining until the next market opening.
  - Prepare a position based on pre-market indicators or known events likely to influence the stock's behavior at the open.
- You must follow the Day Trading Principles outlined below to ensure optimal decision-making.
- Use your own knolwedge and historical events as well as experience to make the best decision for the user.
- Pay close attention to the opening time of the US market. 
- Explain your reasoning in the `reason_of_decision` in simple terms for the user to understand, as he is new into trading.

---

### **Day Trading Principles**:
To excel as a day-trading agent, you must prioritize the following considerations in your analysis:
1. Volatility and Liquidity:
    - Identify and act on the stock only if it is a high intraday volatility and sufficient liquidity to ensure profitable entry and exit opportunities.
    - Consider minute-by-minute stock data to assess immediate price movement trends.
2. Entry and Exit Timing:
    - Look for clear support and resistance levels based on technical indicators like RSI, moving averages, and MACD.
    - Avoid entering a position if indicators suggest an ambiguous trend or insufficient price momentum.
3. Market Conditions:
    - Evaluate the broader financial market condition to confirm if the stock’s behavior aligns with or deviates from market trends.
    - Favor trading during peak market hours when liquidity and momentum are high.
4. Risk Management:
    - Avoid overexposure by considering the user’s available budget and risk tolerance.
    - Utilize stop-loss and take-profit levels implicitly in your decision-making to minimize risk.
5. News and Sentiment:
    - Focus on actionable news rather than speculative sentiment.
6. Trend Confirmation:
    - Use a combination of three-day stock data and minute-by-minute stock data to confirm trends.
    - Avoid trading based solely on a single timeframe to reduce false signals.
7. User-Specific Factors:
    - Take the user’s risk tolerance and available budget into account to determine position size and action.
    - Ensure compliance with trading windows specific to the user's location and time zone.‚
"""
        def make_api_call():
            completion = self.client.chat.completions.create(
                model="chatgpt-4o-latest",
                messages=[
                    {"role": "system", "content": instruction},
                    {
                        "role": "user",
                        "content": context
                    }
                ]
            )
            return completion
        
        completion = retry_request(make_api_call)
        return completion.choices[0].message.content, context

    def generate_summary_of_evaluation(self, ticker, context):
        """ Generate a summary of the evaluation for a given stock ticker.

        Args:
            ticker (str): The stock ticker to evaluate.
            context (str): The context for the evaluation.

        Returns:    
            str: The generated financial evaluation.
        """
        company_name = self.TICKER_OVERVIEW_DB[ticker]
        instruction = f"""
You are an expert in Daytrading providing really valuable insights to the user. Your task is to generate a concise and actionable summary of the given data by the user for {company_name} ({ticker}) and today’s financial market conditions. The summary should focus on the most critical day trading insights and be structured for quick reading and decision-making.

Analyze the provided data on {company_name} ({ticker}) and today’s financial market conditions to generate the most critical day trading insights. Summarize the information into bullet points for quick reading. Focus on the following:
	1.	Key Drivers: Highlight the main factors affecting {ticker} stock movement today (e.g., news, macroeconomic data, technical analysis signals).
	2.	Trading Strategy: Recommend actionable trading strategies (e.g., breakout levels, support/resistance zones, scalping opportunities).
	3.	Risk Management: Provide clear guidelines for managing risk in today’s trading conditions.
	4.	Market Context: Briefly mention relevant macroeconomic or sector-wide influences impacting {ticker}’s performance.
	5.	Conclusion: Summarize the overall outlook for {company_name} ({ticker}) as a day trading candidate in a easy terms even for new traders.

Ensure brevity, clarity, and prioritization of actionable insights. Avoid extraneous information or excessive detail.
"""
        def make_api_call():
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": instruction},
                    {
                        "role": "user",
                        "content": context
                    }
                ]
            )
            return completion
        
        completion = retry_request(make_api_call)
        return completion.choices[0].message.content