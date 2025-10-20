import React from 'react';

function Dashboard({ dashboardData }) {
    if (!dashboardData) {
        return <div>Loading...</div>;
    }

    return (
        <div className="container mt-4">
            <h2 className="mb-4">Dashboard</h2>
            <div className="row">
                <div className="col-md-4">
                    <div className="card text-center">
                        <div className="card-body">
                            <h5 className="card-title">Total Premium Collected</h5>
                            <p className="card-text fs-4">${dashboardData.total_premium_collected.toFixed(2)}</p>
                        </div>
                    </div>
                </div>
                <div className="col-md-4">
                    <div className="card text-center">
                        <div className="card-body">
                            <h5 className="card-title">Total P&L</h5>
                            <p className={`card-text fs-4 ${dashboardData.total_pnl >= 0 ? 'text-success' : 'text-danger'}`}>
                                ${dashboardData.total_pnl.toFixed(2)}
                            </p>
                        </div>
                    </div>
                </div>
                <div className="col-md-4">
                    <div className="card text-center">
                        <div className="card-body">
                            <h5 className="card-title">Win Rate</h5>
                            <p className="card-text fs-4">{dashboardData.win_rate.toFixed(2)}%</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;