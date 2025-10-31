from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func

import models
import schemas
from models import SessionLocal, create_db_and_tables

create_db_and_tables()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://192.168.6.44:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/trades/", response_model=schemas.Trade)
def create_trade(trade: schemas.TradeCreate, db: Session = Depends(get_db)):
    db_trade = models.Trade(**trade.model_dump())
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

@app.get("/api/trades/", response_model=List[schemas.Trade])
def read_trades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    trades = db.query(models.Trade).offset(skip).limit(limit).all()
    return trades

@app.put("/api/trades/{trade_id}", response_model=schemas.Trade)
def update_trade(trade_id: int, trade: schemas.TradeUpdate, db: Session = Depends(get_db)):
    db_trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")

    update_data = trade.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_trade, key, value)

    db.commit()
    db.refresh(db_trade)
    return db_trade

@app.put("/api/trades/{trade_id}/close", response_model=schemas.Trade)
def close_trade(trade_id: int, trade_close: schemas.TradeClose, db: Session = Depends(get_db)):
    db_trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")

    db_trade.buy_back_price = trade_close.buy_back_price
    db_trade.buy_back_date = trade_close.buy_back_date
    db_trade.status = "Closed"
    db_trade.closing_fees = trade_close.closing_fees
    db_trade.net_premium_received = ((db_trade.premium_received - db_trade.buy_back_price) * db_trade.number_of_contracts * 100) - db_trade.fees - db_trade.closing_fees
    db.commit()
    db.refresh(db_trade)
    return db_trade

@app.put("/api/trades/{trade_id}/assign", response_model=schemas.Trade)
def assign_trade(trade_id: int, db: Session = Depends(get_db)):
    db_trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")

    db_trade.assigned = True
    db_trade.status = "Assigned"
    db.commit()
    db.refresh(db_trade)
    return db_trade

@app.post("/api/trades/{trade_id}/roll", response_model=schemas.Trade)
def roll_trade(trade_id: int, trade_roll: schemas.TradeRoll, db: Session = Depends(get_db)):
    db_trade_to_roll = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if db_trade_to_roll is None:
        raise HTTPException(status_code=404, detail="Trade not found")

    # Close the old trade
    db_trade_to_roll.buy_back_price = 0  # Or you can have a separate field for roll cost
    db_trade_to_roll.buy_back_date = trade_roll.roll_date
    db_trade_to_roll.status = "Rolled"
    db_trade_to_roll.closing_fees = trade_roll.closing_fees
    db_trade_to_roll.net_premium_received = (db_trade_to_roll.premium_received * db_trade_to_roll.number_of_contracts * 100) - db_trade_to_roll.fees - db_trade_to_roll.closing_fees

    # Create a new trade
    new_trade = models.Trade(
        underlying_ticker=db_trade_to_roll.underlying_ticker,
        trade_type=db_trade_to_roll.trade_type,
        expiration_date=trade_roll.new_expiration_date,
        strike_price=trade_roll.strike_price,
        premium_received=trade_roll.premium_received,
        number_of_contracts=db_trade_to_roll.number_of_contracts,
        transaction_date=db_trade_to_roll.transaction_date, # Should this be today's date?
        status="Open",
        rolled_from_id=db_trade_to_roll.id,
        fees=trade_roll.fees
    )

    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)

    db.commit()
    db.refresh(db_trade_to_roll)

    return new_trade

@app.get("/api/cost_basis/{ticker}", response_model=schemas.CostBasis)
def get_cost_basis(ticker: str, db: Session = Depends(get_db)):
    assigned_put = db.query(models.Trade).filter(
        models.Trade.underlying_ticker == ticker,
        models.Trade.trade_type == 'Sell Put',
        models.Trade.status == 'Assigned'
    ).order_by(models.Trade.transaction_date.desc()).first()

    if not assigned_put:
        raise HTTPException(status_code=404, detail="No assigned put found for this ticker")

    original_cost_basis = assigned_put.strike_price

    cumulative_premium = db.query(func.sum(models.Trade.premium_received)).filter(
        models.Trade.underlying_ticker == ticker,
        models.Trade.transaction_date >= assigned_put.transaction_date
    ).scalar()

    cumulative_fees = db.query(func.sum(models.Trade.fees + models.Trade.closing_fees)).filter(
        models.Trade.underlying_ticker == ticker,
        models.Trade.transaction_date >= assigned_put.transaction_date
    ).scalar() or 0

    total_contracts = db.query(func.sum(models.Trade.number_of_contracts)).filter(
        models.Trade.underlying_ticker == ticker,
        models.Trade.transaction_date >= assigned_put.transaction_date
    ).scalar() or 0

    cumulative_fees_per_share = 0
    if total_contracts > 0:
        cumulative_fees_per_share = cumulative_fees / (total_contracts * 100)

    return schemas.CostBasis(original_cost_basis=original_cost_basis, cumulative_premium=cumulative_premium or 0, cumulative_fees_per_share=cumulative_fees_per_share)

@app.put("/api/trades/{trade_id}/expire", response_model=schemas.Trade)
def expire_trade(trade_id: int, db: Session = Depends(get_db)):
    db_trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")

    db_trade.status = "Expired"
    db_trade.buy_back_price = 0
    db_trade.net_premium_received = (db_trade.premium_received * db_trade.number_of_contracts * 100) - db_trade.fees
    db.commit()
    db.refresh(db_trade)
    return db_trade

@app.get("/api/cumulative_pnl/{ticker}", response_model=schemas.CumulativePnl)
def get_cumulative_pnl(ticker: str, db: Session = Depends(get_db)):
    assigned_put = db.query(models.Trade).filter(
        models.Trade.underlying_ticker == ticker,
        models.Trade.trade_type == 'Sell Put',
        models.Trade.status == 'Assigned'
    ).order_by(models.Trade.transaction_date.desc()).first()

    if not assigned_put:
        return schemas.CumulativePnl(cumulative_pnl=0)

    trades = db.query(models.Trade).filter(
        models.Trade.underlying_ticker == ticker,
        models.Trade.transaction_date >= assigned_put.transaction_date
    ).all()

    total_net_premium = sum(trade.net_premium_received for trade in trades if trade.net_premium_received is not None)

    assigned_call = next((trade for trade in trades if trade.trade_type == 'Sell Call' and trade.status == 'Closed' and trade.buy_back_price == 0), None)

    if assigned_call:
        cost_basis_data = get_cost_basis(ticker, db)
        adjusted_cost_basis = cost_basis_data.original_cost_basis - cost_basis_data.cumulative_premium + cost_basis_data.cumulative_fees_per_share
        sell_price = assigned_call.strike_price
        number_of_shares = assigned_call.number_of_contracts * 100
        stock_pnl = (sell_price - adjusted_cost_basis) * number_of_shares
        total_cumulative_pnl = total_net_premium + stock_pnl
        return schemas.CumulativePnl(cumulative_pnl=total_cumulative_pnl)
    else:
        return schemas.CumulativePnl(cumulative_pnl=total_net_premium)

@app.get("/api/dashboard/")
def get_dashboard_data(db: Session = Depends(get_db)):
    total_premium_collected = db.query(func.sum((models.Trade.premium_received * models.Trade.number_of_contracts * 100) - models.Trade.fees)).scalar()
    total_net_premium = db.query(func.sum(models.Trade.net_premium_received)).filter(models.Trade.status.in_(["Closed", "Rolled"])).scalar()
    closed_trades = db.query(models.Trade).filter(models.Trade.status.in_(["Closed", "Rolled"])).count()
    winning_trades = db.query(models.Trade).filter(models.Trade.status.in_(["Closed", "Rolled"]), models.Trade.net_premium_received > 0).count()
    win_rate = (winning_trades / closed_trades) * 100 if closed_trades > 0 else 0

    return {
        "total_premium_collected": total_premium_collected or 0,
        "total_net_premium": total_net_premium or 0,
        "win_rate": win_rate
    }

@app.post("/api/analyze")
def analyze_trades(trades: List[schemas.Trade]):
    # Placeholder for Gemini API call
    analysis = "Gemini analysis: Based on your trade history, you are doing great!"
    return {"analysis": analysis}
