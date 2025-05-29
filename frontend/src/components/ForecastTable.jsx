import React from "react";

const ForecastTable = ({ balances }) => {
  return (
    <div className="overflow-x-auto">
      <table className="table-auto border-collapse border border-gray-300 w-full text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="border border-gray-300 px-4 py-2 text-left font-medium text-gray-700">
              Date
            </th>
            <th className="border border-gray-300 px-4 py-2 text-left font-medium text-gray-700">
              Balance
            </th>
          </tr>
        </thead>
        <tbody>
          {balances.map((balance, index) => (
            <tr
              key={index}
              className={index % 2 === 0 ? "bg-white" : "bg-gray-50"}
            >
              <td className="border border-gray-300 px-4 py-2 text-gray-700">
                {balance.date}
              </td>
              <td
                className={`border border-gray-300 px-4 py-2 ${
                  balance.amount < 0 ? "text-red-500" : "text-green-500"
                }`}
              >
                {balance.amount}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ForecastTable;