import React, { useState } from 'react';

function RollTradeModal({ trade, show, onClose, onSave }) {
    const [rollData, setRollData] = useState({
        new_expiration_date: '',
        strike_price: '',
        premium_received: '',
        fees: '0.66',
        closing_fees: '0.66',
        roll_date: new Date().toISOString().slice(0, 10)
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setRollData({ ...rollData, [name]: value });
    };

    const handleSave = () => {
        onSave(trade.id, rollData);
    };

    if (!show) {
        return null;
    }

    return (
        <div className="modal show d-block" tabIndex="-1">
            <div className="modal-dialog">
                <div className="modal-content">
                    <div className="modal-header">
                        <h5 className="modal-title">Roll Trade: {trade.underlying_ticker}</h5>
                        <button type="button" className="btn-close" onClick={onClose}></button>
                    </div>
                    <div className="modal-body">
                        <div className="mb-3">
                            <label htmlFor="new_expiration_date" className="form-label">New Expiration Date</label>
                            <input type="date" className="form-control" id="new_expiration_date" name="new_expiration_date" value={rollData.new_expiration_date} onChange={handleChange} autoFocus />
                        </div>
                        <div className="mb-3">
                            <label htmlFor="strike_price" className="form-label">New Strike Price</label>
                            <input type="number" className="form-control" id="strike_price" name="strike_price" value={rollData.strike_price} onChange={handleChange} />
                        </div>
                        <div className="mb-3">
                            <label htmlFor="premium_received" className="form-label">New Premium Received</label>
                            <input type="number" step="0.01" className="form-control" id="premium_received" name="premium_received" value={rollData.premium_received} onChange={handleChange} />
                        </div>
                        <div className="mb-3">
                            <label htmlFor="fees" className="form-label">New Fees</label>
                            <input type="number" step="0.01" className="form-control" id="fees" name="fees" value={rollData.fees} onChange={handleChange} />
                        </div>
                        <div className="mb-3">
                            <label htmlFor="closing_fees" className="form-label">Closing Fees (Old Trade)</label>
                            <input type="number" step="0.01" className="form-control" id="closing_fees" name="closing_fees" value={rollData.closing_fees} onChange={handleChange} />
                        </div>
                        <div className="mb-3">
                            <label htmlFor="roll_date" className="form-label">Roll Date</label>
                            <input type="date" className="form-control" id="roll_date" name="roll_date" value={rollData.roll_date} onChange={handleChange} />
                        </div>
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-secondary" onClick={onClose}>Close</button>
                        <button type="button" className="btn btn-primary" onClick={handleSave}>Save changes</button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default RollTradeModal;