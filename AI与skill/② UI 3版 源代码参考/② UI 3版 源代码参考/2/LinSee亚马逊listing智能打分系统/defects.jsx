// === 缺陷池 / 全部 TODO 跨 ASIN ===

function DefectPool({ asins, onPick }) {
  const [filter, setFilter] = React.useState('all');
  const all = [];
  asins.forEach(a => (a.defects || []).forEach(d => all.push({ ...d, asin: a.asin, sku: a.sku, image: a.image, title: a.title })));

  const filtered = all.filter(d => {
    if (filter === 'severe') return d.type === 'severe';
    if (filter === 'minor') return d.type === 'minor';
    if (filter === 'pending') return d.status === 'pending';
    if (filter === 'benchmark') return d.status === 'benchmark' || d.status === 'reference';
    return true;
  });

  const counts = {
    all: all.length,
    severe: all.filter(d => d.type === 'severe').length,
    minor: all.filter(d => d.type === 'minor').length,
    pending: all.filter(d => d.status === 'pending').length,
    benchmark: all.filter(d => d.status === 'benchmark' || d.status === 'reference').length,
  };

  return (
    <div style={{ padding: '20px 28px 60px', maxWidth: 1480, margin: '0 auto' }}>
      <div style={{ marginBottom: 14, display: 'flex', alignItems: 'center', gap: 10 }}>
        <h2 style={{ margin: 0, fontSize: 18, fontWeight: 600 }}>缺陷池 · Defective ASINs</h2>
        <span style={{ fontSize: 11, color: 'var(--muted)' }}>聚合所有 CDQ 缺陷与 TODO 状态</span>
        <div style={{ flex: 1 }} />
        <button style={window.btnGhost}><Icon.Doc /> 导出 .xlsx</button>
        <button style={window.btnPrimary}>批量上传修正值</button>
      </div>

      {/* 状态过滤 */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
        {[
          { k: 'all', l: '全部', n: counts.all, c: 'var(--ink)' },
          { k: 'severe', l: '🔴 严重缺陷', n: counts.severe, c: 'oklch(0.50 0.16 25)' },
          { k: 'minor', l: '🟡 非严重缺陷', n: counts.minor, c: 'oklch(0.50 0.13 75)' },
          { k: 'pending', l: 'PENDING', n: counts.pending, c: 'var(--ink)' },
          { k: 'benchmark', l: 'BENCHMARK', n: counts.benchmark, c: 'oklch(0.50 0.10 220)' },
        ].map(f => (
          <button key={f.k} onClick={() => setFilter(f.k)} style={{
            padding: '8px 14px', fontSize: 12, fontWeight: 500, cursor: 'pointer', borderRadius: 6,
            background: filter === f.k ? 'var(--surface)' : 'transparent',
            border: `1px solid ${filter === f.k ? 'var(--border)' : 'transparent'}`,
            color: f.c,
            boxShadow: filter === f.k ? '0 1px 2px rgba(0,0,0,0.05)' : 'none',
          }}>
            {f.l} <span style={{ fontVariantNumeric: 'tabular-nums', opacity: 0.6, marginLeft: 4 }}>{f.n}</span>
          </button>
        ))}
      </div>

      <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 10, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, tableLayout: 'fixed' }}>
          <colgroup>
            <col style={{ width: 280 }} />
            <col style={{ width: 90 }} />
            <col style={{ width: 100 }} />
            <col style={{ width: 'auto' }} />
            <col style={{ width: 280 }} />
            <col style={{ width: 100 }} />
            <col style={{ width: 90 }} />
          </colgroup>
          <thead>
            <tr>
              <th style={{ textAlign: 'left' }}>ASIN / 商品</th>
              <th>等级</th>
              <th>组件</th>
              <th style={{ textAlign: 'left' }}>Catalog Defect</th>
              <th style={{ textAlign: 'left' }}>Merchant Action</th>
              <th>TODO 状态</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((d, i) => (
              <tr key={i} onClick={() => onPick(d.asin)} style={{ cursor: 'pointer' }}>
                <td>
                  <div style={{ display: 'flex', gap: 9, alignItems: 'center' }}>
                    <div style={{ width: 28, height: 28, borderRadius: 3, background: d.image, flex: '0 0 28px', border: '1px solid var(--border)' }} />
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, fontWeight: 600 }}>{d.asin}</div>
                      <div style={{ fontSize: 10.5, color: 'var(--muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{d.title.slice(0, 38)}…</div>
                    </div>
                  </div>
                </td>
                <td><Tag tone={d.type === 'severe' ? 'danger' : 'warn'}>{d.type === 'severe' ? '🔴 严重' : '🟡 非严重'}</Tag></td>
                <td><Tag tone="neutral">{d.cat}</Tag></td>
                <td style={{ fontSize: 11, color: 'var(--ink)', whiteSpace: 'normal' }}>{d.detail}</td>
                <td style={{ fontSize: 11, color: 'var(--muted)', whiteSpace: 'normal' }}>{d.action}</td>
                <td>{(() => {
                  const map = {
                    'pending':   { l: 'PENDING', tone: 'warn' },
                    'reference': { l: 'BENCHMARK', tone: 'info' },
                    'benchmark': { l: '参考竞品', tone: 'info' },
                    'done':      { l: 'DONE', tone: 'success' },
                  };
                  const m = map[d.status] || map.pending;
                  return <Tag tone={m.tone}>{m.l}</Tag>;
                })()}</td>
                <td onClick={(e) => e.stopPropagation()}><button style={{ ...window.btnGhost, height: 24, fontSize: 10, padding: '0 8px' }}>处理 →</button></td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan="7" style={{ padding: 40, textAlign: 'center', color: 'var(--muted)' }}>暂无符合条件的缺陷</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

window.DefectPool = DefectPool;
