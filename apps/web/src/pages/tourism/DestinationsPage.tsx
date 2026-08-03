import { useState, useMemo } from 'react';
import { Search, MapPin, Star, Clock, Users, ArrowRight, Filter } from 'lucide-react';

interface Destination {
  id: string; name: string; nameFa: string; region: string; regionFa: string;
  image: string; rating: number; reviews: number; duration: string;
  price: string; tags: string[]; description: string; bestSeason: string;
  altitude: string; difficulty: 'easy' | 'moderate' | 'challenging'; groupSize: string;
}

const DESTINATIONS: Destination[] = [
  { id: 'd1', name: 'Alamut Valley', nameFa: 'X^U^U^U X^e^]^_^R', region: 'Qazvin', regionFa: 'X^R^T^W^_', image: '', rating: 4.8, reviews: 234, duration: 'X^S Y^T^T', price: 'X^Q,_X^U^P^P,_^P^P^P', tags: ['X^R^a^Y^U^X^_', 'X^g^[^Y^c^R^M^V^Y^W^X^_', 'X^f^T^T^_^T^Y^W^X^_'], description: 'X^R^e^c^P ^T^a^X^S^X^T^Y^e^X^P ^W^X^W Y^e X^f^T^T^c^T^b^T^W^_ X^e^b^U^V^b^X^W', bestSeason: 'X^[^T^a^Y X^T X^[^a^X^U^R', altitude: 'X^Q,_X^P^P^P X^e^R^Y', difficulty: 'moderate' as const, groupSize: 'X^U-X^Q^Q X^c^R^Y' },
  { id: 'd2', name: 'Masal Forest', nameFa: 'X^R^c^V^e^P X^e^a^U^P^e', region: 'Gilan', regionFa: 'X^V^_^P^e', image: '', rating: 4.9, reviews: 312, duration: 'X^Q Y^T^T', price: 'X^Q,_X^[^P^P,_^P^P^P', tags: ['X^R^c^V^e', 'X^_^e^V^a^R', 'X^c^f^a^U^_'], description: 'X^e^P^M^V^U^Y^R^_ X^Y^Y^a^U^_ Y^e^V^a^R^a^R X^e^a^U^P^e', bestSeason: 'X^[^T^a^Y X^T X^R^a^X^e^R^a^P^e', altitude: 'X^Q,_X^Q^P^P X^e^R^Y', difficulty: 'easy' as const, groupSize: 'X^W-X^P^U X^c^R^Y' },
  { id: 'd3', name: 'Lut Desert', nameFa: 'X^f^T^U^Y X^e^T^R', region: 'Kerman', regionFa: 'X^f^Y^X^P^e', image: '', rating: 4.7, reviews: 189, duration: 'X^U Y^T^T', price: 'X^S,_X^Q^P^P,_^P^P^P', tags: ['X^f^T^U^Y', 'X^c^R^T^T', 'X^e^P^R^a^P^U^T^Y^X^P'], description: 'X^W^P^V^M^R^Y^e X^c^R^V^T X^R^e^P X^f^e^T^R^a^T^P^_ X^U^M^P^X^V^X^U^R', bestSeason: 'X^[^a^X^U^R X^T X^T^X^e^R^a^P^e', altitude: 'X^Q^P^P X^e^R^Y', difficulty: 'challenging' as const, groupSize: 'X^U-X^[ X^c^R^Y' },
];
