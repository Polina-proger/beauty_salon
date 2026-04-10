import React, { useState } from 'react';
import { ChevronLeftIcon, ChevronRightIcon, PlusIcon } from '@heroicons/react/24/outline';
import { format, startOfWeek, addDays } from 'date-fns';
import { ru } from 'date-fns/locale';

const masters = ['Елена', 'Мария', 'Анна', 'Светлана'];
const hours = Array.from({ length: 12 }, (_, i) => i + 9);

const bookings = [
  { master: 'Елена', hour: 10, client: 'Анна Смирнова', service: 'Стрижка' },
  { master: 'Мария', hour: 11, client: 'Дмитрий Волков', service: 'Окрашивание' },
  { master: 'Елена', hour: 14, client: 'Ольга Петрова', service: 'Маникюр' }
];

export default function Calendar() {
  const [currentDate] = useState(new Date());
  const weekDays = Array.from({ length: 7 }, (_, i) => addDays(startOfWeek(currentDate, { weekStartsOn: 1 }), i));

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b flex justify-between items-center">
        <h2 className="text-lg font-semibold">{format(currentDate, 'LLLL yyyy', { locale: ru })}</h2>
        <button className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg"><PlusIcon className="w-5 h-5" /><span>Новая запись</span></button>
      </div>
      <div className="overflow-x-auto">
        <div className="min-w-[800px]">
          <div className="grid grid-cols-5 border-b">
            <div className="p-3 bg-gray-50 border-r"></div>
            {masters.map(m => <div key={m} className="p-3 text-center bg-gray-50"><p className="font-medium">{m}</p></div>)}
          </div>
          {hours.map(hour => (
            <div key={hour} className="grid grid-cols-5 border-b hover:bg-gray-50">
              <div className="p-3 border-r text-sm">{hour}:00</div>
              {masters.map(master => {
                const b = bookings.find(b => b.master === master && b.hour === hour);
                return <div key={master} className="p-2 min-h-[80px] border-r">{b && <div className="p-2 bg-green-100 rounded-lg text-xs"><p className="font-medium">{b.client}</p><p className="text-gray-600">{b.service}</p></div>}</div>;
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
