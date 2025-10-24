from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest

from main import app

client = TestClient(app)

def test_calculate_pnl_for_sell_put(db_session: Session):
    # 1. Create a "Sell Put" trade
    trade_data = {
        "underlying_ticker": "SPY",
        "trade_type": "Sell Put",
        "expiration_date": "2025-12-31",
        "strike_price": 400,
        "premium_received": 5.0,
        "number_of_contracts": 2,
        "transaction_date": "2025-01-01",
        "fees": 0.66
    }
    response = client.post("/api/trades/", json=trade_data)
    assert response.status_code == 200
    trade = response.json()
    trade_id = trade["id"]

    # 2. Close the trade
    close_data = {
        "buy_back_price": 2.0,
        "buy_back_date": "2025-02-01",
        "closing_fees": 0.66
    }
    response = client.put(f"/api/trades/{trade_id}/close", json=close_data)
    assert response.status_code == 200
    closed_trade = response.json()

    # 3. Assert that the P/L is calculated correctly
    # P/L = ((premium_received - buy_back_price) * number_of_contracts * 100) - fees - closing_fees
    # P/L = ((5.0 - 2.0) * 2 * 100) - 0.66 - 0.66
    # P/L = (3.0 * 200) - 1.32
    # P/L = 600 - 1.32 = 598.68
    assert closed_trade["pnl"] == pytest.approx(598.68)

def test_wheel_scenario(db_session: Session):
    # 1. Create and assign a "Sell Put" trade
    put_data = {
        "underlying_ticker": "TQQQ",
        "trade_type": "Sell Put",
        "expiration_date": "2025-01-31",
        "strike_price": 100,
        "premium_received": 5.0,
        "number_of_contracts": 1,
        "transaction_date": "2025-01-01",
        "fees": 0.66
    }
    response = client.post("/api/trades/", json=put_data)
    assert response.status_code == 200
    put_trade = response.json()
    put_trade_id = put_trade["id"]

    response = client.put(f"/api/trades/{put_trade_id}/assign")
    assert response.status_code == 200

    # 2. Verify the cost basis
    response = client.get(f"/api/cost_basis/TQQQ")
    assert response.status_code == 200
    cost_basis = response.json()
    assert cost_basis["original_cost_basis"] == 100
    assert cost_basis["cumulative_premium"] == 5.0
    assert cost_basis["cumulative_fees_per_share"] == pytest.approx(0.0066)

    # 3. Create a "Sell Call" trade
    call_data_1 = {
        "underlying_ticker": "TQQQ",
        "trade_type": "Sell Call",
        "expiration_date": "2025-02-28",
        "strike_price": 110,
        "premium_received": 3.0,
        "number_of_contracts": 1,
        "transaction_date": "2025-02-01",
        "fees": 0.66
    }
    response = client.post("/api/trades/", json=call_data_1)
    assert response.status_code == 200

    # 4. Verify the updated cost basis
    response = client.get(f"/api/cost_basis/TQQQ")
    assert response.status_code == 200
    cost_basis = response.json()
    assert cost_basis["original_cost_basis"] == 100
    assert cost_basis["cumulative_premium"] == 8.0
    assert cost_basis["cumulative_fees_per_share"] == pytest.approx(0.0066)
    # 5. Create and assign another "Sell Call" trade
    call_data_2 = {
        "underlying_ticker": "TQQQ",
        "trade_type": "Sell Call",
        "expiration_date": "2025-03-31",
        "strike_price": 120,
        "premium_received": 2.0,
        "number_of_contracts": 1,
        "transaction_date": "2025-03-01",
        "fees": 0.66
    }
    response = client.post("/api/trades/", json=call_data_2)
    assert response.status_code == 200
    call_trade_2 = response.json()
    call_trade_2_id = call_trade_2["id"]

    # When a sell call is assigned, the shares are called away.
    # This is equivalent to closing the option for a buy back price of 0.
    close_data = {
        "buy_back_price": 0,
        "buy_back_date": "2025-03-31",
        "closing_fees": 0.66
    }
    response = client.put(f"/api/trades/{call_trade_2_id}/close", json=close_data)
    assert response.status_code == 200
    closed_call = response.json()

    # 6. Verify the P/L of the final assigned call
    # The P/L of the option trade itself is the premium received minus fees.
    # The profit from the stock sale is not tracked by this application.
    # P/L = (premium_received * 100) - fees - closing_fees
    # P/L = (2.0 * 100) - 0.66 - 0.66 = 198.68
    assert closed_call["pnl"] == pytest.approx(198.68)

def test_wheel_scenario_with_stock_pnl(db_session: Session):
    # 1. Create and assign a "Sell Put" trade
    put_data = {
        "underlying_ticker": "F",
        "trade_type": "Sell Put",
        "expiration_date": "2025-01-31",
        "strike_price": 10,
        "premium_received": 1.0,
        "number_of_contracts": 1,
        "transaction_date": "2025-01-01",
        "fees": 0.66
    }
    response = client.post("/api/trades/", json=put_data)
    assert response.status_code == 200
    put_trade = response.json()
    put_trade_id = put_trade["id"]

    response = client.put(f"/api/trades/{put_trade_id}/assign")
    assert response.status_code == 200

    # 2. Create and expire a "Sell Call" trade
    call_data_1 = {
        "underlying_ticker": "F",
        "trade_type": "Sell Call",
        "expiration_date": "2025-02-28",
        "strike_price": 12,
        "premium_received": 0.5,
        "number_of_contracts": 1,
        "transaction_date": "2025-02-01",
        "fees": 0.66
    }
    response = client.post("/api/trades/", json=call_data_1)
    assert response.status_code == 200
    call_trade_1 = response.json()
    call_trade_1_id = call_trade_1["id"]

    response = client.put(f"/api/trades/{call_trade_1_id}/expire")
    assert response.status_code == 200

    # 3. Create and assign another "Sell Call" trade
    call_data_2 = {
        "underlying_ticker": "F",
        "trade_type": "Sell Call",
        "expiration_date": "2025-03-31",
        "strike_price": 15,
        "premium_received": 0.8,
        "number_of_contracts": 1,
        "transaction_date": "2025-03-01",
        "fees": 0.66
    }
    response = client.post("/api/trades/", json=call_data_2)
    assert response.status_code == 200
    call_trade_2 = response.json()
    call_trade_2_id = call_trade_2["id"]

    close_data = {
        "buy_back_price": 0,
        "buy_back_date": "2025-03-31",
        "closing_fees": 0.66
    }
    response = client.put(f"/api/trades/{call_trade_2_id}/close", json=close_data)
    assert response.status_code == 200

    # 4. Create an open "Sell Call" trade
    call_data_3 = {
        "underlying_ticker": "F",
        "trade_type": "Sell Call",
        "expiration_date": "2025-04-30",
        "strike_price": 16,
        "premium_received": 1.2,
        "number_of_contracts": 1,
        "transaction_date": "2025-04-01",
        "fees": 0.66
    }
    response = client.post("/api/trades/", json=call_data_3)
    assert response.status_code == 200

    # 5. Verify the cumulative P/L
    response = client.get(f"/api/cumulative_pnl/F")
    assert response.status_code == 200
    cumulative_pnl = response.json()["cumulative_pnl"]

    # stock_pnl = (15 - 6.50825) * 100 = 849.175
    # total_cumulative_pnl = 247.36 + 849.175 = 1096.535
    assert cumulative_pnl == pytest.approx(1096.535)
