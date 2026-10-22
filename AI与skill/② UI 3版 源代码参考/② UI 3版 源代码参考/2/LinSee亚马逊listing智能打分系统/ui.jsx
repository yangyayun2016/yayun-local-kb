// === 共享 UI 组件 ===
const { useState, useEffect, useMemo, useRef } = React;

// 等级 chip
function GradeChip({ grade, size = 'md' }) {
  const tone = {
    'A++': { bg: 'oklch(0.94 0.06 160)', fg: 'oklch(0.30 0.10 160)', bd: 'oklch(0.70 0.13 160)' },
    'A+':  { bg: 'oklch(0.95 0.05 195)', fg: 'oklch(0.32 0.09 195)', bd: 'oklch(0.72 0.10 195)' },
    'A':   { bg: 'oklch(0.95 0.04 230)', fg: 'oklch(0.34 0.09 230)', bd: 'oklch(0.72 0.09 230)' },
    'B':   { bg: 'oklch(0.96 0.06 85)',  fg: 'oklch(0.40 0.11 70)',  bd: 'oklch(0.78 0.13 80)' },
    'C':   { bg: 'oklch(0.95 0.07 50)',  fg: 'oklch(0.42 0.13 35)',  bd: 'oklch(0.78 0.14 45)' },
    'D':   { bg: 'oklch(0.94 0.07 25)',  fg: 'oklch(0.42 0.15 25)',  bd: 'oklch(0.72 0.16 25)' },
    'U':   { bg: 'oklch(0.93 0.01 270)', fg: 'oklch(0.30 0.02 270)', bd: 'oklch(0.65 0.02 270)' },
  }[grade] || { bg: '#eee', fg: '#333', bd: '#ccc' };
  const dim = size === 'lg' ? { fz: 24, px: 14, py: 4, w: 56 } : size === 'sm' ? { fz: 11, px: 6, py: 1, w: 28 } : { fz: 13, px: 8, py: 2, w: 36 };
  return (
    <span className="grade-chip" style={{
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      minWidth: dim.w, padding: `${dim.py}px ${dim.px}px`,
      background: tone.bg, color: tone.fg, border: `1px solid ${tone.bd}`,
      borderRadius: 4, fontWeight: 700, fontSize: dim.fz, fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.02em',
    }}>{grade}</span>
  );
}

// 状态点
function Dot({ ok, warn }) {
  const c = ok ? 'oklch(0.65 0.13 155)' : warn ? 'oklch(0.75 0.13 75)' : 'oklch(0.62 0.18 25)';
  return <span style={{ display: 'inline-block', width: 7, height: 7, borderRadius: 99, background: c, boxShadow: `0 0 0 2px ${c}22` }} />;
}

// 进度条
function Bar({ value, max = 100, tone = 'primary', height = 6 }) {
  const pct = Math.min(100, (value / max) * 100);
  const colors = {
    primary: 'oklch(0.55 0.15 250)',
    good:    'oklch(0.65 0.13 155)',
    warn:    'oklch(0.72 0.14 75)',
    bad:     'oklch(0.62 0.18 25)',
  };
  return (
    <div style={{ width: '100%', height, background: 'var(--track)', borderRadius: 99, overflow: 'hidden' }}>
      <div style={{ width: `${pct}%`, height: '100%', background: colors[tone], transition: 'width 0.5s cubic-bezier(.2,.7,.2,1)' }} />
    </div>
  );
}

// 圆环
function Ring({ value, max = 120, size = 130, stroke = 10, label, sub }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.min(1, value / max);
  const tone = value > 100 ? 'oklch(0.65 0.13 155)' : value >= 85 ? 'oklch(0.62 0.13 195)' : value > 70 ? 'oklch(0.72 0.14 75)' : 'oklch(0.62 0.18 25)';
  return (
    <div style={{ position: 'relative', width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--track)" strokeWidth={stroke} />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={tone} strokeWidth={stroke}
          strokeDasharray={c} strokeDashoffset={c * (1 - pct)} strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.7s cubic-bezier(.2,.7,.2,1)' }} />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', lineHeight: 1 }}>
        <div style={{ fontSize: size * 0.30, fontWeight: 700, fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.03em' }}>{label ?? value}</div>
        {sub != null && <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>{sub}</div>}
      </div>
    </div>
  );
}

// 卡片
function Card({ title, right, children, pad = 18, style }) {
  return (
    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 10, ...style }}>
      {(title || right) && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--ink)', letterSpacing: '0.02em', textTransform: 'uppercase' }}>{title}</div>
          {right}
        </div>
      )}
      <div style={{ padding: pad }}>{children}</div>
    </div>
  );
}

// 标签
function Tag({ children, tone = 'neutral' }) {
  const tones = {
    neutral:  { bg: 'oklch(0.96 0.005 270)', fg: 'oklch(0.40 0.01 270)', bd: 'oklch(0.88 0.005 270)' },
    primary:  { bg: 'oklch(0.96 0.04 250)',  fg: 'oklch(0.40 0.13 250)', bd: 'oklch(0.85 0.07 250)' },
    success:  { bg: 'oklch(0.95 0.05 160)',  fg: 'oklch(0.36 0.10 160)', bd: 'oklch(0.82 0.10 160)' },
    warn:     { bg: 'oklch(0.96 0.06 80)',   fg: 'oklch(0.42 0.12 70)',  bd: 'oklch(0.85 0.12 80)' },
    danger:   { bg: 'oklch(0.95 0.06 25)',   fg: 'oklch(0.42 0.16 25)',  bd: 'oklch(0.82 0.13 25)' },
    info:     { bg: 'oklch(0.96 0.04 220)',  fg: 'oklch(0.40 0.10 220)', bd: 'oklch(0.85 0.08 220)' },
  };
  const t = tones[tone];
  return <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, padding: '2px 7px', fontSize: 11, fontWeight: 500, lineHeight: 1.5, background: t.bg, color: t.fg, border: `1px solid ${t.bd}`, borderRadius: 4 }}>{children}</span>;
}

// 国旗 / 市场
function Market({ code }) {
  return <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, fontWeight: 600, padding: '1px 5px', border: '1px solid var(--border)', borderRadius: 3, color: 'var(--muted)' }}>{code}</span>;
}

// 简易图标 (使用 unicode 或 svg)
const Icon = {
  Search: (p) => <svg width="14" height="14" viewBox="0 0 16 16" fill="none" {...p}><circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.4"/><path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/></svg>,
  Filter: (p) => <svg width="14" height="14" viewBox="0 0 16 16" fill="none" {...p}><path d="M2 3h12M4 8h8M6 13h4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/></svg>,
  Down: (p) => <svg width="10" height="10" viewBox="0 0 10 10" fill="none" {...p}><path d="M2 4l3 3 3-3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  Right: (p) => <svg width="10" height="10" viewBox="0 0 10 10" fill="none" {...p}><path d="M4 2l3 3-3 3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  Check: (p) => <svg width="12" height="12" viewBox="0 0 12 12" fill="none" {...p}><path d="M2.5 6.5l2.5 2.5 4.5-5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  X: (p) => <svg width="12" height="12" viewBox="0 0 12 12" fill="none" {...p}><path d="M3 3l6 6M9 3l-6 6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/></svg>,
  Warn: (p) => <svg width="12" height="12" viewBox="0 0 12 12" fill="none" {...p}><path d="M6 2l5 8H1l5-8z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/><circle cx="6" cy="8.3" r="0.6" fill="currentColor"/><path d="M6 5v2.4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/></svg>,
  Refresh: (p) => <svg width="13" height="13" viewBox="0 0 14 14" fill="none" {...p}><path d="M12 7a5 5 0 1 1-1.5-3.5M12 1.5V4.5h-3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  Spark: (p) => <svg width="12" height="12" viewBox="0 0 12 12" fill="none" {...p}><path d="M6 1l1.4 3.6L11 6 7.4 7.4 6 11 4.6 7.4 1 6l3.6-1.4L6 1z" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round"/></svg>,
  Dot:  (p) => <span style={{ display:'inline-block', width: 4, height: 4, borderRadius: 99, background: 'currentColor' }} {...p} />,
  External: (p) => <svg width="11" height="11" viewBox="0 0 12 12" fill="none" {...p}><path d="M5 2H2v8h8V7M7 2h3v3M5 7L10 2" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  Doc: (p) => <svg width="13" height="13" viewBox="0 0 14 14" fill="none" {...p}><path d="M3 1h6l3 3v9H3V1z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/><path d="M9 1v3h3M5 7h4M5 9.5h4M5 5h2" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/></svg>,
};

// 占位图 (条纹SVG)
function PlaceholderImage({ tint = '#ddd', label = '产品图', width, height = 100 }) {
  return (
    <div style={{ width: width || '100%', height, background: tint, position: 'relative', overflow: 'hidden', border: '1px solid var(--border)', borderRadius: 4 }}>
      <svg width="100%" height="100%" style={{ position: 'absolute', inset: 0, opacity: 0.18 }}>
        <defs>
          <pattern id={`s-${label.replace(/\s/g,'')}`} width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="10" stroke="white" strokeWidth="6" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill={`url(#s-${label.replace(/\s/g,'')})`} />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 9, fontFamily: 'JetBrains Mono, monospace', color: 'rgba(255,255,255,0.85)', mixBlendMode: 'difference', textAlign: 'center', padding: 4 }}>{label}</div>
    </div>
  );
}

Object.assign(window, { GradeChip, Dot, Bar, Ring, Card, Tag, Market, Icon, PlaceholderImage });
