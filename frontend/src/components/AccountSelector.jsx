import React from "react";

export default function AccountSelector({ accounts, selected, onChange }) {
  return (
    <select value={selected} onChange={e => onChange(e.target.value)} className="border p-2 rounded">
      {accounts.map(acc => (
        <option key={acc.id} value={acc.id}>{acc.name}</option>
      ))}
    </select>
  );
}