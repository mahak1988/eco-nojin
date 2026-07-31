import React from 'react';
import { Palette, Moon, Sun, Languages } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const ThemeSelector: React.FC = () => {
  const { theme, setTheme, toggleRTL, isRTL } = useTheme();

  const themes = [
    { id: 'light', name: 'روشن', icon: Sun },
    { id: 'dark', name: 'تاریک', icon: Moon },
    { id: 'eco', name: 'اکو', icon: Palette },
    { id: 'ocean', name: 'اقیانوس', icon: Palette },
    { id: 'sunset', name: 'غروب', icon: Palette },
  ];

  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        <Palette className="w-4 h-4" />
        <span className="text-sm font-medium">تم:</span>
      </div>
      
      <div className="flex flex-wrap gap-2">
        {themes.map(({ id, name, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setTheme(id)}
            className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-xs capitalize ${
              theme === id
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted hover:bg-muted/80'
            }`}
            aria-label={`انتخاب تم ${name}`}
          >
            <Icon className="w-3 h-3" />
            {name}
          </button>
        ))}
      </div>
      
      <button
        onClick={toggleRTL}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs ${
          isRTL
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted hover:bg-muted/80'
        }`}
        aria-label={isRTL ? 'تغییر به چینش چپ به راست' : 'تغییر به چینش راست به چپ'}
      >
        <Languages className="w-3 h-3" />
        {isRTL ? 'RTL' : 'LTR'}
      </button>
    </div>
  );
};

export default ThemeSelector;