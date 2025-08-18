import math
from dataclasses import dataclass

@dataclass
class OptionChoice:
    kind: str            # "CALL" or "PUT"
    strike: float
    expiry: str          # YYYY-MM-DD or "NEAREST"
    delta_target: float

def nearest_round(x, step=50):
    return round(x/step)*step

def choose_option(spot: float, bias: int, buy_delta_target=0.35, expiry_preference="nearest") -> OptionChoice:
    # very simple heuristic (no chain yet)
    kind = "CALL" if bias == 1 else "PUT"
    # rough mapping: ~0.1 delta ≈ 1% OTM (only for placeholder)
    otm_pct = (buy_delta_target / 0.1) * 0.01   # e.g. 0.35 -> 3.5% OTM
    strike = spot * (1 + (otm_pct if kind=="CALL" else -otm_pct))
    strike = nearest_round(strike, step=50)
    return OptionChoice(kind=kind, strike=strike, expiry="NEAREST", delta_target=buy_delta_target)




