import React, { useState } from 'react';
import { MagnifyingGlassIcon, UserIcon, PhoneIcon } from '@heroicons/react/24/outline';

const clients = [
  { id: 1, name: 'Анна Смирнова', phone: '+7 (999) 123-45-67', visits: 12, spent: 45600, bonus: 450 },
  { id: 2, name: 'Дмитрий Волков', phone: '+7 (999) 234-56-78', visits: 5, spent: 18900, bonus: 120 },
  { id: 3, name: 'Ольга Петрова', phone: '+7 (999) 345-67-89', visits: 24, spent: 89200, bonus: 890 }
];

export default function Clients() {
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<any>(null);

  const filtered = clients.filter(c => c.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 bg-white rounded-lg shadow-sm">
        <div className="p-6 border-b"><h2 className="text-xl font-semibold mb-4">Клиенты</h2><div className="relative"><MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" /><input type="text" placeholder="Поиск..." value={search} onChange={e => setSearch(e.target.value)} className="w-full pl-10 pr-4 py-2 border rounded-lg" /></div></div>
        <div className="divide-y">{filtered.map(c => (<div key={c.id} onClick={() => setSelected(c)} className="p-4 hover:bg-gray-50 cursor-pointer"><div className="flex justify-between items-center"><div className="flex items-center space-x-3"><div className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center"><UserIcon className="w-5 h-5 text-white" /></div><div><p className="font-medium">{c.name}</p><p className="text-sm text-gray-500">{c.phone}</p></div></div><div className="text-right"><p className="font-medium">{c.spent.toLocaleString()} ₽</p><p className="text-sm text-gray-500">{c.visits} визитов</p></div></div></div>))}</div>
      </div>
      <div className="bg-white rounded-lg shadow-sm p-6">{selected ? (<div><div className="flex items-center space-x-3 mb-6"><div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center"><UserIcon className="w-8 h-8 text-white" /></div><div><h3 className="text-xl font-semibold">{selected.name}</h3><p className="text-gray-500">{selected.phone}</p></div></div><div className="grid grid-cols-2 gap-4"><div className="bg-gray-50 p-3 rounded-lg"><p className="text-xs text-gray-500">Визитов</p><p className="text-2xl font-bold">{selected.visits}</p></div><div className="bg-gray-50 p-3 rounded-lg"><p className="text-xs text-gray-500">Бонусов</p><p className="text-2xl font-bold">{selected.bonus}</p></div></div><button className="w-full mt-6 px-4 py-2 bg-red-600 text-white rounded-lg">Записать</button></div>) : (<div className="text-center py-12"><UserIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" /><p>Выберите клиента</p></div>)}</div>
    </div>
  );
}
