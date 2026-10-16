import React, { useEffect, useState } from "react";
import axios from "axios";
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    PieChart,
    Pie,
    Cell,
    Legend,
    LineChart,
    Line,
    Area
} from "recharts";
import "./App.css";

const API_URL = "http://localhost:8000";

const CHART_COLORS = ["#2563eb", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"];

function App() {
    const [formData, setFormData] = useState({
        step: 1,
        type: "TRANSFER",
        amount: 1000,
        oldbalanceOrg: 5000,
        newbalanceOrig: 4000,
        oldbalanceDest: 2000,
        newbalanceDest: 3000
    });

    const [result, setResult] = useState(null);
    const [activeTab, setActiveTab] = useState("Dashboard");
    const [transactions, setTransactions] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [unreadAlertCount, setUnreadAlertCount] = useState(0);
    const [loadingTransactions, setLoadingTransactions] = useState(false);
    const [loadingAlerts, setLoadingAlerts] = useState(false);
    const [loading, setLoading] = useState(false);
    const [apiError, setApiError] = useState("");

    const [summary, setSummary] = useState({
        total_predictions: 0,
        fraud_predictions: 0,
        legitimate_predictions: 0,
        fraud_rate: 0
    });
    const [reportMetrics, setReportMetrics] = useState({
        threshold: 0.9,
        precision: 0,
        recall: 0,
        f1_score: 0
    });
    const [selectedTransactionIds, setSelectedTransactionIds] = useState([]);

    const loadUnreadAlertCount = async () => {
        try {
            const response = await axios.get(`${API_URL}/alerts/unread-count`);
            setUnreadAlertCount(Number(response.data.unread_alerts || 0));
            return Number(response.data.unread_alerts || 0);
        } catch (error) {
            console.error("Unread count error:", error);
            setUnreadAlertCount(0);
            return 0;
        }
    };

    const loadTransactions = async () => {
        setLoadingTransactions(true);

        try {
            const response = await axios.get(`${API_URL}/transactions`);
            setTransactions(response.data);
            return response.data;
        } catch (error) {
            console.error("Transactions error:", error);
            setApiError("Unable to load transactions. Check the backend.");
            return [];
        } finally {
            setLoadingTransactions(false);
        }
    };

    const loadAlerts = async () => {
        setLoadingAlerts(true);

        try {
            const response = await axios.get(`${API_URL}/alerts`);
            setAlerts(response.data);
            setApiError("");
            await loadUnreadAlertCount();
            return response.data;
        } catch (error) {
            console.error("Alerts error:", error);
            setApiError("Unable to load alerts. Check the backend.");
            return [];
        } finally {
            setLoadingAlerts(false);
        }
    };

    const loadSummary = async () => {
        try {
            const response = await axios.get(`${API_URL}/reports`);
            const reportData = response.data || {};
            const nextSummary = reportData.summary || reportData;
            setSummary(nextSummary);
            setReportMetrics(reportData.model_metrics || {
                threshold: 0.9,
                precision: 0,
                recall: 0,
                f1_score: 0
            });
            setApiError("");
        } catch (error) {
            console.error("Summary error:", error);
            try {
                const fallbackResponse = await axios.get(`${API_URL}/monitoring`);
                setSummary(fallbackResponse.data);
                setReportMetrics({
                    threshold: 0.9,
                    precision: 0,
                    recall: 0,
                    f1_score: 0
                });
                setApiError("");
            } catch (fallbackError) {
                console.error("Fallback summary error:", fallbackError);
                setApiError("Unable to connect to the backend API.");
            }
        }
    };

    const markAlertAsRead = async (alertId) => {
        try {
            await axios.patch(`${API_URL}/alerts/${alertId}/read`);
            await loadAlerts();
            await loadUnreadAlertCount();
        } catch (error) {
            console.error("Mark alert as read error:", error);
            setApiError("Unable to update alert status.");
        }
    };

    const deleteAlert = async (alertId) => {
        const confirmed = window.confirm("Delete this alert?");
        if (!confirmed) {
            return;
        }

        try {
            await axios.delete(`${API_URL}/alerts/${alertId}`);
            setAlerts((previous) =>
                previous.filter((alert) => alert.id !== alertId)
            );
            await loadUnreadAlertCount();
            setApiError("");
        } catch (error) {
            console.error("Delete alert error:", error);
            setApiError("Unable to delete the alert.");
        }
    };

    const deleteTransaction = async (transactionId) => {
        const confirmed = window.confirm(
            "Are you sure you want to delete this transaction?"
        );
        if (!confirmed) {
            return;
        }

        try {
            await axios.delete(`${API_URL}/transactions/${transactionId}`);
            await loadTransactions();
            await loadSummary();
            await loadAlerts();
            await loadUnreadAlertCount();
            setApiError("");
        } catch (error) {
            console.error("Delete transaction error:", error);
            const detail =
                error.response?.data?.detail ||
                error.response?.data?.message ||
                error.message ||
                "Unable to delete the transaction.";
            setApiError(`Unable to delete the transaction: ${detail}`);
        }
    };

    const toggleTransactionSelection = (transactionId) => {
        setSelectedTransactionIds((previous) =>
            previous.includes(transactionId)
                ? previous.filter((id) => id !== transactionId)
                : [...previous, transactionId]
        );
    };

    const deleteSelectedTransactions = async () => {
        if (selectedTransactionIds.length === 0) {
            return;
        }

        const confirmed = window.confirm(
            `Delete ${selectedTransactionIds.length} selected transaction(s)?`
        );
        if (!confirmed) {
            return;
        }

        try {
            await axios.delete(`${API_URL}/transactions/selected`, {
                data: { transaction_ids: selectedTransactionIds }
            });
            setSelectedTransactionIds([]);
            await loadTransactions();
            await loadSummary();
            await loadAlerts();
            await loadUnreadAlertCount();
            setApiError("");
        } catch (error) {
            console.error("Delete selected transactions error:", error);
            const detail =
                error.response?.data?.detail ||
                error.response?.data?.message ||
                error.message ||
                "Unable to delete the selected transactions.";
            setApiError(`Unable to delete the selected transactions: ${detail}`);
        }
    };

    useEffect(() => {
        loadSummary();
        loadTransactions();
        loadAlerts();
    }, [activeTab]);

    const handleChange = (event) => {
        const { name, value } = event.target;

        setFormData((previous) => ({
            ...previous,
            [name]: value
        }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        setApiError("");

        try {
            const payload = {
                ...formData,
                step: Number(formData.step),
                amount: Number(formData.amount),
                oldbalanceOrg: Number(formData.oldbalanceOrg),
                newbalanceOrig: Number(formData.newbalanceOrig),
                oldbalanceDest: Number(formData.oldbalanceDest),
                newbalanceDest: Number(formData.newbalanceDest)
            };

            const response = await axios.post(
                `${API_URL}/predict`,
                payload
            );

            setResult(response.data);

            await loadTransactions();
            await loadSummary();
            await loadAlerts();
        } catch (error) {
            console.error("Prediction error:", error);

            const detail = error.response?.data?.detail;

            setResult({
                error: Array.isArray(detail)
                    ? detail.map((item) => item.msg).join(", ")
                    : detail || "Unable to connect to the Fraud Detection API."
            });
        } finally {
            setLoading(false);
        }
    };

    const navigateTo = (tab) => {
        setActiveTab(tab);
        setApiError("");
    };

    const formatAmount = (amount) =>
        Number(amount || 0).toLocaleString("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 2
        });

    const formatDate = (date) => {
        if (!date) return "—";
        return new Date(date).toLocaleString("en-IN");
    };

    const latestTransaction = transactions[0] || null;
    const latestAlert = alerts[0] || null;
    const currentThreshold = Number(result?.threshold ?? latestTransaction?.threshold ?? 0.9);

    const latestTransactionSummary = (() => {
        if (result && !result.error) {
            return {
                amount: Number(formData.amount || 0),
                type: formData.type || "—",
                oldbalanceOrg: Number(formData.oldbalanceOrg || 0),
                oldbalanceDest: Number(formData.oldbalanceDest || 0),
                newbalanceOrig: Number(formData.newbalanceOrig || 0),
                newbalanceDest: Number(formData.newbalanceDest || 0)
            };
        }

        if (!latestTransaction) {
            return null;
        }

        return {
            amount: Number(latestTransaction.amount || 0),
            type: latestTransaction.type || "—",
            oldbalanceOrg: Number(latestTransaction.oldbalanceOrg || 0),
            oldbalanceDest: Number(latestTransaction.oldbalanceDest || 0),
            newbalanceOrig: Number(latestTransaction.newbalanceOrig || 0),
            newbalanceDest: Number(latestTransaction.newbalanceDest || 0)
        };
    })();

    const fraudTransactions = transactions.filter(
        (item) => item.prediction === "Fraud"
    );

    const highRiskTransactions = transactions.filter(
        (item) =>
            Number(item.fraud_probability) >= 0.5 &&
            item.prediction !== "Fraud"
    );

    const hasFraudAlert = alerts.some(
        (alert) => alert.status === "Unread" || alert.severity === "High"
    );

    const fraudChartData = [
        {
            name: "Legitimate",
            count: Number(summary.legitimate_predictions || 0)
        },
        {
            name: "Fraud",
            count: Number(summary.fraud_predictions || 0)
        }
    ];

    const transactionTypeData = Object.entries(
        transactions.reduce((counts, item) => {
            const type = item.type || "Unknown";
            counts[type] = (counts[type] || 0) + 1;
            return counts;
        }, {})
    ).map(([name, value]) => ({ name, value }));

    const fraudByTypeData = Object.entries(
        transactions.reduce((counts, item) => {
            const isFraud = String(item.prediction || "").toLowerCase() === "fraud";
            if (!isFraud) {
                return counts;
            }

            const type = item.type || "Unknown";
            counts[type] = (counts[type] || 0) + 1;
            return counts;
        }, {})
    )
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value);

    const fraudTrendData = [...transactions]
        .filter(
            (item) =>
                item.created_at &&
                Number.isFinite(Number(item.fraud_probability)) &&
                Number(item.fraud_probability) >= 0
        )
        .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
        .map((item) => ({
            id: item.id,
            timestamp: item.created_at,
            probability: Number(item.fraud_probability) * 100,
            prediction: item.prediction,
            label: new Date(item.created_at).toLocaleString("en-IN")
        }));

    const highestObservedProbability = fraudTrendData.length
        ? Math.max(...fraudTrendData.map((item) => Number(item.probability || 0)))
        : 0;

    const rawFraudRate = Number(summary.fraud_rate || 0);
    const fraudRatePercent =
        rawFraudRate <= 1 ? rawFraudRate * 100 : rawFraudRate;

    const reportThresholdValue = Number(reportMetrics.threshold || 0.9);
    const modelMetricsCards = [
        {
            key: "precision",
            label: "Precision",
            value: `${(Number(reportMetrics.precision || 0) * 100).toFixed(2)}%`,
            icon: "◎",
            description: "Share of flagged fraud cases that were actually fraudulent."
        },
        {
            key: "recall",
            label: "Recall",
            value: `${(Number(reportMetrics.recall || 0) * 100).toFixed(2)}%`,
            icon: "↗",
            description: "Share of actual fraud cases successfully identified."
        },
        {
            key: "f1_score",
            label: "F1-Score",
            value: `${(Number(reportMetrics.f1_score || 0) * 100).toFixed(2)}%`,
            icon: "◌",
            description: "Balanced measure combining precision and recall."
        },
        {
            key: "threshold",
            label: "Detection Threshold",
            value: `${reportThresholdValue.toFixed(2)} (${(reportThresholdValue * 100).toFixed(0)}%)`,
            icon: "⚑",
            description: "Decision cutoff used to classify a transaction as fraud."
        }
    ];

    const downloadReport = () => {
        const rows = [
            ["section", "value"],
            ["total_predictions", Number(summary.total_predictions || 0)],
            ["fraud_predictions", Number(summary.fraud_predictions || 0)],
            ["legitimate_predictions", Number(summary.legitimate_predictions || 0)],
            ["fraud_rate_percent", Number(fraudRatePercent.toFixed(2))],
            ["model_threshold", Number(reportMetrics.threshold || 0.9)],
            ["precision", Number(reportMetrics.precision || 0)],
            ["recall", Number(reportMetrics.recall || 0)],
            ["f1_score", Number(reportMetrics.f1_score || 0)],
            ["transactions_exported", transactions.length]
        ];

        const csvContent = rows
            .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","))
            .join("\n");

        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "fraud_detection_report.csv";
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    };

    const renderTransactionsTable = (items) => {
        if (items.length === 0) {
            return (
                <div className="empty-state">
                    <div className="empty-icon">📋</div>
                    <h3>No transactions found</h3>
                    <p>Saved predictions will appear here.</p>
                </div>
            );
        }

        return (
            <div style={{ overflowX: "auto" }}>
                <table
                    style={{
                        width: "100%",
                        borderCollapse: "collapse",
                        textAlign: "left"
                    }}
                >
                    <thead>
                        <tr>
                            {[
                                "Select",
                                "ID",
                                "Type",
                                "Amount",
                                "Prediction",
                                "Fraud Probability",
                                "Date",
                                "Action"
                            ].map((heading) => (
                                <th
                                    key={heading}
                                    style={{
                                        padding: "13px 10px",
                                        borderBottom: "1px solid #e5e7eb",
                                        whiteSpace: "nowrap"
                                    }}
                                >
                                    {heading}
                                </th>
                            ))}
                        </tr>
                    </thead>

                    <tbody>
                        {items.map((item) => (
                            <tr key={item.id}>
                                <td style={{ padding: "13px 10px" }}>
                                    <input
                                        type="checkbox"
                                        checked={selectedTransactionIds.includes(item.id)}
                                        onChange={() => toggleTransactionSelection(item.id)}
                                        aria-label={`Select transaction ${item.id}`}
                                    />
                                </td>
                                <td style={{ padding: "13px 10px" }}>
                                    {item.id}
                                </td>
                                <td style={{ padding: "13px 10px" }}>
                                    {item.type}
                                </td>
                                <td style={{ padding: "13px 10px" }}>
                                    {formatAmount(item.amount)}
                                </td>
                                <td style={{ padding: "13px 10px" }}>
                                    <span
                                        style={{
                                            color:
                                                item.prediction === "Fraud"
                                                    ? "#dc2626"
                                                    : "#15803d",
                                            fontWeight: 600
                                        }}
                                    >
                                        {item.prediction}
                                    </span>
                                </td>
                                <td style={{ padding: "13px 10px" }}>
                                    {(Number(item.fraud_probability) * 100).toFixed(2)}%
                                </td>
                                <td
                                    style={{
                                        padding: "13px 10px",
                                        whiteSpace: "nowrap"
                                    }}
                                >
                                    {formatDate(item.created_at)}
                                </td>
                                <td style={{ padding: "13px 10px" }}>
                                    <button
                                        type="button"
                                        className="danger-button"
                                        onClick={() => deleteTransaction(item.id)}
                                        style={{ padding: "8px 12px", fontSize: "12px" }}
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };

    const renderSummaryCards = () => (
        <section className="summary-grid">
            <div className="stat-card">
                <div className="stat-icon blue">↗</div>
                <div>
                    <span>Total Predictions</span>
                    <h3>
                        {Number(summary.total_predictions || 0).toLocaleString("en-IN")}
                    </h3>
                </div>
            </div>

            <div className="stat-card">
                <div className="stat-icon red">⚠</div>
                <div>
                    <span>Fraud Detected</span>
                    <h3>
                        {Number(summary.fraud_predictions || 0).toLocaleString("en-IN")}
                    </h3>
                </div>
            </div>

            <div className="stat-card">
                <div className="stat-icon green">✓</div>
                <div>
                    <span>Legitimate</span>
                    <h3>
                        {Number(summary.legitimate_predictions || 0).toLocaleString("en-IN")}
                    </h3>
                </div>
            </div>

            <div className="stat-card">
                <div className="stat-icon purple">◎</div>
                <div>
                    <span>Detection Threshold</span>
                    <h3>0.90</h3>
                </div>
            </div>
        </section>
    );

    return (
        <div className="dashboard-shell">
            <aside className="sidebar">
                <div className="brand">
                    <div className="brand-icon">🛡️</div>
                    <div>
                        <h2>Fraud Suite</h2>
                        <span>Detection System</span>
                    </div>
                </div>

                <nav className="sidebar-nav">
                    {[
                        { name: "Dashboard", icon: "▣" },
                        { name: "Transactions", icon: "▤" },
                        { name: "Alerts", icon: "⚠" },
                        { name: "Reports", icon: "▥" }
                    ].map((item) => (
                        <div
                            key={item.name}
                            className={`nav-item ${
                                activeTab === item.name ? "active" : ""
                            }`}
                            role="button"
                            tabIndex={0}
                            onClick={() => navigateTo(item.name)}
                            onKeyDown={(event) => {
                                if (
                                    event.key === "Enter" ||
                                    event.key === " "
                                ) {
                                    navigateTo(item.name);
                                }
                            }}
                        >
                            <span>{item.icon}</span>
                            <span>{item.name}</span>
                            {item.name === "Alerts" && unreadAlertCount > 0 && (
                                <span className="nav-alert-badge" aria-label={`${unreadAlertCount} unread alerts`}>
                                    {unreadAlertCount}
                                </span>
                            )}
                        </div>
                    ))}
                </nav>

                <div className="sidebar-footer">
                    <div className="system-dot"></div>
                    <div>
                        <strong>System Online</strong>
                        <small>ML Model Active</small>
                    </div>
                </div>
            </aside>

            <main className="main-panel">
                <header className="topbar">
                    <div>
                        <p className="breadcrumb">
                            {activeTab} / Fraud Detection
                        </p>
                        <h1>
                            {activeTab === "Dashboard"
                                ? "Fraud Detection Dashboard"
                                : activeTab === "Reports"
                                ? "Fraud Detection Reports"
                                : activeTab}
                        </h1>
                        <p className="subtitle">
                            {activeTab === "Dashboard"
                                ? "Monitor and analyze suspicious transactions."
                                : activeTab === "Transactions"
                                ? "View all saved transaction predictions."
                                : activeTab === "Alerts"
                                ? "Review fraud predictions and high-risk transactions."
                                : "Monitor transaction predictions and model performance."}
                        </p>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                        {activeTab === "Reports" && (
                            <button
                                className="primary-button"
                                type="button"
                                onClick={async () => {
                                    await loadSummary();
                                    await loadTransactions();
                                }}
                            >
                                Refresh
                            </button>
                        )}
                        <div className="status-pill">
                            <span></span>
                            System Active
                        </div>
                    </div>
                </header>

                {apiError && (
                    <div
                        className="result error"
                        style={{ marginBottom: "20px", padding: "16px" }}
                    >
                        {apiError}
                    </div>
                )}

                {renderSummaryCards()}

                {activeTab === "Dashboard" && (
                    <section className="content-grid">
                        <div className="panel form-panel">
                            <div className="panel-header">
                                <div>
                                    <h2>Transaction Analysis</h2>
                                    <p>Enter transaction details to predict fraud risk.</p>
                                </div>
                                <div className="model-badge">Random Forest</div>
                            </div>

                            <form
                                className="prediction-form"
                                onSubmit={handleSubmit}
                            >
                                <div className="form-row">
                                    <div className="input-group">
                                        <label>Step</label>
                                        <input
                                            type="number"
                                            name="step"
                                            min="1"
                                            required
                                            value={formData.step}
                                            onChange={handleChange}
                                        />
                                    </div>

                                    <div className="input-group">
                                        <label>Transaction Type</label>
                                        <select
                                            name="type"
                                            value={formData.type}
                                            onChange={handleChange}
                                        >
                                            <option value="PAYMENT">PAYMENT</option>
                                            <option value="TRANSFER">TRANSFER</option>
                                            <option value="CASH_OUT">CASH_OUT</option>
                                            <option value="DEBIT">DEBIT</option>
                                            <option value="CASH_IN">CASH_IN</option>
                                        </select>
                                    </div>
                                </div>

                                {[
                                    ["amount", "Transaction Amount"],
                                    ["oldbalanceOrg", "Old Balance (Origin)"],
                                    ["newbalanceOrig", "New Balance (Origin)"],
                                    ["oldbalanceDest", "Old Balance (Destination)"],
                                    ["newbalanceDest", "New Balance (Destination)"]
                                ].map(([name, label]) => (
                                    <div className="input-group" key={name}>
                                        <label>{label}</label>
                                        <input
                                            type="number"
                                            name={name}
                                            min="0"
                                            required
                                            value={formData[name]}
                                            onChange={handleChange}
                                        />
                                    </div>
                                ))}

                                <button
                                    type="submit"
                                    className="primary-button"
                                    disabled={loading}
                                >
                                    {loading ? "Analyzing..." : "🔍 Analyze Transaction"}
                                </button>
                            </form>
                        </div>

                        <div className="panel result-panel">
                            <div className="panel-header">
                                <div>
                                    <h2>Prediction Result</h2>
                                    <p>Latest transaction analysis</p>
                                </div>
                            </div>

                            {!result && (
                                <div className="empty-state">
                                    <div className="empty-icon">🛡️</div>
                                    <h3>Ready for Analysis</h3>
                                    <p>
                                        Enter transaction details and click Analyze Transaction.
                                    </p>
                                </div>
                            )}

                            {result?.error && (
                                <div className="result error">
                                    <div className="result-icon">!</div>
                                    <h3>Prediction Error</h3>
                                    <p>{result.error}</p>
                                </div>
                            )}

                            {result && !result.error && (
                                <div className="result-stack">
                                    <div
                                        className={
                                            result.prediction === "Fraud"
                                                ? "result fraud compact-result"
                                                : "result legitimate compact-result"
                                        }
                                    >
                                        <div className="result-header-row">
                                            <div className="result-icon">
                                                {result.prediction === "Fraud" ? "⚠" : "✓"}
                                            </div>
                                            <div>
                                                <span className="result-label">Transaction Status</span>
                                                <h3>{result.prediction}</h3>
                                            </div>
                                        </div>

                                        <div className="probability-box">
                                            <div>
                                                <span>Fraud probability</span>
                                                <strong>
                                                    {(Number(result.fraud_probability || 0) * 100).toFixed(2)}%
                                                </strong>
                                            </div>
                                            <div>
                                                <span>Threshold</span>
                                                <strong>{Number(currentThreshold || 0.9).toFixed(2)} ({(Number(currentThreshold || 0.9) * 100).toFixed(0)}%)</strong>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="summary-card">
                                        <div className="mini-card-header">
                                            <h4>Transaction Summary</h4>
                                        </div>
                                        {latestTransactionSummary ? (
                                            <div className="summary-grid-compact">
                                                <div>
                                                    <span>Amount</span>
                                                    <strong>{formatAmount(latestTransactionSummary.amount)}</strong>
                                                </div>
                                                <div>
                                                    <span>Type</span>
                                                    <strong>{latestTransactionSummary.type}</strong>
                                                </div>
                                                <div>
                                                    <span>Origin Balance</span>
                                                    <strong>{formatAmount(latestTransactionSummary.oldbalanceOrg)}</strong>
                                                </div>
                                                <div>
                                                    <span>Destination Balance</span>
                                                    <strong>{formatAmount(latestTransactionSummary.oldbalanceDest)}</strong>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="empty-inline">
                                                <p>No transaction summary available.</p>
                                            </div>
                                        )}
                                    </div>

                                    <div className="summary-card">
                                        <div className="mini-card-header">
                                            <h4>Latest Alert Status</h4>
                                        </div>
                                        {latestAlert ? (
                                            <div className="alert-inline-status">
                                                <span className={`status-pill-inline ${latestAlert.status === "Unread" ? "unread" : "read"}`}>
                                                    {latestAlert.status}
                                                </span>
                                                <strong>{latestAlert.severity}</strong>
                                                <p>{latestAlert.message}</p>
                                            </div>
                                        ) : (
                                            <div className="empty-inline">
                                                <p>No alert data available.</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    </section>
                )}

                {activeTab === "Transactions" && (
                    <section className="panel" style={{ padding: "24px" }}>
                        <div className="panel-header">
                            <div>
                                <h2>Transaction History</h2>
                                <p>{transactions.length} saved prediction(s)</p>
                            </div>
                            <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
                                <button
                                    className="primary-button"
                                    type="button"
                                    onClick={loadTransactions}
                                    disabled={loadingTransactions}
                                >
                                    {loadingTransactions ? "Refreshing..." : "Refresh"}
                                </button>
                                <button
                                    className="danger-button"
                                    type="button"
                                    onClick={deleteSelectedTransactions}
                                    disabled={selectedTransactionIds.length === 0 || loadingTransactions}
                                >
                                    Delete Selected
                                </button>
                            </div>
                        </div>

                        {loadingTransactions ? (
                            <p>Loading transactions...</p>
                        ) : (
                            renderTransactionsTable(transactions)
                        )}
                    </section>
                )}

                {activeTab === "Alerts" && (
                    <section style={{ display: "grid", gap: "24px" }}>
                        <div className="panel" style={{ padding: "24px" }}>
                            <div className="panel-header">
                                <div>
                                    <h2>Security Alerts Center</h2>
                                    <p>
                                        Review fraud alerts and persistent security events.
                                    </p>
                                </div>

                                <button
                                    className="primary-button"
                                    type="button"
                                    onClick={loadAlerts}
                                    disabled={loadingAlerts}
                                >
                                    {loadingAlerts ? "Refreshing..." : "↻ Refresh Alerts"}
                                </button>
                            </div>

                            <div className="summary-grid">
                                <div className="stat-card">
                                    <div className="stat-icon red">⚠</div>
                                    <div>
                                        <span>Unread Alerts</span>
                                        <h3>{unreadAlertCount}</h3>
                                    </div>
                                </div>

                                <div className="stat-card">
                                    <div className="stat-icon purple">◎</div>
                                    <div>
                                        <span>Total Alerts</span>
                                        <h3>{alerts.length}</h3>
                                    </div>
                                </div>

                                <div className="stat-card">
                                    <div className="stat-icon blue">▤</div>
                                    <div>
                                        <span>Transactions Checked</span>
                                        <h3>{transactions.length}</h3>
                                    </div>
                                </div>

                                <div className="stat-card">
                                    <div className="stat-icon green">✓</div>
                                    <div>
                                        <span>Alert Status</span>
                                        <h3 style={{ fontSize: "17px" }}>
                                            {unreadAlertCount > 0 ? "Review Needed" : "No Fraud Alerts"}
                                        </h3>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="panel" style={{ padding: "24px" }}>
                            <div className="panel-header">
                                <div>
                                    <h2>Alert History</h2>
                                    <p>
                                        {unreadAlertCount} unread alert(s) need attention.
                                    </p>
                                </div>
                            </div>

                            {loadingAlerts ? (
                                <p>Loading alerts...</p>
                            ) : alerts.length === 0 ? (
                                <div className="empty-state">
                                    <div className="empty-icon">📋</div>
                                    <h3>No alerts found</h3>
                                    <p>
                                        Fraud alerts appear here when the backend classifies a transaction as potentially fraudulent.
                                    </p>
                                </div>
                            ) : (
                                <div className="alert-list">
                                    {alerts.map((alert) => (
                                        <div
                                            key={alert.id}
                                            className={`alert-card ${
                                                alert.status === "Unread" ? "unread" : "read"
                                            }`}
                                        >
                                            <div className="alert-header">
                                                <div>
                                                    <span className="alert-title">Alert #{alert.id}</span>
                                                    <p>Transaction #{alert.transaction_id}</p>
                                                </div>
                                                <span
                                                    className="severity-pill"
                                                    style={{
                                                        background:
                                                            alert.severity === "Critical"
                                                                ? "#fee2e2"
                                                                : alert.severity === "High"
                                                                ? "#fef3c7"
                                                                : "#dcfce7",
                                                        color:
                                                            alert.severity === "Critical"
                                                                ? "#b91c1c"
                                                                : alert.severity === "High"
                                                                ? "#b45309"
                                                                : "#15803d"
                                                    }}
                                                >
                                                    {alert.severity}
                                                </span>
                                            </div>

                                            <div className="alert-message">
                                                ⚠️ Fraud Alert: This transaction has been classified as potentially fraudulent. Please verify it immediately.
                                            </div>

                                            <div className="alert-metadata">
                                                <div>
                                                    <span>Date & Time</span>
                                                    <strong>{formatDate(alert.created_at)}</strong>
                                                </div>
                                                <div>
                                                    <span>Amount</span>
                                                    <strong>{formatAmount(alert.amount)}</strong>
                                                </div>
                                                <div>
                                                    <span>Type</span>
                                                    <strong>{alert.transaction_type}</strong>
                                                </div>
                                                <div>
                                                    <span>Risk</span>
                                                    <strong>{(Number(alert.fraud_probability) * 100).toFixed(2)}%</strong>
                                                </div>
                                                <div>
                                                    <span>Status</span>
                                                    <strong>{alert.status}</strong>
                                                </div>
                                            </div>

                                            <div className="alert-actions">
                                                <button
                                                    type="button"
                                                    className="secondary-button"
                                                    onClick={() => markAlertAsRead(alert.id)}
                                                >
                                                    {alert.status === "Unread" ? "Mark as Read" : "Read"}
                                                </button>
                                                <button
                                                    type="button"
                                                    className="danger-button"
                                                    onClick={() => deleteAlert(alert.id)}
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </section>
                )}

                {activeTab === "Reports" && (
                    <section style={{ display: "grid", gap: "24px" }}>
                        <div className="panel" style={{ padding: "24px" }}>
                            <div className="panel-header">
                                <div>
                                    <h2>Analytics Overview</h2>
                                    <p>Summary calculated from saved model predictions.</p>
                                </div>
                            </div>
                        </div>

                        <div className="report-grid three-up-grid">
                            <div className="panel report-chart-panel">
                                <div className="mini-chart-header">
                                    <div className="mini-chart-icon">◔</div>
                                    <div>
                                        <h2>Transaction Type Analysis</h2>
                                        <p>Saved transaction mix</p>
                                    </div>
                                </div>

                                {transactionTypeData.length === 0 ? (
                                    <div className="empty-state compact-empty-mini">
                                        <div className="empty-icon">📊</div>
                                        <h3>No chart data yet</h3>
                                    </div>
                                ) : (
                                    <div className="chart-wrap compact-chart-wrap">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <PieChart>
                                                <Pie
                                                    data={transactionTypeData}
                                                    dataKey="value"
                                                    nameKey="name"
                                                    cx="50%"
                                                    cy="52%"
                                                    outerRadius={62}
                                                    innerRadius={28}
                                                    paddingAngle={3}
                                                >
                                                    {transactionTypeData.map((entry, index) => (
                                                        <Cell
                                                            key={entry.name}
                                                            fill={CHART_COLORS[index % CHART_COLORS.length]}
                                                        />
                                                    ))}
                                                </Pie>
                                                <Tooltip
                                                    formatter={(value) => [value, "Transactions"]}
                                                    contentStyle={{ borderRadius: 12, border: "1px solid #dfe7f5", boxShadow: "0 10px 25px rgba(15, 23, 42, 0.08)" }}
                                                />
                                                <Legend wrapperStyle={{ fontSize: "11px" }} />
                                            </PieChart>
                                        </ResponsiveContainer>
                                    </div>
                                )}
                            </div>

                            <div className="panel report-chart-panel">
                                <div className="mini-chart-header">
                                    <div className="mini-chart-icon">▥</div>
                                    <div>
                                        <h2>Prediction Distribution</h2>
                                        <p>Fraud vs legitimate results</p>
                                    </div>
                                </div>

                                <div className="chart-wrap compact-chart-wrap">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={fraudChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#dfe7f5" vertical={false} />
                                            <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#475569" }} axisLine={false} tickLine={false} />
                                            <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#475569" }} axisLine={false} tickLine={false} />
                                            <Tooltip
                                                formatter={(value) => [value, "Transactions"]}
                                                contentStyle={{ borderRadius: 12, border: "1px solid #dfe7f5", boxShadow: "0 10px 25px rgba(15, 23, 42, 0.08)" }}
                                            />
                                            <Legend wrapperStyle={{ fontSize: "11px" }} />
                                            <Bar dataKey="count" name="Transactions" radius={[8, 8, 0, 0]}>
                                                {fraudChartData.map((entry, index) => (
                                                    <Cell
                                                        key={entry.name}
                                                        fill={index === 0 ? "#22c55e" : "#ef4444"}
                                                    />
                                                ))}
                                            </Bar>
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            <div className="panel report-chart-panel">
                                <div className="mini-chart-header">
                                    <div className="mini-chart-icon">▣</div>
                                    <div>
                                        <h2>Fraud by Transaction Type</h2>
                                        <p>Fraud counts grouped by transaction type</p>
                                    </div>
                                </div>

                                {fraudByTypeData.length === 0 ? (
                                    <div className="empty-state compact-empty-mini">
                                        <div className="empty-icon">📉</div>
                                        <h3>No fraud-by-type data</h3>
                                    </div>
                                ) : (
                                    <div className="chart-wrap compact-chart-wrap">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <BarChart data={fraudByTypeData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                                <CartesianGrid strokeDasharray="3 3" stroke="#dfe7f5" vertical={false} />
                                                <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#475569" }} axisLine={false} tickLine={false} />
                                                <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#475569" }} axisLine={false} tickLine={false} />
                                                <Tooltip
                                                    formatter={(value) => [value, "Fraud Cases"]}
                                                    contentStyle={{ borderRadius: 12, border: "1px solid #dfe7f5", boxShadow: "0 10px 25px rgba(15, 23, 42, 0.08)" }}
                                                />
                                                <Bar dataKey="value" name="Fraud Cases" radius={[8, 8, 0, 0]}>
                                                    {fraudByTypeData.map((entry, index) => (
                                                        <Cell
                                                            key={entry.name}
                                                            fill={CHART_COLORS[index % CHART_COLORS.length]}
                                                        />
                                                    ))}
                                                </Bar>
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="panel report-trend-panel full-width-trend-panel">
                            <div className="mini-chart-header">
                                <div className="mini-chart-icon">📈</div>
                                <div>
                                    <h2>Fraud Probability Trend</h2>
                                    <p>Saved backend history</p>
                                </div>
                            </div>

                            <div className="chart-summary-row compact-summary-row">
                                <div className="chart-summary-pill compact-pill">
                                    <span>Predictions</span>
                                    <strong>{fraudTrendData.length}</strong>
                                </div>
                                <div className="chart-summary-pill compact-pill">
                                    <span>Peak</span>
                                    <strong>{fraudTrendData.length ? `${highestObservedProbability.toFixed(2)}%` : "0.00%"}</strong>
                                </div>
                            </div>

                            {fraudTrendData.length === 0 ? (
                                <div className="empty-state compact-empty-mini">
                                    <div className="empty-icon">📈</div>
                                    <h3>No trend data</h3>
                                </div>
                            ) : (
                                <div className="chart-wrap compact-chart-wrap trend-chart-wrap full-width-chart-wrap">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={fraudTrendData} margin={{ top: 8, right: 10, left: 0, bottom: 10 }}>
                                            <defs>
                                                <linearGradient id="fraudTrendFill" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="0%" stopColor="#F59E0B" stopOpacity={0.24} />
                                                    <stop offset="100%" stopColor="#F59E0B" stopOpacity={0.03} />
                                                </linearGradient>
                                            </defs>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                                            <XAxis
                                                dataKey="timestamp"
                                                interval={Math.max(0, Math.ceil(fraudTrendData.length / 4) - 1)}
                                                tickFormatter={(value) => {
                                                    const date = new Date(value);
                                                    if (Number.isNaN(date.getTime())) {
                                                        return "—";
                                                    }
                                                    return date.toLocaleString("en-IN", {
                                                        month: "short",
                                                        day: "numeric",
                                                        hour: "2-digit",
                                                        minute: "2-digit"
                                                    });
                                                }}
                                                tick={{ fontSize: 10, fill: "#475569" }}
                                                axisLine={false}
                                                tickLine={false}
                                                minTickGap={12}
                                            />
                                            <YAxis
                                                domain={[0, 100]}
                                                tickFormatter={(value) => `${value}%`}
                                                tick={{ fontSize: 10, fill: "#475569" }}
                                                axisLine={false}
                                                tickLine={false}
                                            />
                                            <Tooltip
                                                cursor={{ stroke: "#fbbf24", strokeDasharray: "4 4" }}
                                                content={({ active, payload }) => {
                                                    if (!active || !payload || !payload.length) {
                                                        return null;
                                                    }
                                                    const point = payload[0].payload;
                                                    const probability = Number(point.probability || 0);
                                                    const timestamp = point.timestamp ? new Date(point.timestamp) : null;
                                                    return (
                                                        <div className="premium-tooltip compact-tooltip">
                                                            <div className="premium-tooltip-header">Fraud probability</div>
                                                            <div className="premium-tooltip-row">
                                                                <span>Transaction ID</span>
                                                                <strong>{point.id ?? "—"}</strong>
                                                            </div>
                                                            <div className="premium-tooltip-row">
                                                                <span>Time</span>
                                                                <strong>{timestamp && !Number.isNaN(timestamp.getTime()) ? timestamp.toLocaleString("en-IN") : "—"}</strong>
                                                            </div>
                                                            <div className="premium-tooltip-row highlight-row">
                                                                <span>Probability</span>
                                                                <strong>{probability.toFixed(2)}%</strong>
                                                            </div>
                                                        </div>
                                                    );
                                                }}
                                            />
                                            <Area type="monotone" dataKey="probability" fill="url(#fraudTrendFill)" stroke="none" isAnimationActive={false} />
                                            <Line
                                                type="monotone"
                                                dataKey="probability"
                                                stroke="#F59E0B"
                                                strokeWidth={2.5}
                                                dot={(props) => {
                                                    const { cx, cy, payload } = props;
                                                    const isFraud = payload?.prediction === "Fraud";
                                                    return (
                                                        <circle
                                                            cx={cx}
                                                            cy={cy}
                                                            r={isFraud ? 4.5 : 3.5}
                                                            fill={isFraud ? "#ef4444" : "#f59e0b"}
                                                            stroke="#ffffff"
                                                            strokeWidth={2}
                                                        />
                                                    );
                                                }}
                                                activeDot={{ r: 6, fill: "#f59e0b", stroke: "#ffffff", strokeWidth: 2 }}
                                                isAnimationActive={false}
                                                connectNulls={false}
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            )}
                        </div>

                        <div className="panel report-metrics-panel">
                            <div className="panel-header">
                                <div>
                                    <h2>Model Performance</h2>
                                    <p>
                                        Evaluation dataset: artifacts/threshold_evaluation.csv • Decision threshold: {reportThresholdValue.toFixed(2)} ({(reportThresholdValue * 100).toFixed(0)}%)
                                    </p>
                                </div>
                                <button
                                    className="secondary-button"
                                    type="button"
                                    onClick={downloadReport}
                                >
                                    Download Report
                                </button>
                            </div>

                            <div className="metric-grid">
                                {modelMetricsCards.map((metric) => (
                                    <div
                                        key={metric.key}
                                        className="metric-card"
                                        title={metric.description}
                                    >
                                        <div className="metric-icon">{metric.icon}</div>
                                        <span>{metric.label}</span>
                                        <strong>{metric.value}</strong>
                                        <small>{metric.description}</small>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="panel" style={{ padding: "24px" }}>
                            <div className="panel-header">
                                <div>
                                    <h2>Recent Transactions</h2>
                                    <p>Latest 10 saved predictions</p>
                                </div>
                            </div>

                            {loadingTransactions ? (
                                <p>Loading transactions...</p>
                            ) : (
                                renderTransactionsTable(transactions.slice(0, 10))
                            )}
                        </div>
                    </section>
                )}

                <footer className="dashboard-footer">
                    <span>Fraud Detection ML System</span>
                    <span>Random Forest • Threshold 0.90</span>
                </footer>
            </main>
        </div>
    );
}

export default App;
