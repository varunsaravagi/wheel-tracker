from pydantic import BaseModel, ConfigDict
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

class TradeUpdate(BaseModel):
    underlying_ticker: Optional[str] = None
    trade_type: Optional[str] = None
    expiration_date: Optional[date] = None
    strike_price: Optional[float] = None
    premium_received: Optional[float] = None
    number_of_contracts: Optional[int] = None
    transaction_date: Optional[date] = None
    fees: Optional[float] = None

class Trade(TradeBase):
    id: int
    status: str
    buy_back_price: Optional[float] = None
    buy_back_date: Optional[date] = None
    pnl: Optional[float] = None
    assigned: bool
    rolled_from_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class CostBasis(BaseModel):
    original_cost_basis: float
    cumulative_premium: float
    cumulative_fees_per_share: float

    model_config = ConfigDict(from_attributes=True)

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

class CumulativePnl(BaseModel):
    cumulative_pnl: float
