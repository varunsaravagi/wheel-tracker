import csv
import requests
import re
from datetime import datetime

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/api"
CSV_FILE_PATH = "/root/options_wheel_tracker/wheel_transactions.csv"

# --- In-memory store for open trades ---
# Key: (Ticker, Strike, Expiration, Type)
# Value: Database ID of the trade
open_trades = {}

def parse_option_symbol(symbol):
    """
    Parses the option symbol string to extract ticker, expiration, strike, and type.
    Example: "CRWV 11/07/2025 143.00 C"
    """
    match = re.search(r"([A-Z]+)\s+([\d\/]+)\s+([\d\.]+)\s+(C|P)", symbol)
    if not match:
        return None, None, None, None

    ticker, expiration, strike, option_type_char = match.groups()
    
    expiration_date = datetime.strptime(expiration, "%m/%d/%Y").strftime("%Y-%m-%d")
    
    trade_type = "Sell Call" if option_type_char == 'C' else "Sell Put"

    return ticker, float(strike), expiration_date, trade_type

def parse_date(date_str):
    """Parses dates that might have 'as of' clauses."""
    if " as of " in date_str:
        date_str = date_str.split(" as of ")[1]
    return datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")

def run_import():
    # Clear the database to ensure a fresh start
    print("Clearing database for clean import...")
    # This is a placeholder; in a real app, you'd have a dedicated endpoint for this.
    # For this exercise, we'll just delete and let it be recreated.
    import os
    if os.path.exists("../trades.db"):
        os.remove("../trades.db")
    print("Database cleared.")

    with open(CSV_FILE_PATH, 'r') as f:
        rows = list(csv.DictReader(f))
        rows.reverse()

    print(f"Found {len(rows)} transactions. Starting import...")

    i = 0
    while i < len(rows):
        row = rows[i]
        action = row["Action"]
        symbol = row["Symbol"]
        
        if action not in ["Sell to Open", "Buy to Close", "Expired", "Assigned", "Sell", "Buy"]:
            i += 1
            continue

        print(f"Processing row {i+1}: {action} - {symbol}")

        ticker, strike, expiration, trade_type = parse_option_symbol(symbol)
        
        if not ticker:
            if action == "Sell" and row["Symbol"].isalpha():
                payload = {
                    "ticker": row["Symbol"],
                    "sell_price": float(row["Price"].replace('$', '')),
                    "sell_date": parse_date(row["Date"]),
                    "fees": float(row["Fees & Comm"].replace('$', '')) if row["Fees & Comm"] else 0.0
                }
                res = requests.post(f"{API_BASE_URL}/sell_stock", json=payload)
                if res.status_code == 200:
                    print(f"  -> Processed stock sale for {row['Symbol']}")
                    for k in list(open_trades.keys()):
                        if k[0] == row["Symbol"]:
                            del open_trades[k]
                else:
                    print(f"  -> ERROR selling stock: {res.status_code} - {res.text}")
            else:
                print(f"  -> SKIPPING: Not an option or relevant stock trade.")
            i += 1
            continue

        # --- Roll Detection ---
        if action == "Buy to Close" and (i + 1) < len(rows) and rows[i+1]["Action"] == "Sell to Open":
            new_ticker, new_strike, new_exp, _ = parse_option_symbol(rows[i+1]["Symbol"])
            if ticker == new_ticker:
                print("  -> Detected a ROLL.")
                trade_key = (ticker, strike, expiration, trade_type)
                if trade_key not in open_trades:
                    print(f"  -> ERROR: Could not find open trade to roll for {trade_key}")
                    i += 1
                    continue
                
                trade_id_to_roll = open_trades.pop(trade_key)
                roll_payload = {
                    "new_expiration_date": new_exp, "strike_price": new_strike,
                    "premium_received": float(rows[i+1]["Price"].replace('$', '')),
                    "fees": float(rows[i+1]["Fees & Comm"].replace('$', '')),
                    "closing_fees": float(row["Fees & Comm"].replace('$', '')),
                    "roll_date": parse_date(row["Date"])
                }
                res = requests.post(f"{API_BASE_URL}/trades/{trade_id_to_roll}/roll", json=roll_payload)
                if res.status_code == 200:
                    new_trade = res.json()
                    new_trade_key = (new_ticker, new_strike, new_exp, new_trade['trade_type'])
                    open_trades[new_trade_key] = new_trade['id']
                    print(f"  -> Successfully rolled trade {trade_id_to_roll} to new trade {new_trade['id']}")
                else:
                    print(f"  -> ERROR rolling trade: {res.status_code} - {res.text}")
                i += 2
                continue
        
        # --- Single Actions ---
        if action == "Sell to Open":
            payload = {
                "underlying_ticker": ticker, "trade_type": trade_type, "expiration_date": expiration,
                "strike_price": strike, "premium_received": float(row["Price"].replace('$', '')),
                "number_of_contracts": int(row["Quantity"]), "transaction_date": parse_date(row["Date"]),
                "fees": float(row["Fees & Comm"].replace('$', ''))
            }
            res = requests.post(f"{API_BASE_URL}/trades/", json=payload)
            if res.status_code == 200:
                new_trade = res.json()
                trade_key = (ticker, strike, expiration, trade_type)
                open_trades[trade_key] = new_trade['id']
                print(f"  -> Opened new trade {new_trade['id']}")
            else:
                print(f"  -> ERROR creating trade: {res.status_code} - {res.text}")

        elif action in ["Buy to Close", "Expired", "Assigned"]:
            trade_key = (ticker, strike, expiration, trade_type)
            if trade_key not in open_trades:
                print(f"  -> ERROR: Could not find open trade for {action}: {trade_key}")
            else:
                trade_id = open_trades[trade_key]
                if action != "Assigned":
                    open_trades.pop(trade_key)

                if action == "Buy to Close":
                    payload = {"buy_back_price": float(row["Price"].replace('$', '')), "buy_back_date": parse_date(row["Date"]), "closing_fees": float(row["Fees & Comm"].replace('$', ''))}
                    res = requests.put(f"{API_BASE_URL}/trades/{trade_id}/close", json=payload)
                elif action == "Expired":
                    res = requests.put(f"{API_BASE_URL}/trades/{trade_id}/expire")
                elif action == "Assigned":
                    res = requests.put(f"{API_BASE_URL}/trades/{trade_id}/assign")
                
                if res.status_code == 200:
                    print(f"  -> Processed {action} for trade {trade_id}")
                else:
                    print(f"  -> ERROR processing {action}: {res.status_code} - {res.text}")
        
        i += 1

    print("Import finished.")
    print("Remaining open trades:", open_trades)

if __name__ == "__main__":
    run_import()
