import React, { useState } from 'react';
import { CalendarIcon, ClockIcon, UserIcon, ScissorsIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

const activeBookings = [
  { id: 1, client: 'Анна Смирнова', phone: '+7 (999) 123-45-67', service: 'Стрижка + укладка', master: 'Елена', date: '2025-05-15', time: '14:00', price: 2500, status: 'confirmed', prepayment: 500 },
  { id: 2, client: 'Дмитрий Волков', phone: '+7 (999) 234-56-78', service: 'Окрашивание', master: 'Мария', date: '2025-05-15', time: '11:00', price: 4500, status: 'pending' },
  { id: 3, client: 'Ольга Петрова', phone: '+7 (999) 345-67-89', service: 'Маникюр', master: 'Анна', date: '2025-05-16', time: '10:00', price: 1800, status: 'confirmed' }
];

const history = [
  { id: 1, client: 'Анна Смирнова', service: 'Стрижка', master: 'Елена', date: '2025-05-01', price: 1500, status: 'completed', rating: 5 },
  { id: 2, client: 'Дмитрий Волков', service: 'Стрижка', master: 'Елена', date: '2025-04-20', price: 1500, status: 'completed', rating: 4 }
];

export default function Bookings() {
  const [tab, setTab] = useState<'active' | 'history'>('active');
  const [selected, setSelected] = useState<any>(null);

  const items = tab === 'active' ? activeBookings : history;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 bg-white rounded-lg shadow-sm">
        <div className="border-b flex">
          <button onClick={() => setTab('active')} className={`flex-1 px-6 py-4 text-center border-b-2 ${tab === 'active' ? 'border-red-500 text-red-600' : 'border-transparent'}`}>Активные ({activeBookings.length})</button>
          <button onClick={() => setTab('history')} className={`flex-1 px-6 py-4 text-center border-b-2 ${tab === 'history' ? 'border-red-500 text-red-600' : 'border-transparent'}`}>История ({history.length})</button>
        </div>
        <div className="divide-y">
          {items.map(b => (
            <div key={b.id} onClick={() => setSelected(b)} className="p-4 hover:bg-gray-50 cursor-pointer">
              <div className="flex justify-between items-start">
                <div><h3 className="font-medium">{b.client}</h3><div className="grid grid-cols-2 gap-2 text-sm text-gray-600 mt-2"><span>{b.service}</span><span>Мастер: {b.master}</span><span>{b.date}</span><span>{b.time || '—'}</span></div></div>
                <ChevronRightIcon className="w-5 h-5 text-gray-400" />
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="bg-white rounded-lg shadow-sm p-6">
        {selected ? (<div><h3 className="font-semibold text-lg mb-4">Детали</h3><div className="space-y-3"><p><span className="text-gray-500">Клиент:</span> {selected.client}</p><p><span className="text-gray-500">Услуга:</span> {selected.service}</p><p><span className="text-gray-500">Мастер:</span> {selected.master}</p><p><span className="text-gray-500">Стоимость:</span> {selected.price} ₽</p><div className="flex space-x-2 pt-4"><button className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg">Подтвердить</button><button className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg">Отменить</button></div></div></div>) : (<div className="text-center text-gray-500 py-12"><CalendarIcon className="w-16 h-16 mx-auto mb-4 text-gray-300" /><p>Выберите запись</p></div>)}
      </div>
    </div>
  );
}
