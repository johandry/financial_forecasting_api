import React from "react";

export default function Alerts({ alerts }) {
  if (!alerts.length) return null;
  return (
    <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mt-4">
      <strong>Alerts:</strong>
      <ul>
        {alerts.map(date => <li key={date}>{date}</li>)}
      </ul>
    </div>
  );
}