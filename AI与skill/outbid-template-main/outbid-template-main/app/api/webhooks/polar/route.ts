import { Webhooks } from '@polar-sh/nextjs';
import { getSupabaseServerClient } from '@/lib/supabase/server';
import { invalidateLeaderboardCache } from '@/lib/leaderboard';

export const POST = Webhooks({
  webhookSecret: process.env.POLAR_WEBHOOK_SECRET!,
  onOrderPaid: async ({ data: order }) => {
    const metadata = order.metadata as { url?: string; name?: string; amountCents?: string };
    if (!metadata.url || !metadata.amountCents) return;

    const supabase = getSupabaseServerClient();
    const amountCents = Number(metadata.amountCents);

    await supabase
      .from('bids')
      .update({ status: 'paid' })
      .eq('polar_checkout_id', order.checkoutId ?? '');

    await supabase.from('leaderboard_entries').upsert(
      {
        url: metadata.url,
        name: metadata.name ?? new URL(metadata.url).hostname,
        bid_cents: amountCents,
        claimed_at: new Date().toISOString(),
      },
      { onConflict: 'url' }
    );

    await invalidateLeaderboardCache();
  },
});
