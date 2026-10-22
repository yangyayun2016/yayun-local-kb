'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LatestActivitySkeleton } from '@/components/latest-activity-skeleton';

const latestActivity = [
  { name: 'nippy.host', rank: 132, amount: '$14', time: 'just now' },
  { name: 'maltacasino.se', rank: 169, amount: '$7', time: 'just now' },
  { name: 'jobfast.co', rank: 233, amount: '$5', time: '2 minutes ago' },
  { name: 'outrank.so', rank: 1, amount: '$12,052', time: '3 minutes ago' },
  { name: 'aiapply.co', rank: 131, amount: '$14', time: '4 minutes ago' },
];

export function LatestActivity() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 500);
    return () => clearTimeout(timer);
  }, []);

  if (isLoading) return <LatestActivitySkeleton />;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <span className="relative flex size-1.5">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary opacity-75"></span>
            <span className="relative inline-flex size-1.5 rounded-full bg-primary"></span>
          </span>
          Latest activity
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {latestActivity.map((item, i) => (
            <div key={i} className="flex items-center justify-between text-sm min-w-0 gap-2">
              <div className="flex items-center gap-1 min-w-0 flex-1">
                <Image
                  src={`https://www.google.com/s2/favicons?domain=${item.name}&sz=32`}
                  alt={item.name}
                  width={16}
                  height={16}
                  className="rounded flex-shrink-0"
                  unoptimized
                />
                <span className="font-medium truncate">{item.name}</span>
                <Badge variant="outline" className="text-xs flex-shrink-0">
                  #{item.rank}
                </Badge>
                <span className="text-xs text-muted-foreground flex-shrink-0">·</span>
                <span className="text-xs text-muted-foreground flex-shrink-0">{item.amount}</span>
              </div>
              <span className="text-xs text-muted-foreground flex-shrink-0">{item.time}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
