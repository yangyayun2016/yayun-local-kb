'use client';

import Image from 'next/image';
import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { MobileLayout } from '@/components/mobile-layout';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ExternalLink } from 'lucide-react';

const friends = [
  {
    name: 'outbid.lol',
    description: 'The original pay-to-rank website leaderboard.',
    tag: 'The OG',
    icon: 'https://outbid.lol/icon.png',
  },
  {
    name: 'topapp.lol',
    description: 'An App Store leaderboard where the highest bidder wins.',
    tag: null,
    icon: 'https://topapp.lol/favicon.png',
  },
  {
    name: 'whosetheboss.lol',
    description: 'A leaderboard where one company gets to wear the crown.',
    tag: null,
    icon: 'https://whosetheboss.lol/icon.png',
  },
  {
    name: 'xbid.lol',
    description: 'A public leaderboard for X accounts, ranked by bids.',
    tag: null,
    icon: 'https://xbid.lol/icon.svg',
  },
  {
    name: 'dontbid.lol',
    description: 'A product directory ranked by how much each listing has bid.',
    tag: null,
    icon: 'https://dontbid.lol/icon.svg',
  },
  {
    name: 'warmap.lol',
    description: 'A world map where companies bid to conquer countries.',
    tag: null,
    icon: 'https://warmap.lol/icon.svg',
  },
  {
    name: 'vibewar.lol',
    description: 'A pay-to-rank battlefield for vibecoded apps and SaaS.',
    tag: null,
    icon: 'https://vibewar.lol/icon.png',
  },
  {
    name: 'payluck.lol',
    description: 'A startup directory where luck sets the listing price.',
    tag: null,
    icon: 'https://payluck.lol/icon.png',
  },
  {
    name: 'tweetbid.lol',
    description: 'A pay-to-rank leaderboard for tweets.',
    tag: null,
    icon: 'https://tweetbid.lol/favicon.svg',
  },
  {
    name: 'rankbid.lol',
    description: 'A leaderboard where bigger bids buy better positions.',
    tag: null,
    icon: 'https://rankbid.lol/assets/logo-sqr.png',
  },
  {
    name: 'uprank.lol',
    description: "A website leaderboard ranked by each site's lifetime total.",
    tag: null,
    icon: 'https://uprank.lol/favicon.ico',
  },
  {
    name: 'bidanything.lol',
    description: 'A leaderboard where anything with a link can bid for the top.',
    tag: null,
    icon: 'https://bidanything.lol/favicon.ico',
  },
  {
    name: 'toplocal.lol',
    description: 'A pay-to-rank leaderboard with a top spot for every country.',
    tag: null,
    icon: 'https://toplocal.lol/icon.svg',
  },
];

export default function FriendsPage() {
  return (
    <MobileLayout>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1">
          <div className="max-w-4xl mx-auto px-4 py-16">
            <h1 className="text-4xl font-bold tracking-tight">Outbid & friends</h1>
            <p className="text-muted-foreground mt-2">
              A list of .lol domains inspired by outbid.lol.
            </p>
            <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {friends.map((friend) => (
                <a
                  key={friend.name}
                  href={`https://${friend.name}?utm_source=outbid&utm_medium=friends&utm_campaign=reciprocal`}
                  target="_blank"
                  rel="sponsored noopener noreferrer"
                  className="group"
                >
                  <Card className="p-4 h-full transition-colors hover:bg-muted/50">
                    <div className="flex items-start gap-3.5">
                      <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-muted border border-border/40">
                        <Image
                          alt={friend.name}
                          className="size-full object-contain p-1"
                          src={friend.icon}
                          width={36}
                          height={36}
                          unoptimized
                        />
                      </span>
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="font-semibold underline decoration-border/60 underline-offset-4 transition group-hover:decoration-foreground group-hover:text-primary flex items-center gap-1">
                            {friend.name}
                            <ExternalLink className="size-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                          </span>
                          {friend.tag && (
                            <Badge
                              variant="secondary"
                              className="text-[10px] font-bold uppercase tracking-wider"
                            >
                              {friend.tag}
                            </Badge>
                          )}
                        </div>
                        <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
                          {friend.description}
                        </p>
                      </div>
                    </div>
                  </Card>
                </a>
              ))}
            </div>
          </div>
        </main>
        <Footer />
      </div>
    </MobileLayout>
  );
}
