import React from "react";

export default function Alerts({ alerts }) {
  if (!alerts.length) return null;
  return (
    <div className="space-y-4">
      {alerts.map((alert, index) => (
        <div
          key={index}
          className="border border-red-500 bg-red-100 text-red-700 px-4 py-2 rounded"
        >
          <p>{alert}</p>
        </div>
      ))}
    </div>
  );
}