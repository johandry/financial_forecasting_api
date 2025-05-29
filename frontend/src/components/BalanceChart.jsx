import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const BalanceChart = ({ balances }) => {
  return (
    <div className="mt-6">
      <h2 className="text-xl font-bold mb-4">Balance Over Time</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={balances}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="amount" stroke="#8884d8" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default BalanceChart;