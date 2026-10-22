// ==================================================================
//  LinSee · Shell (nav + topbar)
// ==================================================================

window.Shell = function Shell({ page, setPage, lang, theme, setTheme, openTweaks, onNewAudit }) {
  const t = LS_I18N[lang];
  const items = [
    { key: "dashboard", icon: Icons.dash,  label: t.navDashboard, badge: "4" },
    { key: "diagnose", icon: Icons.diag,  label: t.navDiagnose },
    { key: "compare",  icon: Icons.cmp,   label: t.navCompare },
    { key: "history",  icon: Icons.hist,  label: t.navHistory },
  ];
  const items2 = [
    { key: "knowledge", icon: Icons.kb,   label: t.navKnowledge },
    { key: "team",      icon: Icons.team, label: t.navTeam, badge: "3" },
    { key: "member",    icon: Icons.crown, label: t.navMember },
  ];
  const crumbMap = {
    dashboard: [t.navDashboard],
    diagnose: [t.navDashboard, "B09GTRVJQM"],
    compare: [t.navCompare, lang === "zh" ? "我 vs 竞品" : "Me vs competitors"],
    history: [t.navHistory],
    knowledge: [t.navKnowledge],
    team: [t.navTeam],
    member: [t.navMember],
  };

  return (
    <>
      <aside className="nav">
        <div className="nav-brand">
          <div className="nav-brand-mark">L</div>
          <div>
            <div className="nav-brand-name"><em>Lin</em>See</div>
            <div className="nav-brand-sub">{t.appSub}</div>
          </div>
        </div>

        <button className="btn btn-accent" style={{ justifyContent: "center", marginBottom: 14 }} onClick={onNewAudit}>
          <Icon d={Icons.plus} size={14} />
          {t.navNew}
        </button>

        <div className="nav-section">{lang === "zh" ? "工作区" : "Workspace"}</div>
        {items.map(it => (
          <button key={it.key} className={`nav-item ${page === it.key ? "active" : ""}`} onClick={() => setPage(it.key)}>
            <Icon d={it.icon} className="nav-item-icon" />
            <span>{it.label}</span>
            {it.badge && <span className="nav-item-badge">{it.badge}</span>}
          </button>
        ))}

        <div className="nav-section">{lang === "zh" ? "资源" : "Resources"}</div>
        {items2.map(it => (
          <button key={it.key} className={`nav-item ${page === it.key ? "active" : ""}`} onClick={() => setPage(it.key)}>
            <Icon d={it.icon} className="nav-item-icon" />
            <span>{it.label}</span>
            {it.badge && <span className="nav-item-badge">{it.badge}</span>}
          </button>
        ))}

        <div className="nav-foot">
          <div className="nav-user">
            <div className="nav-avatar">MC</div>
            <div className="nav-user-info">
              <div className="nav-user-name">Maya Chen</div>
              <div className="nav-user-plan">Growth · 余 246 次</div>
            </div>
          </div>
        </div>
      </aside>

      <main className="main">
        <div className="topbar">
          <div className="crumbs">
            <span>LinSee</span>
            {crumbMap[page].map((c, i, arr) => (
              <React.Fragment key={i}>
                <Icon d={Icons.chevronR} size={12} />
                {i === arr.length - 1 ? <b>{c}</b> : <span>{c}</span>}
              </React.Fragment>
            ))}
          </div>

          <div className="topbar-search">
            <Icon d={Icons.search} size={14} />
            <input placeholder={t.searchPlaceholder} />
            <kbd>⌘K</kbd>
          </div>

          <button className="iconbtn" title={lang === "zh" ? "设置" : "Settings"} onClick={openTweaks}>
            <Icon d={Icons.settings} size={16} />
          </button>
          <button className="iconbtn" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                  title={theme === "dark" ? "Light" : "Dark"}>
            <Icon d={theme === "dark" ? Icons.sun : Icons.moon} size={16} />
          </button>
          <button className="iconbtn" title="Notifications">
            <Icon d={Icons.bell} size={16} />
            <span className="dot" />
          </button>
        </div>

        <div className="content" id="content-root" />
      </main>
    </>
  );
};
