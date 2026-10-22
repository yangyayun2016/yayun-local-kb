// ==================================================================
//  LinSee · shared icons + small components
// ==================================================================
const { useState, useEffect, useMemo, useRef } = React;

// --- Icons (inline SVG so no assets needed) ---
const Icon = ({ d, size = 16, fill = "none", stroke = "currentColor", sw = 1.6, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={fill} stroke={stroke}
       strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" className={className}>
    {typeof d === "string" ? <path d={d} /> : d}
  </svg>
);

const Icons = {
  dash: <><path d="M3 12h7V3H3z"/><path d="M14 21h7V10h-7z"/><path d="M14 7h7V3h-7z"/><path d="M3 21h7v-5H3z"/></>,
  diag: <><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/><path d="M11 8v6"/><path d="M8 11h6"/></>,
  cmp:  <><path d="M4 5h7"/><path d="M4 12h7"/><path d="M4 19h7"/><path d="m15 5 5 5-5 5"/><path d="M20 19h-5"/></>,
  hist: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
  kb:   <><path d="M4 5a2 2 0 0 1 2-2h11v16H6a2 2 0 0 0-2 2z"/><path d="M4 5v14"/><path d="M8 7h6"/><path d="M8 11h6"/></>,
  team: <><circle cx="9" cy="8" r="3"/><path d="M4 20c0-3 2.5-5 5-5s5 2 5 5"/><circle cx="17" cy="9" r="2.5"/><path d="M14 20c0-2 1.5-4 4-4s4 2 4 4"/></>,
  star: <path d="m12 3 2.6 5.6 6 .9-4.4 4.2 1 6.1L12 17l-5.3 2.8 1-6.1L3.4 9.5l6-.9z"/>,
  plus: <><path d="M12 5v14"/><path d="M5 12h14"/></>,
  search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></>,
  bell: <><path d="M6 8a6 6 0 0 1 12 0v5l2 3H4l2-3z"/><path d="M10 19a2 2 0 0 0 4 0"/></>,
  moon: <path d="M20 14.5A8 8 0 1 1 9.5 4a6 6 0 0 0 10.5 10.5z"/>,
  sun: <><circle cx="12" cy="12" r="4"/><path d="M12 3v2"/><path d="M12 19v2"/><path d="M3 12h2"/><path d="M19 12h2"/><path d="m5.6 5.6 1.4 1.4"/><path d="m17 17 1.4 1.4"/><path d="m5.6 18.4 1.4-1.4"/><path d="m17 7 1.4-1.4"/></>,
  check: <path d="m5 12 4 4 10-10"/>,
  x: <><path d="M6 6l12 12"/><path d="M18 6L6 18"/></>,
  alert: <><path d="M12 8v5"/><path d="M12 16.5v.5"/><circle cx="12" cy="12" r="9"/></>,
  chevronR: <path d="m9 6 6 6-6 6"/>,
  chevronD: <path d="m6 9 6 6 6-6"/>,
  share: <><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 10.5 6.8-4"/><path d="m8.6 13.5 6.8 4"/></>,
  download: <><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M4 21h16"/></>,
  settings: <><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.6 1.6 0 0 0 .4 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-1.8-.4 1.6 1.6 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.6 1.6 0 0 0-1-1.5 1.6 1.6 0 0 0-1.8.4l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0 .4-1.8 1.6 1.6 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.6 1.6 0 0 0 1.5-1 1.6 1.6 0 0 0-.4-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 1.8.4H9a1.6 1.6 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.8-.4l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.4 1.8V9a1.6 1.6 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1z"/></>,
  play: <path d="M6 4v16l14-8z"/>,
  refresh: <><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/><path d="M3 21v-5h5"/></>,
  user: <><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.5 3.5-7 8-7s8 2.5 8 7"/></>,
  crown: <><path d="m3 18 2-10 5 5 2-8 2 8 5-5 2 10z"/><path d="M3 21h18"/></>,
  edit: <><path d="M15 4l5 5-11 11H4v-5z"/><path d="m13 6 5 5"/></>,
  copy: <><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></>,
  external: <><path d="M14 4h6v6"/><path d="M20 4 10 14"/><path d="M20 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h4"/></>,
  note: <><path d="M5 3h10l4 4v14H5z"/><path d="M15 3v4h4"/><path d="M9 12h6"/><path d="M9 16h6"/></>,
};

// --- Grade helpers ---
window.gradeOf = function(score) {
  if (score === null || score === undefined || isNaN(score)) return { g: "U", cls: "grade-u", colorKey: "u", label: "未分级 · 政策违规" };
  if (score > 100) return { g: "A++", cls: "grade-a", colorKey: "a", label: "极高 · 加分" };
  if (score >= 92)  return { g: "A+", cls: "grade-a", colorKey: "a", label: "高质量" };
  if (score >= 85)  return { g: "A", cls: "grade-a", colorKey: "a", label: "尚可" };
  if (score >= 70)  return { g: "B", cls: "grade-b", colorKey: "b", label: "低质量 · 无缺陷" };
  if (score > 0)    return { g: "C", cls: "grade-c", colorKey: "c", label: "低质量 · 非严重缺陷" };
  if (score === 0)  return { g: "D", cls: "grade-d", colorKey: "d", label: "低质量 · 严重缺陷" };
  return { g: "U", cls: "grade-u", colorKey: "u", label: "未分级" };
};

window.barClassOf = function(v) {
  if (v >= 85) return "good";
  if (v >= 70) return "ok";
  if (v > 0) return "bad";
  return "worst";
};

window.calcTotal = function(scores, weights) {
  const ws = weights || LS_RUBRIC.reduce((m, r) => (m[r.key] = r.weight, m), {});
  let coreW = 0, coreSum = 0, bonus = 0;
  for (const r of LS_RUBRIC) {
    const w = Number(ws[r.key] ?? r.weight);
    const s = Number(scores?.[r.key] ?? 0);
    if (r.bonus) { bonus += (s * w) / 100; }
    else { coreW += w; coreSum += s * w; }
  }
  const core = coreW === 0 ? 0 : coreSum / coreW;
  return Math.round(core + bonus);
};

// --- Ring (circular progress) ---
window.ScoreRing = function({ score, size = 180 }) {
  const r = size / 2 - 10;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - Math.max(0, Math.min(100, score)) / 100);
  const g = gradeOf(score);
  const color = getComputedStyle(document.documentElement)
    .getPropertyValue(`--grade-${g.colorKey}`) || "#c06138";
  return (
    <div className="ring" style={{ width: size, height: size }}>
      <svg>
        <circle className="ring-bg" cx={size/2} cy={size/2} r={r} />
        <circle className="ring-fg" cx={size/2} cy={size/2} r={r}
                stroke={color.trim()}
                strokeDasharray={c} strokeDashoffset={offset} />
      </svg>
      <div className="ring-text">
        <div className="ring-val">{score}<sup>/120</sup></div>
        <div className="ring-sub">{g.g} · {g.label}</div>
      </div>
    </div>
  );
};

// --- Grade badge ---
window.GradeBadge = function({ score, size = "sm" }) {
  const g = gradeOf(score);
  if (size === "lg") {
    const bg = getComputedStyle(document.documentElement).getPropertyValue(`--grade-${g.colorKey}`).trim();
    return <div className="grade-big" style={{ background: bg }}>{g.g}</div>;
  }
  return <span className={`grade ${g.cls}`}>{g.g}</span>;
};

// --- Bar ---
window.ScoreBar = function({ value, label }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <div className="bar" style={{ flex: 1 }}>
        <div className={`bar-fill ${barClassOf(value)}`} style={{ width: `${value}%` }} />
      </div>
      <div className="asin-mono" style={{ minWidth: 38, textAlign: "right" }}>{value}</div>
    </div>
  );
};

// --- Radar chart (SVG, 6 axes) ---
window.Radar = function({ scores, size = 260 }) {
  const cx = size / 2, cy = size / 2;
  const R = size / 2 - 36;
  const axes = LS_RUBRIC;
  const N = axes.length;
  const pts = axes.map((a, i) => {
    const angle = -Math.PI / 2 + (i * 2 * Math.PI) / N;
    const v = (scores?.[a.key] ?? 0) / 100;
    const x = cx + Math.cos(angle) * R * v;
    const y = cy + Math.sin(angle) * R * v;
    return `${x},${y}`;
  }).join(" ");
  const rings = [0.25, 0.5, 0.75, 1];

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {rings.map((k, i) => (
        <polygon key={i} fill="none" stroke="var(--rule)" strokeWidth="1"
          points={axes.map((_, j) => {
            const ang = -Math.PI / 2 + (j * 2 * Math.PI) / N;
            return `${cx + Math.cos(ang) * R * k},${cy + Math.sin(ang) * R * k}`;
          }).join(" ")} />
      ))}
      {axes.map((a, i) => {
        const ang = -Math.PI / 2 + (i * 2 * Math.PI) / N;
        const x = cx + Math.cos(ang) * R;
        const y = cy + Math.sin(ang) * R;
        return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="var(--rule)" strokeWidth="1" />;
      })}
      <polygon fill="rgba(192,97,56,.18)" stroke="var(--primary)" strokeWidth="1.5" points={pts} />
      {axes.map((a, i) => {
        const ang = -Math.PI / 2 + (i * 2 * Math.PI) / N;
        const x = cx + Math.cos(ang) * (R + 18);
        const y = cy + Math.sin(ang) * (R + 18);
        return (
          <text key={i} x={x} y={y} fontSize="11" fill="var(--ink-mute)"
                textAnchor="middle" dominantBaseline="middle"
                style={{ fontFamily: "var(--f-sans)" }}>
            {a.name}
          </text>
        );
      })}
    </svg>
  );
};

// --- Sparkline ---
window.Sparkline = function({ data, width = 120, height = 32, stroke = "var(--primary)" }) {
  if (!data || !data.length) return null;
  const vals = data.map(d => d.s);
  const min = Math.min(...vals) - 2;
  const max = Math.max(...vals) + 2;
  const range = max - min || 1;
  const step = width / (data.length - 1);
  const pts = data.map((d, i) => `${i * step},${height - ((d.s - min) / range) * height}`).join(" ");
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <polyline fill="none" stroke={stroke} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" points={pts} />
    </svg>
  );
};

// --- Check list row ---
window.CheckRow = function({ type, text }) {
  const iconMap = {
    pass: Icons.check,
    warn: Icons.alert,
    fail: Icons.x,
  };
  return (
    <div className={`check ${type}`}>
      <Icon d={iconMap[type]} className="check-icon" size={14} />
      <span>{text}</span>
    </div>
  );
};

window.Icons = Icons;
window.Icon = Icon;
