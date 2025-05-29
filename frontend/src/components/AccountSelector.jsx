import React from "react";

const AccountSelector = ({ accounts, selectedAccount, onChange }) => {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700">Select Account</label>
      <select
        value={selectedAccount}
        onChange={e => onChange(e.target.value)}
        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm"
      >
        <option value="">-- Select an Account --</option>
        {accounts.map(account => (
          <option key={account.id} value={account.id}>
            {account.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default AccountSelector;