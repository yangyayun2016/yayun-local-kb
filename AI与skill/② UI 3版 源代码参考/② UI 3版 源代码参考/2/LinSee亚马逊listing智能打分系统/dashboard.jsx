// === 仪表板 / ASIN 列表 ===
const { useState: useStateD, useMemo: useMemoD } = React;

function Dashboard({ asins, onPick, onJumpDefects }) {
  const [q, setQ] = useStateD('');
  const [gradeFilter, setGradeFilter] = useStateD('all');
  const [sortBy, setSortBy] = useStateD('total');
  const [sortDir, setSortDir] = useStateD('desc');

  const filtered = useMemoD(() => {
    let r = asins.slice();
    if (q.trim()) {
      const k = q.trim().toLowerCase();
      r = r.filter(a => a.asin.toLowerCase().includes(k) || a.sku.toLowerCase().includes(k) || a.title.toLowerCase().includes(k));
    }
    if (gradeFilter !== 'all') r = r.filter(a => a.grade === gradeFilter);
    r.sort((a, b) => {
      const dir = sortDir === 'desc' ? -1 : 1;
      if (sortBy === 'total') return (a.total - b.total) * dir;
      if (sortBy === 'pv') return (a.pv30 - b.pv30) * dir;
      return 0;
    });
    return r;
  }, [asins, q, gradeFilter, sortBy, sortDir]);

  // 总览统计
  const stats = useMemoD(() => {
    const t = asins.length;
    const avg = Math.round(asins.reduce((s, a) => s + a.total, 0) / t);
    const dist = { 'A++': 0, 'A+': 0, 'B': 0, 'C': 0, 'D': 0 };
    asins.forEach(a => { dist[a.grade] = (dist[a.grade] || 0) + 1; });
    const defects = asins.reduce((s, a) => s + (a.defects?.length || 0), 0);
    const severe = asins.reduce((s, a) => s + (a.defects?.filter(d => d.type === 'severe').length || 0), 0);
    return { t, avg, dist, defects, severe };
  }, [asins]);

  const SortIcon = ({ k }) => sortBy !== k ? null : <span style={{ fontSize: 9, marginLeft: 3, color: 'var(--primary)' }}>{sortDir === 'desc' ? '▼' : '▲'}</span>;
  const setSort = (k) => {
    if (sortBy === k) setSortDir(sortDir === 'desc' ? 'asc' : 'desc');
    else { setSortBy(k); setSortDir('desc'); }
  };

  return (
    <div style={{ padding: '20px 28px 60px', maxWidth: 1480, margin: '0 auto' }}>
      {/* 顶部统计行 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr 1fr 1fr', gap: 14, marginBottom: 20 }}>
        {/* 总分布 */}
        <Card title="ASIN 等级分布" pad={16}>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 12 }}>
            <div style={{ fontSize: 36, fontWeight: 700, letterSpacing: '-0.03em', lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>{stats.t}</div>
            <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 4 }}>纳入评估的 ASIN</div>
          </div>
          <div style={{ display: 'flex', gap: 4, marginTop: 14, height: 8 }}>
            {['A++','A+','B','C','D'].map(g => {
              const w = (stats.dist[g] / stats.t) * 100;
              if (!w) return null;
              const tone = { 'A++': 'oklch(0.65 0.13 155)', 'A+': 'oklch(0.62 0.13 195)', 'B': 'oklch(0.72 0.14 75)', 'C': 'oklch(0.70 0.16 45)', 'D': 'oklch(0.62 0.18 25)' }[g];
              return <div key={g} style={{ flex: w, background: tone, borderRadius: 2 }} title={`${g}: ${stats.dist[g]}`} />;
            })}
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginTop: 10, fontSize: 11 }}>
            {Object.entries(stats.dist).filter(([,v]) => v > 0).map(([g, v]) => (
              <span key={g} style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
                <GradeChip grade={g} size="sm" /> <span style={{ color: 'var(--muted)' }}>{v}</span>
              </span>
            ))}
          </div>
        </Card>
        <Card title="平均得分 · CDQ v3" pad={16}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
            <div style={{ fontSize: 36, fontWeight: 700, letterSpacing: '-0.03em', lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>{stats.avg}</div>
            <div style={{ fontSize: 14, color: 'var(--muted)' }}>/ 120</div>
          </div>
          <div style={{ marginTop: 16 }}><Bar value={stats.avg} max={120} tone={stats.avg > 100 ? 'good' : stats.avg >= 85 ? 'primary' : 'warn'} height={5} /></div>
          <div style={{ marginTop: 8, fontSize: 11, color: 'var(--muted)' }}>较上周 <span style={{ color: 'oklch(0.55 0.13 155)', fontWeight: 600 }}>↑ 3.2%</span></div>
        </Card>
        <Card title="待处理缺陷" pad={16}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
            <div style={{ fontSize: 36, fontWeight: 700, letterSpacing: '-0.03em', lineHeight: 1, fontVariantNumeric: 'tabular-nums', color: 'oklch(0.55 0.16 25)' }}>{stats.defects}</div>
            <div style={{ fontSize: 12, color: 'var(--muted)' }}>项</div>
          </div>
          <div style={{ marginTop: 14, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            <Tag tone="danger">严重 {stats.severe}</Tag>
            <Tag tone="warn">非严重 {stats.defects - stats.severe}</Tag>
          </div>
          <button onClick={onJumpDefects} style={{ marginTop: 10, padding: 0, background: 'transparent', border: 'none', color: 'var(--primary)', fontSize: 11, cursor: 'pointer', fontWeight: 500 }}>查看缺陷池 →</button>
        </Card>
        <Card title="本周高频违规词" pad={16}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
            {[
              { w: 'Antimicrobial', n: 3, sev: true },
              { w: 'Best Seller', n: 2, sev: false },
              { w: '!', n: 5, sev: false },
              { w: 'Free Shipping', n: 1, sev: false },
              { w: 'UV Sterilizes', n: 1, sev: true },
            ].map(t => (
              <span key={t.w} style={{ display: 'inline-flex', alignItems: 'center', gap: 4, padding: '3px 8px', fontSize: 11, background: t.sev ? 'oklch(0.95 0.06 25)' : 'oklch(0.96 0.06 80)', color: t.sev ? 'oklch(0.42 0.16 25)' : 'oklch(0.42 0.12 70)', border: `1px solid ${t.sev ? 'oklch(0.82 0.13 25)' : 'oklch(0.85 0.12 80)'}`, borderRadius: 99, fontFamily: 'JetBrains Mono, monospace' }}>
                {t.w}<span style={{ opacity: 0.6 }}>×{t.n}</span>
              </span>
            ))}
          </div>
        </Card>
      </div>

      {/* 查询 + 工具栏 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
        <div style={{ position: 'relative', flex: '0 0 320px' }}>
          <Icon.Search style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--muted)' }} />
          <input value={q} onChange={e => setQ(e.target.value)} placeholder="搜索 ASIN / SKU / 标题…"
            style={{ width: '100%', height: 32, padding: '0 10px 0 30px', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 12, color: 'var(--ink)', outline: 'none' }} />
        </div>
        <div style={{ display: 'inline-flex', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 6, padding: 2 }}>
          {['all', 'A++', 'A+', 'B', 'C'].map(g => (
            <button key={g} onClick={() => setGradeFilter(g)}
              style={{ padding: '4px 10px', fontSize: 11, fontWeight: 500, border: 'none', borderRadius: 4, cursor: 'pointer',
                background: gradeFilter === g ? 'var(--primary-soft)' : 'transparent',
                color: gradeFilter === g ? 'var(--primary)' : 'var(--muted)' }}>
              {g === 'all' ? '全部等级' : g}
            </button>
          ))}
        </div>
        <button style={btnGhost}><Icon.Filter /> 高级筛选</button>
        <div style={{ flex: 1 }} />
        <span style={{ fontSize: 11, color: 'var(--muted)' }}>共 <b style={{ color: 'var(--ink)', fontVariantNumeric: 'tabular-nums' }}>{filtered.length}</b> 条</span>
        <button style={btnGhost}><Icon.Refresh /> 重新打分</button>
        <button style={btnPrimary}><Icon.Doc /> 导出报告</button>
      </div>

      {/* 主表格 */}
      <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 10, overflow: 'hidden' }}>
        <table className="asin-tbl" style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12, tableLayout: 'fixed' }}>
          <colgroup>
            <col style={{ width: 36 }} />
            <col style={{ width: 'auto' }} />
            <col style={{ width: 110 }} />
            <col style={{ width: 80 }} />
            <col style={{ width: 90 }} />
            <col style={{ width: 80 }} />
            <col style={{ width: 360 }} />
            <col style={{ width: 90 }} />
            <col style={{ width: 70 }} />
          </colgroup>
          <thead>
            <tr>
              <th><input type="checkbox" /></th>
              <th style={{ textAlign: 'left' }}>商品</th>
              <th>ASIN / SKU</th>
              <th style={{ cursor: 'pointer' }} onClick={() => setSort('pv')}>PV/30 <SortIcon k="pv" /></th>
              <th>销售额</th>
              <th style={{ cursor: 'pointer' }} onClick={() => setSort('total')}>总分 <SortIcon k="total" /></th>
              <th>七维分布</th>
              <th>缺陷 / 操作</th>
              <th>市场</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(a => <ASINRow key={a.asin} a={a} onPick={onPick} />)}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const btnGhost = { display: 'inline-flex', alignItems: 'center', gap: 6, height: 32, padding: '0 12px', fontSize: 12, fontWeight: 500, color: 'var(--ink)', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 6, cursor: 'pointer' };
const btnPrimary = { display: 'inline-flex', alignItems: 'center', gap: 6, height: 32, padding: '0 14px', fontSize: 12, fontWeight: 600, color: '#fff', background: 'var(--primary)', border: '1px solid var(--primary)', borderRadius: 6, cursor: 'pointer' };

function ASINRow({ a, onPick }) {
  const dims = window.CDQ_DIMENSIONS;
  return (
    <tr onClick={() => onPick(a.asin)} style={{ cursor: 'pointer' }}>
      <td onClick={(e) => e.stopPropagation()}><input type="checkbox" /></td>
      <td>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <div style={{ width: 38, height: 38, borderRadius: 4, background: a.image, flex: '0 0 38px', border: '1px solid var(--border)', position: 'relative', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg, transparent 50%, rgba(255,255,255,0.15) 50%)' }} />
          </div>
          <div style={{ minWidth: 0, flex: 1 }}>
            <div style={{ fontSize: 12, fontWeight: 500, color: 'var(--ink)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{a.title}</div>
            <div style={{ fontSize: 10.5, color: 'var(--muted)', marginTop: 2 }}>
              <span>{a.cat}</span> · <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>{a.pt}</span>
            </div>
          </div>
        </div>
      </td>
      <td>
        <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: 'var(--ink)', fontWeight: 600 }}>{a.asin}</div>
        <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: 'var(--muted)' }}>{a.sku}</div>
      </td>
      <td style={{ fontVariantNumeric: 'tabular-nums', textAlign: 'right', paddingRight: 14 }}>{a.pv30.toLocaleString()}</td>
      <td style={{ fontVariantNumeric: 'tabular-nums', fontWeight: 500, textAlign: 'right', paddingRight: 14 }}>{a.sales30}</td>
      <td>
        <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
          <div style={{ fontSize: 18, fontWeight: 700, fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.03em', minWidth: 30 }}>{a.total}</div>
          <GradeChip grade={a.grade} size="sm" />
        </div>
      </td>
      <td>
        <div style={{ display: 'flex', gap: 2, alignItems: 'flex-end', height: 30 }}>
          {dims.map(d => {
            const v = a.scores[d.key];
            if (v == null) return (
              <div key={d.key} title={`${d.name} N/A (Orphan ASIN)`} style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', height: '100%' }}>
                <div style={{ height: '100%', border: '1px dashed var(--border)', borderRadius: '2px 2px 0 0', background: 'transparent' }} />
              </div>
            );
            const pct = v / d.weight;
            const tone = pct >= 0.95 ? 'oklch(0.65 0.13 155)' : pct >= 0.7 ? 'oklch(0.62 0.13 195)' : pct >= 0.4 ? 'oklch(0.72 0.14 75)' : 'oklch(0.62 0.18 25)';
            return (
              <div key={d.key} title={`${d.name} ${v}/${d.weight}`} style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', height: '100%' }}>
                <div style={{ height: `${Math.max(8, pct * 100)}%`, background: tone, borderRadius: '2px 2px 0 0' }} />
              </div>
            );
          })}
        </div>
        <div style={{ display: 'flex', gap: 2, fontSize: 9, color: 'var(--muted)', marginTop: 3, fontFamily: 'JetBrains Mono, monospace' }}>
          {dims.map(d => <span key={d.key} style={{ flex: 1, textAlign: 'center' }}>{a.scores[d.key] ?? '–'}</span>)}
        </div>
      </td>
      <td>
        {a.defects?.length ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {a.defects.slice(0, 2).map((d, i) => (
              <div key={i} style={{ fontSize: 10.5, color: d.type === 'severe' ? 'oklch(0.50 0.16 25)' : 'oklch(0.50 0.10 75)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                <span style={{ fontWeight: 600 }}>{d.type === 'severe' ? '🔴' : '🟡'} {d.cat}</span> · {d.detail.slice(0, 40)}
              </div>
            ))}
            {a.defects.length > 2 && <div style={{ fontSize: 10, color: 'var(--muted)' }}>+{a.defects.length - 2} 项</div>}
          </div>
        ) : (
          <Tag tone="success">无缺陷</Tag>
        )}
      </td>
      <td><Market code={a.market} /></td>
    </tr>
  );
}

window.Dashboard = Dashboard;
