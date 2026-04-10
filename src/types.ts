export interface Booking {
  id: string;
  clientName: string;
  serviceName: string;
  masterName: string;
  date: string;
  time: string;
  price: number;
  status: string;
}

export interface Client {
  id: string;
  name: string;
  phone: string;
  visits: number;
  spent: number;
}
