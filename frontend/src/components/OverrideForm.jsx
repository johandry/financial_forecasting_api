import React, { useState } from "react";

export default function OverrideForm({ onSubmit }) {
  const [eventType, setEventType] = useState("bill");
  const [eventId, setEventId] = useState("");
  const [eventDate, setEventDate] = useState("");
  const [skip, setSkip] = useState(false);
  const [overrideAmount, setOverrideAmount] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit({
      event_type: eventType,
      event_id: Number(eventId),
      event_date: eventDate,
      skip,
      override_amount: overrideAmount ? Number(overrideAmount) : undefined,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 space-y-2">
      <select value={eventType} onChange={e => setEventType(e.target.value)} className="border p-1">
        <option value="bill">Bill</option>
        <option value="transaction">Transaction</option>
      </select>
      <input type="number" placeholder="Event ID" value={eventId} onChange={e => setEventId(e.target.value)} className="border p-1" required />
      <input type="date" value={eventDate} onChange={e => setEventDate(e.target.value)} className="border p-1" required />
      <label>
        <input type="checkbox" checked={skip} onChange={e => setSkip(e.target.checked)} />
        Skip
      </label>
      <input type="number" placeholder="Override Amount" value={overrideAmount} onChange={e => setOverrideAmount(e.target.value)} className="border p-1" />
      <button type="submit" className="bg-blue-500 text-white px-3 py-1 rounded">Submit Override</button>
    </form>
  );
}