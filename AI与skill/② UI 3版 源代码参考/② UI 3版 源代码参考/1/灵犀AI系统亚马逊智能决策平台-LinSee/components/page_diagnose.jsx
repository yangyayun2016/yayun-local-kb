// ==================================================================
//  LinSee · Diagnose detail (CDQv3 细化版)
// ==================================================================

window.PageDiagnose = function PageDiagnose({ asin, weights, lang, setPage }) {
  const p = LS_PRODUCTS[asin] || LS_PRODUCTS["B09GTRVJQM"];
  const total = calcTotal(p.scores, weights);
  const [tab, setTab] = useState("detail");
  const [openKey, setOpenKey] = useState("title");

  return (
    <>
      <div className="page-accent" />
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 14, fontSize: 12.5, color: "var(--ink-mute)" }}>
        <button className="btn btn-ghost btn-sm" onClick={() => setPage("dashboard")}>
          <Icon d={Icons.chevronR} size={12} style={{ transform: "rotate(180deg)" }} /> {lang === "zh" ? "返回列表" : "Back"}
        </button>
        <span>·</span>
        <span>{lang === "zh" ? "上次诊断" : "Last audit"}: 2026-04-16 14:32</span>
        <span>·</span>
        <span>CDQv3 · TQS · IAI · 总分 100–120</span>
      </div>

      <div className="listing-hero" style={{ marginBottom: 18 }}>
        <div className="thumb-lg" />
        <div style={{ minWidth: 0 }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4 }}>
            <span className="tag tag-info">{p.marketplace}</span>
            <span className="tag">{p.brand}</span>
            <span className="asin-mono">{p.asin}</span>
          </div>
          <h2 className="listing-title-big">{p.title}</h2>
          <div className="listing-meta">
            <span><b>{p.category}</b></span>
            <span>{p.price}</span>
            <span>★ {p.stars} · {p.reviews.toLocaleString()} {lang === "zh" ? "条评价" : "reviews"}</span>
            <span>{p.titleLen} chars</span>
          </div>
        </div>
        <div style={{ display: "flex", gap: 8, flexDirection: "column", alignItems: "flex-end" }}>
          <button className="btn btn-sm"><Icon d={Icons.share} size={12} /> {lang === "zh" ? "分享链接" : "Share"}</button>
          <button className="btn btn-sm"><Icon d={Icons.external} size={12} /> {lang === "zh" ? "打开源页" : "Open on Amazon"}</button>
          <button className="btn btn-sm"><Icon d={Icons.refresh} size={12} /> {lang === "zh" ? "重新诊断" : "Re-run"}</button>
        </div>
      </div>

      {/* Policy flags banner */}
      <PolicyBanner p={p} lang={lang} />

      <div style={{ display: "grid", gridTemplateColumns: "260px 1fr 280px", gap: 18, marginBottom: 18 }}>
        <div className="card" style={{ display: "grid", placeItems: "center", padding: 20 }}>
          <ScoreRing score={total} size={170} />
          <div style={{ marginTop: 8, fontSize: 12.5, color: "var(--ink-mute)" }}>
            {lang === "zh" ? "CDQv3 加权总分" : "CDQv3 weighted total"}
          </div>
        </div>
        <div className="card">
          <div className="card-h">
            <h3>{lang === "zh" ? "七维诊断图谱" : "Seven-axis radar"}</h3>
            <span className="muted">· {lang === "zh" ? "相对历史均值" : "vs historical mean"}</span>
          </div>
          <div className="radar-wrap"><Radar scores={p.scores} size={230} /></div>
        </div>
        <div className="card">
          <div className="card-h"><h3>{lang === "zh" ? "分数构成" : "Contribution"}</h3></div>
          <div className="card-body" style={{ paddingTop: 10 }}>
            {LS_RUBRIC.map(r => {
              const s = p.scores[r.key] ?? 0;
              const contrib = Math.round((s * weights[r.key]) / 100);
              return (
                <div key={r.key} style={{ display: "flex", justifyContent: "space-between", fontSize: 12.5, padding: "5px 0", borderBottom: "1px dashed var(--rule-soft)" }}>
                  <span>{lang === "zh" ? r.name : r.nameEn}
                    <span className="asin-mono" style={{ color: "var(--ink-faint)", marginLeft: 6 }}>{r.bonus ? "加分" : `×${weights[r.key]}%`}</span>
                  </span>
                  <span className="asin-mono">{s} → <b style={{ color: r.bonus ? "var(--accent)" : "var(--primary)" }}>+{contrib}</b></span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="tabs">
        {[
          { k: "detail", l: lang === "zh" ? "七维细则" : "Rubric" },
          { k: "find",   l: lang === "zh" ? "可发现性（预览）" : "Findability" },
          { k: "raw",    l: lang === "zh" ? "原始数据" : "Raw" },
          { k: "anno",   l: lang === "zh" ? "团队批注" : "Notes" },
          { k: "log",    l: lang === "zh" ? "历史快照" : "Snapshots" },
        ].map(t => (
          <button key={t.k} className={`tab ${tab === t.k ? "active" : ""}`} onClick={() => setTab(t.k)}>{t.l}</button>
        ))}
      </div>

      {tab === "detail" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 320px", gap: 18 }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {LS_RUBRIC.map((r, i) => (
              <DimCard key={r.key} r={r} idx={i} p={p} weight={weights[r.key]} lang={lang}
                open={openKey === r.key} onToggle={() => setOpenKey(openKey === r.key ? null : r.key)} />
            ))}
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
            <div className="card">
              <div className="card-h"><h3>{lang === "zh" ? "优先级行动清单" : "Priority actions"}</h3></div>
              <div className="card-body">
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {[
                    { lvl: "high", t: "去掉标题末尾冗余颜色", imp: "+6", dim: "标题" },
                    { lvl: "high", t: "修复变体信息冗余（严重缺陷）", imp: "+8", dim: "变体" },
                    { lvl: "high", t: "统一 '6ft / 6 Foot' 单位制", imp: "+4", dim: "变体" },
                    { lvl: "mid",  t: "补 Compatible Devices + Data Rate", imp: "+4", dim: "属性" },
                    { lvl: "mid",  t: "升级 Premium A+", imp: "+10", dim: "图片" },
                    { lvl: "low",  t: "Bullet 按 0-1-3 原则重组", imp: "+2", dim: "五点" },
                  ].map((x, i) => (
                    <div key={i} style={{ display: "flex", gap: 10, alignItems: "center", padding: "8px 10px", background: "var(--bg-soft)", borderRadius: 6, border: "1px solid var(--rule-soft)" }}>
                      <span className={`tag ${x.lvl === "high" ? "tag-fail" : x.lvl === "mid" ? "tag-warn" : "tag-info"}`}>{x.dim}</span>
                      <span style={{ flex: 1, fontSize: 13 }}>{x.t}</span>
                      <span className="asin-mono" style={{ color: "var(--green)" }}>{x.imp}</span>
                    </div>
                  ))}
                </div>
                <hr className="hr" />
                <div style={{ fontSize: 12, color: "var(--ink-mute)", lineHeight: 1.6 }}>
                  {lang === "zh"
                    ? "若全部采纳，预计总分从 84 → 93（A 级）。改动由 ASCS 目录团队 72h 内复核。"
                    : "Adopting all will raise 84 → 93 (A). ASCS reviews within 72h."}
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-h"><h3>{lang === "zh" ? "12 周趋势" : "12-week trend"}</h3></div>
              <div className="card-body">
                <Sparkline data={LS_TREND} width={260} height={60} />
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--ink-mute)", marginTop: 4, fontFamily: "var(--f-mono)" }}>
                  {LS_TREND.map(d => <span key={d.d}>{d.d.slice(3)}</span>)}
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-h"><h3>{lang === "zh" ? "TQS · IAI 指数" : "TQS · IAI"}</h3></div>
              <div className="card-body">
                <div style={{ fontSize: 12.5, display: "flex", flexDirection: "column", gap: 8 }}>
                  <Meter label="TQS 标题质量" v={p.sub?.title?.tqs ?? 78} suf="%" />
                  <Meter label="IAI 属性综合" v={Math.round((p.sub?.attr?.iai ?? 0.48) * 100)} suf="%" threshold={40} />
                  <Meter label="完整性(≥3 属性)" v={Math.round((p.sub?.title?.complete ?? 66))} suf="%" threshold={60} />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {tab === "find" && <FindabilityTab lang={lang} />}

      {tab === "raw" && (
        <div className="card"><div className="card-body" style={{ padding: 0 }}>
          <table className="tbl">
            <thead><tr><th>{lang === "zh" ? "字段" : "Field"}</th><th>{lang === "zh" ? "数值" : "Value"}</th><th>{lang === "zh" ? "状态" : "Status"}</th></tr></thead>
            <tbody>
              <tr><td style={{ width: 200 }}>Brand</td><td>{p.brand}</td><td><span className="tag tag-pass">Valid</span></td></tr>
              <tr><td>Title</td><td style={{ maxWidth: 500 }}>{p.title}</td><td><span className="tag tag-warn">Redundant suffix</span></td></tr>
              <tr><td>Title length</td><td className="asin-mono">{p.titleLen} / 200</td><td><span className="tag tag-pass">OK</span></td></tr>
              <tr><td>Category (leaf)</td><td>{p.category}</td><td><span className="tag tag-pass">Correct</span></td></tr>
              <tr><td>Product Type (PT)</td><td className="asin-mono">CABLE_USB_C_TO_C</td><td><span className="tag tag-pass">Leaf</span></td></tr>
              <tr><td>Bullet points</td><td>5 / 5</td><td><span className="tag tag-pass">OK</span></td></tr>
              <tr><td>A+ content</td><td>Basic, 3 modules</td><td><span className="tag tag-warn">Upgrade to Premium</span></td></tr>
              <tr><td>Variation theme</td><td>Color + Length</td><td><span className="tag tag-warn">Redundant</span></td></tr>
              <tr><td>Images</td><td>7 (MAIN, PT01-PT06)</td><td><span className="tag tag-pass">OK</span></td></tr>
              <tr><td>Compatible Devices</td><td><span className="muted">— missing —</span></td><td><span className="tag tag-fail">Missing</span></td></tr>
              <tr><td>Data Transfer Rate</td><td><span className="muted">— missing —</span></td><td><span className="tag tag-fail">Missing</span></td></tr>
              <tr><td>Restricted keywords</td><td>None detected</td><td><span className="tag tag-pass">Clean</span></td></tr>
            </tbody>
          </table>
        </div></div>
      )}

      {tab === "anno" && <AnnotationsView lang={lang} />}
      {tab === "log" && <SnapshotsView lang={lang} />}
    </>
  );
};

// ---------- Policy banner ----------
function PolicyBanner({ p, lang }) {
  const flags = (typeof LS_FLAGS !== 'undefined' && LS_FLAGS[0]) || { items: [] };
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 18 }}>
      <div className="card" style={{ borderColor: "var(--rule)", background: "var(--bg-soft)" }}>
        <div className="card-h" style={{ background: "transparent" }}>
          <span className="grade grade-a" style={{ background: "var(--green)" }}>✓</span>
          <h3 style={{ color: "var(--green)" }}>{lang === "zh" ? "策略违规 · 全通过" : "Policy · All pass"}</h3>
          <span className="muted" style={{ marginLeft: "auto", fontSize: 11.5 }}>{lang === "zh" ? "一票否决项" : "Hard gate"}</span>
        </div>
        <div className="card-body" style={{ paddingTop: 8 }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 5, fontSize: 12.5, color: "var(--ink-soft)" }}>
            {flags.items.map((t, i) => (
              <div key={i} style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
                <Icon d={Icons.check} size={12} style={{ color: "var(--green)", marginTop: 3, flexShrink: 0 }} />
                <span>{t}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="card" style={{ borderColor: "var(--primary-soft)", background: "linear-gradient(135deg, var(--primary-soft), var(--bg-card))" }}>
        <div className="card-h" style={{ background: "transparent" }}>
          <Icon d={Icons.alert} size={14} style={{ color: "var(--primary)" }} />
          <h3>{lang === "zh" ? "可发现性加分通道" : "Findability channels"}</h3>
          <span className="tag tag-warn" style={{ marginLeft: "auto" }}>2026-05-01</span>
        </div>
        <div className="card-body" style={{ paddingTop: 8 }}>
          <div style={{ fontSize: 12, color: "var(--ink-mute)", marginBottom: 8 }}>
            {lang === "zh" ? "即将上线，当前为预览。你的 ASIN 已命中 6/7 条加分项，预估额外 +42.5。" : "Launching 2026-05-01. Your ASIN hits 6/7 boosters."}
          </div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <span className="tag tag-pass">叶节点 +10</span>
            <span className="tag tag-pass">搜索关键词 +5</span>
            <span className="tag tag-pass">A+ 页面 +12.5</span>
            <span className="tag tag-pass">品牌前置 +5</span>
            <span className="tag tag-pass">Bullet ≥3 +5</span>
            <span className="tag tag-pass">1 主 3 魅力 +10</span>
            <span className="tag tag-fail">关键属性全填 −2.5</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------- Dimension card (细化) ----------
function DimCard({ r, idx, p, weight, lang, open, onToggle }) {
  const score = p.scores[r.key] ?? 0;
  const sub = p.sub?.[r.key] || {};
  const checks = p.checks?.[r.key] || [];
  const suggestion = p.suggestions?.[r.key];
  const tier = sub.tier;

  // Header bar color reflects grade
  const g = gradeOf(score);

  return (
    <div className="card">
      <div style={{ padding: "16px 18px", borderBottom: open ? "1px solid var(--rule)" : "none", display: "flex", alignItems: "center", gap: 14, cursor: "pointer" }} onClick={onToggle}>
        <div className="dim-num" style={{ fontSize: 18, minWidth: 26 }}>{String(idx + 1).padStart(2, "0")}</div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <div className="dim-name" style={{ margin: 0 }}>
              {lang === "zh" ? r.name : r.nameEn}
              <span className="w">· {lang === "zh" ? "权重" : "weight"} {weight}%</span>
            </div>
            {tier && <span className={`grade grade-${tier.toLowerCase()}`}>{tier}</span>}
            {r.key === "title" && sub.tqs != null && <span className="tag tag-info">TQS {sub.tqs}%</span>}
            {r.key === "attr" && sub.iai != null && <span className="tag tag-info">IAI {sub.iai.toFixed(2)}</span>}
          </div>
          <div className="dim-desc" style={{ margin: 0 }}>{lang === "zh" ? r.desc : r.descEn}</div>
          <div style={{ marginTop: 8, maxWidth: 420 }}><ScoreBar value={score} /></div>
        </div>
        <div className="dim-score" style={{ minWidth: 74 }}>
          {score}<small>{r.bonus ? " 加分" : "/100"}</small>
        </div>
        <Icon d={open ? Icons.chevronD : Icons.chevronR} size={14} style={{ color: "var(--ink-mute)" }} />
      </div>

      {open && (
        <div style={{ padding: "14px 20px 18px" }}>
          {/* Formula bar */}
          {r.formula && (
            <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 12px", marginBottom: 12, background: "var(--bg-soft)", border: "1px dashed var(--rule)", borderRadius: 6 }}>
              <span style={{ fontSize: 10, textTransform: "uppercase", letterSpacing: ".1em", color: "var(--ink-faint)" }}>公式</span>
              <code style={{ fontFamily: "var(--f-mono)", fontSize: 11.5, color: "var(--primary)", flex: 1 }}>{r.formula}</code>
              <span className="tag" style={{ fontSize: 10 }}>{r.maxHint}</span>
            </div>
          )}

          {/* Tier ladder for Title */}
          {r.key === "title" && <TitleTierRibbon tier={tier} lang={lang} rubric={r} />}

          {/* Sub-rules matrix */}
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 11, letterSpacing: ".1em", textTransform: "uppercase", color: "var(--ink-mute)", marginBottom: 8 }}>
              {lang === "zh" ? "子规则细则" : "Sub-rules"}
            </div>
            <SubRulesGrid subs={r.subs} vals={sub} lang={lang} dimKey={r.key} />
          </div>

          {/* Attr: RAI / Band grouping */}
          {r.key === "attr" && (
            <div style={{ display: "flex", gap: 10, marginBottom: 12, flexWrap: "wrap" }}>
              <span className="tag tag-info">RAI Top 6: 6/6 填写</span>
              <span className="tag tag-pass">Band A 覆盖率 89%</span>
              <span className="tag tag-warn">Band B 覆盖率 64%</span>
              <span className="tag tag-pass">IAI = {sub.iai} ≥ 0.4 达标 +10</span>
              {sub.top4 && <span className="tag tag-pass">Top 4 相关属性最优 +5</span>}
            </div>
          )}

          {/* Image scoring matrix */}
          {r.matrix && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 11, letterSpacing: ".1em", textTransform: "uppercase", color: "var(--ink-mute)", marginBottom: 8 }}>
                {lang === "zh" ? "四象限判定矩阵" : "Scoring matrix"}
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 8 }}>
                {r.matrix.map((m, i) => (
                  <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 10, padding: "8px 10px", background: "var(--bg-soft)", border: "1px solid var(--rule)", borderRadius: 6, fontSize: 12 }}>
                    <span style={{ color: "var(--ink-soft)" }}>{m.cond}</span>
                    <span className={`tag tag-${m.tone}`} style={{ fontFamily: "var(--f-mono)" }}>{m.score}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Variation criticals */}
          {r.key === "vari" && (r.criticalsStrict || r.criticalsSoft) && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 12 }}>
              <CritBox title="严重缺陷（立即采取行动）" color="var(--red)"
                items={r.criticalsStrict || []} hits={sub.hitStrict || []} dot="●" />
              <CritBox title="非严重缺陷（随时间改善）" color="var(--gold)"
                items={r.criticalsSoft || []} hits={sub.hitSoft || []} dot="□" />
            </div>
          )}

          {/* Checks */}
          {checks.length > 0 && (
            <div className="checks" style={{ marginBottom: 10 }}>
              {checks.map((c, j) => <CheckRow key={j} {...c} />)}
            </div>
          )}

          {suggestion && (
            <div className="suggest">
              <b>{lang === "zh" ? "改进方向 · " : "Direction · "}</b>
              {suggestion}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ---------- Sub rules grid ----------
function SubRulesGrid({ subs, vals, lang, dimKey }) {
  if (!subs) return null;
  const [openIdx, setOpenIdx] = useState(-1);
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 8 }}>
      {subs.map((s, i) => {
        const v = vals[s.k];
        const score = typeof v === "number" ? (v <= 1 ? Math.round(v * 100) : v) : (v === true ? 100 : null);
        const pass = score == null ? null : score >= 85;
        const warn = score != null && score >= 60 && score < 85;
        const open = openIdx === i;
        return (
          <div key={s.k} style={{
            padding: "8px 10px",
            border: "1px solid var(--rule)",
            borderLeft: `3px solid ${pass ? "var(--green)" : warn ? "var(--gold)" : score != null ? "var(--red)" : "var(--rule)"}`,
            borderRadius: 6,
            background: "var(--bg-soft)",
          }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 6, cursor: "pointer" }}
                 onClick={() => setOpenIdx(open ? -1 : i)}>
              <div>
                <div style={{ fontSize: 12.5, fontWeight: 500, color: "var(--ink)", marginBottom: 2, display: "flex", alignItems: "center", gap: 6 }}>
                  <span>{lang === "zh" ? s.n : s.nEn}</span>
                  {s.band && <span className="asin-mono" style={{ color: s.band === "RAI" ? "var(--primary)" : s.band === "A" ? "var(--accent)" : "var(--gold)", fontSize: 10 }}>{s.band}</span>}
                  <Icon d={open ? Icons.chevronD : Icons.chevronR} size={10} style={{ color: "var(--ink-faint)", marginLeft: "auto" }} />
                </div>
                <div style={{ fontSize: 11.5, color: "var(--ink-mute)", lineHeight: 1.4 }}>{s.rule}</div>
              </div>
              <div style={{ textAlign: "right", minWidth: 44 }}>
                <div className="asin-mono" style={{ fontSize: 13, fontWeight: 600, color: pass ? "var(--green)" : warn ? "var(--gold)" : score != null ? "var(--red)" : "var(--ink-faint)" }}>
                  {score != null ? score : "—"}
                </div>
                <div className="asin-mono" style={{ fontSize: 10, color: "var(--ink-faint)" }}>w{s.weight}</div>
              </div>
            </div>
            {open && (
              <div style={{ marginTop: 8, paddingTop: 8, borderTop: "1px dashed var(--rule)", fontSize: 11.5, lineHeight: 1.6 }}>
                {s.formula && (
                  <div style={{ marginBottom: 6 }}>
                    <span style={{ color: "var(--ink-faint)", fontSize: 10, textTransform: "uppercase", letterSpacing: ".08em", marginRight: 6 }}>公式</span>
                    <code style={{ fontFamily: "var(--f-mono)", color: "var(--primary)", fontSize: 11 }}>{s.formula}</code>
                  </div>
                )}
                {s.ladder && (
                  <div style={{ marginBottom: 6, display: "flex", gap: 4, flexWrap: "wrap" }}>
                    {s.ladder.map((t, j) => (
                      <span key={j} className={`tag tag-${t.g === "A" ? "pass" : t.g === "B" ? "warn" : "fail"}`} style={{ fontSize: 10 }}>
                        {t.g} · {t.cond}{t.hint ? ` · ${t.hint}` : ""}
                      </span>
                    ))}
                  </div>
                )}
                {s.eg && (
                  <div style={{ color: "var(--ink-soft)", padding: "5px 8px", background: "var(--bg-card)", borderRadius: 4, fontSize: 11 }}>
                    <span style={{ color: "var(--ink-faint)", fontSize: 10, textTransform: "uppercase", letterSpacing: ".08em", marginRight: 6 }}>示例</span>
                    {s.eg}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ---------- Title tier ribbon ----------
function TitleTierRibbon({ tier, lang, rubric }) {
  const tiers = rubric && rubric.tiers;
  if (!tiers || !tiers.length) return null;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8, marginBottom: 12 }}>
      {tiers.map(t => {
        const active = tier === t.g;
        const bg = t.g === "A" ? "var(--green)" : t.g === "B" ? "var(--gold)" : "var(--red)";
        return (
          <div key={t.g} style={{
            padding: "10px 12px",
            border: `1px solid ${active ? bg : "var(--rule)"}`,
            borderRadius: 6,
            background: active ? `color-mix(in oklab, ${bg} 14%, var(--bg-card))` : "var(--bg-card)",
            opacity: active ? 1 : 0.55,
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
              <span className={`grade grade-${t.g.toLowerCase()}`}>{t.g}</span>
              <span style={{ fontSize: 12.5, fontWeight: 500 }}>{t.label}</span>
              <span className="asin-mono" style={{ marginLeft: "auto", fontSize: 10.5, color: "var(--ink-mute)" }}>
                {t.score[0] === t.score[1] ? t.score[0] : `${t.score[0]}-${t.score[1]}`}
              </span>
            </div>
            <div style={{ fontSize: 11.5, color: "var(--ink-mute)", lineHeight: 1.5 }}>{t.cond}</div>
          </div>
        );
      })}
    </div>
  );
}

// ---------- Critical box (variation) ----------
function CritBox({ title, color, items, hits, dot }) {
  return (
    <div style={{ padding: "10px 12px", background: "var(--bg-soft)", border: "1px solid var(--rule)", borderRadius: 6 }}>
      <div style={{ fontSize: 12, fontWeight: 500, color, marginBottom: 6 }}>{dot} {title}</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {items.map((t, i) => {
          const hit = hits.includes(t);
          return (
            <div key={i} style={{ fontSize: 12, color: hit ? "var(--red)" : "var(--ink-soft)", display: "flex", gap: 6, alignItems: "center" }}>
              <Icon d={hit ? Icons.alert : Icons.check} size={11} style={{ color: hit ? "var(--red)" : "var(--ink-faint)" }} />
              <span style={{ textDecoration: hit ? "none" : "none", opacity: hit ? 1 : 0.65 }}>{t}</span>
              {hit && <span className="tag tag-fail" style={{ marginLeft: "auto" }}>命中</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ---------- Small meter ----------
function Meter({ label, v, suf, threshold }) {
  const ok = threshold ? v >= threshold : v >= 60;
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <span>{label}</span>
        <span className="asin-mono" style={{ color: ok ? "var(--green)" : "var(--gold)" }}>{v}{suf}</span>
      </div>
      <div className="bar"><div className="bar-fill" style={{ width: `${Math.min(100, v)}%`, background: ok ? "var(--green)" : "var(--gold)" }} /></div>
    </div>
  );
}

// ---------- Findability tab ----------
function FindabilityTab({ lang }) {
  const f = (typeof LS_FLAGS !== 'undefined' && LS_FLAGS[1]) || { desc: '', items: [], note: '' };
  return (
    <div className="card">
      <div className="card-h">
        <h3>{lang === "zh" ? "可发现性评分通道" : "Findability boosters"}</h3>
        <span className="tag tag-warn" style={{ marginLeft: "auto" }}>Rollout 2026-05-01</span>
      </div>
      <div className="card-body">
        <div style={{ fontSize: 12.5, color: "var(--ink-mute)", marginBottom: 14 }}>{f.desc}</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 10 }}>
          {f.items.map((it, i) => (
            <div key={i} style={{ padding: "10px 12px", background: "var(--bg-soft)", border: "1px solid var(--rule)", borderRadius: 6, display: "flex", gap: 10, alignItems: "center" }}>
              <Icon d={Icons.check} size={14} style={{ color: "var(--green)" }} />
              <span style={{ fontSize: 13, flex: 1 }}>{it.text}</span>
              <span className="tag tag-pass">已命中</span>
            </div>
          ))}
        </div>
        <div style={{ fontSize: 11, color: "var(--ink-faint)", marginTop: 14, textAlign: "right" }}>{f.note}</div>
      </div>
    </div>
  );
}

// ---------- Snapshots / Annotations ----------
function SnapshotsView({ lang }) {
  return (
    <div className="card"><div className="card-body">
      {[
        { d: "2026-04-16", s: 84, n: "Maya 触发" },
        { d: "2026-04-09", s: 81, n: "每周自动快照" },
        { d: "2026-04-02", s: 79, n: "变体模板被目录归一化改写" },
        { d: "2026-03-26", s: 78, n: "手动诊断" },
      ].map((x, i) => (
        <div key={i} className="log">
          <div className="log-dot" />
          <div>
            <div className="log-time">{x.d} · score {x.s} · <GradeBadge score={x.s} /></div>
            <div className="log-msg">{x.n}</div>
          </div>
        </div>
      ))}
    </div></div>
  );
}

function AnnotationsView({ lang }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
      {Object.entries(LS_COMMENTS).map(([dim, comments]) => {
        const r = LS_RUBRIC.find(x => x.key === dim);
        return (
          <div key={dim} className="card">
            <div className="card-h">
              <h3>{lang === "zh" ? r.name : r.nameEn}</h3>
              <span className="muted">· {comments.length} 条批注</span>
            </div>
            <div className="card-body">
              <div className="thread">
                {comments.map((c, i) => (
                  <div key={i} className="comment">
                    <div className="comment-avatar" style={{ background: c.color }}>{c.init}</div>
                    <div className="comment-body">
                      <div className="comment-meta"><b>{c.who}</b><span>{c.when}</span></div>
                      <div className="comment-text">{c.text}</div>
                    </div>
                  </div>
                ))}
                <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 6 }}>
                  <input placeholder="回复批注… @ 可提及成员" style={{
                    flex: 1, padding: "7px 10px", border: "1px solid var(--rule)", borderRadius: 6,
                    background: "var(--bg-soft)", color: "var(--ink)", fontSize: 13,
                  }} />
                  <button className="btn btn-primary btn-sm">发送</button>
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
