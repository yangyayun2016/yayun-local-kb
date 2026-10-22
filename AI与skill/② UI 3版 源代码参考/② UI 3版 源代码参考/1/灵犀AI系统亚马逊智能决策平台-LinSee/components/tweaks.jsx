// ==================================================================
//  LinSee · Tweaks panel (floating)
// ==================================================================

window.TweaksPanel = function TweaksPanel({
  open, onClose,
  weights, setWeights,
  gradeSystem, setGradeSystem,
  lang, setLang,
  theme, setTheme,
  currentAsin, setCurrentAsin,
}) {
  if (!open) return null;
  const coreTotal = LS_RUBRIC.filter(r => !r.bonus).reduce((s, r) => s + Number(weights[r.key]), 0);
  const bonusTotal = LS_RUBRIC.filter(r => r.bonus).reduce((s, r) => s + Number(weights[r.key]), 0);
  return (
    <div className="tweaks-panel">
      <div className="tweaks-panel-h">
        <Icon d={Icons.settings} size={14} />
        <h4>Tweaks</h4>
        <button className="iconbtn" style={{ marginLeft: "auto", width: 26, height: 26 }} onClick={onClose}>
          <Icon d={Icons.x} size={13} />
        </button>
      </div>
      <div className="tweaks-panel-body">
        <h5>{lang === "zh" ? "主题" : "Theme"}</h5>
        <div className="seg" style={{ width: "100%" }}>
          <button className={theme === "light" ? "active" : ""} onClick={() => setTheme("light")} style={{ flex: 1 }}>
            <Icon d={Icons.sun} size={12} /> {lang === "zh" ? "明" : "Light"}
          </button>
          <button className={theme === "dark" ? "active" : ""} onClick={() => setTheme("dark")} style={{ flex: 1 }}>
            <Icon d={Icons.moon} size={12} /> {lang === "zh" ? "暗" : "Dark"}
          </button>
        </div>

        <h5>{lang === "zh" ? "语言" : "Language"}</h5>
        <div className="seg" style={{ width: "100%" }}>
          <button className={lang === "zh" ? "active" : ""} onClick={() => setLang("zh")} style={{ flex: 1 }}>中文</button>
          <button className={lang === "en" ? "active" : ""} onClick={() => setLang("en")} style={{ flex: 1 }}>English</button>
        </div>

        <h5>{lang === "zh" ? "评级体系" : "Grade System"}</h5>
        <div className="seg" style={{ width: "100%" }}>
          <button className={gradeSystem === "letter" ? "active" : ""} onClick={() => setGradeSystem("letter")} style={{ flex: 1 }}>A-D</button>
          <button className={gradeSystem === "percent" ? "active" : ""} onClick={() => setGradeSystem("percent")} style={{ flex: 1 }}>{lang === "zh" ? "百分制" : "Percent"}</button>
        </div>

        <h5>{lang === "zh" ? "示例 Listing" : "Sample listing"}</h5>
        <select value={currentAsin} onChange={e => setCurrentAsin(e.target.value)} style={{
          width: "100%", padding: "6px 8px", border: "1px solid var(--rule)", borderRadius: 6,
          background: "var(--bg-soft)", color: "var(--ink)", fontSize: 12.5, fontFamily: "var(--f-mono)",
        }}>
          {Object.keys(LS_PRODUCTS).map(a => (
            <option key={a} value={a}>{a} · {LS_PRODUCTS[a].brand}</option>
          ))}
        </select>

        <h5>{lang === "zh" ? "各维度权重" : "Dimension weights"}
          <span style={{ marginLeft: 8, fontFamily: "var(--f-mono)", color: coreTotal === 100 ? "var(--green)" : "var(--red)" }}>
            核心 {coreTotal}% + 加分 {bonusTotal}
          </span>
        </h5>
        {LS_RUBRIC.map(r => (
          <div key={r.key} className="weight-row">
            <span style={{ fontSize: 12 }}>{lang === "zh" ? r.name : r.nameEn}</span>
            <input type="range" min="0" max="50" step="1" value={weights[r.key]}
                   onChange={e => setWeights({ ...weights, [r.key]: Number(e.target.value) })} />
            <span className="weight-val">{weights[r.key]}%</span>
          </div>
        ))}
        <button className="btn btn-sm" style={{ width: "100%", justifyContent: "center", marginTop: 6 }}
                onClick={() => setWeights(LS_RUBRIC.reduce((m, r) => (m[r.key] = r.weight, m), {}))}>
          <Icon d={Icons.refresh} size={12} /> {lang === "zh" ? "恢复 CDQv3 默认" : "Reset to CDQv3"}
        </button>
      </div>
    </div>
  );
};
