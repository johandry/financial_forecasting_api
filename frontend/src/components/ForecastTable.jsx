import React from "react";

export default function ForecastTable({ balances }) {
  return (
    <table className="min-w-full border mt-4">
      <thead>
        <tr>
          <th className="border px-2">Date</th>
          <th className="border px-2">Balance</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(balances).map(([date, bal]) => (
          <tr key={date}>
            <td className="border px-2">{date}</td>
            <td className="border px-2">${bal}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}