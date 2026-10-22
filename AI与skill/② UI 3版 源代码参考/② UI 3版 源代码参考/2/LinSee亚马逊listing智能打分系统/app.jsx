// === 主应用 ===
const { useState: uSA, useEffect: uEA } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "theme": "light",
  "lang": "zh",
  "gradeSystem": "percent",
  "currentAsin": "B09GTRVJQM",
  "primaryHue": 250,
  "density": "comfortable",
  "showSidebar": true
}/*EDITMODE-END*/;

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  window.__setTweak = setTweak;
  const [view, setView] = uSA('dashboard');
  const [currentAsin, setCurrentAsin] = uSA(t.currentAsin || 'B09GTRVJQM');

  uEA(() => {
    if (t.currentAsin && t.currentAsin !== currentAsin) setCurrentAsin(t.currentAsin);
  }, [t.currentAsin]);

  // theme
  uEA(() => {
    document.documentElement.setAttribute('data-theme', t.theme);
    document.documentElement.style.setProperty('--primary-hue', t.primaryHue);
  }, [t.theme, t.primaryHue]);

  const goDetail = (asin) => {
    setCurrentAsin(asin);
    setView('detail');
    if (window.__setTweak) window.__setTweak('currentAsin', asin);
  };

  const navItems = [
    { k: 'dashboard', l: '仪表板', en: 'Overview', icon: '◫' },
    { k: 'detail',    l: 'ASIN 详情', en: 'Listing Detail', icon: '◐' },
    { k: 'defects',   l: '缺陷池',  en: 'Defect Queue', icon: '◉' },
    { k: 'rules',     l: '规则中心', en: 'Rules', icon: '◇' },
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top bar */}
      <header style={{ position: 'sticky', top: 0, zIndex: 10, height: 49, display: 'flex', alignItems: 'center', padding: '0 22px', background: 'var(--surface)', borderBottom: '1px solid var(--border)', gap: 18 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
          <Logo />
          <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.15 }}>
            <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: '-0.01em' }}>LinSee · CDQ</div>
            <div style={{ fontSize: 9.5, color: 'var(--muted)', fontFamily: 'JetBrains Mono, monospace' }}>Listing Quality v3</div>
          </div>
        </div>

        <nav style={{ display: 'flex', alignItems: 'center', gap: 2, marginLeft: 8 }}>
          {navItems.map(n => (
            <button key={n.k} onClick={() => setView(n.k)}
              style={{
                display: 'flex', alignItems: 'center', gap: 6,
                height: 30, padding: '0 12px', borderRadius: 6,
                fontSize: 12, fontWeight: 500,
                background: view === n.k ? 'var(--primary-soft)' : 'transparent',
                color: view === n.k ? 'var(--primary)' : 'var(--muted)',
                border: 'none', cursor: 'pointer',
              }}>
              <span style={{ fontSize: 13, opacity: 0.85 }}>{n.icon}</span> {n.l}
            </button>
          ))}
        </nav>

        <div style={{ flex: 1 }} />

        {/* breadcrumb path */}
        <div style={{ fontSize: 11, color: 'var(--muted)', fontFamily: 'JetBrains Mono, monospace' }}>
          stq-manage / operations / catalog / cdq
        </div>

        {/* user */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Bell />
          <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'oklch(0.55 0.15 250)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 700 }}>LS</div>
        </div>
      </header>

      <main style={{ flex: 1, background: 'var(--bg)' }}>
        {view === 'dashboard' && (
          <Dashboard asins={window.ASINS} onPick={goDetail} onJumpDefects={() => setView('defects')} />
        )}
        {view === 'detail' && (
          <Detail asin={currentAsin} asins={window.ASINS} onBack={() => setView('dashboard')} onPick={goDetail} />
        )}
        {view === 'defects' && (
          <DefectPool asins={window.ASINS} onPick={goDetail} />
        )}
        {view === 'rules' && (
          <RulesPanel />
        )}
      </main>

      <footer style={{ height: 28, display: 'flex', alignItems: 'center', padding: '0 22px', background: 'var(--surface)', borderTop: '1px solid var(--border)', fontSize: 10.5, color: 'var(--muted)', fontFamily: 'JetBrains Mono, monospace', gap: 14 }}>
        <span>© LinSee 2026</span>
        <span>·</span>
        <span>CDQ v3 · 2025-03 ASCS</span>
        <span>·</span>
        <span>last sync 2 min ago</span>
        <div style={{ flex: 1 }} />
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
          <span style={{ width: 6, height: 6, borderRadius: 99, background: 'oklch(0.65 0.13 155)' }} />
          algo build #v3.2.1
        </span>
      </footer>

      <Tweaks t={t} setTweak={setTweak} />
    </div>
  );
}

function Logo() {
  return (
    <div style={{ width: 28, height: 28, borderRadius: 6, background: 'linear-gradient(135deg, oklch(0.55 0.15 250) 0%, oklch(0.55 0.15 220) 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', overflow: 'hidden' }}>
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M2 13V3M2 13h11" stroke="white" strokeWidth="1.6" strokeLinecap="round" />
        <rect x="4.5" y="9" width="2" height="3.5" fill="white" />
        <rect x="7.5" y="6" width="2" height="6.5" fill="white" />
        <rect x="10.5" y="3.5" width="2" height="9" fill="white" />
        <circle cx="13.5" cy="3" r="1.6" fill="oklch(0.78 0.15 145)" stroke="white" strokeWidth="0.6" />
      </svg>
    </div>
  );
}

function Bell() {
  return (
    <button style={{ position: 'relative', width: 30, height: 30, background: 'transparent', border: 'none', borderRadius: 6, cursor: 'pointer', color: 'var(--muted)' }}>
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ display: 'block', margin: 'auto' }}>
        <path d="M4 12V7a4 4 0 1 1 8 0v5l1 1.5H3L4 12z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
        <path d="M6.5 14a1.5 1.5 0 0 0 3 0" stroke="currentColor" strokeWidth="1.4" />
      </svg>
      <span style={{ position: 'absolute', top: 6, right: 6, width: 6, height: 6, borderRadius: 99, background: 'oklch(0.62 0.18 25)' }} />
    </button>
  );
}

// === Tweaks Panel ===
function Tweaks({ t, setTweak }) {
  return (
    <TweaksPanel title="Tweaks">
      <TweakSection label="外观" />
      <TweakRadio label="主题" value={t.theme} onChange={v => setTweak('theme', v)}
        options={[{ value: 'light', label: '亮色' }, { value: 'dark', label: '暗色' }]} />
      <TweakRadio label="密度" value={t.density} onChange={v => setTweak('density', v)}
        options={[{ value: 'compact', label: '紧凑' }, { value: 'comfortable', label: '舒适' }]} />
      <TweakSlider label="主色相" value={t.primaryHue} onChange={v => setTweak('primaryHue', v)} min={200} max={310} step={5} />

      <TweakSection label="评分体系" />
      <TweakRadio label="得分显示" value={t.gradeSystem} onChange={v => setTweak('gradeSystem', v)}
        options={[{ value: 'percent', label: '120 分' }, { value: 'letter', label: '等级' }]} />
      <TweakSelect label="语言" value={t.lang} onChange={v => setTweak('lang', v)}
        options={[{ value: 'zh', label: '中文' }, { value: 'en', label: 'English' }, { value: 'mixed', label: '中英混合' }]} />

      <TweakSection label="ASIN 切换" />
      <TweakSelect label="当前 ASIN" value={t.currentAsin} onChange={v => setTweak('currentAsin', v)}
        options={window.ASINS.map(a => ({ value: a.asin, label: `${a.asin} · ${a.grade} (${a.total})` }))} />
    </TweaksPanel>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
