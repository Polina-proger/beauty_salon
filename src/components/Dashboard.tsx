import React from 'react';
import { CurrencyDollarIcon, UserGroupIcon, CalendarIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const revenue = [
  { day: 'Пн', value: 24500 }, { day: 'Вт', value: 32800 }, { day: 'Ср', value: 31200 },
  { day: 'Чт', value: 38900 }, { day: 'Пт', value: 45200 }, { day: 'Сб', value: 56700 }, { day: 'Вс', value: 42300 }
];

const services = [
  { name: 'Стрижка', value: 35, color: '#ef4444' },
  { name: 'Окрашивание', value: 28, color: '#f97316' },
  { name: 'Маникюр', value: 22, color: '#eab308' },
  { name: 'Уход', value: 15, color: '#22c55e' }
];

const stats = [
  { name: 'Выручка сегодня', value: '45 200 ₽', icon: CurrencyDollarIcon, change: '+12%', color: 'bg-green-500' },
  { name: 'Клиентов сегодня', value: '18', icon: UserGroupIcon, change: '+3', color: 'bg-blue-500' },
  { name: 'Записей сегодня', value: '23', icon: CalendarIcon, change: '+5', color: 'bg-purple-500' },
  { name: 'Завершено', value: '14', icon: CheckCircleIcon, change: '+8', color: 'bg-orange-500' }
];

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map(s => (
          <div key={s.name} className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm text-gray-600">{s.name}</p>
                <p className="text-2xl font-bold mt-2">{s.value}</p>
                <p className="text-sm text-green-600 mt-2">{s.change}</p>
              </div>
              <div className={`${s.color} p-3 rounded-full`}><s.icon className="w-6 h-6 text-white" /></div>
            </div>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="font-semibold mb-4">Динамика выручки</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={revenue}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="day" /><YAxis /><Tooltip /><Area type="monotone" dataKey="value" stroke="#ef4444" fill="#fecaca" /></AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="font-semibold mb-4">Популярность услуг</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart><Pie data={services} cx="50%" cy="50%" label={({name,percent}) => `${name} ${(percent*100).toFixed(0)}%`} outerRadius={80} dataKey="value">{services.map((e,i) => <Cell key={i} fill={e.color} />)}</Pie><Tooltip /></PieChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="font-semibold mb-4">Ближайшие записи</h3>
        <div className="space-y-3">
          {[{time:'10:00',client:'Анна Смирнова',service:'Стрижка'},{time:'11:30',client:'Дмитрий Волков',service:'Окрашивание'},{time:'13:00',client:'Ольга Петрова',service:'Маникюр'}].map((b,i)=>(
            <div key={i} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"><div><span className="font-medium">{b.time}</span><p>{b.client}</p><p className="text-sm text-gray-500">{b.service}</p></div><span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Подтверждено</span></div>
          ))}
        </div>
      </div>
    </div>
  );
}
