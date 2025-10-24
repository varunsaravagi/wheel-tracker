from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = "sqlite:////root/options_wheel_tracker/trades.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    underlying_ticker = Column(String, index=True)
    trade_type = Column(String)
    expiration_date = Column(Date)
    strike_price = Column(Float)
    premium_received = Column(Float)
    number_of_contracts = Column(Integer)
    transaction_date = Column(Date)
    status = Column(String, default="Open")
    buy_back_price = Column(Float, nullable=True)
    buy_back_date = Column(Date, nullable=True)
    pnl = Column(Float, nullable=True)
    fees = Column(Float, default=0.0)
    closing_fees = Column(Float, default=0.0)
    assigned = Column(Boolean, default=False)
    rolled_from_id = Column(Integer, ForeignKey("trades.id"), nullable=True)

    # This is the parent trade
    rolled_from = relationship("Trade", remote_side=[id], back_populates="rolled_to")

    # This is the child trade
    rolled_to = relationship("Trade", uselist=False, back_populates="rolled_from")

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

