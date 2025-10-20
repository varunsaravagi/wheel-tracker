from pydantic import BaseModel
from datetime import date
from typing import Optional

class TradeBase(BaseModel):
    underlying_ticker: str
    trade_type: str
    expiration_date: date
    strike_price: float
    premium_received: float
    number_of_contracts: int
    transaction_date: date
    fees: float = 0.0

class TradeCreate(TradeBase):
    pass

class Trade(TradeBase):
    id: int
    status: str
    buy_back_price: Optional[float] = None
    buy_back_date: Optional[date] = None
    pnl: Optional[float] = None
    assigned: bool
    rolled_from_id: Optional[int] = None

    class Config:
        orm_mode = True

class TradeClose(BaseModel):
    buy_back_price: float
    buy_back_date: date
    closing_fees: float = 0.0

class TradeRoll(BaseModel):
    new_expiration_date: date
    strike_price: float
    premium_received: float
    fees: float = 0.0
    closing_fees: float = 0.0
    roll_date: date