import React from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';

const BalanceCalendar = ({ balances }) => {
  const tileContent = ({ date }) => {
    const balance = balances.find((b) => new Date(b.date).toDateString() === date.toDateString());
    return balance ? (
      <div className={`text-sm ${balance.amount < 0 ? 'text-red-500' : 'text-green-500'}`}>
        {balance.amount}
      </div>
    ) : null;
  };

  return (
    <div className="mt-6">
      <h2 className="text-xl font-bold mb-4">Balance Calendar</h2>
      <Calendar tileContent={tileContent} />
    </div>
  );
};

export default BalanceCalendar;