from dataclasses import dataclass

@dataclass
class RiskParams:
    capital: float
    risk_per_trade: float
    option_sl_pct: float
    option_tp_pct: float
    trail_trigger_pct: float
    trail_step_pct: float
    lot_size: int
    slippage_pct: float

    def __post_init__(self):
        # Validate and adjust parameters if necessary
        self.capital = max(0, self.capital)
        self.risk_per_trade = self._validate_percentage(self.risk_per_trade)
        self.option_sl_pct = self._validate_percentage(self.option_sl_pct)
        self.option_tp_pct = self._validate_percentage(self.option_tp_pct)
        self.trail_trigger_pct = self._validate_percentage(self.trail_trigger_pct)
        self.trail_step_pct = self._validate_percentage(self.trail_step_pct)
        self.lot_size = max(1, self.lot_size)
        self.slippage_pct = self._validate_percentage(self.slippage_pct)

    def _validate_percentage(self, value: float) -> float:
        if not (0 <= value <= 1):
            raise ValueError("Percentage values must be between 0 and 1.")
        return value

def position_size(premium: float, rp: RiskParams):
    max_risk_cash = rp.capital * rp.risk_per_trade
    # risk per lot approximated by SL distance
    risk_per_lot = premium * rp.option_sl_pct * rp.lot_size
    if risk_per_lot <= 0:
        return 0
    lots = int(max_risk_cash // risk_per_lot)
    return max(0, lots)



