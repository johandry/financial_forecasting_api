const API_URL = import.meta.env.VITE_REACT_APP_API_URL;

export async function fetchAccounts() {
  const res = await fetch(`${API_URL}/accounts`);
  if (!res.ok) throw new Error("Failed to fetch accounts");
  return res.json();
}

export async function fetchForecast(accountId, months = 3, buffer = 50) {
  const res = await fetch(
    `${API_URL}/forecast?account_id=${accountId}&months=${months}&buffer=${buffer}`
  );
  if (!res.ok) throw new Error("Failed to fetch forecast");
  return res.json();
}

export async function submitOverride(data) {
  const res = await fetch(`${API_URL}/overrides`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to submit override");
  return res.json();
}