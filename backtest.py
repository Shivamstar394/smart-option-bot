import argparse, yaml
import pandas as pd
from signal_engine import add_indicators, generate_signals
from data_providers import CSVProvider
from strategies.simple_strategy import SimpleStrategy, StrategyConfig
from option_selector import choose_option
from executor import PaperExecutor
from risk_manager import RiskParams, position_size
from utils import iv_percentile

def estimate_option_price(spot, strike, kind, iv_proxy, dte):
    # Simplified: option price ~ max(Intrinsic, spot*iv_proxy*sqrt(dte/365)*0.5)
    import math
    intrinsic = max(0.0, spot - strike) if kind=="CALL" else max(0.0, strike - spot)
    time_val = spot * iv_proxy * math.sqrt(max(dte,1)/365) * 0.5
    return max(intrinsic, time_val)

def run_backtest(cfg_path):
    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)

    df = CSVProvider(cfg["data"]["csv_path"]).load()
    df = add_indicators(df, cfg["strategy"]["ema_fast"], cfg["strategy"]["ema_slow"],
                        cfg["strategy"]["rsi_period"], cfg["strategy"]["atr_period"])
    df = generate_signals(df, cfg["strategy"]["rsi_long"], cfg["strategy"]["rsi_short"])

    strat = SimpleStrategy(StrategyConfig(**cfg["strategy"]))
    ex = PaperExecutor(slippage_bps=cfg["backtest"]["slippage_bps"], lot_size=cfg["market"]["lot_size"])

    rp = RiskParams(
        capital=cfg["risk"]["capital"],
        risk_per_trade=cfg["risk"]["risk_per_trade"],
        option_sl_pct=cfg["risk"]["option_stop_loss_pct"],
        option_tp_pct=cfg["risk"]["option_take_profit_pct"],
        trail_trigger_pct=cfg["risk"]["trail_trigger_pct"],
        trail_step_pct=cfg["risk"]["trail_step_pct"],
        lot_size=cfg["market"]["lot_size"],
    )

    # IV proxy if missing
    if "iv" not in df.columns:
        df["iv"] = df["close"].pct_change().rolling(252).std() * (252**0.5)
    df["ivp"] = df["iv"].rolling(252).apply(
        lambda s: (s<=s.iloc[-1]).sum()/len(s)*100 if len(s.dropna())>0 else float("nan"), raw=False
    )

    open_trade = None
    results = []
    for _, row in df.iterrows():
        spot = row["close"]
        ivp = row.get("ivp", 50)
        ts = row["datetime"]

        # exits
        if open_trade is not None:
            prem_now = estimate_option_price(spot, open_trade["strike"], open_trade["kind"], row["iv"], dte=5)
            change = (prem_now - open_trade["entry_price"]) / open_trade["entry_price"]
            if change <= -cfg["risk"]["option_stop_loss_pct"] or change >= cfg["risk"]["option_take_profit_pct"]:
                open_trade["exit_time"] = ts
                open_trade["exit_price"] = prem_now
                pnl = (prem_now - open_trade["entry_price"]) * open_trade["lots"] * cfg["market"]["lot_size"]
                open_trade["pnl"] = pnl
                results.append(open_trade)
                open_trade = None
                continue

        # entries
        if open_trade is None and ivp < cfg["strategy"]["ivp_threshold_buy"]:
            if strat.should_buy_calls(row):
                choice = choose_option(spot, bias=1, buy_delta_target=cfg["options"]["buy_delta_target"])
            elif strat.should_buy_puts(row):
                choice = choose_option(spot, bias=-1, buy_delta_target=cfg["options"]["buy_delta_target"])
            else:
                continue

            prem = estimate_option_price(spot, choice.strike, choice.kind, row["iv"], dte=5)
            lots = position_size(prem, rp)
            if lots > 0:
                open_trade = {
                    "entry_time": ts, "kind": choice.kind, "strike": choice.strike,
                    "entry_price": prem, "lots": lots
                }

    if open_trade is not None:
        row = df.iloc[-1]
        prem_now = estimate_option_price(row["close"], open_trade["strike"], open_trade["kind"], row["iv"], dte=1)
        open_trade["exit_time"] = row["datetime"]
        open_trade["exit_price"] = prem_now
        pnl = (prem_now - open_trade["entry_price"]) * open_trade["lots"] * cfg["market"]["lot_size"]
        open_trade["pnl"] = pnl
        results.append(open_trade)

    res_df = pd.DataFrame(results)
    if len(res_df):
        print(res_df[["entry_time","exit_time","kind","strike","entry_price","exit_price","lots","pnl"]].to_string(index=False))
        print("\nSummary:")
        print("Trades:", len(res_df))
        print("Win rate:", float((res_df["pnl"]>0).mean()))
        print("Total PnL:", round(res_df["pnl"].sum(), 2))
        print("Avg PnL:", round(res_df["pnl"].mean(), 2))
    else:
        print("No trades generated. Try relaxing thresholds or check data.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    a = p.parse_args()
    run_backtest(a.config)

import yfinance as yf