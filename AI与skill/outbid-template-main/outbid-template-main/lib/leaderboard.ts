import { redis } from '@/lib/redis';
import { getSupabaseServerClient } from '@/lib/supabase/server';
import type { LeaderboardItem } from '@/lib/leaderboard-data';

const CACHE_KEY = 'leaderboard:v1';
const CACHE_TTL_SECONDS = 30;

// Cache-aside: serve from Redis when possible so the leaderboard page
// (read constantly) doesn't hit Postgres on every request. The cache is
// invalidated the moment a bid is paid, so it's never more than
// CACHE_TTL_SECONDS stale even without an explicit invalidation.
export async function getLeaderboard(): Promise<LeaderboardItem[]> {
  const cached = await redis.get<LeaderboardItem[]>(CACHE_KEY);
  if (cached) return cached;

  const items = await fetchLeaderboardFromDatabase();
  await redis.set(CACHE_KEY, items, { ex: CACHE_TTL_SECONDS });
  return items;
}

export async function invalidateLeaderboardCache() {
  await redis.del(CACHE_KEY);
}

async function fetchLeaderboardFromDatabase(): Promise<LeaderboardItem[]> {
  const supabase = getSupabaseServerClient();
  const { data, error } = await supabase
    .from('leaderboard_entries')
    .select('url, name, bid_cents, clicks, claimed_at')
    .order('bid_cents', { ascending: false });

  if (error) throw error;

  return (data ?? []).map((row, index) => ({
    rank: index + 1,
    name: row.name,
    bid: row.bid_cents / 100,
    url: row.url,
    clicks: row.clicks,
    time: formatRelativeTime(row.claimed_at),
  }));
}

function formatRelativeTime(iso: string) {
  const minutes = Math.floor((Date.now() - new Date(iso).getTime()) / 60_000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes} minute${minutes === 1 ? '' : 's'} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours === 1 ? '' : 's'} ago`;
  const days = Math.floor(hours / 24);
  return days === 1 ? 'yesterday' : `${days} days ago`;
}
