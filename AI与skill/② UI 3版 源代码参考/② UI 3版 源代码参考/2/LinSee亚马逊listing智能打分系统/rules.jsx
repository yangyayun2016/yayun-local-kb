// === 规则中心：违禁词字典 + 评分规则手册 ===

function RulesPanel() {
  const [tab, setTab] = React.useState('restricted');
  const dict = window.RESTRICTED_DICT;

  return (
    <div style={{ padding: '20px 28px 60px', maxWidth: 1480, margin: '0 auto' }}>
      <div style={{ marginBottom: 14 }}>
        <h2 style={{ margin: 0, fontSize: 18, fontWeight: 600 }}>规则与字典</h2>
        <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4 }}>CDQ v3 · 由亚马逊精选与目录系统团队 (ASCS) 2025-03 推出</div>
      </div>

      <div style={{ display: 'flex', gap: 4, marginBottom: 16, borderBottom: '1px solid var(--border)' }}>
        {[
          { k: 'restricted', l: '违禁 / 敏感词字典' },
          { k: 'tqs', l: 'TQS 评分逻辑' },
          { k: 'weights', l: '权重分配' },
          { k: 'policy', l: '亚马逊政策摘录' },
        ].map(t => (
          <button key={t.k} onClick={() => setTab(t.k)}
            style={{ padding: '10px 14px', fontSize: 12, fontWeight: 500, background: 'none', border: 'none', borderBottom: `2px solid ${tab === t.k ? 'var(--primary)' : 'transparent'}`, color: tab === t.k ? 'var(--primary)' : 'var(--muted)', cursor: 'pointer' }}>
            {t.l}
          </button>
        ))}
      </div>

      {tab === 'restricted' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 16 }}>
          <Card title={`违禁词 / 敏感词字典 · ${dict.length} 条`} right={
            <button style={{ ...window.btnGhost, height: 26, fontSize: 11 }}>+ 添加词条</button>
          }>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  <th style={{ textAlign: 'left', padding: '8px 6px', fontSize: 10.5, color: 'var(--muted)', textTransform: 'uppercase', fontWeight: 500 }}>词条</th>
                  <th style={{ textAlign: 'left', padding: '8px 6px', fontSize: 10.5, color: 'var(--muted)', textTransform: 'uppercase', fontWeight: 500 }}>分类</th>
                  <th style={{ textAlign: 'left', padding: '8px 6px', fontSize: 10.5, color: 'var(--muted)', textTransform: 'uppercase', fontWeight: 500 }}>风险等级</th>
                  <th style={{ textAlign: 'left', padding: '8px 6px', fontSize: 10.5, color: 'var(--muted)', textTransform: 'uppercase', fontWeight: 500 }}>命中处理</th>
                </tr>
              </thead>
              <tbody>
                {dict.map(w => (
                  <tr key={w.word} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '9px 6px', fontFamily: 'JetBrains Mono, monospace', fontWeight: 600 }}>{w.word}</td>
                    <td style={{ padding: '9px 6px', color: 'var(--muted)' }}>{w.cat}</td>
                    <td style={{ padding: '9px 6px' }}>
                      <Tag tone={w.risk === 'severe' ? 'danger' : w.risk === 'high' ? 'warn' : 'neutral'}>
                        {w.risk === 'severe' ? '严重 · CDQ 直接降至 U 级' : w.risk === 'high' ? '高 · 标题降为 C 级' : '低 · 建议规避'}
                      </Tag>
                    </td>
                    <td style={{ padding: '9px 6px', color: 'var(--muted)' }}>
                      {w.risk === 'severe' ? '索引抑制 · 立即整改' : w.risk === 'high' ? 'TQS 强制 C 级 · 立即整改' : 'TQS 扣分 · 计划整改'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <Card title="风险等级说明">
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <div>
                  <Tag tone="danger">严重</Tag>
                  <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 5, lineHeight: 1.5 }}>健康/医疗/杀虫声明类，触发即降至 CDQv3 U 级（政策违规）。</div>
                </div>
                <div>
                  <Tag tone="warn">高</Tag>
                  <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 5, lineHeight: 1.5 }}>促销主观语 / 误导性表达，TQS 直接 C 级。</div>
                </div>
                <div>
                  <Tag tone="neutral">低</Tag>
                  <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 5, lineHeight: 1.5 }}>建议规避词（Gift / Warranty 等），不构成硬违规但减分。</div>
                </div>
              </div>
            </Card>
            <Card title="数据源">
              <div style={{ fontSize: 11, color: 'var(--muted)', lineHeight: 1.6 }}>
                <div>· 亚马逊 Listing Quality Optimizer</div>
                <div>· 亚马逊商品名称要求</div>
                <div>· USPTO 商标数据库</div>
                <div>· CDQ v3 内部 Wiki</div>
              </div>
            </Card>
          </div>
        </div>
      )}

      {tab === 'tqs' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
          {[
            {
              g: 'A', tone: 'oklch(0.55 0.13 155)', label: '高质量',
              score: 'CDQ 标题质量评分 = 100%',
              cond: ['标题完整性 ≥ 0.6（品牌名 + 主关键词 + ≥3 个核心属性）', '冗余度 = 1（无冗余）', '总长度 ≤ 200（标题 ≤ 75 + Highlight ≤ 125）', '管套评分 > 0（含分隔符 |）', '特殊字符 = 1', '受限短语 = 1'],
            },
            {
              g: 'B', tone: 'oklch(0.55 0.13 75)', label: '中等质量',
              score: 'CDQ 标题质量评分 ≥ 50%',
              cond: ['未违反政策', '至少一个维度未达 A 级标准', 'TQS 各维度部分达标'],
            },
            {
              g: 'C', tone: 'oklch(0.55 0.18 25)', label: '违规',
              score: 'CDQ 标题质量评分 = 0%（CDQv3 = U）',
              cond: ['完整性 < 0.4（标记属性 < 2）', '或 冗余度 ≤ 0.6（同语境 > 2 重复）', '或 长度 > 200', '或 受限短语阈值 < 1'],
            },
          ].map(g => (
            <Card key={g.g} title={`${g.g} 级 · ${g.label}`}>
              <div style={{ fontSize: 64, fontWeight: 800, color: g.tone, letterSpacing: '-0.05em', lineHeight: 1, marginBottom: 8 }}>{g.g}</div>
              <div style={{ fontSize: 11.5, color: 'var(--muted)', marginBottom: 14 }}>{g.score}</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {g.cond.map((c, i) => (
                  <div key={i} style={{ fontSize: 11.5, paddingLeft: 14, position: 'relative', lineHeight: 1.5 }}>
                    <span style={{ position: 'absolute', left: 0, top: 7, width: 5, height: 5, borderRadius: 99, background: g.tone }} />
                    {c}
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
      )}

      {tab === 'weights' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <Card title="七维权重">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {window.CDQ_DIMENSIONS.map(d => (
                <div key={d.key}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <div style={{ fontSize: 12, fontWeight: 600, flex: 1 }}>{d.name}</div>
                    <div style={{ fontSize: 10.5, color: 'var(--muted)' }}>{d.group}</div>
                    <div style={{ fontSize: 13, fontWeight: 700, fontVariantNumeric: 'tabular-nums', minWidth: 40, textAlign: 'right' }}>{d.weight}%</div>
                  </div>
                  <div style={{ height: 18, background: 'var(--track)', borderRadius: 3, overflow: 'hidden', position: 'relative' }}>
                    <div style={{ width: `${(d.weight / 30) * 100}%`, height: '100%', background: 'var(--primary)', opacity: 0.85, display: 'flex', alignItems: 'center', paddingLeft: 6, fontSize: 10, color: '#fff', fontFamily: 'JetBrains Mono, monospace', fontWeight: 600 }}>{d.nameEn}</div>
                  </div>
                  <div style={{ fontSize: 10.5, color: 'var(--muted)', marginTop: 4 }}>{d.desc}</div>
                </div>
              ))}
            </div>
            <div style={{ marginTop: 14, padding: '10px 12px', background: 'var(--primary-soft)', borderRadius: 5, fontSize: 11.5, color: 'var(--primary)', fontFamily: 'JetBrains Mono, monospace' }}>
              合计 <b>100–120%</b>（产品分类 0–20% 浮动）· Orphan ASIN：变体 N/A 权重重新分配
            </div>
          </Card>

          <Card title="加分项细则 · CDQ v3">
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11.5 }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  <th style={{ textAlign: 'left', padding: '6px', fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', fontWeight: 500 }}>规则</th>
                  <th style={{ textAlign: 'right', padding: '6px', fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', fontWeight: 500 }}>加分</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['有分类叶节点 (Leaf Node)', '+10%'],
                  ['有搜索关键词', '+5%'],
                  ['有 A+ 页面 / 高级 A+', '+5% / +10%'],
                  ['标题以品牌名开头', '+5%'],
                  ['标题不堆砌词', '+5%'],
                  ['有 1 条商品要点', '+5%'],
                  ['有 3 条或以上商品要点', '+5%'],
                  ['遵循 0-1-3 原则', '+10%'],
                  ['关键词属性全部填写', '+25%'],
                  ['图片信息完善度', '+5%'],
                  ['有 4 张或以上图片', '+5%'],
                  ['主图缩放功能 (zoom)', '+10%'],
                  ['图片含相关属性完整性', '+5%'],
                  ['详情页 A+ 客户反馈关键信息', '+12.5%'],
                  ['IAI ≥ 0.4', '+10%'],
                ].map((r, i) => (
                  <tr key={i} style={{ borderBottom: '1px dashed var(--border)' }}>
                    <td style={{ padding: '7px 6px' }}>{r[0]}</td>
                    <td style={{ padding: '7px 6px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 700, color: 'oklch(0.55 0.13 155)' }}>{r[1]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}

      {tab === 'policy' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <Card title="字符与格式（标题）">
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, lineHeight: 1.7, color: 'var(--ink)' }}>
              <li>总长不超过 200 字符（含空格），推荐 75–200</li>
              <li>二段式标题：标题 ≤ 75 字符 + Highlight ≤ 125 字符（移动端友好）</li>
              <li>禁用特殊字符：<code style={{ fontFamily: 'JetBrains Mono, monospace', background: 'var(--bg)', padding: '0 4px', borderRadius: 2 }}>! $ ? _ {'{'} {'}'} ^ ¬ ¦</code></li>
              <li>仅每词首字母大写（介词/连词/冠词除外）</li>
              <li>使用阿拉伯数字（"2" 而非 "two"）</li>
              <li>计量单位可缩写（cm / oz / in / kg）</li>
              <li>不可重复（品牌名最多 1 次；介词/连词/冠词例外）</li>
            </ul>
          </Card>
          <Card title="禁止内容">
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, lineHeight: 1.7, color: 'var(--ink)' }}>
              <li>促销语 / 主观评价 / 价格 / 库存</li>
              <li>HTML / JS / 代码（&lt;br&gt; 例外）</li>
              <li>电话 / 邮箱 / URL / 联系方式</li>
              <li>评论 / 评价请求</li>
              <li>剧透 / 时效信息（活动日期）</li>
              <li>受限短语（如 "符合 FSA/HSA 要求"）</li>
            </ul>
          </Card>
          <Card title="结构化属性原则">
            <div style={{ fontSize: 12, color: 'var(--ink)', lineHeight: 1.65 }}>
              <p style={{ margin: '0 0 8px' }}><b>正确性 (60%) &gt; 完整性 (40%)</b>：错误属性会被 Rufus AI 识别冲突，触发降权。</p>
              <p style={{ margin: '0 0 8px' }}>无法填写的字段 → <b>填空格</b>，让系统识别为"已填空值"，不会被检索跳过。</p>
              <p style={{ margin: 0 }}>类目无关字段（如服饰类的电池字段）→ 可忽略。</p>
            </div>
          </Card>
          <Card title="变体与分类">
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, lineHeight: 1.7, color: 'var(--ink)' }}>
              <li>主题属性一致性 / 正确性 / 避免重复</li>
              <li>变体数量 ≥ 2</li>
              <li>不同商标必须创建新 ASIN（不可改商标）</li>
              <li>放置在最相关的叶节点 (Node ID)</li>
              <li>PT 精确（如 OXFORD 而非 SHOES）</li>
            </ul>
          </Card>
        </div>
      )}
    </div>
  );
}

window.RulesPanel = RulesPanel;
