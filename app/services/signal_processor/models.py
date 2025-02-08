from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional

class SignalType(str, Enum):
    FOREX = "forex"
    CRYPTO = "crypto"
    STOCKS = "stocks"

class TradingSignal(BaseModel):
    id: Optional[int] = None
    market: SignalType
    symbol: str
    action: str
    price: float
    stop_loss: float
    take_profit: float
    timeframe: str
    strategy: str
    created_at: datetime = datetime.now()

    class Config:
        use_enum_values = True
