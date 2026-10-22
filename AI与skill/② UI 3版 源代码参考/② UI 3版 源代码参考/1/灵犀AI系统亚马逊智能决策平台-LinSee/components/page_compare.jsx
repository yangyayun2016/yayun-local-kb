// ==================================================================
//  LinSee · Compare page (1v1 / 1vN)
// ==================================================================

window.PageCompare = function PageCompare({ weights, lang }) {
  const [mode, setMode] = useState("multi");  // "solo" (1v1) or "multi"
  const mine = "B09GTRVJQM";
  const [rivals, setRivals] = useState(["B0CHX2F5QN", "B0B2D77YB8", "B08L5WRWNW"]);
  const items = mode === "solo" ? [mine, rivals[0]] : [mine, ...rivals];
  const list = items.map(a => {
    const p = LS_PRODUCTS[a];
    return { ...p, total: calcTotal(p.scores, weights) };
  });
  const bestPerDim = LS_RUBRIC.reduce((m, r) => {
    m[r.key] = Math.max(...list.map(x => x.scores[r.key]));
    return m;
  }, {});

  const cols = `220px repeat(${list.length}, 1fr)`;

  return (
    <>
      <div className="page-accent" />
      <div className="page-h">
        <div>
          <h1 className="page-title">{lang === "zh" ? <>竞品 <em>对比分析</em></> : <>Competitor <em>Compare</em></>}</h1>
          <div className="page-sub">
            {lang === "zh"
              ? "把你的 Listing 与 1–5 个竞品 ASIN 并排放在 CDQv3 指标上，快速看出差距与机会点。"
              : "Side-by-side CDQv3 diff between your ASIN and up to 5 competitors."}
          </div>
        </div>
        <div className="row">
          <div className="seg">
            <button className={mode === "solo" ? "active" : ""} onClick={() => setMode("solo")}>1 vs 1</button>
            <button className={mode === "multi" ? "active" : ""} onClick={() => setMode("multi")}>1 vs N</button>
          </div>
          <button className="btn btn-sm"><Icon d={Icons.plus} size={12} /> {lang === "zh" ? "添加竞品" : "Add rival"}</button>
          <button className="btn btn-primary btn-sm"><Icon d={Icons.download} size={12} /> {lang === "zh" ? "导出对比报告" : "Export report"}</button>
        </div>
      </div>

      {/* Hero row: title + score ring per column */}
      <div className="cmp-grid" style={{ marginBottom: 18 }}>
        <div className="cmp-head" style={{ gridTemplateColumns: cols }}>
          <div className="cmp-cell label">{lang === "zh" ? "维度 \\ 产品" : "Dim \\ Product"}</div>
          {list.map((p, i) => (
            <div key={p.asin} className={`cmp-cell ${i === 0 ? "hero" : ""}`} style={{ background: i === 0 ? undefined : "var(--bg-soft)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                <div className="thumb" style={{ width: 36, height: 36 }} />
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: 11, color: "var(--ink-mute)", fontWeight: 500 }}>
                    {i === 0 ? (lang === "zh" ? "我的 ASIN" : "MINE") : `${lang === "zh" ? "竞品" : "RIVAL"} ${i}`}
                  </div>
                  <div style={{ fontWeight: 500, fontSize: 13 }}>{p.brand}</div>
                </div>
              </div>
              <div style={{ fontSize: 12, color: "var(--ink-soft)", lineHeight: 1.35, marginBottom: 6,
                   display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                {p.title}
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span className="asin-mono">{p.asin}</span>
                <GradeBadge score={p.total} />
                <span className="asin-mono" style={{ fontSize: 16, fontWeight: 600, color: "var(--ink)" }}>{p.total}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Component rows */}
        {LS_RUBRIC.map(r => (
          <div key={r.key} className="cmp-row" style={{ gridTemplateColumns: cols }}>
            <div className="cmp-cell label">
              <div>{lang === "zh" ? r.name : r.nameEn}</div>
              <div className="asin-mono" style={{ color: "var(--ink-faint)", fontSize: 11 }}>weight {weights[r.key]}%</div>
            </div>
            {list.map((p, i) => {
              const s = p.scores[r.key];
              const isBest = s === bestPerDim[r.key] && list.length > 1;
              const diff = i === 0 ? 0 : s - list[0].scores[r.key];
              return (
                <div key={p.asin} className="cmp-cell" style={{ background: i === 0 ? "var(--primary-soft)" : undefined }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                    <span className="asin-mono" style={{ fontSize: 15, fontWeight: 600, color: "var(--ink)" }}>{s}</span>
                    <GradeBadge score={s} />
                    {isBest && <span className="tag tag-pass">{lang === "zh" ? "最佳" : "Best"}</span>}
                    {i !== 0 && diff !== 0 && (
                      <span className="asin-mono" style={{ color: diff > 0 ? "var(--red)" : "var(--green)", fontSize: 11 }}>
                        {diff > 0 ? "+" : ""}{diff}
                      </span>
                    )}
                  </div>
                  <div className="bar"><div className={`bar-fill ${barClassOf(s)}`} style={{ width: `${s}%` }} /></div>
                </div>
              );
            })}
          </div>
        ))}

        {/* Commerce meta row */}
        <div className="cmp-row" style={{ gridTemplateColumns: cols, background: "var(--bg-soft)" }}>
          <div className="cmp-cell label">{lang === "zh" ? "商业指标" : "Commerce"}</div>
          {list.map((p, i) => (
            <div key={p.asin} className="cmp-cell" style={{ background: i === 0 ? "var(--primary-soft)" : undefined }}>
              <div style={{ fontSize: 12, color: "var(--ink-soft)", display: "flex", flexDirection: "column", gap: 3 }}>
                <span>{p.price} · ★ {p.stars}</span>
                <span className="muted">{p.reviews.toLocaleString()} reviews</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Gap insights */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
        <div className="card">
          <div className="card-h"><h3>{lang === "zh" ? "差距洞察" : "Gap insights"}</h3></div>
          <div className="card-body">
            {[
              { dim: lang === "zh" ? "标题质量" : "Title", gap: -18, note: lang === "zh" ? "Anker 用了 'Bio-Nylon' 与 '240W' 两个高密度关键词，你可借鉴结构" : "Anker leverages 'Bio-Nylon' and '240W' keywords" },
              { dim: lang === "zh" ? "变体质量" : "Variation", gap: -18, note: lang === "zh" ? "Anker 的变体家族一致性为 90+，建议同步 2-Pack 模板" : "Anker keeps variation family at 90+; sync 2-Pack template" },
              { dim: lang === "zh" ? "结构化属性" : "Attributes", gap: -8, note: lang === "zh" ? "Compatible Devices / Data Transfer Rate 是主要缺项" : "Compatible Devices / Transfer Rate are the main gaps" },
            ].map((x, i) => (
              <div key={i} style={{ padding: "10px 0", borderBottom: i < 2 ? "1px solid var(--rule-soft)" : "none" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                  <span className="tag tag-fail">{x.dim}</span>
                  <span className="asin-mono" style={{ color: "var(--red)" }}>{x.gap}</span>
                  <span className="muted" style={{ fontSize: 12 }}>{lang === "zh" ? "对比 Anker" : "vs. Anker"}</span>
                </div>
                <div style={{ fontSize: 13, color: "var(--ink-soft)" }}>{x.note}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <div className="card-h"><h3>{lang === "zh" ? "雷达叠加" : "Radar overlay"}</h3></div>
          <div className="card-body" style={{ display: "grid", placeItems: "center" }}>
            <RadarOverlay list={list} />
            <div style={{ display: "flex", gap: 18, marginTop: 10, fontSize: 12 }}>
              {list.slice(0, 3).map((p, i) => (
                <span key={p.asin} className="legend-item">
                  <span className="legend-dot" style={{ background: ["var(--primary)", "var(--accent)", "var(--gold)"][i] }} />
                  {p.brand}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

function RadarOverlay({ list }) {
  const size = 260, cx = size / 2, cy = size / 2, R = size / 2 - 30;
  const N = LS_RUBRIC.length;
  const colors = ["var(--primary)", "var(--accent)", "var(--gold)", "var(--blue)", "var(--red)"];

  const ptsFor = (scores) => LS_RUBRIC.map((a, i) => {
    const ang = -Math.PI / 2 + (i * 2 * Math.PI) / N;
    const v = (scores[a.key] ?? 0) / 100;
    return `${cx + Math.cos(ang) * R * v},${cy + Math.sin(ang) * R * v}`;
  }).join(" ");

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {[0.25, 0.5, 0.75, 1].map((k, i) => (
        <polygon key={i} fill="none" stroke="var(--rule)" strokeWidth="1"
          points={LS_RUBRIC.map((_, j) => {
            const ang = -Math.PI / 2 + (j * 2 * Math.PI) / N;
            return `${cx + Math.cos(ang) * R * k},${cy + Math.sin(ang) * R * k}`;
          }).join(" ")} />
      ))}
      {list.slice(0, 3).map((p, i) => (
        <polygon key={p.asin} fill={colors[i]} fillOpacity={i === 0 ? 0.25 : 0.1}
                 stroke={colors[i]} strokeWidth={i === 0 ? 2 : 1.2} points={ptsFor(p.scores)} />
      ))}
      {LS_RUBRIC.map((a, i) => {
        const ang = -Math.PI / 2 + (i * 2 * Math.PI) / N;
        const x = cx + Math.cos(ang) * (R + 14);
        const y = cy + Math.sin(ang) * (R + 14);
        return <text key={i} x={x} y={y} fontSize="10.5" fill="var(--ink-mute)"
                     textAnchor="middle" dominantBaseline="middle">{a.name}</text>;
      })}
    </svg>
  );
}
