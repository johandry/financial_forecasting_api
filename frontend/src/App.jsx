import React, { useEffect, useState } from 'react';
import ForecastTable from './components/ForecastTable.jsx';
import Alerts from './components/Alerts.jsx';
import OverrideForm from './components/OverrideForm.jsx';
import AccountSelector from './components/AccountSelector.jsx';
import BalanceChart from './components/BalanceChart.jsx';
import BalanceCalendar from './components/BalanceCalendar.jsx';

const API_URL = import.meta.env.VITE_REACT_APP_API_URL;

function App() {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState('');
  const [forecast, setForecast] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('calendar'); // Toggle between 'calendar', 'list', and 'graph'

  useEffect(() => {
    // Fetch accounts
    fetch(`${API_URL}/accounts`)
      .then((res) => res.json())
      .then((data) => setAccounts(data))
      .catch(() => console.error('Failed to fetch accounts'));
  }, []);

  useEffect(() => {
    if (!selectedAccount) return;

    setLoading(true);
    const months = 3;
    const buffer = 50;

    fetch(`${API_URL}/forecast?account_id=${selectedAccount}&months=${months}&buffer=${buffer}`)
      .then((res) => res.json())
      .then((data) => {
        const sortedBalances = Object.entries(data.balances || {})
          .map(([date, amount]) => ({ date, amount }))
          .sort((a, b) => new Date(a.date) - new Date(b.date));

        setForecast({ ...data, balances: sortedBalances });
        setAlerts(data.alerts || []);
      })
      .catch(() => console.error('Failed to fetch forecast'))
      .finally(() => setLoading(false));
  }, [selectedAccount]);

  const handleOverrideSubmit = (data) => {
    fetch(`${API_URL}/overrides`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...data, account_id: selectedAccount }),
    })
      .then((res) => res.json())
      .then(() => alert('Override submitted!'))
      .catch(() => alert('Failed to submit override.'));
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Financial Forecast</h1>
      <AccountSelector
        accounts={accounts}
        selectedAccount={selectedAccount}
        onChange={setSelectedAccount}
      />
      <div className="flex space-x-4 mb-4">
        <button
          className={`px-4 py-2 rounded ${view === 'calendar' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          onClick={() => setView('calendar')}
        >
          Calendar
        </button>
        <button
          className={`px-4 py-2 rounded ${view === 'list' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          onClick={() => setView('list')}
        >
          List
        </button>
        <button
          className={`px-4 py-2 rounded ${view === 'graph' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          onClick={() => setView('graph')}
        >
          Graph
        </button>
      </div>
      {loading && <div>Loading...</div>}
      {!loading && forecast === null && <div>Failed to load forecast. Please try again.</div>}
      {forecast && forecast.balances && Array.isArray(forecast.balances) ? (
        <>
          {view === 'calendar' && <BalanceCalendar balances={forecast.balances} />}
          {view === 'list' && <ForecastTable balances={forecast.balances} />}
          {view === 'graph' && <BalanceChart balances={forecast.balances} />}
        </>
      ) : (
        <div>No forecast data available.</div>
      )}
      <Alerts alerts={alerts} />
      <OverrideForm onSubmit={handleOverrideSubmit} />
    </div>
  );
}

export default App;
