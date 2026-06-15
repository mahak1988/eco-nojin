import { apiClient } from '../core/instance';
import { Destination, Booking } from '@econojin/types';

export const ecoTourismApi = {
  getDestinations: () => apiClient.get<Destination[]>('/eco-tourism/destinations'),
  createBooking: (data: Partial<Booking>) => apiClient.post<Booking>('/eco-tourism/bookings', data),
};
