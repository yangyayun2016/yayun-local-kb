import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { MobileLayout } from '@/components/mobile-layout';

export default function StatsPage() {
  return (
    <MobileLayout>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1">
          <div className="max-w-4xl mx-auto px-4 py-16">
            <h1 className="text-4xl font-bold tracking-tight">Live Stats</h1>
            <p className="text-muted-foreground mt-4">Real-time statistics for the leaderboard.</p>
            <div className="mt-8 grid grid-cols-2 sm:grid-cols-4 gap-4">
              {/* Add stat cards here */}
            </div>
          </div>
        </main>
        <Footer />
      </div>
    </MobileLayout>
  );
}
