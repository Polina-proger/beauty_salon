import React from 'react';
import { GiftIcon, HeartIcon, SparklesIcon, FireIcon, TagIcon } from '@heroicons/react/24/outline';

const offers = [
  { id: 1, client: 'Анна Смирнова', title: 'Скидка 20% на день рождения', discount: 20, valid: '2025-06-01', type: 'birthday', used: false },
  { id: 2, client: 'Анна Смирнова', title: '5-й визит в подарок', discount: 100, valid: '2025-12-31', type: 'loyalty', used: false },
  { id: 3, client: 'Дмитрий Волков', title: 'Приведи друга', discount: 30, valid: '2025-07-15', type: 'referral', used: false },
  { id: 4, client: 'Ольга Петрова', title: 'Весеннее обновление', discount: 15, valid: '2025-05-30', type: 'seasonal', used: true }
];

const getIcon = (type: string) => {
  switch(type) {
    case 'birthday': return <HeartIcon className="w-6 h-6 text-pink-500" />;
    case 'loyalty': return <SparklesIcon className="w-6 h-6 text-purple-500" />;
    case 'seasonal': return <FireIcon className="w-6 h-6 text-orange-500" />;
    default: return <TagIcon className="w-6 h-6 text-blue-500" />;
  }
};

export default function Offers() {
  const active = offers.filter(o => !o.used);
  const used = offers.filter(o => o.used);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold flex items-center space-x-2"><GiftIcon className="w-6 h-6 text-red-500" /><span>Персональные предложения</span></h2>
        <div className="grid grid-cols-2 gap-4 mt-6"><div className="bg-red-50 p-4 rounded-lg"><p className="text-sm">Активные</p><p className="text-3xl font-bold text-red-600">{active.length}</p></div><div className="bg-gray-50 p-4 rounded-lg"><p className="text-sm">Использовано</p><p className="text-3xl font-bold text-gray-600">{used.length}</p></div></div>
      </div>
      <div className="bg-white rounded-lg shadow-sm">
        <div className="px-6 py-4 bg-red-500 rounded-t-lg"><h3 className="text-white font-semibold">Доступные предложения</h3></div>
        <div className="divide-y">{active.map(o => (<div key={o.id} className="p-6 flex justify-between items-start"><div className="flex space-x-4"><div>{getIcon(o.type)}</div><div><h4 className="font-semibold">{o.title}</h4><p className="text-sm text-gray-600">Для {o.client}</p><p className="text-xs text-gray-500">До {o.valid}</p></div></div><button className="px-4 py-2 bg-red-600 text-white rounded-lg">Активировать</button></div>))}</div>
      </div>
      {used.length > 0 && (<div className="bg-white rounded-lg shadow-sm"><div className="px-6 py-4 bg-gray-100 rounded-t-lg"><h3 className="font-semibold text-gray-700">Использованные</h3></div><div className="divide-y">{used.map(o => (<div key={o.id} className="p-6 bg-gray-50"><div className="flex space-x-4 opacity-50"><div>{getIcon(o.type)}</div><div><h4 className="font-semibold">{o.title}</h4><p className="text-sm text-gray-500">Для {o.client}</p></div></div></div>))}</div></div>)}
    </div>
  );
}
