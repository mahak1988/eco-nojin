'use client';

import { useEffect, useRef } from 'react';

export interface InteractiveMapProps {
  className?: string;
  center?: [number, number];
  zoom?: number;
  children?: React.ReactNode;
}

export function InteractiveMap({ 
  className = '', 
  center = [32.4279, 53.6880], 
  zoom = 5,
  children 
}: InteractiveMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    console.log('InteractiveMap initialized', { center, zoom });
  }, [center, zoom]);

  return (
    <div ref={mapRef} className={`w-full h-full ${className}`}>
      <div className="flex items-center justify-center h-full bg-gray-100">
        <p className="text-gray-500">Interactive Map - Placeholder</p>
        {children}
      </div>
    </div>
  );
}

export default InteractiveMap;