# Options Wheel Tracker

This project is a simple Hello World application with a Python FastAPI backend and a React frontend.

## Setup

### Backend

1.  Navigate to the `backend` directory:
    ```sh
    cd backend
    ```
2.  Create a virtual environment:
    ```sh
    python3 -m venv venv
    ```
3.  Activate the virtual environment:
    ```sh
    source venv/bin/activate
    ```
4.  Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

### Frontend

1.  Navigate to the `frontend` directory:
    ```sh
    cd frontend
    ```
2.  Install the required Node.js packages:
    ```sh
    npm install
    ```

## Running the Application

### Backend

1.  Navigate to the `backend` directory:
    ```sh
    cd backend
    ```
2.  Activate the virtual environment:
    ```sh
    source venv/bin/activate
    ```
3.  Start the FastAPI server:
    ```sh
    uvicorn main:app --reload
    ```
    The backend will be running at `http://localhost:8000`.

### Frontend

1.  Navigate to the `frontend` directory:
    ```sh
    cd frontend
    ```
2.  Start the React development server:
    ```sh
    npm start
    ```
    The frontend will be running at `http://localhost:3000`.

Open your browser and navigate to `http://localhost:3000` to see the application running.
