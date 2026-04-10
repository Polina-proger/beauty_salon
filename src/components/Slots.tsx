import React, { useState } from 'react';
import { ClockIcon, UserIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { format, addDays } from 'date-fns';
import { ru } from 'date-fns/locale';

const masters = ['Елена', 'Мария', 'Анна', 'Светлана'];

const generateSlots = () => {
  const slots = [];
  const hours = [10, 11, 12, 13, 14, 15, 16, 17];
  masters.forEach(master => {
    hours.forEach(hour => {
      if (Math.random() > 0.5) slots.push({ master, time: `${hour}:00`, duration: 60 });
    });
  });
  return slots;
};

export default function Slots() {
  const [date, setDate] = useState(new Date());
  const [slots] = useState(generateSlots());

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">Свободные окна на {format(date, 'd MMMM yyyy', { locale: ru })}</h2>
        <div className="flex space-x-2 mb-6 overflow-x-auto">
          {[0,1,2,3,4,5,6].map(i => (<button key={i} onClick={() => setDate(addDays(new Date(), i))} className={`px-4 py-2 rounded-lg text-sm ${format(addDays(new Date(), i), 'dd.MM') === format(date, 'dd.MM') ? 'bg-red-600 text-white' : 'bg-gray-100'}`}>{format(addDays(new Date(), i), 'EEE d', { locale: ru })}</button>))}
        </div>
        <div className="grid gap-3">
          {slots.map((s, i) => (<div key={i} className="flex justify-between items-center p-4 border rounded-lg hover:bg-gray-50"><div className="flex items-center space-x-4"><div className="w-10 h-10 bg-pink-100 rounded-full flex items-center justify-center"><UserIcon className="w-5 h-5 text-pink-600" /></div><div><p className="font-medium">{s.master}</p><p className="text-sm text-gray-500 flex items-center space-x-1"><ClockIcon className="w-4 h-4" /><span>{s.time}</span></p></div></div><button className="px-4 py-2 bg-red-600 text-white rounded-lg flex items-center space-x-2"><CheckCircleIcon className="w-5 h-5" /><span>Записаться</span></button></div>))}
        </div>
      </div>
    </div>
  );
}
