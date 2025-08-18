import argparse, yaml
from random import choice
import notifier
from signal_engine import add_indicators, generate_signals
from data_providers import CSVProvider
from strategies.simple_strategy import SimpleStrategy, StrategyConfig
from option_selector import choose_option
from notifier import Notifier
import pandas as pd

def run_bot(cfg_path):
    print("Starting bot...")
    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)
        print("Config loaded")

    notifier = Notifier(console=cfg["alerts"]["console"], telegram=cfg["alerts"]["telegram"])
    df = CSVProvider(cfg["data"]["csv_path"]).load()
    print(f"Loaded data: {len(df)} rows")
    df = df[df["datetime"].apply(is_market_time)].reset_index(drop=True)
    print(f"After market time filter: {len(df)} rows")
    df = add_indicators(df, cfg["strategy"]["ema_fast"], cfg["strategy"]["ema_slow"],
                        cfg["strategy"]["rsi_period"], cfg["strategy"]["atr_period"])
    df = generate_signals(df, cfg["strategy"]["rsi_long"], cfg["strategy"]["rsi_short"])

    strategy_dict = cfg["strategy"]
    strategy_dict = dict(strategy_dict)  # Make a copy to avoid mutating the original config
    strategy_dict.pop("name", None)     # Remove 'name' if present
    strat = SimpleStrategy(StrategyConfig(**strategy_dict))

    open_trade = None
    for _, row in df.iterrows():
        ts = row["datetime"]
        ts_time = pd.to_datetime(row["datetime"]).time()
            
        # block fresh entries after 15:10 (exit-only)
        if ts_time >= pd.to_datetime("15:10").time():
        # allow exits but skip new entries
            if open_trade is not None and ((row["long_signal"] and open_trade["kind"]=="PUT") or (row["short_signal"] and open_trade["kind"]=="CALL")):
                notifier.send(f"[EXIT] {ts} Close {open_trade['kind']} at strike {open_trade['strike']} — Opposite signal")
                open_trade = None
            continue

        if open_trade is None and row["long_signal"] and row["bias"]==1:
            choice = choose_option(row["close"], bias=1, buy_delta_target=cfg["options"]["buy_delta_target"])
            notifier.send(f"[ENTRY] {ts} BUY CALL {choice.strike} (nearest expiry) — Reason: EMA trend + RSI breakout")
            open_trade = {"kind":"CALL", "strike": choice.strike, "entry_time": ts}
        elif open_trade is None and row["short_signal"] and row["bias"]==-1:
            choice = choose_option(row["close"], bias=-1, buy_delta_target=cfg["options"]["buy_delta_target"])
            notifier.send(f"[ENTRY] {ts} BUY PUT {choice.strike} (nearest expiry) — Reason: EMA trend + RSI breakdown")
            open_trade = {"kind":"PUT", "strike": choice.strike, "entry_time": ts}
        elif open_trade is not None and ((row["long_signal"] and open_trade["kind"]=="PUT") or (row["short_signal"] and open_trade["kind"]=="CALL")):
            notifier.send(f"[EXIT] {ts} Close {open_trade['kind']} at strike {open_trade['strike']} — Opposite signal")
            open_trade = None
def is_market_time(ts):
    ts = pd.to_datetime(ts)
    # if your CSV is naive local time, this still works; if UTC, first localize & convert
    hour = ts.hour
    minute = ts.minute
    # 09:15 <= time <= 15:30
    return (hour > 9 or (hour == 9 and minute >= 15)) and (hour < 15 or (hour == 15 and minute <= 30))
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    a = p.parse_args()
run_bot(a.config)
