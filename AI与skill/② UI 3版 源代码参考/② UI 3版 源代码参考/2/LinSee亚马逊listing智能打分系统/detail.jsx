// === ASIN 详情页 ===
const { useState: uS } = React;

function Detail({ asin, asins, onBack, onPick }) {
  const a = asins.find(x => x.asin === asin) || asins[0];
  const [tab, setTab] = uS('overview');

  const dims = window.CDQ_DIMENSIONS;

  const tabs = [
    { k: 'overview',   l: '总览' },
    { k: 'title',      l: '标题质量' },
    { k: 'attrs',      l: '结构化属性' },
    { k: 'bullets',    l: '五点 & 描述' },
    { k: 'media',      l: '图片 & A+' },
    { k: 'variation',  l: '变体 & 分类' },
    { k: 'keywords',   l: '关键词词频' },
    { k: 'defects',    l: '缺陷 & TODO' },
  ];

  return (
    <div style={{ padding: '16px 28px 60px', maxWidth: 1480, margin: '0 auto' }}>
      {/* breadcrumb + asin selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: 'var(--muted)', marginBottom: 14 }}>
        <button onClick={onBack} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--muted)', fontSize: 12, padding: 0 }}>仪表板</button>
        <Icon.Right />
        <span style={{ color: 'var(--ink)', fontFamily: 'JetBrains Mono, monospace', fontWeight: 600 }}>{a.asin}</span>
        <select value={a.asin} onChange={e => onPick(e.target.value)} style={{ marginLeft: 12, height: 24, fontSize: 11, padding: '0 6px', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 4, color: 'var(--ink)', fontFamily: 'JetBrains Mono, monospace' }}>
          {asins.map(x => <option key={x.asin} value={x.asin}>{x.asin} · {x.grade}</option>)}
        </select>
      </div>

      {/* hero */}
      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: 18, marginBottom: 18 }}>
        {/* product card */}
        <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 10, padding: 16 }}>
          <div style={{ aspectRatio: '1/1', background: a.image, borderRadius: 6, marginBottom: 14, position: 'relative', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, transparent 35%, rgba(0,0,0,0.15) 100%)' }} />
            <div style={{ position: 'absolute', top: 8, left: 8, fontSize: 10, fontFamily: 'JetBrains Mono, monospace', color: 'rgba(255,255,255,0.7)', mixBlendMode: 'difference' }}>主图占位</div>
          </div>
          <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 13, fontWeight: 700, color: 'var(--ink)' }}>{a.asin}</div>
          <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: 'var(--muted)', marginTop: 2 }}>{a.sku}</div>
          <div style={{ fontSize: 12, color: 'var(--ink)', marginTop: 10, lineHeight: 1.45 }}>{a.title}</div>
          <div style={{ display: 'flex', gap: 5, marginTop: 12, flexWrap: 'wrap' }}>
            <Tag tone="info">{a.cat}</Tag>
            <Tag tone="neutral"><span style={{ fontFamily: 'JetBrains Mono, monospace' }}>PT: {a.pt}</span></Tag>
            <Market code={a.market} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 14, paddingTop: 14, borderTop: '1px dashed var(--border)' }}>
            <div>
              <div style={{ fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>30D PV</div>
              <div style={{ fontSize: 16, fontWeight: 700, fontVariantNumeric: 'tabular-nums', marginTop: 2 }}>{a.pv30.toLocaleString()}</div>
            </div>
            <div>
              <div style={{ fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>30D Sales</div>
              <div style={{ fontSize: 16, fontWeight: 700, fontVariantNumeric: 'tabular-nums', marginTop: 2 }}>{a.sales30}</div>
            </div>
          </div>
          <button style={{ ...btnGhost, width: '100%', marginTop: 14, justifyContent: 'center' }}>
            <Icon.External /> 查看亚马逊详情页
          </button>
        </div>

        {/* score panel */}
        <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 10, padding: 20, position: 'relative', overflow: 'hidden' }}>
          {/* subtle bg pattern */}
          <div style={{ position: 'absolute', top: -40, right: -40, width: 240, height: 240, background: 'radial-gradient(circle, var(--primary-soft) 0%, transparent 70%)', opacity: 0.5 }} />

          <div style={{ position: 'relative', display: 'grid', gridTemplateColumns: '160px 1fr', gap: 24 }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
              <Ring value={a.total} max={120} size={150} stroke={11} sub="/ 120" />
              <GradeChip grade={a.grade} size="lg" />
              <div style={{ fontSize: 11, color: 'var(--muted)', textAlign: 'center' }}>
                {window.CDQ_GRADES.find(g => g.grade === a.grade)?.label}
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 14 }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--ink)' }}>七维评估</div>
                <div style={{ fontSize: 11, color: 'var(--muted)' }}>CDQ v3 · {new Date().toLocaleDateString('zh-CN')} 重新计算</div>
                <div style={{ flex: 1 }} />
                <button style={{ ...btnGhost, height: 26, fontSize: 11 }}><Icon.Refresh /> 重算</button>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 8 }}>
                {dims.map(d => {
                  const v = a.scores[d.key];
                  if (v == null) return (
                    <div key={d.key} style={{ padding: '12px 10px', border: '1px dashed var(--border)', borderRadius: 6, background: 'var(--bg)', opacity: 0.7 }}>
                      <div style={{ fontSize: 10.5, color: 'var(--muted)', minHeight: 28, lineHeight: 1.3 }}>{d.name}</div>
                      <div style={{ fontSize: 15, fontWeight: 700, marginTop: 6, color: 'var(--muted)' }}>N/A</div>
                      <div style={{ fontSize: 9, color: 'var(--muted)', marginTop: 8 }}>Orphan ASIN</div>
                    </div>
                  );
                  const pct = v / d.weight;
                  const tone = pct >= 0.95 ? 'good' : pct >= 0.7 ? 'primary' : pct >= 0.4 ? 'warn' : 'bad';
                  return (
                    <div key={d.key} style={{ padding: '12px 10px', border: '1px solid var(--border)', borderRadius: 6, background: 'var(--bg)' }}>
                      <div style={{ fontSize: 10.5, color: 'var(--muted)', minHeight: 28, lineHeight: 1.3 }}>{d.name}</div>
                      <div style={{ display: 'flex', alignItems: 'baseline', gap: 3, marginTop: 6 }}>
                        <div style={{ fontSize: 19, fontWeight: 700, fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.03em' }}>{v}</div>
                        <div style={{ fontSize: 10, color: 'var(--muted)' }}>/{d.weight}</div>
                      </div>
                      <div style={{ marginTop: 8 }}><Bar value={v} max={d.weight} tone={tone} height={3} /></div>
                    </div>
                  );
                })}
              </div>

              {/* flag chips */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginTop: 14 }}>
                {Object.entries({
                  'Search Indexed': a.flags.indexed,
                  'Website Active': a.flags.websiteActive,
                  'Leaf Node': a.flags.leafNode,
                  'Brand Start': a.flags.titleStartsBrand,
                  'Title Length OK': a.flags.titleLengthCorrect,
                  'Main Image Zoom': a.flags.mainImageZoom,
                  'RAC Top4': a.flags.racTop4,
                  'RAC Top10': a.flags.racTop10,
                  'A+ Content': a.aplus?.has,
                }).map(([k, v]) => (
                  <span key={k} style={{ display: 'inline-flex', alignItems: 'center', gap: 4, padding: '2px 7px', fontSize: 10.5, borderRadius: 99, background: v ? 'oklch(0.96 0.04 160)' : 'oklch(0.96 0.03 25)', color: v ? 'oklch(0.40 0.10 160)' : 'oklch(0.45 0.13 25)', border: `1px solid ${v ? 'oklch(0.85 0.08 160)' : 'oklch(0.85 0.10 25)'}` }}>
                    {v ? <Icon.Check /> : <Icon.X />} {k}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* tabs */}
      <div style={{ display: 'flex', gap: 2, borderBottom: '1px solid var(--border)', marginBottom: 18, position: 'sticky', top: 49, background: 'var(--bg)', zIndex: 5 }}>
        {tabs.map(t => (
          <button key={t.k} onClick={() => setTab(t.k)}
            style={{ padding: '10px 14px', fontSize: 12, fontWeight: 500, background: 'none', border: 'none', borderBottom: `2px solid ${tab === t.k ? 'var(--primary)' : 'transparent'}`, color: tab === t.k ? 'var(--primary)' : 'var(--muted)', cursor: 'pointer' }}>
            {t.l}
          </button>
        ))}
      </div>

      {tab === 'overview' && <OverviewPanel a={a} />}
      {tab === 'title' && <TitlePanel a={a} />}
      {tab === 'attrs' && <AttrsPanel a={a} />}
      {tab === 'bullets' && <BulletsPanel a={a} />}
      {tab === 'media' && <MediaPanel a={a} />}
      {tab === 'variation' && <VariationPanel a={a} />}
      {tab === 'keywords' && <KeywordsPanel a={a} />}
      {tab === 'defects' && <DefectsPanel a={a} />}
    </div>
  );
}

// ====== Sub-panels ======

function OverviewPanel({ a }) {
  const dims = window.CDQ_DIMENSIONS;
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 16 }}>
      <Card title="维度详细评分">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {dims.map(d => {
            const v = a.scores[d.key];
            if (v == null) return (
              <div key={d.key}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 6 }}>
                  <div style={{ fontSize: 12.5, fontWeight: 600 }}>{d.name}</div>
                  <Tag tone="neutral">N/A · Orphan ASIN</Tag>
                  <div style={{ flex: 1 }} />
                  <div style={{ fontSize: 11, color: 'var(--muted)' }}>{d.group} · 权重重新分配</div>
                </div>
                <Bar value={0} max={d.weight} tone="primary" height={5} />
                <div style={{ fontSize: 10.5, color: 'var(--muted)', marginTop: 5 }}>该 ASIN 为独立商品（无变体家族），变体质量不参与评分，其余维度按有效权重折算。</div>
              </div>
            );
            const pct = v / d.weight;
            const tone = pct >= 0.95 ? 'good' : pct >= 0.7 ? 'primary' : pct >= 0.4 ? 'warn' : 'bad';
            return (
              <div key={d.key}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 6 }}>
                  <div style={{ fontSize: 12.5, fontWeight: 600 }}>{d.name}</div>
                  <Tag tone="neutral"><span style={{ fontFamily: 'JetBrains Mono, monospace' }}>{d.nameEn}</span></Tag>
                  <div style={{ flex: 1 }} />
                  <div style={{ fontSize: 11, color: 'var(--muted)' }}>{d.group} · 权重 {d.weight}%</div>
                  <div style={{ fontSize: 14, fontWeight: 700, fontVariantNumeric: 'tabular-nums', minWidth: 56, textAlign: 'right' }}>{v} <span style={{ color: 'var(--muted)', fontSize: 10, fontWeight: 400 }}>/ {d.weight}</span></div>
                </div>
                <Bar value={v} max={d.weight} tone={tone} height={5} />
                <div style={{ fontSize: 10.5, color: 'var(--muted)', marginTop: 5 }}>{d.desc}</div>
              </div>
            );
          })}
        </div>
      </Card>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <Card title="算法权重示意">
          <div style={{ position: 'relative', display: 'flex', flexDirection: 'column', gap: 4 }}>
            {dims.map(d => {
              const w = (d.weight / 120) * 100;
              return (
                <div key={d.key} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 11 }}>
                  <div style={{ width: 86, color: 'var(--muted)' }}>{d.name}</div>
                  <div style={{ flex: 1, height: 14, background: 'var(--track)', borderRadius: 3, overflow: 'hidden', position: 'relative' }}>
                    <div style={{ width: `${w}%`, height: '100%', background: 'var(--primary)', opacity: 0.85 }} />
                    <div style={{ position: 'absolute', inset: 0, paddingLeft: 6, display: 'flex', alignItems: 'center', fontSize: 10, color: '#fff', fontFamily: 'JetBrains Mono, monospace', fontWeight: 600 }}>{d.weight}%</div>
                  </div>
                </div>
              );
            })}
            <div style={{ display: 'flex', gap: 8, marginTop: 10, paddingTop: 10, borderTop: '1px dashed var(--border)', fontSize: 11, color: 'var(--muted)' }}>
              <span>合计</span><b style={{ color: 'var(--ink)' }}>120%</b><span>= 120 分制</span>
            </div>
          </div>
        </Card>

        <Card title="等级标尺">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
            {[
              { g: 'A++', r: '> 100 · 极高', t: 'oklch(0.65 0.13 155)' },
              { g: 'A+',  r: '85 – 100 · 高质量', t: 'oklch(0.62 0.13 195)' },
              { g: 'B',   r: '70 – 85 · 低质量·无缺陷', t: 'oklch(0.72 0.14 75)' },
              { g: 'C',   r: '0 – 69.99 · 低质量·非严重', t: 'oklch(0.70 0.16 45)' },
              { g: 'D',   r: '0 · 严重缺陷', t: 'oklch(0.62 0.18 25)' },
              { g: 'U',   r: 'N/A · 政策违规', t: 'oklch(0.55 0.02 270)' },
            ].map(row => (
              <div key={row.g} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px 8px', borderRadius: 4, background: a.grade === row.g ? 'var(--primary-soft)' : 'transparent' }}>
                <GradeChip grade={row.g} size="sm" />
                <div style={{ fontSize: 11, color: 'var(--ink)' }}>{row.r}</div>
                {a.grade === row.g && <span style={{ marginLeft: 'auto', fontSize: 10, color: 'var(--primary)', fontWeight: 600 }}>当前 ←</span>}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

function TitlePanel({ a }) {
  const t = a.titleAnalysis || {};
  const tqs = a.titleTQS || 'B';
  const isC = tqs === 'C';
  // 高亮 issues
  const lower = a.title.toLowerCase();
  const flagged = [];
  ['best seller', 'top rated', '#1', 'free shipping', 'antimicrobial', 'antibacterial', 'anti-mites', 'sanitize', 'detoxify', 'cheapest', 'hot item', '!', '$', '?'].forEach(w => {
    let i = lower.indexOf(w);
    while (i !== -1) { flagged.push({ w, i, len: w.length }); i = lower.indexOf(w, i + 1); }
  });
  // segment title
  const segments = [];
  let cursor = 0;
  flagged.sort((a, b) => a.i - b.i).forEach(f => {
    if (f.i > cursor) segments.push({ text: a.title.slice(cursor, f.i), flag: false });
    segments.push({ text: a.title.slice(f.i, f.i + f.len), flag: true });
    cursor = f.i + f.len;
  });
  if (cursor < a.title.length) segments.push({ text: a.title.slice(cursor), flag: false });

  // 重复词
  const words = a.title.toLowerCase().replace(/[^a-z0-9 ]/g, ' ').split(/\s+/).filter(w => w.length > 2);
  const counts = {};
  words.forEach(w => { counts[w] = (counts[w] || 0) + 1; });
  const dup = Object.entries(counts).filter(([w, n]) => n > 2 && !['for', 'and', 'with', 'the', 'are', 'all'].includes(w));

  const tqsColor = tqs === 'A' ? 'oklch(0.55 0.13 155)' : tqs === 'B' ? 'oklch(0.62 0.13 75)' : 'oklch(0.55 0.18 25)';

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 16 }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <Card title="标题正文 · 高亮检测" right={<Tag tone={isC ? 'danger' : tqs === 'A' ? 'success' : 'warn'}>TQS {tqs}级</Tag>}>
          <div style={{ padding: '12px 14px', background: 'var(--bg)', borderRadius: 6, border: '1px solid var(--border)', fontSize: 13.5, lineHeight: 1.7, fontFamily: 'system-ui, sans-serif', wordBreak: 'break-word' }}>
            {segments.map((s, i) => s.flag ? (
              <span key={i} style={{ background: 'oklch(0.93 0.10 25)', color: 'oklch(0.40 0.16 25)', padding: '1px 4px', borderRadius: 3, borderBottom: '2px solid oklch(0.65 0.18 25)', fontWeight: 600 }}>{s.text}</span>
            ) : <span key={i}>{s.text}</span>)}
          </div>
          <div style={{ display: 'flex', gap: 14, marginTop: 12, fontSize: 11, color: 'var(--muted)', flexWrap: 'wrap' }}>
            <span>总长度 <b style={{ color: t.length > 200 ? 'oklch(0.55 0.18 25)' : t.length < 75 ? 'oklch(0.55 0.13 75)' : 'var(--ink)', fontVariantNumeric: 'tabular-nums' }}>{t.length}</b> / 200 字符</span>
            <span>二段式：标题 ≤ 75 + Highlight ≤ 125</span>
            <span>标记属性 <b style={{ color: 'var(--ink)' }}>{t.attrCount}</b></span>
            <span>分隔符 <b style={{ color: t.pipeScore ? 'oklch(0.55 0.13 155)' : 'oklch(0.55 0.18 25)' }}>{t.pipeScore ? '已使用 |' : '缺少'}</b></span>
            <span>品牌开头 <b style={{ color: t.brandStart ? 'oklch(0.55 0.13 155)' : 'oklch(0.55 0.18 25)' }}>{t.brandStart ? '是' : '否'}</b></span>
          </div>
        </Card>

        <Card title="TQS 评分维度（六项）">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
            {[
              { l: '完整性 (≥0.6)', v: t.integrity, scale: 1, ok: t.integrity >= 0.6 },
              { l: '冗余度 (=1)', v: t.redundancy, scale: 1, ok: t.redundancy >= 1 },
              { l: '管套评分 (>0)', v: t.pipeScore, scale: 1, ok: t.pipeScore > 0 },
              { l: '特殊字符 (=1)', v: t.special, scale: 1, ok: t.special === 1 },
              { l: '受限短语 (=1)', v: t.restricted, scale: 1, ok: t.restricted === 1 },
              { l: '长度 ≤ 200', v: t.length, scale: 200, ok: t.length <= 200 && t.length >= 75 },
            ].map((m, i) => (
              <div key={i} style={{ padding: '10px 12px', border: '1px solid var(--border)', borderRadius: 6, background: 'var(--bg)' }}>
                <div style={{ fontSize: 10.5, color: 'var(--muted)' }}>{m.l}</div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginTop: 4 }}>
                  <div style={{ fontSize: 18, fontWeight: 700, fontVariantNumeric: 'tabular-nums', color: m.ok ? 'var(--ink)' : 'oklch(0.55 0.18 25)' }}>{typeof m.v === 'number' && m.v < 10 ? m.v.toFixed(2) : m.v}</div>
                  {m.ok ? <Icon.Check style={{ color: 'oklch(0.55 0.13 155)' }} /> : <Icon.X style={{ color: 'oklch(0.55 0.18 25)' }} />}
                </div>
                <div style={{ marginTop: 6 }}><Bar value={m.ok ? m.scale : (typeof m.v === 'number' ? m.v : 0)} max={m.scale} tone={m.ok ? 'good' : 'bad'} height={3} /></div>
              </div>
            ))}
          </div>
        </Card>

        {(t.issues?.length > 0 || dup.length > 0) && (
          <Card title="检测到的问题">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {t.issues?.map((iss, i) => (
                <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'center', padding: '8px 10px', background: 'oklch(0.97 0.04 25)', border: '1px solid oklch(0.88 0.07 25)', borderRadius: 5, fontSize: 12 }}>
                  <Icon.Warn style={{ color: 'oklch(0.55 0.18 25)' }} />
                  <span style={{ color: 'oklch(0.40 0.13 25)' }}>{iss}</span>
                </div>
              ))}
              {dup.map(([w, n], i) => (
                <div key={'d'+i} style={{ display: 'flex', gap: 8, alignItems: 'center', padding: '8px 10px', background: 'oklch(0.97 0.05 75)', border: '1px solid oklch(0.88 0.10 75)', borderRadius: 5, fontSize: 12 }}>
                  <Icon.Warn style={{ color: 'oklch(0.55 0.13 75)' }} />
                  <span style={{ color: 'oklch(0.40 0.13 75)' }}>关键词冗余：<b style={{ fontFamily: 'JetBrains Mono, monospace' }}>{w}</b> 出现 {n} 次（>2 触发）</span>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <Card title="TQS 等级">
          <div style={{ textAlign: 'center', padding: '14px 0' }}>
            <div style={{ fontSize: 56, fontWeight: 800, color: tqsColor, letterSpacing: '-0.05em', lineHeight: 1 }}>{tqs}</div>
            <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 6 }}>
              {tqs === 'A' ? 'CDQ 标题质量评分 = 100%' : tqs === 'B' ? 'CDQ 标题质量评分 ≥ 50%' : 'CDQ 标题质量评分 = 0% · CDQv3 U 级'}
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 8, fontSize: 11 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--muted)' }}>权重</span><b>25%</b></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--muted)' }}>得分</span><b style={{ fontVariantNumeric: 'tabular-nums' }}>{a.scores.title} / 25</b></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--muted)' }}>建议长度</span><b>75 – 200 字符</b></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span style={{ color: 'var(--muted)' }}>二段式结构</span><b>75 + 125 (Highlight)</b></div>
          </div>
        </Card>

        <Card title="规则检查清单">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 5, fontSize: 11.5 }}>
            {[
              { l: '≤ 200 字符（总长）', ok: t.length <= 200 },
              { l: '推荐 75–200 字符（标题≤75 + Highlight≤125）', ok: t.length >= 75 && t.length <= 200 },
              { l: '无特殊字符 ! $ ? { } _ ^ ¬', ok: t.special === 1 },
              { l: '无重复词堆砌（同词 ≤ 2 次）', ok: t.redundancy >= 1 },
              { l: '无促销语 / 主观评价', ok: t.restricted === 1 },
              { l: '以品牌名开头', ok: t.brandStart },
              { l: '使用分隔符 |', ok: t.pipeScore > 0 },
              { l: '完整性：品牌名 + 主关键词 + 3个及以上核心属性', ok: t.integrity >= 0.6 },
              { l: '无健康/医疗/杀虫剂类敏感词', ok: !lower.match(/antimicrobial|antibacterial|antifungal|anti-mites|sanitize|detoxify|uv steril|pesticide|insecticide/) },
              { l: '阿拉伯数字非英文单词', ok: true },
              { l: '大小写规范（每词首字母大写）', ok: true },
            ].map((r, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0' }}>
                <span style={{ width: 14, height: 14, borderRadius: 3, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', background: r.ok ? 'oklch(0.92 0.07 160)' : 'oklch(0.92 0.07 25)', color: r.ok ? 'oklch(0.45 0.13 160)' : 'oklch(0.50 0.16 25)' }}>
                  {r.ok ? <Icon.Check /> : <Icon.X />}
                </span>
                <span style={{ color: r.ok ? 'var(--ink)' : 'oklch(0.40 0.13 25)' }}>{r.l}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

function AttrsPanel({ a }) {
  const attrs = a.attributes || {};
  const rai = Object.entries(attrs).filter(([, v]) => v.band === 'RAI');
  const bandA = Object.entries(attrs).filter(([, v]) => v.band === 'A');
  const bandB = Object.entries(attrs).filter(([, v]) => v.band === 'B');

  const Section = ({ title, sub, items, weight }) => {
    const ok = items.filter(([, v]) => v.ok).length;
    return (
      <Card title={title} right={
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: 11 }}>
          <span style={{ color: 'var(--muted)' }}>{sub}</span>
          <span style={{ fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}>{ok}/{items.length}</span>
          {weight && <Tag tone="primary">权重 {weight}</Tag>}
        </div>
      }>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8 }}>
          {items.map(([k, v]) => (
            <div key={k} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 10px', borderRadius: 5, background: v.ok ? 'transparent' : 'oklch(0.97 0.04 25)', border: `1px solid ${v.ok ? 'var(--border)' : 'oklch(0.86 0.08 25)'}` }}>
              <Dot ok={v.ok} />
              <div style={{ minWidth: 0, flex: 1 }}>
                <div style={{ fontSize: 11.5, fontWeight: 500, color: 'var(--ink)' }}>{k}</div>
                <div style={{ fontSize: 11, color: v.ok ? 'var(--muted)' : 'oklch(0.45 0.13 25)', fontFamily: v.val === '—' ? 'JetBrains Mono, monospace' : 'inherit' }}>{v.val || '—'}</div>
              </div>
              {!v.ok && <button style={{ ...btnGhost, height: 24, fontSize: 10, padding: '0 8px' }}>填充</button>}
            </div>
          ))}
        </div>
      </Card>
    );
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 16 }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        {rai.length > 0 && <Section title="RAI 核心属性" sub="前 6 项 · Top 4/10" items={rai} weight="高" />}
        {bandA.length > 0 && <Section title="Band A · 转化动力" sub="规格 / 物理 / 型号" items={bandA} weight="中高" />}
        {bandB.length > 0 && <Section title="Band B · 体验增强" sub="特殊功能 / 目标人群 / 场景" items={bandB} weight="中" />}
        {Object.keys(attrs).length === 0 && (
          <Card title="结构化属性"><div style={{ fontSize: 12, color: 'var(--muted)' }}>该 ASIN 暂无详细属性数据，请在亚马逊后台同步后查看。</div></Card>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <Card title="评分公式">
          <div style={{ fontSize: 11.5, lineHeight: 1.6, fontFamily: 'JetBrains Mono, monospace', background: 'var(--bg)', padding: 10, borderRadius: 5, border: '1px solid var(--border)' }}>
            Score = Σ(<br />
            &nbsp;&nbsp;weight × <br />
            &nbsp;&nbsp;integrity × <br />
            &nbsp;&nbsp;correctness <br />
            )
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 10, fontSize: 11 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--muted)' }}>完整性 (Integrity)</span>
              <b>40%</b>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--muted)' }}>正确性 (Correctness)</span>
              <b>60%</b>
            </div>
            <div style={{ paddingTop: 8, borderTop: '1px dashed var(--border)', fontSize: 10.5, color: 'var(--muted)', lineHeight: 1.5 }}>
              正确 &gt; 完整。宁可空缺也不填错——错误属性会被 Rufus AI 识别冲突，导致信任分下滑。
            </div>
          </div>
        </Card>
        <Card title="RAI 是什么？">
          <div style={{ fontSize: 11.5, color: 'var(--muted)', lineHeight: 1.6 }}>
            <p style={{ margin: '0 0 8px' }}><b style={{ color: 'var(--ink)' }}>RAI = Relevance Attribute Index</b>，NLP 模型按类目动态排序属性重要性（非固定），数据源：</p>
            <div>· 客户评论 / Q&A 对话</div>
            <div>· 搜索查询词</div>
            <div>· 商品标题与描述</div>
            <div>· 制造商 / 竞品网站</div>
            <p style={{ margin: '8px 0 0' }}>Band A（本质属性）+ Band B（变体差异属性）构成详情页“深度信息”组件 (Depth Widget)。</p>
          </div>
        </Card>
        <Card title="空值填充建议">
          <div style={{ fontSize: 11.5, lineHeight: 1.55, color: 'var(--muted)' }}>
            <p style={{ margin: 0 }}>
              下拉框 / 自由输入字段，<b style={{ color: 'var(--ink)' }}>无值时填空格</b>（不留空），保证不被亚马逊检索引擎跳过。
            </p>
            <div style={{ marginTop: 10, padding: '8px 10px', background: 'var(--primary-soft)', borderRadius: 4, color: 'var(--primary)', fontSize: 11, fontFamily: 'JetBrains Mono, monospace' }}>
              IDQ 89 → 98（属性补全后）
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

function BulletsPanel({ a }) {
  const bullets = a.bullets || [];
  const score = bullets.length >= 3 ? 100 : bullets.length >= 1 ? 50 : 0;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 16 }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <Card title="五点描述" right={
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: 11 }}>
            <Tag tone={bullets.length >= 3 ? 'success' : 'warn'}>{bullets.length} 条</Tag>
            <Tag tone="neutral">{score}% 满分</Tag>
          </div>
        }>
          {bullets.length === 0 ? (
            <div style={{ padding: 30, textAlign: 'center', color: 'var(--muted)', fontSize: 12 }}>暂无五点描述数据</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {bullets.map((b, i) => (
                <div key={i} style={{ display: 'flex', gap: 12, padding: '12px 14px', border: '1px solid var(--border)', borderRadius: 6 }}>
                  <div style={{ width: 26, height: 26, borderRadius: 4, background: b.flag === 'core' ? 'oklch(0.92 0.10 250)' : 'var(--bg)', color: b.flag === 'core' ? 'oklch(0.40 0.13 250)' : 'var(--muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 700, flex: '0 0 26px' }}>{i + 1}</div>
                  <div style={{ flex: 1, fontSize: 12.5, lineHeight: 1.55, color: 'var(--ink)' }}>{b.text}</div>
                  <div style={{ flex: '0 0 auto' }}>
                    {b.flag === 'core' ? <Tag tone="primary">核心卖点</Tag> : <Tag tone="neutral">魅力卖点</Tag>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card title="0-1-3 法则评估">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
            {[
              { n: '0', l: '基础功能', sub: '无遗漏', c: 'oklch(0.55 0.13 195)' },
              { n: '1', l: '核心卖点', sub: '主要差异化', c: 'oklch(0.55 0.13 250)' },
              { n: '3+', l: '魅力卖点', sub: '场景 / 体验', c: 'oklch(0.55 0.13 285)' },
            ].map((s, i) => (
              <div key={i} style={{ padding: 14, border: '1px solid var(--border)', borderRadius: 6, position: 'relative' }}>
                <div style={{ fontSize: 32, fontWeight: 800, color: s.c, lineHeight: 1, letterSpacing: '-0.04em' }}>{s.n}</div>
                <div style={{ fontSize: 12, fontWeight: 600, marginTop: 6 }}>{s.l}</div>
                <div style={{ fontSize: 10.5, color: 'var(--muted)', marginTop: 2 }}>{s.sub}</div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <Card title="违禁词扫描">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {window.RESTRICTED_DICT.slice(0, 8).map(w => {
              const hit = bullets.some(b => b.text.toLowerCase().includes(w.word.toLowerCase())) || a.title.toLowerCase().includes(w.word.toLowerCase());
              return (
                <div key={w.word} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '5px 8px', borderRadius: 4, background: hit ? 'oklch(0.95 0.07 25)' : 'transparent', fontSize: 11 }}>
                  <Dot ok={!hit} warn={false} />
                  <span style={{ fontFamily: 'JetBrains Mono, monospace', color: hit ? 'oklch(0.45 0.16 25)' : 'var(--ink)' }}>{w.word}</span>
                  <div style={{ flex: 1 }} />
                  <span style={{ fontSize: 10, color: 'var(--muted)' }}>{w.cat}</span>
                </div>
              );
            })}
          </div>
        </Card>
        <Card title="得分规则">
          <div style={{ fontSize: 11.5, display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>≥ 3 条 bullet</span><b style={{ color: 'oklch(0.55 0.13 155)' }}>100%</b></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>≥ 1 条 bullet</span><b style={{ color: 'oklch(0.55 0.13 75)' }}>50%</b></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>无 bullet</span><b style={{ color: 'oklch(0.55 0.18 25)' }}>0%</b></div>
            <div style={{ paddingTop: 8, borderTop: '1px dashed var(--border)', fontSize: 10.5, color: 'var(--muted)' }}>
              CDQ v3 已移除产品描述（Description）评分项。
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

function MediaPanel({ a }) {
  const imgs = a.images || Array.from({ length: a.flags?.image ? 4 : 2 }, (_, i) => ({ kind: i === 0 ? 'main' : 'detail', ok: true, note: i === 0 ? '主图占位' : `辅图 ${i}` }));
  const aplus = a.aplus || { has: a.flags?.image, advanced: false, modules: 0 };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <Card title="商品图片" right={
        <div style={{ display: 'flex', gap: 6, alignItems: 'center', fontSize: 11 }}>
          <Tag tone={imgs.length >= 4 ? 'success' : 'warn'}>{imgs.length} 张</Tag>
          {a.flags?.mainImageZoom ? <Tag tone="success">主图缩放✓</Tag> : <Tag tone="danger">无缩放</Tag>}
        </div>
      }>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 10 }}>
          {imgs.map((img, i) => (
            <div key={i}>
              <div style={{ aspectRatio: '1/1', background: a.image, borderRadius: 4, position: 'relative', overflow: 'hidden', border: i === 0 ? '2px solid var(--primary)' : '1px solid var(--border)' }}>
                <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg, transparent 50%, rgba(0,0,0,0.18) 100%)' }} />
                {i === 0 && <div style={{ position: 'absolute', top: 4, left: 4, fontSize: 9, padding: '1px 5px', background: 'var(--primary)', color: '#fff', borderRadius: 2, fontWeight: 600 }}>MAIN</div>}
              </div>
              <div style={{ fontSize: 10.5, color: 'var(--muted)', marginTop: 5, textAlign: 'center' }}>{img.note}</div>
            </div>
          ))}
          {Array.from({ length: Math.max(0, 6 - imgs.length) }).map((_, i) => (
            <div key={'empty' + i}>
              <div style={{ aspectRatio: '1/1', borderRadius: 4, border: '1.5px dashed var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--muted)', fontSize: 10 }}>建议补充</div>
              <div style={{ fontSize: 10.5, color: 'var(--muted)', marginTop: 5, textAlign: 'center', opacity: 0.5 }}>—</div>
            </div>
          ))}
        </div>
      </Card>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <Card title="A+ 内容" right={aplus.has ? (aplus.advanced ? <Tag tone="success">高级 A+</Tag> : <Tag tone="info">标准 A+</Tag>) : <Tag tone="danger">未启用</Tag>}>
          {aplus.has ? (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 6, marginBottom: 12 }}>
                {Array.from({ length: aplus.modules }).map((_, i) => (
                  <div key={i} style={{ aspectRatio: '4/3', background: i % 2 === 0 ? 'var(--bg)' : 'oklch(0.97 0.01 270)', borderRadius: 3, border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 9, color: 'var(--muted)', fontFamily: 'JetBrains Mono, monospace' }}>M{i + 1}</div>
                ))}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11 }}>
                <span style={{ color: 'var(--muted)' }}>模块数</span><b>{aplus.modules}</b>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginTop: 4 }}>
                <span style={{ color: 'var(--muted)' }}>含对比表格</span><b>{aplus.hasComparison ? '是' : '否'}</b>
              </div>
              <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px dashed var(--border)', fontSize: 10.5, color: 'var(--muted)', lineHeight: 1.5 }}>
                A+ 评分为二元：存在 = 100% · 不存在 = 0%。A+ 内容质量评估计划于 2026 上线。
              </div>
            </div>
          ) : (
            <div style={{ padding: '20px 0', textAlign: 'center', color: 'var(--muted)', fontSize: 12 }}>
              <div style={{ fontSize: 32, opacity: 0.3 }}>＋</div>
              <div style={{ marginTop: 8 }}>未上传 A+ 详情页</div>
              <button style={{ ...btnPrimary, marginTop: 12, fontSize: 11, height: 28 }}>申请高级 A+</button>
            </div>
          )}
        </Card>

        <Card title="图片评分矩阵 · CDQ v3">
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11.5, marginBottom: 14 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ textAlign: 'left', padding: '6px', fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', fontWeight: 500 }}>条件</th>
                <th style={{ textAlign: 'right', padding: '6px', fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', fontWeight: 500 }}>得分</th>
              </tr>
            </thead>
            <tbody>
              {[
                { l: '≥ 4 张 且 无图片缺陷', s: '1.0 (100%)', ok: imgs.length >= 4, active: imgs.length >= 4 },
                { l: '≥ 4 张 但 存在缺陷', s: '0.4 (40%)', ok: false, active: false },
                { l: '< 4 张 且 无缺陷', s: '0.6 (60%)', ok: false, active: imgs.length < 4 },
                { l: '< 4 张 且 存在缺陷', s: '0.0 (0%)', ok: false, active: false },
              ].map((r, i) => (
                <tr key={i} style={{ borderBottom: '1px dashed var(--border)', background: r.active ? 'var(--primary-soft)' : 'transparent' }}>
                  <td style={{ padding: '7px 6px' }}>{r.l}{r.active && <span style={{ marginLeft: 6, fontSize: 10, color: 'var(--primary)', fontWeight: 600 }}>当前 ←</span>}</td>
                  <td style={{ padding: '7px 6px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 700 }}>{r.s}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: 11.5 }}>
            {[
              { l: '主图 zoom 功能 (1000px+)', ok: a.flags?.mainImageZoom },
              { l: 'IAI (Imaging Attribute Index) ≥ 0.4', ok: imgs.length >= 4 },
              { l: '产品有效像素占比 ≥ 85%', ok: true },
              { l: '图片 alt 标签埋入相关属性关键词', ok: imgs.length >= 4 },
            ].map((r, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <Dot ok={r.ok} />
                <span style={{ flex: 1 }}>{r.l}</span>
              </div>
            ))}
            <div style={{ paddingTop: 8, borderTop: '1px dashed var(--border)', fontSize: 10.5, color: 'var(--muted)', lineHeight: 1.5 }}>
              Orphan ASIN 的图片权重从 15% 提升至 18.75%（变体权重重新分配）。IAI 衡量图片元数据与同类目竞品的完整度对比。
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

function VariationPanel({ a }) {
  const isOrphan = a.scores?.variation == null;
  const v = a.variation || { count: a.flags?.image ? 8 : 0, themes: ['Color'], consistent: true, duplicates: 0 };
  if (isOrphan) {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <Card title="变体家族" right={<Tag tone="neutral">N/A · Orphan ASIN</Tag>}>
          <div style={{ padding: '20px 0', textAlign: 'center', color: 'var(--muted)', fontSize: 12, lineHeight: 1.7 }}>
            该 ASIN 为独立商品，不属于任何变体家族。<br />
            变体质量 20% 权重重新分配至其余维度（如图片 15% → 18.75%）。
          </div>
        </Card>
        <Card title="产品分类节点">
          <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 6 }}>叶节点 (Leaf Node ID)</div>
          <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 14, fontWeight: 600 }}>{a.cat}</div>
          <div style={{ display: 'flex', gap: 6, marginTop: 12, flexWrap: 'wrap' }}>
            {a.flags?.leafNode ? <Tag tone="success"><Icon.Check /> 叶节点正确</Tag> : <Tag tone="danger">非叶节点</Tag>}
            {a.flags?.keywords ? <Tag tone="success"><Icon.Check /> 含搜索词</Tag> : <Tag tone="warn">缺关键词</Tag>}
          </div>
        </Card>
      </div>
    );
  }
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
      <Card title="变体家族">
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 14 }}>
          <div style={{ fontSize: 36, fontWeight: 700, fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.03em' }}>{v.count}</div>
          <div style={{ fontSize: 12, color: 'var(--muted)' }}>个子项</div>
        </div>
        <div style={{ display: 'flex', gap: 6, marginBottom: 14, flexWrap: 'wrap' }}>
          {v.themes.map(t => <Tag key={t} tone="primary">{t}</Tag>)}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 11.5 }}>
          {[
            { l: '主题属性一致性', ok: v.consistent },
            { l: '变体值正确性', ok: v.consistent },
            { l: '无子项重复', ok: v.duplicates === 0 },
            { l: '变体数量 ≥ 2', ok: v.count >= 2 },
          ].map((r, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Dot ok={r.ok} /><span>{r.l}</span></div>
          ))}
        </div>
      </Card>
      <Card title="变体缺陷分级">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div style={{ padding: 12, background: 'oklch(0.97 0.04 25)', border: '1px solid oklch(0.86 0.08 25)', borderRadius: 6 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'oklch(0.42 0.16 25)' }}>🔴 严重缺陷 · 立即处理</div>
            <div style={{ fontSize: 11, color: 'oklch(0.40 0.13 25)', marginTop: 6, lineHeight: 1.55 }}>
              错误属性值 · 单位制混用 · 变体信息冗余 · 本地化错误 · 子项重复
            </div>
          </div>
          <div style={{ padding: 12, background: 'oklch(0.97 0.05 75)', border: '1px solid oklch(0.86 0.10 75)', borderRadius: 6 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'oklch(0.42 0.13 75)' }}>🟡 非严重缺陷 · 随时间改善</div>
            <div style={{ fontSize: 11, color: 'oklch(0.40 0.10 75)', marginTop: 6, lineHeight: 1.55 }}>
              未标准化值 · 格式不匹配 · 变异主题错误
            </div>
          </div>
        </div>
      </Card>
      <Card title="产品分类节点">
        <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 6 }}>叶节点 (Leaf Node ID)</div>
        <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 14, fontWeight: 600 }}>{a.cat}</div>
        <div style={{ display: 'flex', gap: 6, marginTop: 12, flexWrap: 'wrap' }}>
          {a.flags?.leafNode ? <Tag tone="success"><Icon.Check /> 叶节点正确</Tag> : <Tag tone="danger">非叶节点</Tag>}
          {a.flags?.keywords ? <Tag tone="success"><Icon.Check /> 含搜索词</Tag> : <Tag tone="warn">缺关键词</Tag>}
        </div>
      </Card>
      <Card title="可发现性得分">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 11.5 }}>
          {[
            { l: '有分类叶节点', w: 10, ok: a.flags?.leafNode },
            { l: '有搜索关键词', w: 5, ok: a.flags?.keywords },
            { l: 'PT 精确（如 OXFORD 而非 SHOES）', w: 5, ok: true },
          ].map((r, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <Dot ok={r.ok} />
              <span style={{ flex: 1 }}>{r.l}</span>
              <span style={{ fontSize: 10, color: 'var(--muted)' }}>+{r.w}%</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function KeywordsPanel({ a }) {
  const data = window.KEYWORD_FREQ;
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 16 }}>
      <Card title="高频词分析" right={<Tag tone="info">频次 ≥ 3 加速收录</Tag>}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11.5 }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              <th style={{ textAlign: 'left', padding: '8px 6px', fontWeight: 500, color: 'var(--muted)', fontSize: 10.5, textTransform: 'uppercase' }}>关键词</th>
              <th style={{ textAlign: 'left', padding: '8px 6px', fontWeight: 500, color: 'var(--muted)', fontSize: 10.5, textTransform: 'uppercase' }}>分类</th>
              <th style={{ textAlign: 'right', padding: '8px 6px', fontWeight: 500, color: 'var(--muted)', fontSize: 10.5, textTransform: 'uppercase' }}>频次</th>
              <th style={{ textAlign: 'left', padding: '8px 6px', fontWeight: 500, color: 'var(--muted)', fontSize: 10.5, textTransform: 'uppercase' }}>埋点位置</th>
              <th style={{ textAlign: 'right', padding: '8px 6px', fontWeight: 500, color: 'var(--muted)', fontSize: 10.5, textTransform: 'uppercase' }}>密度</th>
            </tr>
          </thead>
          <tbody>
            {data.map(k => (
              <tr key={k.word} style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '8px 6px', fontFamily: 'JetBrains Mono, monospace', fontWeight: 600 }}>{k.word}</td>
                <td style={{ padding: '8px 6px' }}><Tag tone="neutral">{k.type}</Tag></td>
                <td style={{ padding: '8px 6px', textAlign: 'right', fontVariantNumeric: 'tabular-nums', fontWeight: 700, color: k.freq >= 3 ? 'oklch(0.55 0.13 155)' : 'var(--ink)' }}>{k.freq}</td>
                <td style={{ padding: '8px 6px' }}>
                  <div style={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                    {k.places.map(p => <span key={p} style={{ fontSize: 9.5, padding: '1px 5px', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: 3, fontFamily: 'JetBrains Mono, monospace', color: 'var(--muted)' }}>{p}</span>)}
                  </div>
                </td>
                <td style={{ padding: '8px 6px', textAlign: 'right', fontVariantNumeric: 'tabular-nums', color: 'var(--muted)' }}>{k.density}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <Card title="埋点矩阵">
          <div style={{ display: 'grid', gridTemplateColumns: '80px repeat(5, 1fr)', gap: 4, fontSize: 10 }}>
            <div></div>
            {['Title', 'BP', 'Q&A', 'A+', 'Image-Alt'].map(p => <div key={p} style={{ textAlign: 'center', color: 'var(--muted)', fontFamily: 'JetBrains Mono, monospace' }}>{p}</div>)}
            {data.slice(0, 5).map(k => (
              <React.Fragment key={k.word}>
                <div style={{ fontSize: 10.5, fontFamily: 'JetBrains Mono, monospace', color: 'var(--ink)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{k.word}</div>
                {['Title', 'BP', 'Q&A', 'A+', 'Image-Alt'].map(p => {
                  const hit = k.places.some(pp => pp.startsWith(p) || pp === p);
                  return <div key={p} style={{ aspectRatio: '1/1', background: hit ? 'oklch(0.55 0.15 250)' : 'var(--bg)', border: '1px solid var(--border)', borderRadius: 3, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 10 }}>{hit ? '●' : ''}</div>;
                })}
              </React.Fragment>
            ))}
          </div>
        </Card>
        <Card title="A9/A10 收录提示">
          <div style={{ fontSize: 11.5, color: 'var(--muted)', lineHeight: 1.55 }}>
            页面关键词出现频次 <b style={{ color: 'var(--ink)' }}>&gt; 3 次</b> 视为高频词，亚马逊机器学习模型据此判定 ASIN 实际经营品类。Title / BP / Q&A / A+ / Image-Alt 五处全埋可达成最大收录权重。
          </div>
        </Card>
      </div>
    </div>
  );
}

function DefectsPanel({ a }) {
  const defects = a.defects || [];
  if (!defects.length) {
    return <Card><div style={{ padding: 30, textAlign: 'center' }}>
      <div style={{ fontSize: 36, color: 'oklch(0.65 0.13 155)' }}>✓</div>
      <div style={{ marginTop: 10, fontSize: 13, fontWeight: 600 }}>该 ASIN 无待处理缺陷</div>
      <div style={{ marginTop: 4, fontSize: 11, color: 'var(--muted)' }}>所有 CDQ 维度均符合质量标准</div>
    </div></Card>;
  }
  return (
    <Card title="缺陷与待处理项" right={<Tag tone="danger">{defects.length} 项</Tag>}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11.5 }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)' }}>
            <th style={{ textAlign: 'left', padding: '8px 6px', fontWeight: 500, color: 'var(--muted)', fontSize: 10.5, textTransform: 'uppercase' }}>等级</th>
            <th style={{ textAlign: 'left', padding: '8px 6px', fontWeight: 500, color: 'var(--muted)', fontSize: 10.5, textTransform: 'uppercase' }}>组件</th>
            <th style={{ textAlign: 'left', padding: '8px 6px', fontWeight: 500, color: 'var(--muted)', fontSize: 10.5, textTransform: 'uppercase' }}>Catalog Defect</th>
            <th style={{ textAlign: 'left', padding: '8px 6px', fontWeight: 500, color: 'var(--muted)', fontSize: 10.5, textTransform: 'uppercase' }}>Merchant Action</th>
            <th style={{ textAlign: 'left', padding: '8px 6px', fontWeight: 500, color: 'var(--muted)', fontSize: 10.5, textTransform: 'uppercase' }}>TODO</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {defects.map((d, i) => (
            <tr key={i} style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '10px 6px' }}>
                <Tag tone={d.type === 'severe' ? 'danger' : 'warn'}>{d.type === 'severe' ? '🔴 严重' : '🟡 非严重'}</Tag>
              </td>
              <td style={{ padding: '10px 6px', fontWeight: 600 }}>{d.cat}</td>
              <td style={{ padding: '10px 6px', fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }}>{d.detail}</td>
              <td style={{ padding: '10px 6px', color: 'var(--muted)', fontSize: 11 }}>{d.action}</td>
              <td style={{ padding: '10px 6px' }}><TodoStatus status={d.status} /></td>
              <td style={{ padding: '10px 6px' }}><button style={{ ...btnGhost, height: 24, fontSize: 10, padding: '0 8px' }}>处理</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

function TodoStatus({ status }) {
  const map = {
    'pending':   { l: 'PENDING',     tone: 'warn' },
    'rectify':   { l: '待整改',       tone: 'danger' },
    'reference': { l: 'BENCHMARK',    tone: 'info' },
    'benchmark': { l: '参考竞品',     tone: 'info' },
    'noFix':     { l: '无需整改',     tone: 'neutral' },
    'done':      { l: 'DONE',         tone: 'success' },
  };
  const m = map[status] || map.pending;
  return <Tag tone={m.tone}>{m.l}</Tag>;
}

window.Detail = Detail;
window.btnGhost = btnGhost;
window.btnPrimary = btnPrimary;
