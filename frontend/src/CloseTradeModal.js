import React, { useState } from 'react';

function CloseTradeModal({ trade, show, onClose, onSave }) {
    const [buyBackPrice, setBuyBackPrice] = useState('');
    const [closingFees, setClosingFees] = useState('0.66');
    const [buyBackDate, setBuyBackDate] = useState(new Date().toISOString().slice(0, 10));

    const handleSave = () => {
        onSave(trade.id, {
            buy_back_price: buyBackPrice,
            closing_fees: closingFees,
            buy_back_date: buyBackDate
        });
    };

    if (!show) {
        return null;
    }

    return (
        <div className="modal show d-block" tabIndex="-1">
            <div className="modal-dialog">
                <div className="modal-content">
                    <div className="modal-header">
                        <h5 className="modal-title">Close Trade: {trade.underlying_ticker}</h5>
                        <button type="button" className="btn-close" onClick={onClose}></button>
                    </div>
                    <div className="modal-body">
                        <div className="mb-3">
                            <label htmlFor="buyBackPrice" className="form-label">Buy Back Price</label>
                            <input type="number" step="0.01" className="form-control" id="buyBackPrice" value={buyBackPrice} onChange={(e) => setBuyBackPrice(e.target.value)} autoFocus />
                        </div>
                        <div className="mb-3">
                            <label htmlFor="closingFees" className="form-label">Closing Fees</label>
                            <input type="number" step="0.01" className="form-control" id="closingFees" value={closingFees} onChange={(e) => setClosingFees(e.target.value)} />
                        </div>
                        <div className="mb-3">
                            <label htmlFor="buyBackDate" className="form-label">Close Date</label>
                            <input type="date" className="form-control" id="buyBackDate" value={buyBackDate} onChange={(e) => setBuyBackDate(e.target.value)} />
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

export default CloseTradeModal;