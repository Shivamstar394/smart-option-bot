
import yfinance as yf
import pandas as pd
import os



def fetch_live_data():
    # Fetch latest 1 day data with 5 min interval
    ticker = yf.Ticker("^NSEI")
    live_data = ticker.history(period="1d", interval="5m")
    live_data.reset_index(inplace=True)

    live_data = live_data[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
    os.makedirs("data", exist_ok=True)
    live_data.to_csv("data/underlying.csv", index=False)
    print("✅ Live Data saved to data/underlying.csv")

if __name__ == "__main__":
    fetch_live_data()
    print("Fetching live data...")
    

