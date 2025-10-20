import React, { useState } from 'react';
import { createTrade } from './api';

function TradeForm({ onTradeCreated }) {
    const [trade, setTrade] = useState({
        underlying_ticker: '',
        trade_type: 'Sell Put',
        strike_price: '',
        premium_received: '',
        number_of_contracts: '',
        transaction_date: new Date().toISOString().slice(0, 10),
        expiration_date: '',
        fees: '0.66'
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setTrade({ ...trade, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const newTrade = await createTrade(trade);
            if (onTradeCreated) {
                onTradeCreated(newTrade.data);
            }
            // Reset form
            setTrade({
                underlying_ticker: '',
                trade_type: 'Sell Put',
                strike_price: '',
                premium_received: '',
                number_of_contracts: '',
                transaction_date: new Date().toISOString().slice(0, 10),
                expiration_date: '',
                fees: '0.66'
            });
        } catch (error) {
            console.error("Error creating trade:", error);
        }
    };

    return (
        <div className="container mt-4">
            <h2 className="mb-4">New Trade</h2>
            <form onSubmit={handleSubmit}>
                <div className="row mb-3">
                    <div className="col">
                        <label htmlFor="underlying_ticker" className="form-label">Ticker</label>
                        <input type="text" className="form-control" id="underlying_ticker" name="underlying_ticker" value={trade.underlying_ticker} onChange={handleChange} required autoFocus />
                    </div>
                    <div className="col">
                        <label htmlFor="trade_type" className="form-label">Trade Type</label>
                        <select className="form-select" id="trade_type" name="trade_type" value={trade.trade_type} onChange={handleChange}>
                            <option>Sell Put</option>
                            <option>Sell Call</option>
                        </select>
                    </div>
                </div>
                <div className="row mb-3">
                    <div className="col">
                        <label htmlFor="strike_price" className="form-label">Strike</label>
                        <input type="number" className="form-control" id="strike_price" name="strike_price" value={trade.strike_price} onChange={handleChange} required />
                    </div>
                    <div className="col">
                        <label htmlFor="premium_received" className="form-label">Premium</label>
                        <input type="number" step="0.01" className="form-control" id="premium_received" name="premium_received" value={trade.premium_received} onChange={handleChange} required />
                    </div>
                    <div className="col">
                        <label htmlFor="number_of_contracts" className="form-label">Quantity</label>
                        <input type="number" className="form-control" id="number_of_contracts" name="number_of_contracts" value={trade.number_of_contracts} onChange={handleChange} required />
                    </div>
                </div>
                <div className="row mb-3">
                    <div className="col">
                        <label htmlFor="transaction_date" className="form-label">Trade Date</label>
                        <input type="date" className="form-control" id="transaction_date" name="transaction_date" value={trade.transaction_date} onChange={handleChange} required />
                    </div>
                    <div className="col">
                        <label htmlFor="expiration_date" className="form-label">Expiration Date</label>
                        <input type="date" className="form-control" id="expiration_date" name="expiration_date" value={trade.expiration_date} onChange={handleChange} required />
                    </div>
                    <div className="col">
                        <label htmlFor="fees" className="form-label">Fees/Commission</label>
                        <input type="number" step="0.01" className="form-control" id="fees" name="fees" value={trade.fees} onChange={handleChange} required />
                    </div>
                </div>
                <button type="submit" className="btn btn-primary">Create Trade</button>
            </form>
        </div>
    );
}

export default TradeForm;