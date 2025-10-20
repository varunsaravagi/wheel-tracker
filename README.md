# Options Wheel Tracker

This project is a web application designed to track options trades, specifically for the "wheel" strategy. It helps users track their trades, calculate Profit/Loss (P/L), and view dashboard metrics.

## Features

-   **Dashboard:** Displays key metrics like total premium collected, total P/L, and win rate.
-   **Trade Management:** Allows users to create, close, and roll trades.
-   **P/L Calculation:** Calculates P/L for each trade, including opening and closing fees.
-   **Keyboard-Friendly UI:** The application is designed to be used with minimal mouse clicks, especially for data entry.
-   **Light Theme:** A clean and simple light theme for the user interface.

## Technology Stack

-   **Frontend:** React.js
-   **Backend:** FastAPI (Python)
-   **Database:** SQLite
-   **Styling:** Bootstrap

## Prerequisites

Before you begin, ensure you have the following installed on your system:

-   Python 3.10 or higher
-   Node.js 14.x or higher
-   npm 6.x or higher

## Setup and Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/varunsaravagi/wheel-tracker.git
    cd wheel-tracker
    ```

2.  **Backend Setup:**
    -   Navigate to the `backend` directory:
        ```sh
        cd backend
        ```
    -   Create and activate a Python virtual environment:
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```
    -   Install the required Python packages:
        ```sh
        pip install -r requirements.txt
        ```

3.  **Frontend Setup:**
    -   Navigate to the `frontend` directory:
        ```sh
        cd ../frontend
        ```
    -   Install the required Node.js packages:
        ```sh
        npm install
        ```

## Running the Application

1.  **Start the Backend Server:**
    -   Navigate to the `backend` directory:
        ```sh
        cd backend
        ```
    -   Activate the virtual environment:
        ```sh
        source venv/bin/activate
        ```
    -   Start the FastAPI server:
        ```sh
        uvicorn main:app --reload
        ```
    The backend server will be running at `http://localhost:8000`.

2.  **Start the Frontend Development Server:**
    -   In a new terminal, navigate to the `frontend` directory:
        ```sh
        cd frontend
        ```
    -   Start the React development server:
        ```sh
        npm start
        ```
    The frontend development server will be running at `http://localhost:3000`.

3.  **Access the Application:**
    Open your web browser and navigate to `http://localhost:3000` to use the application.

## Project Structure

```
options_wheel_tracker/
├── backend/            # FastAPI backend code
│   ├── main.py         # Main application file
│   ├── models.py       # SQLAlchemy models
│   ├── schemas.py      # Pydantic schemas
│   └── requirements.txt # Python dependencies
├── frontend/           # React frontend code
│   ├── src/
│   │   ├── App.js        # Main application component
│   │   ├── Dashboard.js  # Dashboard component
│   │   ├── TradeForm.js  # New trade form component
│   │   └── api.js        # API communication logic
│   └── package.json    # Node.js dependencies
├── trades.db           # SQLite database file
└── README.md           # This file
```