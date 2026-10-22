import { NextRequest, NextResponse } from 'next/server';
import { polar } from '@/lib/polar';
import { getSupabaseServerClient } from '@/lib/supabase/server';

// Statement descriptor: Polar is a Merchant of Record, so the billing descriptor
// shown on credit card statements is configured in your Polar dashboard under
// Organization Settings > Statement Descriptor. Set it to something recognisable
// like "OUTBID" or "OUTBID*LISTING" so customers don't dispute the charge.

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => null);
  const url: string | undefined = body?.url;
  const name: string | undefined = body?.name;
  const bid: number | undefined = body?.bid;

  if (!url || !bid || bid < 1) {
    return NextResponse.json(
      { error: 'A URL and a bid of at least $1 are required' },
      { status: 400 }
    );
  }

  let hostname: string;
  try {
    hostname = new URL(url).hostname;
  } catch {
    return NextResponse.json({ error: 'Invalid URL' }, { status: 400 });
  }

  const productId = process.env.POLAR_PRODUCT_ID;
  if (!productId) {
    return NextResponse.json({ error: 'Polar product is not configured' }, { status: 500 });
  }

  const amountCents = Math.round(bid * 100);
  const supabase = getSupabaseServerClient();

  const { data: existing } = await supabase
    .from('leaderboard_entries')
    .select('bid_cents')
    .eq('url', url)
    .maybeSingle();

  if (existing && existing.bid_cents >= amountCents) {
    return NextResponse.json(
      { error: 'Your bid must beat the current bid for this listing' },
      { status: 400 }
    );
  }

  const entryName = name || hostname;

  const checkout = await polar.checkouts.create({
    products: [productId],
    prices: {
      [productId]: [{ amountType: 'fixed', priceAmount: amountCents, priceCurrency: 'usd' }],
    },
    successUrl: `${process.env.NEXT_PUBLIC_SITE_URL}/?claimed=1`,
    metadata: {
      url,
      name: entryName,
      amountCents: String(amountCents),
      description: `Outbid listing: ${entryName}`,
    },
  });

  const { error } = await supabase.from('bids').insert({
    entry_url: url,
    entry_name: entryName,
    amount_cents: amountCents,
    polar_checkout_id: checkout.id,
    status: 'pending',
  });

  if (error) {
    return NextResponse.json({ error: 'Failed to record bid' }, { status: 500 });
  }

  return NextResponse.json({ checkoutUrl: checkout.url });
}
