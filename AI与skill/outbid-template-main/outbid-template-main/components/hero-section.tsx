'use client';

import { useState, forwardRef } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Globe, Minus, Plus } from 'lucide-react';

const XIcon = ({ className, ...props }: React.ComponentProps<'svg'>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="currentColor"
    className={className}
    {...props}
  >
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
  </svg>
);

interface HeroSectionProps {
  ref?: React.Ref<HTMLInputElement>;
  selectedRank?: number;
  selectedBid?: number;
  onBidChange?: (bid: number) => void;
}

export const HeroSection = forwardRef<HTMLInputElement, HeroSectionProps>(function HeroSection(
  { selectedRank, selectedBid, onBidChange },
  ref
) {
  const [url, setUrl] = useState('');
  const [bid, setBid] = useState(selectedBid || 1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleClaim = async () => {
    if (!url.trim()) {
      setError('Enter a URL or @handle first');
      return;
    }
    const normalizedUrl = /^https?:\/\//.test(url) ? url : `https://${url.replace(/^@/, '')}`;

    setIsSubmitting(true);
    setError(null);
    try {
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: normalizedUrl, bid }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || 'Something went wrong');
        return;
      }
      window.location.href = data.checkoutUrl;
    } catch {
      setError('Something went wrong');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDecrease = () => {
    const newBid = Math.max(1, bid - 1);
    setBid(newBid);
    onBidChange?.(newBid);
  };

  const handleIncrease = () => {
    const newBid = Math.min(100000, bid + 1);
    setBid(newBid);
    onBidChange?.(newBid);
  };

  const displayRank = selectedRank || 1;
  const bidText = `$${bid.toLocaleString()}`;
  const isHandle = url.startsWith('@');

  return (
    <section className="text-center overflow-hidden">
      <div className="inline-flex items-center gap-2 bg-muted px-2.5 py-1 rounded-full text-xs mb-6">
        <span className="relative flex size-1.5">
          <span className="absolute inline-flex size-full animate-ping rounded-full bg-green-500 opacity-75"></span>
          <span className="relative inline-flex size-1.5 rounded-full bg-green-500"></span>
        </span>
        2,934 online
      </div>
      <h1 className="text-3xl sm:text-5xl md:text-6xl font-bold tracking-tight">
        Claim #{displayRank} for{' '}
        <div className="inline-flex items-center gap-1 sm:gap-2 text-primary align-middle justify-center flex-wrap">
          <button
            type="button"
            onClick={handleDecrease}
            className="inline-flex items-center justify-center size-8 sm:size-10 rounded-full bg-primary/10 hover:bg-primary/20 transition-colors flex-shrink-0"
          >
            <Minus className="h-4 w-4 sm:h-5 sm:w-5" />
          </button>
          <input
            type="text"
            value={bidText}
            onChange={(e) => {
              const num = parseInt(e.target.value.replace(/[^0-9]/g, ''), 10);
              if (!isNaN(num) && num >= 1 && num <= 100000) {
                setBid(num);
                onBidChange?.(num);
              }
            }}
            className="bg-transparent border-none outline-none text-primary text-center font-bold text-3xl sm:text-5xl md:text-6xl p-0 focus:ring-0 w-auto min-w-0"
            size={bidText.length}
          />
          <button
            type="button"
            onClick={handleIncrease}
            className="inline-flex items-center justify-center size-8 sm:size-10 rounded-full bg-primary/10 hover:bg-primary/20 transition-colors flex-shrink-0"
          >
            <Plus className="h-4 w-4 sm:h-5 sm:w-5" />
          </button>
        </div>
      </h1>
      <p className="text-muted-foreground mt-3 text-base sm:text-lg max-w-3xl mx-auto px-4">
        New spots start at $1. Paying less than the #1 price still puts you on the board at whatever
        place that bid can take.
      </p>

      <div className="mt-8 max-w-lg mx-auto px-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1 min-w-0">
            {isHandle ? (
              <XIcon className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            ) : (
              <Globe className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            )}
            <Input
              ref={ref}
              placeholder="Your product's URL or @handle"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="pl-11 h-12 text-base rounded-full min-w-0"
            />
          </div>
          <Button
            size="lg"
            className="h-12 px-8 rounded-full shrink-0"
            onClick={handleClaim}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Redirecting…' : 'Claim'}
          </Button>
        </div>
        {error && <p className="text-xs text-destructive mt-2">{error}</p>}
        <p className="text-xs text-muted-foreground mt-2">
          Already on the list? Enter the same URL or @handle and up your bid — you only pay the
          difference.
        </p>
      </div>
    </section>
  );
});
