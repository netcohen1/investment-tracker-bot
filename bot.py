import os
import requests
import json
import time
import schedule
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
USER_CHAT_ID = os.getenv("USER_CHAT_ID")
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)

with open("portfolio.json", "r") as f:
    portfolio = json.load(f)

def check_stock(symbol, buy_price, alert_drop_percent):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        price = float(data["Global Quote"]["05. price"])
        change_percent = ((price - buy_price) / buy_price) * 100

        if change_percent < -alert_drop_percent:
            bot.send_message(chat_id=USER_CHAT_ID,
                             text=f"🚨 {symbol} ירדה ביותר מ-{alert_drop_percent}%! שקול פעולה.\nמחיר נוכחי: {price:.2f}$")
    except Exception as e:
        print(f"שגיאה בבדיקת {symbol}: {e}")

def check_portfolio():
    for stock in portfolio:
        check_stock(stock["symbol"], stock["buy_price"], stock["alert_drop_percent"])

def quarterly_report():
    msg = "📊 דוח רבעוני:\n"
    for stock in portfolio:
        msg += f"- {stock['symbol']}: יעד {stock['buy_price']}$ | אזור התראה: {stock['alert_drop_percent']}%\n"
    bot.send_message(chat_id=USER_CHAT_ID, text=msg)

schedule.every(1).minutes.do(check_portfolio)
schedule.every(13).weeks.do(quarterly_report)

while True:
    schedule.run_pending()
    time.sleep(1)
