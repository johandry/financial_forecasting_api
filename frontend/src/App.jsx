import React, { useEffect, useState } from "react";
import AccountSelector from "./components/AccountSelector.jsx";
import ForecastTable from "./components/ForecastTable.jsx";
import Alerts from "./components/Alerts.jsx";
import OverrideForm from "./components/OverrideForm.jsx";
import './App.css'

const API_URL = import.meta.env.VITE_REACT_APP_API_URL;

function App() {
  const [user, setUser] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState("");
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // 1. Check for user
  useEffect(() => {
    setLoading(true);
    setError("");
    fetch(`${API_URL}/users`)
      .then(res => res.json())
      .then(users => {
        if (users.length === 0) {
          // Create a user if none exists
          return fetch(`${API_URL}/users`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: "user@example.com", password: "yourpassword" }),
          })
            .then(res => res.json())
            .then(newUser => setUser(newUser));
        } else {
          setUser(users[0]);
        }
      })
      .catch(() => setError("Unable to load users. Please check your API connection."))
      .finally(() => setLoading(false));
  }, []);

  // 2. Check for accounts for the user
  useEffect(() => {
    if (!user) return;
    setLoading(true);
    setError("");
    fetch(`${API_URL}/accounts?user_id=${user.id}`)
      .then(res => res.json())
      .then(data => {
        if (data.length === 0) {
          // Create an account if none exists
          return fetch(`${API_URL}/accounts`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: user.id, name: "Default Account", current_balance: 0 }),
          })
            .then(res => res.json())
            .then(newAccount => {
              setAccounts([newAccount]);
              setSelectedAccount(newAccount.id);
            });
        } else {
          setAccounts(data);
          setSelectedAccount(data[0].id);
        }
      })
      .catch(() => setError("Unable to load accounts. Please check your API connection."))
      .finally(() => setLoading(false));
  }, [user]);

  // 3. Load forecast for selected account
  useEffect(() => {
    if (!selectedAccount) return;
    setLoading(true);
    setError("");
    fetch(`${API_URL}/forecast?account_id=${selectedAccount}&months=3&buffer=50`)
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch forecast");
        return res.json();
      })
      .then(data => {
        setForecast(data);
        setLoading(false);
      })
      .catch(() => {
        setError("Unable to load forecast. Please check your API connection.");
        setLoading(false);
      });
  }, [selectedAccount]);

  function handleOverrideSubmit(data) {
    fetch(`${API_URL}/overrides`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...data, account_id: selectedAccount, user_id: user.id }),
    })
      .then(res => res.json())
      .then(() => alert("Override submitted!"))
      .catch(() => alert("Failed to submit override. Please check your API connection."));
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Financial Forecast</h1>
      {loading && <div className="text-gray-500">Loading...</div>}
      {error && <div className="text-red-600">{error}</div>}
      {!loading && !error && !user && (
        <div>
          <p>No user found. Please create a user.</p>
          {/* Render a user creation form here */}
        </div>
      )}
      {!loading && !error && user && accounts.length > 0 && (
        <>
          <AccountSelector
            accounts={accounts}
            selected={selectedAccount}
            onChange={setSelectedAccount}
          />
          {forecast && (
            <>
              <ForecastTable balances={forecast.balances} />
              <Alerts alerts={forecast.alerts} />
            </>
          )}
          <OverrideForm onSubmit={handleOverrideSubmit} />
        </>
      )}
    </div>
  );
}

export default App;
