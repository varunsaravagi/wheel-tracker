import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { getTrades, closeTrade, assignTrade, rollTrade, getDashboardData, updateTrade, getCostBasis, expireTrade, getCumulativePnl } from './api';
import Dashboard from './Dashboard';
import TradeForm from './TradeForm';
import CloseTradeModal from './CloseTradeModal';
import RollTradeModal from './RollTradeModal';
import EditTradeModal from './EditTradeModal';
import './App.css';

function App() {
    return (
        <Router>
            <div className="App">
                <nav className="navbar navbar-expand-lg navbar-light bg-light">
                    <div className="container-fluid">
                        <Link className="navbar-brand" to="/">Options Wheel Tracker</Link>
                        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                            <span className="navbar-toggler-icon"></span>
                        </button>
                        <div className="collapse navbar-collapse" id="navbarNav">
                            <ul className="navbar-nav">
                                <li className="nav-item">
                                    <Link className="nav-link" to="/">Dashboard & Trades</Link>
                                </li>
                                <li className="nav-item">
                                    <Link className="nav-link" to="/new-trade">New Trade</Link>
                                </li>
                            </ul>
                        </div>
                    </div>
                </nav>

                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/new-trade" element={<NewTrade />} />
                </Routes>
            </div>
        </Router>
    );
}

function Home() {
    const [trades, setTrades] = useState([]);
    const [dashboardData, setDashboardData] = useState(null);
    const [costBasisData, setCostBasisData] = useState({});
    const [cumulativePnlData, setCumulativePnlData] = useState({});
    const [showCloseModal, setShowCloseModal] = useState(false);
    const [showRollModal, setShowRollModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [selectedTrade, setSelectedTrade] = useState(null);

    useEffect(() => {
        fetchTrades();
        fetchDashboardData();
    }, []);

    const fetchTrades = async () => {
        const response = await getTrades();
        setTrades(response.data);

        const sellCallTrades = response.data.filter(t => t.trade_type === 'Sell Call');
        const tickers = [...new Set(sellCallTrades.map(t => t.underlying_ticker))];
        
        const costBasisPromises = tickers.map(t => getCostBasis(t));
        const costBasisResults = await Promise.all(costBasisPromises);
        const costBasisMap = costBasisResults.reduce((acc, res, i) => {
            acc[tickers[i]] = res.data;
            return acc;
        }, {});
        setCostBasisData(costBasisMap);

        const cumulativePnlPromises = tickers.map(t => getCumulativePnl(t));
        const cumulativePnlResults = await Promise.all(cumulativePnlPromises);
        const cumulativePnlMap = cumulativePnlResults.reduce((acc, res, i) => {
            acc[tickers[i]] = res.data;
            return acc;
        }, {});
        setCumulativePnlData(cumulativePnlMap);
    };

    const fetchDashboardData = async () => {
        try {
            const response = await getDashboardData();
            setDashboardData(response.data);
        } catch (error) {
            console.error("Error fetching dashboard data:", error);
        }
    };

    const handleCloseTrade = async (tradeId, closeData) => {
        await closeTrade(tradeId, closeData);
        fetchTrades();
        fetchDashboardData();
        setShowCloseModal(false);
    };

    const handleAssignTrade = async (tradeId) => {
        await assignTrade(tradeId);
        fetchTrades();
    };

    const handleRollTrade = async (tradeId, rollData) => {
        await rollTrade(tradeId, rollData);
        fetchTrades();
        fetchDashboardData();
        setShowRollModal(false);
    };

    const handleUpdateTrade = async (tradeId, tradeData) => {
        await updateTrade(tradeId, tradeData);
        fetchTrades();
        fetchDashboardData();
        setShowEditModal(false);
    };

    const handleExpireTrade = async (tradeId) => {
        await expireTrade(tradeId);
        fetchTrades();
        fetchDashboardData();
    };

    const openCloseModal = (trade) => {
        setSelectedTrade(trade);
        setShowCloseModal(true);
    };

    const openRollModal = (trade) => {
        setSelectedTrade(trade);
        setShowRollModal(true);
    };

    const openEditModal = (trade) => {
        setSelectedTrade(trade);
        setShowEditModal(true);
    };

    const getTradeRowClass = (trade) => {
        if (trade.status === 'Closed' || trade.status === 'Expired') {
            return trade.net_premium_received >= 0 ? 'table-success' : 'table-danger';
        } else if (trade.status === 'Rolled') {
            return 'table-info';
        } else if (trade.status === 'Assigned') {
            return 'table-warning';
        }
        return '';
    };

    const sellPutTrades = trades.filter(t => t.trade_type === 'Sell Put');
    const sellCallTrades = trades.filter(t => t.trade_type === 'Sell Call');

    return (
        <>
            <Dashboard dashboardData={dashboardData} />
            <div className="container-fluid mt-4">
                <h2>Sell Puts</h2>
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Ticker</th>
                            <th>Expiration</th>
                            <th>Strike</th>
                            <th>Premium</th>
                            <th>Contracts</th>
                            <th>Transaction Date</th>
                            <th>Status</th>
                            <th>Net Premium</th>
                            <th>Days Held</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sellPutTrades.map(trade => {
                            const transactionDate = new Date(trade.transaction_date);
                            const buyBackDate = trade.buy_back_date ? new Date(trade.buy_back_date) : new Date();
                            const daysHeld = Math.ceil((buyBackDate - transactionDate) / (1000 * 60 * 60 * 24));

                            return (
                                <tr key={trade.id} className={getTradeRowClass(trade)}>
                                    <td>{trade.id}</td>
                                    <td>{trade.underlying_ticker}</td>
                                    <td>{trade.expiration_date}</td>
                                    <td>{trade.strike_price}</td>
                                    <td>{trade.premium_received}</td>
                                    <td>{trade.number_of_contracts}</td>
                                    <td>{trade.transaction_date}</td>
                                    <td>{trade.status}</td>
                                    <td>{trade.net_premium_received ? trade.net_premium_received.toFixed(2) : ''}</td>
                                    <td>{daysHeld}</td>
                                    <td>
                                        <button className="btn btn-sm btn-warning me-1" onClick={() => openEditModal(trade)}>Edit</button>
                                        {trade.status === 'Open' &&
                                            <>
                                                <button className="btn btn-sm btn-primary" onClick={() => openCloseModal(trade)}>Close</button>
                                                <button className="btn btn-sm btn-secondary" onClick={() => handleAssignTrade(trade.id)}>Assign</button>
                                                <button className="btn btn-sm btn-info" onClick={() => openRollModal(trade)}>Roll</button>
                                            </>
                                        }
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>

                <h2>Sell Calls</h2>
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Ticker</th>
                            <th>Expiration</th>
                            <th>Strike</th>
                            <th>Premium</th>
                            <th>Contracts</th>
                            <th>Transaction Date</th>
                            <th>Status</th>
                            <th>Original Cost Basis</th>
                            <th>Adjusted Cost Basis</th>
                            <th>Net Premium</th>
                            <th>Cumulative P&L</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sellCallTrades.map(trade => {
                            const basis = costBasisData[trade.underlying_ticker];
                            const originalCostBasis = basis ? basis.original_cost_basis.toFixed(2) : 'N/A';
                            const adjustedCostBasis = basis ? (basis.original_cost_basis - basis.cumulative_premium + basis.cumulative_fees_per_share).toFixed(2) : 'N/A';
                            const cumulativePnl = cumulativePnlData[trade.underlying_ticker] ? cumulativePnlData[trade.underlying_ticker].cumulative_pnl.toFixed(2) : 'N/A';

                            return (
                                <tr key={trade.id} className={getTradeRowClass(trade)}>
                                    <td>{trade.id}</td>
                                    <td>{trade.underlying_ticker}</td>
                                    <td>{trade.expiration_date}</td>
                                    <td>{trade.strike_price}</td>
                                    <td>{trade.premium_received}</td>
                                    <td>{trade.number_of_contracts}</td>
                                    <td>{trade.transaction_date}</td>
                                    <td>{trade.status}</td>
                                    <td>{originalCostBasis}</td>
                                    <td>{adjustedCostBasis}</td>
                                    <td>{trade.net_premium_received ? trade.net_premium_received.toFixed(2) : ''}</td>
                                    <td>{cumulativePnl}</td>
                                    <td>
                                        <button className="btn btn-sm btn-warning me-1" onClick={() => openEditModal(trade)}>Edit</button>
                                        {trade.status === 'Open' &&
                                            <>
                                                <button className="btn btn-sm btn-danger me-1" onClick={() => handleExpireTrade(trade.id)}>Expire</button>
                                                <button className="btn btn-sm btn-info" onClick={() => openRollModal(trade)}>Roll</button>
                                            </>
                                        }
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>

            {selectedTrade && (
                <>
                    <CloseTradeModal trade={selectedTrade} show={showCloseModal} onClose={() => setShowCloseModal(false)} onSave={handleCloseTrade} />
                    <RollTradeModal trade={selectedTrade} show={showRollModal} onClose={() => setShowRollModal(false)} onSave={handleRollTrade} />
                    <EditTradeModal trade={selectedTrade} show={showEditModal} onClose={() => setShowEditModal(false)} onSave={handleUpdateTrade} />
                </>
            )}
        </>
    );
}

function NewTrade() {
    const navigate = useNavigate();

    const handleTradeCreated = (newTrade) => {
        navigate('/');
    };

    return <TradeForm onTradeCreated={handleTradeCreated} />;
}

export default App;