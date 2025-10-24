import axios from 'axios';

const API_URL = 'http://192.168.6.44:8000/api';

export const getTrades = async () => {
    return await axios.get(`${API_URL}/trades/`);
};

export const createTrade = async (trade) => {
    return await axios.post(`${API_URL}/trades/`, trade);
};

export const closeTrade = async (tradeId, closeData) => {
    return await axios.put(`${API_URL}/trades/${tradeId}/close`, closeData);
};

export const assignTrade = async (tradeId) => {
    return await axios.put(`${API_URL}/trades/${tradeId}/assign`);
};

export const rollTrade = async (tradeId, rollData) => {
    return await axios.post(`${API_URL}/trades/${tradeId}/roll`, rollData);
};

export const updateTrade = async (tradeId, tradeData) => {
    return await axios.put(`${API_URL}/trades/${tradeId}`, tradeData);
};

export const getCostBasis = async (ticker) => {
    return await axios.get(`${API_URL}/cost_basis/${ticker}`);
};

export const expireTrade = async (tradeId) => {
    return await axios.put(`${API_URL}/trades/${tradeId}/expire`);
};

export const getCumulativePnl = async (ticker) => {
    return await axios.get(`${API_URL}/cumulative_pnl/${ticker}`);
};

export const getDashboardData = async () => {
    return await axios.get(`${API_URL}/dashboard/`);
};