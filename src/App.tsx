import React, { useState } from 'react';
import { 
  ChartBarIcon, CalendarIcon, ClockIcon, 
  UsersIcon, ScissorsIcon, TagIcon, 
  GiftIcon, Cog6Icon 
} from '@heroicons/react/24/outline';
import Dashboard from './components/Dashboard';
import Calendar from './components/Calendar';
import Bookings from './components/Bookings';
import Clients from './components/Clients';
import Slots from './components/Slots';
import Offers from './components/Offers';
import Services from './components/Services';
import Finance from './components/Finance';

type Tab = 'dashboard' | 'calendar' | 'bookings' | 'clients' | 'slots' | 'offers' | 'services' | 'finance';

const tabs: { id: Tab; name: string; icon: any }[] = [
  { id: 'dashboard', name: 'Дашборд', icon: ChartBarIcon },
  { id: 'calendar', name: 'Расписание', icon: CalendarIcon },
  { id: 'bookings', name: 'Записи', icon: ClockIcon },
  { id: 'clients', name: 'Клиенты', icon: UsersIcon },
  { id: 'slots', name: 'Свободные окна', icon: ScissorsIcon },
  { id: 'offers', name: 'Предложения', icon: TagIcon },
  { id: 'services', name: 'Услуги', icon: GiftIcon },
  { id: 'finance', name: 'Финансы', icon: Cog6Icon },
];

export default function App() {
  const [active, setActive] = useState<Tab>('dashboard');

  const render = () => {
    switch(active) {
      case 'dashboard': return <Dashboard />;
      case 'calendar': return <Calendar />;
      case 'bookings': return <Bookings />;
      case 'clients': return <Clients />;
      case 'slots': return <Slots />;
      case 'offers': return <Offers />;
      case 'services': return <Services />;
      case 'finance': return <Finance />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-red-600">✨ Beauty Salon PRO</h1>
        </div>
      </header>
      <nav className="bg-white border-b sticky top-16 z-10 overflow-x-auto">
        <div className="max-w-7xl mx-auto px-4 flex space-x-4">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActive(tab.id)}
              className={`flex items-center space-x-2 py-3 px-2 border-b-2 text-sm font-medium whitespace-nowrap transition ${
                active === tab.id ? 'border-red-500 text-red-600' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              <span>{tab.name}</span>
            </button>
          ))}
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-8">{render()}</main>
    </div>
  );
}
