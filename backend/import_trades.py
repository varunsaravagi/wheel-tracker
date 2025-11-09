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
known_tickers = set()

def get_known_tickers(rows):
    """Pre-scans the CSV to get a set of all potential stock tickers."""
    tickers = set()
    for row in rows:
        # Add from Symbol column
        if row["Symbol"] and row["Symbol"].isalpha() and len(row["Symbol"]) <= 5:
            tickers.add(row["Symbol"])
        # Add from Description column
        match = re.search(r"(PUT|CALL)\s+([\w\s\.\-]+?)\s+\$?", row["Description"])
        if match:
            # Get the first word, assuming it's the ticker
            ticker = match.group(2).strip().split(" ")[0]
            if ticker.isalpha() and len(ticker) <= 5:
                tickers.add(ticker)
    return tickers


def parse_option_description(description):
    """
    Parses the option description string to extract ticker, expiration, strike, and type.
    """
    match = re.search(r"^(PUT|CALL)\s+(.+?)\s+\$?([\d\.]+)\s+EXP\s+([\d\/]+)", description)
    if not match:
        return None, None, None, None

    option_type_str, full_name, strike, expiration = match.groups()
    
    # --- Ticker Parsing (V4) ---
    ticker = None
    # Try to find a known ticker in the full name string
    for t in known_tickers:
        if t in full_name:
            ticker = t
            break
    
    if not ticker:
        # Fallback to the first word if no known ticker is found
        ticker = full_name.strip().split(" ")[0]
        if not ticker.isalpha() or len(ticker) > 5:
             return None, None, None, None # Give up if it's not a valid-looking ticker

    expiration_date = datetime.strptime(expiration, "%m/%d/%y").strftime("%Y-%m-%d")
    trade_type = f"Sell {option_type_str.title()}"

    return ticker, float(strike), expiration_date, trade_type

def parse_date(date_str):
    """Parses dates that might have 'as of' clauses."""
    if " as of " in date_str:
        date_str = date_str.split(" as of ")[1]
    return datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")

def find_trade_key_for_wheel(ticker, strike, expiration, trade_type):
    """Finds a trade, being aware of the wheel state."""
    direct_key = (ticker, strike, expiration, trade_type)
    if direct_key in open_trades:
        return direct_key

    # If not found, check for an active wheel for this ticker
    # An active wheel is an assigned put that hasn't been closed by a stock sale
    for (t, s, e, tt), trade_id in open_trades.items():
        if t == ticker and tt == "Sell Put": # Found the base of a wheel
            # Now, let's see if the current action matches this wheel
            # This is a heuristic: we assume a call action belongs to the open put wheel
            if trade_type == "Sell Call":
                 # This is complex. For now, we'll assume the first open call we find for a ticker is the one.
                 # A better implementation would require the API to return the wheel chain.
                 # Let's try to find ANY open call for this ticker.
                 for k_inner, v_inner in open_trades.items():
                     if k_inner[0] == ticker and k_inner[3] == "Sell Call" and k_inner[1] == strike and k_inner[2] == expiration:
                         return k_inner
    return None


def run_import():
    global known_tickers
    
    with open(CSV_FILE_PATH, 'r') as f:
        rows = list(csv.DictReader(f))
        rows.reverse()

    known_tickers = get_known_tickers(rows)
    print(f"Found {len(rows)} transactions and {len(known_tickers)} unique tickers. Starting import...")

    i = 0
    while i < len(rows):
        row = rows[i]
        action = row["Action"]
        description = row["Description"]
        
        if action not in ["Sell to Open", "Buy to Close", "Expired", "Assigned", "Sell", "Buy"]:
            i += 1
            continue

        print(f"Processing row {i+1}: {action} - {description}")

        ticker, strike, expiration, trade_type = parse_option_description(description)
        
        if not ticker:
            if action == "Sell" and row["Symbol"] in known_tickers:
                payload = {
                    "ticker": row["Symbol"],
                    "sell_price": float(row["Price"].replace('$', '')),
                    "sell_date": parse_date(row["Date"]),
                    "fees": float(row["Fees & Comm"].replace('$', '')) if row["Fees & Comm"] else 0.0
                }
                res = requests.post(f"{API_BASE_URL}/sell_stock", json=payload)
                if res.status_code == 200:
                    print(f"  -> Processed stock sale for {row['Symbol']}")
                    # Clean up all trades for this wheel
                    for k in list(open_trades.keys()):
                        if k[0] == row["Symbol"]:
                            del open_trades[k]
                else:
                    print(f"  -> ERROR selling stock: {res.status_code} - {res.text}")
            else:
                print(f"  -> SKIPPING: Could not parse or not a relevant stock trade.")
            i += 1
            continue

        # --- Roll Detection ---
        if action == "Buy to Close" and (i + 1) < len(rows) and rows[i+1]["Action"] == "Sell to Open":
            new_ticker, new_strike, new_exp, _ = parse_option_description(rows[i+1]["Description"])
            if ticker == new_ticker:
                print("  -> Detected a ROLL.")
                trade_key = find_trade_key_for_wheel(ticker, strike, expiration, trade_type)
                if not trade_key:
                    print(f"  -> ERROR: Could not find open trade to roll for {(ticker, strike, expiration, trade_type)}")
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
            trade_key = find_trade_key_for_wheel(ticker, strike, expiration, trade_type)
            if not trade_key:
                print(f"  -> ERROR: Could not find open trade for {action}: {(ticker, strike, expiration, trade_type)}")
            else:
                trade_id = open_trades[trade_key]
                if action != "Assigned": # Don't pop if assigned, it's still active
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