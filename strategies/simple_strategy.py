from dataclasses import dataclass

@dataclass
class StrategyConfig:
    ema_fast: int
    ema_slow: int
    rsi_period: int
    rsi_long: int
    rsi_short: int
    atr_period: int
    ivp_threshold_buy: float

class SimpleStrategy:
    def __init__(self, cfg: StrategyConfig):
        self.cfg = cfg
        self.name = "SimpleStrategy"

    def should_buy_calls(self, row):
        return row["bias"] == 1 and row["long_signal"]

    def should_buy_puts(self, row):
        return row["bias"] == -1 and row["short_signal"]

    def should_sell_calls(self, row):
        return row["bias"] == 1 and row["sell_signal"]

    def should_sell_puts(self, row):
        return row["bias"] == -1 and row["sell_signal"]
