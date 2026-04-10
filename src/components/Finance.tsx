import React from 'react';
import { TrendingUpIcon, TrendingDownIcon, CashIcon } from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const monthly = [
  { month: 'Янв', revenue: 125000, expenses: 45000 },
  { month: 'Фев', revenue: 142000, expenses: 48000 },
  { month: 'Мар', revenue: 168000, expenses: 52000 },
  { month: 'Апр', revenue: 185000, expenses: 55000 },
  { month: 'Май', revenue: 210000, expenses: 58000 }
];

const masters = [
  { name: 'Елена', revenue: 89000, commission: 35600 },
  { name: 'Мария', revenue: 76000, commission: 30400 },
  { name: 'Анна', revenue: 67000, commission: 26800 }
];

export default function Finance() {
  const totalRevenue = 210000;
  const totalExpenses = 58000;
  const profit = totalRevenue - totalExpenses;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6"><div className="flex justify-between"><div><p className="text-sm text-gray-600">Выручка</p><p className="text-2xl font-bold">{totalRevenue.toLocaleString()} ₽</p><p className="text-sm text-green-600">+12%</p></div><div className="bg-green-100 p-3 rounded-full"><TrendingUpIcon className="w-6 h-6 text-green-600" /></div></div></div>
        <div className="bg-white rounded-lg shadow-sm p-6"><div className="flex justify-between"><div><p className="text-sm text-gray-600">Расходы</p><p className="text-2xl font-bold">{totalExpenses.toLocaleString()} ₽</p><p className="text-sm text-red-600">+5%</p></div><div className="bg-red-100 p-3 rounded-full"><TrendingDownIcon className="w-6 h-6 text-red-600" /></div></div></div>
        <div className="bg-white rounded-lg shadow-sm p-6"><div className="flex justify-between"><div><p className="text-sm text-gray-600">Прибыль</p><p className="text-2xl font-bold">{profit.toLocaleString()} ₽</p><p className="text-sm text-green-600">+18%</p></div><div className="bg-blue-100 p-3 rounded-full"><CashIcon className="w-6 h-6 text-blue-600" /></div></div></div>
      </div>
      <div className="bg-white rounded-lg shadow-sm p-6"><h3 className="font-semibold mb-4">Динамика доходов и расходов</h3><ResponsiveContainer width="100%" height={350}><BarChart data={monthly}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="month" /><YAxis /><Tooltip /><Bar dataKey="revenue" fill="#ef4444" name="Выручка" /><Bar dataKey="expenses" fill="#f97316" name="Расходы" /></BarChart></ResponsiveContainer></div>
      <div className="bg-white rounded-lg shadow-sm overflow-hidden"><div className="px-6 py-4 border-b"><h3 className="font-semibold">Зарплата мастеров</h3></div><table className="w-full"><thead className="bg-gray-50"><tr><th className="px-6 py-3 text-left text-xs">Мастер</th><th className="px-6 py-3 text-left text-xs">Выручка</th><th className="px-6 py-3 text-left text-xs">Комиссия</th><th className="px-6 py-3 text-left text-xs">Итого</th></tr></thead><tbody>{masters.map(m => (<tr key={m.name} className="border-b"><td className="px-6 py-4">{m.name}</td><td className="px-6 py-4">{m.revenue.toLocaleString()} ₽</td><td className="px-6 py-4">{m.commission.toLocaleString()} ₽</td><td className="px-6 py-4 font-medium">{(m.revenue - m.commission).toLocaleString()} ₽</td></tr>))}</tbody></table></div>
    </div>
  );
}
