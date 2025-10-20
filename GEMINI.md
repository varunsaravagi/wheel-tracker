# Project: Options Wheel Tracker

This file contains project-specific context for the Options Wheel Tracker application.

## Project Overview

This project is a web application designed to track options trades, specifically for the "wheel" strategy. It helps users track their trades, calculate Profit/Loss (P/L), and view dashboard metrics.

## Technology Stack

-   **Frontend:** React.js
-   **Backend:** FastAPI (Python)
-   **Database:** SQLite (`trades.db`)
-   **Styling:** Bootstrap

## Key Features

-   **Dashboard:** Displays key metrics like total premium collected, total P/L, and win rate.
-   **Trade Management:** Allows users to create, close, and roll trades.
-   **P/L Calculation:** Calculates P/L for each trade, including fees.

## Development Preferences

-   **UI/UX:** The user prefers a light UI and keyboard-friendly input for data entry.
-   **Trade Types:** The primary trade types are "Sell Put" and "Sell Call".
-   **Fees:** Fees (commissions) are an important part of the P/L calculation and should be included for opening, closing, and rolling trades.

## Database Schema

The main database table is `trades`, which includes the following columns:
-   `id`
-   `underlying_ticker`
-   `trade_type`
-   `expiration_date`
-   `strike_price`
-   `premium_received`
-   `number_of_contracts`
-   `transaction_date`
-   `status`
-   `buy_back_price`
-   `buy_back_date`
-   `pnl`
-   `assigned`
-   `rolled_from_id`
-   `fees`
-   `closing_fees`
