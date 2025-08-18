# Smart Options Trading Bot — Starter (Educational)

**What it does**
- Decides Call vs Put using EMA(20/50) trend + RSI cross + IV percentile filter
- Entry/Exit alerts
- Strike choice by target delta (heuristic)
- Risk: position sizing by capital & SL%, TP%, trailing start/step
- Backtest on CSV; Paper alerts loop

## Run
1) `pip install -r requirements.txt`
2) Put your OHLCV in `data/underlying.csv` (sample included)
3) Backtest: `python backtest.py --config config.yaml`
4) Alerts loop: `python bot.py --config config.yaml`

## Notes
- IVP < 60 → prefer option buys; else consider spreads (future work)
- Replace CSV with live feed + broker when ready.
- Not financial advice; paper trade first.
