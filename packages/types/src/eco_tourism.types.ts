// اکوتوریسم
export interface Destination {
  id: string;
  name: string;
  carryingCapacity: number;
  ecoScore: number;
}

export interface Booking {
  id: string;
  destinationId: string;
  date: string;
  status: 'pending' | 'confirmed' | 'cancelled';
}
