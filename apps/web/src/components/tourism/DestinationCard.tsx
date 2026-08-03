import { MapPin, Star, Clock, Users } from 'lucide-react';

interface DestinationCardProps {
  name: string; nameFa: string; region: string; regionFa: string;
  rating: number; reviews: number; duration: string; price: string;
  tags: string[]; description: string;
  altitude: string; difficulty: 'easy' | 'moderate' | 'challenging';
  groupSize: string; onView?: () => void;
}

const DIFFICULTY = {
  easy: { color: 'bg-emerald-100 text-emerald-700', label: 'آسان' },
  moderate: { color: 'bg-amber-100 text-amber-700', label: 'متوسط' },
  challenging: { color: 'bg-red-100 text-red-700', label: 'چالش‌برانگیز' },
};

export default function DestinationCard(props: DestinationCardProps) {
  return (
    <div className="group bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-stone-100 hover:border-emerald-200">
      <div className="h-48 bg-gradient-to-br from-emerald-400 to-teal-600 relative">
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
          <span className="text-white/80 text-sm">{props.regionFa}</span>
        </div>
      </div>
      <div className="p-5">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-lg font-bold text-stone-800">{props.nameFa}</h3>
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
            <span className="text-sm font-medium">{props.rating}</span>
          </div>
        </div>
        <p className="text-sm text-stone-600 mb-3 line-clamp-2">{props.description}</p>
        <div className="flex flex-wrap gap-2 mb-3">
          {props.tags.map(t => <span key={t} className="text-xs px-2 py-1 rounded-full bg-emerald-50 text-emerald-600">{t}</span>)}
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs text-stone-500 mb-4">
          <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{props.duration}</span>
          <span className="flex items-center gap-1"><Users className="w-3 h-3" />{props.groupSize}</span>
          <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{props.altitude}</span>
          <span className={'px-2 py-0.5 rounded-full text-xs ' + DIFFICULTY[props.difficulty].color}>{DIFFICULTY[props.difficulty].label}</span>
        </div>
        <div className="flex items-center justify-between pt-3 border-t border-stone-100">
          <span className="text-emerald-700 font-bold">{props.price} تومان</span>
          <button onClick={props.onView} className="text-sm font-medium text-emerald-600 hover:text-emerald-700">مشاهده تور</button>
        </div>
      </div>
    </div>
  );
}
