import pandas as pd
from pathlib import Path

class CSVProvider:
    def __init__(self, path: str):
        self.path = Path(path)

    def load(self) -> pd.DataFrame:
        if not self.path.exists():
            raise FileNotFoundError(f"CSV not found: {self.path}")
        df = pd.read_csv(self.path, parse_dates=["datetime"])
        # expected columns: datetime, open, high, low, close, volume, [iv]
        return df.sort_values("datetime").reset_index(drop=True)

    def get_latest_iv(self) -> float:
        df = self.load()
        if "iv" in df.columns:
            return df["iv"].iloc[-1]
        return 0.0
    
    def save(self, df: pd.DataFrame):
        df.to_csv(self.path, index=False)
        print(f"✅ Data saved to {self.path}")

        
