// ==================================================================
//  LinSee · Dashboard (portfolio overview)
// ==================================================================

window.PageDashboard = function PageDashboard({ weights, onSelect, lang, tweaks }) {
  const portfolio = LS_PORTFOLIO.map(asin => {
    const p = LS_PRODUCTS[asin];
    const total = calcTotal(p.scores, weights);
    return { ...p, total };
  });
  const avg = Math.round(portfolio.reduce((s, p) => s + p.total, 0) / portfolio.length);
  const aCount = portfolio.filter(p => p.total >= 85).length;
  const issues = portfolio.filter(p => p.total < 70).length;
  const tplus = calcTotal(LS_PRODUCTS["B0CHX2F5QN"].scores, weights);

  return (
    <>
      <div className="page-accent" />
      <div className="page-h">
        <div>
          <h1 className="page-title">{lang === "zh" ? <>我的 <em>Listing</em> 质量仪表盘</> : <>My Listing Quality <em>Dashboard</em></>}</h1>
          <div className="page-sub">
            {lang === "zh"
              ? "基于亚马逊 CDQv3 指标体系（ASCS · 2025.03），实时监测你在 US 站点的 4 个 ASIN 的目录数据完整性、准确性与一致性。"
              : "Powered by Amazon CDQv3 (ASCS · Mar 2025). Live monitor on 4 US-marketplace ASINs."}
          </div>
        </div>
        <div className="row">
          <button className="btn btn-sm"><Icon d={Icons.refresh} size={12} /> {lang === "zh" ? "重新拉取" : "Refresh"}</button>
          <button className="btn btn-sm"><Icon d={Icons.download} size={12} /> {lang === "zh" ? "导出 CSV" : "Export CSV"}</button>
          <button className="btn btn-primary btn-sm"><Icon d={Icons.plus} size={12} /> {lang === "zh" ? "添加 ASIN" : "Add ASIN"}</button>
        </div>
      </div>

      {/* Top stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14, marginBottom: 22 }}>
        <div className="stat">
          <span className="stat-label">{lang === "zh" ? "组合平均分" : "Portfolio avg."}</span>
          <div className="stat-value" style={{ display: "flex", alignItems: "center", gap: 10 }}>
            {avg}
            <GradeBadge score={avg} />
          </div>
          <div className="stat-delta up">▲ 3.2 {lang === "zh" ? "相比上周" : "vs last week"}</div>
        </div>
        <div className="stat">
          <span className="stat-label">{lang === "zh" ? "A 级 Listing" : "A-grade listings"}</span>
          <div className="stat-value">{aCount}<span style={{ fontSize: 14, color: "var(--ink-mute)", marginLeft: 6 }}>/ {portfolio.length}</span></div>
          <div className="stat-delta">{lang === "zh" ? "保持稳定" : "stable"}</div>
        </div>
        <div className="stat">
          <span className="stat-label">{lang === "zh" ? "需优先处理" : "Needs attention"}</span>
          <div className="stat-value" style={{ color: issues > 0 ? "var(--red)" : "var(--ink)" }}>{issues}</div>
          <div className="stat-delta down">▼ 1 {lang === "zh" ? "本周处理" : "fixed this week"}</div>
        </div>
        <div className="stat">
          <span className="stat-label">{lang === "zh" ? "竞品标杆分" : "Top competitor"}</span>
          <div className="stat-value" style={{ color: "var(--accent)" }}>{tplus}</div>
          <div className="stat-delta">Anker · B0CHX2F5QN</div>
        </div>
      </div>

      {/* Main row: table + side */}
      <div style={{ display: "grid", gridTemplateColumns: "1.7fr 1fr", gap: 18 }}>
        <div className="card">
          <div className="card-h">
            <h3>{lang === "zh" ? "Listing 列表" : "Listings"}</h3>
            <span className="muted">· {portfolio.length} ASIN · CDQv3 · {lang === "zh" ? "权重已自定义" : "Weights customized"}</span>
            <div style={{ marginLeft: "auto" }}>
              <div className="seg">
                <button className="active">{lang === "zh" ? "按分数" : "By score"}</button>
                <button>{lang === "zh" ? "按更新时间" : "By updated"}</button>
                <button>{lang === "zh" ? "按类目" : "By category"}</button>
              </div>
            </div>
          </div>
          <table className="tbl">
            <thead>
              <tr>
                <th style={{ width: 68 }}>{lang === "zh" ? "产品" : "Item"}</th>
                <th>{lang === "zh" ? "标题 / ASIN" : "Title / ASIN"}</th>
                <th style={{ width: 80 }}>{lang === "zh" ? "评级" : "Grade"}</th>
                <th style={{ width: 170 }}>{lang === "zh" ? "总分" : "Score"}</th>
                <th style={{ width: 110 }}>{lang === "zh" ? "趋势" : "Trend"}</th>
                <th style={{ width: 90 }}>{lang === "zh" ? "最近更新" : "Updated"}</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.sort((a, b) => b.total - a.total).map(p => (
                <tr key={p.asin} onClick={() => onSelect(p.asin)}>
                  <td><div className="thumb" /></td>
                  <td>
                    <div style={{ fontWeight: 500, marginBottom: 2, fontSize: 13.5,
                          display: "-webkit-box", WebkitLineClamp: 1, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                      {p.title}
                    </div>
                    <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                      <span className="asin-mono">{p.asin}</span>
                      <span className="asin-mono">· {p.marketplace}</span>
                      <span className="asin-mono">· {p.brand}</span>
                    </div>
                  </td>
                  <td><GradeBadge score={p.total} /></td>
                  <td><ScoreBar value={p.total} /></td>
                  <td><Sparkline data={LS_TREND} width={90} height={28} /></td>
                  <td className="asin-mono">{p.updated.slice(5)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
          <div className="card">
            <div className="card-h">
              <h3>{lang === "zh" ? "维度表现" : "By dimension"}</h3>
              <span className="muted">· {lang === "zh" ? "组合平均" : "avg."}</span>
            </div>
            <div className="card-body">
              {LS_RUBRIC.map(r => {
                const a = Math.round(portfolio.reduce((s, p) => s + (p.scores[r.key] || 0), 0) / portfolio.length);
                return (
                  <div key={r.key} style={{ marginBottom: 12 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                      <span style={{ fontSize: 13 }}>{lang === "zh" ? r.name : r.nameEn}
                        <span className="asin-mono" style={{ marginLeft: 6, color: "var(--ink-faint)" }}>w{weights[r.key]}</span>
                      </span>
                      <span className="asin-mono">{a}</span>
                    </div>
                    <div className="bar"><div className={`bar-fill ${barClassOf(a)}`} style={{ width: `${a}%` }} /></div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="card">
            <div className="card-h">
              <h3>{lang === "zh" ? "最近动态" : "Recent activity"}</h3>
            </div>
            <div className="card-body" style={{ paddingTop: 8 }}>
              {LS_ACTIVITY.map((a, i) => (
                <div key={i} className="log">
                  <div className="log-dot" />
                  <div>
                    <div className="log-time">{a.t} · {a.a}</div>
                    <div className="log-msg" dangerouslySetInnerHTML={{ __html: a.msg }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
