from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class Trade:
    entry_time: datetime
    exit_time: Optional[datetime]
    kind: str     # CALL/PUT
    strike: float
    direction: str  # "BUY"
    entry_price: float
    exit_price: Optional[float]
    lots: int
    pnl: Optional[float] = None

class PaperExecutor:
    def __init__(self, slippage_bps=5, lot_size=50):
        self.slippage_bps = slippage_bps
        self.lot_size = lot_size
        self.trades = []

    def _apply_slippage(self, price, side="buy"):
        bps = self.slippage_bps / 10000
        return price * (1 + bps if side=="buy" else 1 - bps)

    def open_trade(self, ts, kind, strike, price, lots):
        price = self._apply_slippage(price, "buy")
        t = Trade(entry_time=ts, exit_time=None, kind=kind, strike=strike, direction="BUY",
                  entry_price=price, exit_price=None, lots=lots)
        self.trades.append(t)
        return t

    def close_trade(self, trade: Trade, ts, price):
        price = self._apply_slippage(price, "sell")
        trade.exit_time = ts
        trade.exit_price = price
        trade.pnl = (price - trade.entry_price) * trade.lots * self.lot_size
        return trade

    def get_open_trades(self):
        return [t for t in self.trades if t.exit_time is None]

    def get_closed_trades(self):
        return [t for t in self.trades if t.exit_time is not None]

    def get_trade_history(self):
        return self.trades
    
