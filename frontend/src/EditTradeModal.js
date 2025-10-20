import React, { useState, useEffect } from 'react';

function EditTradeModal({ trade, show, onClose, onSave }) {
    const [editedTrade, setEditedTrade] = useState(trade);

    useEffect(() => {
        setEditedTrade(trade);
    }, [trade]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setEditedTrade({ ...editedTrade, [name]: value });
    };

    const handleSave = () => {
        onSave(editedTrade.id, editedTrade);
    };

    if (!show) {
        return null;
    }

    return (
        <div className="modal show d-block" tabIndex="-1">
            <div className="modal-dialog">
                <div className="modal-content">
                    <div className="modal-header">
                        <h5 className="modal-title">Edit Trade: {editedTrade.underlying_ticker}</h5>
                        <button type="button" className="btn-close" onClick={onClose}></button>
                    </div>
                    <div className="modal-body">
                        <form>
                            <div className="row mb-3">
                                <div className="col">
                                    <label htmlFor="underlying_ticker" className="form-label">Ticker</label>
                                    <input type="text" className="form-control" id="underlying_ticker" name="underlying_ticker" value={editedTrade.underlying_ticker} onChange={handleChange} required autoFocus />
                                </div>
                                <div className="col">
                                    <label htmlFor="trade_type" className="form-label">Trade Type</label>
                                    <select className="form-select" id="trade_type" name="trade_type" value={editedTrade.trade_type} onChange={handleChange}>
                                        <option>Sell Put</option>
                                        <option>Sell Call</option>
                                    </select>
                                </div>
                            </div>
                            <div className="row mb-3">
                                <div className="col">
                                    <label htmlFor="strike_price" className="form-label">Strike</label>
                                    <input type="number" className="form-control" id="strike_price" name="strike_price" value={editedTrade.strike_price} onChange={handleChange} required />
                                </div>
                                <div className="col">
                                    <label htmlFor="premium_received" className="form-label">Premium</label>
                                    <input type="number" step="0.01" className="form-control" id="premium_received" name="premium_received" value={editedTrade.premium_received} onChange={handleChange} required />
                                </div>
                                <div className_="col">
                                    <label htmlFor="number_of_contracts" className="form-label">Quantity</label>
                                    <input type="number" className="form-control" id="number_of_contracts" name="number_of_contracts" value={editedTrade.number_of_contracts} onChange={handleChange} required />
                                </div>
                            </div>
                            <div className="row mb-3">
                                <div className="col">
                                    <label htmlFor="transaction_date" className="form-label">Trade Date</label>
                                    <input type="date" className="form-control" id="transaction_date" name="transaction_date" value={editedTrade.transaction_date} onChange={handleChange} required />
                                </div>
                                <div className="col">
                                    <label htmlFor="expiration_date" className="form-label">Expiration Date</label>
                                    <input type="date" className="form-control" id="expiration_date" name="expiration_date" value={editedTrade.expiration_date} onChange={handleChange} required />
                                </div>
                                <div className="col">
                                    <label htmlFor="fees" className="form-label">Fees/Commission</label>
                                    <input type="number" step="0.01" className="form-control" id="fees" name="fees" value={editedTrade.fees} onChange={handleChange} required />
                                </div>
                            </div>
                        </form>
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

export default EditTradeModal;
