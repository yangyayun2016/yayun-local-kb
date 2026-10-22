import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { MobileLayout } from '@/components/mobile-layout';

export default function AboutPage() {
  return (
    <MobileLayout>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1">
          <div className="max-w-4xl mx-auto px-4 py-16">
            <h1 className="text-4xl font-bold tracking-tight">About</h1>
            <div className="mt-8 space-y-6 text-muted-foreground">
              <p>
                Outbid is a public leaderboard. There are no ads, no API keys, and no revenue share.
                You pay to stand above everyone else. Rank is the bid — nothing else.
              </p>
              <p>
                The concept is simple: place a bid, get a rank. The higher your bid, the higher your
                rank. If someone outbids you, you can pay the difference to reclaim your spot.
              </p>
              <p>
                This project was built as a simple side project to explore the concept of paid
                rankings and real-time leaderboards.
              </p>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    </MobileLayout>
  );
}
