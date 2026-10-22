'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Flame } from 'lucide-react';
import { TrendingSkeleton } from '@/components/trending-skeleton';

const trendingItems = [
  { name: 'outrank.so', clicks: '869 clicks/h' },
  { name: 'orynth.dev', clicks: '671 clicks/h' },
  { name: 'shows.farm', clicks: '288 clicks/h' },
  { name: 'foundrlist.com', clicks: '277 clicks/h' },
  { name: 'redreplier.com', clicks: '265 clicks/h' },
];

export function TrendingSection() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 500);
    return () => clearTimeout(timer);
  }, []);

  if (isLoading) return <TrendingSkeleton />;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Flame className="h-4 w-4 text-muted-foreground" />
          Trending right now
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {trendingItems.map((item, i) => (
            <div key={i} className="flex items-center justify-between text-sm min-w-0">
              <div className="flex items-center gap-2 min-w-0">
                <Image
                  src={`https://www.google.com/s2/favicons?domain=${item.name}&sz=32`}
                  alt={item.name}
                  width={16}
                  height={16}
                  className="rounded flex-shrink-0"
                  unoptimized
                />
                <span className="font-medium truncate">{item.name}</span>
              </div>
              <Badge variant="secondary" className="text-xs flex-shrink-0">
                {item.clicks}
              </Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
