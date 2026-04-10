import React from 'react';
import { ScissorsIcon, PaintBrushIcon, HandRaisedIcon, FaceSmileIcon } from '@heroicons/react/24/outline';

const services = [
  { id: 1, name: 'Стрижка', category: 'Волосы', duration: 60, price: 1500, icon: ScissorsIcon },
  { id: 2, name: 'Окрашивание', category: 'Волосы', duration: 120, price: 3500, icon: PaintBrushIcon },
  { id: 3, name: 'Маникюр', category: 'Ногти', duration: 60, price: 1800, icon: HandRaisedIcon },
  { id: 4, name: 'Уход за лицом', category: 'Лицо', duration: 90, price: 3200, icon: FaceSmileIcon }
];

export default function Services() {
  return (
    <div className="bg-white rounded-lg shadow-sm">
      <div className="px-6 py-4 border-b flex justify-between items-center">
        <h2 className="text-xl font-semibold">Услуги</h2>
        <button className="px-4 py-2 bg-red-600 text-white rounded-lg">+ Добавить услугу</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 p-6">
        {services.map(s => (<div key={s.id} className="border rounded-lg p-4 hover:shadow-lg transition"><div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-4"><s.icon className="w-6 h-6 text-red-600" /></div><h3 className="font-semibold text-lg">{s.name}</h3><p className="text-sm text-gray-500">{s.category}</p><p className="text-sm text-gray-500 mt-2">{s.duration} мин</p><p className="text-2xl font-bold text-red-600 mt-2">{s.price.toLocaleString()} ₽</p><button className="w-full mt-4 px-4 py-2 border border-red-600 text-red-600 rounded-lg hover:bg-red-50">Редактировать</button></div>))}
      </div>
    </div>
  );
}
