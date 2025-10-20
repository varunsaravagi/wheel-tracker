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
    db_trade = models.Trade(**trade.dict())
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

@app.get("/api/trades/", response_model=List[schemas.Trade])
def read_trades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    trades = db.query(models.Trade).offset(skip).limit(limit).all()
    return trades

@app.put("/api/trades/{trade_id}/close", response_model=schemas.Trade)
def close_trade(trade_id: int, trade_close: schemas.TradeClose, db: Session = Depends(get_db)):
    db_trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")

    db_trade.buy_back_price = trade_close.buy_back_price
    db_trade.buy_back_date = trade_close.buy_back_date
    db_trade.status = "Closed"
    db_trade.closing_fees = trade_close.closing_fees
    db_trade.pnl = ((db_trade.premium_received - db_trade.buy_back_price) * db_trade.number_of_contracts * 100) - db_trade.fees - db_trade.closing_fees
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
    db_trade_to_roll.pnl = (db_trade_to_roll.premium_received * db_trade_to_roll.number_of_contracts * 100) - db_trade_to_roll.fees - db_trade_to_roll.closing_fees

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

@app.get("/api/dashboard/")
def get_dashboard_data(db: Session = Depends(get_db)):
    total_premium_collected = db.query(func.sum((models.Trade.premium_received * models.Trade.number_of_contracts * 100) - models.Trade.fees)).scalar()
    total_pnl = db.query(func.sum(models.Trade.pnl)).filter(models.Trade.status.in_(["Closed", "Rolled"])).scalar()
    closed_trades = db.query(models.Trade).filter(models.Trade.status.in_(["Closed", "Rolled"])).count()
    winning_trades = db.query(models.Trade).filter(models.Trade.status.in_(["Closed", "Rolled"]), models.Trade.pnl > 0).count()
    win_rate = (winning_trades / closed_trades) * 100 if closed_trades > 0 else 0

    return {
        "total_premium_collected": total_premium_collected or 0,
        "total_pnl": total_pnl or 0,
        "win_rate": win_rate
    }

@app.post("/api/analyze")
def analyze_trades(trades: List[schemas.Trade]):
    # Placeholder for Gemini API call
    analysis = "Gemini analysis: Based on your trade history, you are doing great!"
    return {"analysis": analysis}
