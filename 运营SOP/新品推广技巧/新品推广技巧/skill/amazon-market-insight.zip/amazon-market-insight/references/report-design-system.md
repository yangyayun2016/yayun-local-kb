# Amazon Market Insight — Report Design System

## 1. 品牌身份

本设计体系服务于 Amazon Market Intelligence Report 系列，涵盖三份报告：
- `MarketingInsight.html` — 市场洞察
- `ConsumerInsight.html` — 消费者洞察  
- `ProductSolution.html` — 产品成功方案

品牌参考：**LUXEPET PRO** by LynxAI Strategic Output

---

## 2. 颜色系统

### 背景层级
```css
--bg-primary:    #0a0e1a;   /* 主背景 — 深海蓝黑 */
--bg-card:       #111827;   /* 卡片背景 */
--bg-card-hover: #1a2235;   /* 卡片悬停 */
--bg-section:    #0d1321;   /* 区块背景 */
```

### 强调色
```css
--accent-gold:      #f0c040;  /* 金色主强调 — 数据高亮、标题装饰 */
--accent-gold-dim:  #b8922e;  /* 暗金色 — 次级强调 */
--accent-blue:      #4a9eff;  /* 蓝色 — 链接、信息标签 */
--accent-green:     #22c55e;  /* 绿色 — 正向指标、机会标记 ✅ */
--accent-red:       #ef4444;  /* 红色 — 风险、负向指标 ❌ */
--accent-orange:    #f97316;  /* 橙色 — 警示、中等风险 ⚠️ */
--accent-purple:    #a855f7;  /* 紫色 — 消费者洞察专属 */
```

### 文字层级
```css
--text-primary:   #f0f4ff;   /* 主标题、关键数据 */
--text-secondary: #94a3b8;   /* 正文、说明文字 */
--text-muted:     #475569;   /* 辅助信息、括号内容 */
```

### 渐变方案
```css
--gradient-gold:    linear-gradient(135deg, #f0c040, #b8922e);
--gradient-blue:    linear-gradient(135deg, #1e3a5f, #0d1321);
--gradient-purple:  linear-gradient(135deg, #2d1b69, #0d1321);
--gradient-green:   linear-gradient(135deg, #14532d, #0d1321);
--gradient-header:  linear-gradient(135deg, #1e3a5f 0%, #0a0e1a 50%, #1a1a2e 100%);
```

---

## 3. 排版系统

### 字体栈
```css
font-family: 'Segoe UI', system-ui, -apple-system, 'Microsoft YaHei', sans-serif;
```

### 字号层级
| 用途 | 大小 | 字重 | 颜色 |
|------|------|------|------|
| 报告主标题 (H1) | 2.5rem | 800 | --text-primary |
| 章节标题 (H2) | 1.6rem | 700 | --accent-gold |
| 卡片标题 (H3) | 1.1rem | 600 | --text-primary |
| 正文 | 0.9rem | 400 | --text-secondary |
| 数据大字 | 2.8rem | 800 | --accent-gold |
| 标签/角标 | 0.72rem | 500 | --text-muted |

---

## 4. 组件规范

### 4.1 报告卡片（基础单元）
```css
.card {
  background: var(--bg-card);
  border: 1px solid rgba(240, 192, 64, 0.12);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(240, 192, 64, 0.08);
}
```

### 4.2 卡片顶部装饰线
```css
.card-accent-top {
  border-top: 3px solid var(--accent-gold);
}
.card-accent-blue { border-top: 3px solid var(--accent-blue); }
.card-accent-green { border-top: 3px solid var(--accent-green); }
.card-accent-purple { border-top: 3px solid var(--accent-purple); }
```

### 4.3 数据指标卡（Metric Card）
```html
<div class="metric-card">
  <div class="metric-value">636</div>
  <div class="metric-label">HHI 赫芬达尔指数</div>
  <div class="metric-badge badge-green">高度竞争</div>
</div>
```
```css
.metric-value { font-size: 2.8rem; font-weight: 800; color: var(--accent-gold); }
.metric-label { font-size: 0.78rem; color: var(--text-muted); margin-top: 0.3rem; }
.badge-green  { background: rgba(34,197,94,0.15); color: #22c55e; 
                padding: 2px 10px; border-radius: 20px; font-size: 0.72rem; }
```

### 4.4 数据表格
```css
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}
.data-table th {
  background: rgba(240, 192, 64, 0.08);
  color: var(--accent-gold);
  padding: 0.7rem 1rem;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid rgba(240,192,64,0.2);
}
.data-table td {
  padding: 0.65rem 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  color: var(--text-secondary);
}
.data-table tr:nth-child(even) td { background: rgba(255,255,255,0.02); }
.data-table tr:hover td { background: rgba(240, 192, 64, 0.04); }
```

### 4.5 波士顿矩阵（2×2 象限）
```css
.bcg-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 0.5rem;
  min-height: 280px;
}
.bcg-quadrant { padding: 1rem; border-radius: 8px; }
.bcg-q1 { background: rgba(34, 197, 94, 0.08); border: 1px solid rgba(34,197,94,0.2); } /* 新星爆发 */
.bcg-q2 { background: rgba(240,192,64, 0.08); border: 1px solid rgba(240,192,64,0.2); } /* 核心主流 */
.bcg-q3 { background: rgba(248,113,113,0.06); border: 1px solid rgba(248,113,113,0.15);} /* 利基衰退 */
.bcg-q4 { background: rgba(100,116,139,0.06); border: 1px solid rgba(100,116,139,0.15);} /* 成熟存量 */
```

### 4.6 竞争强度评级徽章
```css
.ci-high   { background: rgba(239,68,68,0.15);  color: #ef4444; padding: 3px 12px; border-radius: 20px; }
.ci-medium { background: rgba(249,115,22,0.15); color: #f97316; padding: 3px 12px; border-radius: 20px; }
.ci-low    { background: rgba(34,197,94,0.15);  color: #22c55e; padding: 3px 12px; border-radius: 20px; }
```

### 4.7 SI 指数着色规则
| SI 区间 | 角色标签 | 颜色 |
|---------|---------|------|
| ≥ 1.2 | 核心成交 🎯 | #22c55e |
| 1.0-1.2 | 溢价支撑 💎 | #f0c040 |
| 0.8-1.0 | 基础准入 📋 | #94a3b8 |
| < 0.8 | 无差别/反向 ❌ | #475569 |

### 4.8 Persona 卡片
```css
.persona-card {
  border-left: 4px solid var(--accent-purple);
  background: linear-gradient(135deg, rgba(168,85,247,0.05), rgba(11,14,26,0.95));
  border-radius: 12px;
  padding: 1.5rem;
}
.persona-avatar { width: 48px; height: 48px; border-radius: 50%; 
                  background: var(--gradient-purple); display: flex; 
                  align-items: center; justify-content: center; font-size: 1.4rem; }
.persona-share { font-size: 2rem; font-weight: 800; color: var(--accent-purple); }
```

### 4.9 JTBD 任务矩阵行
```css
.jtbd-row { 
  display: grid; 
  grid-template-columns: 2fr 2fr 1.5fr 1.5fr;
  gap: 1rem; 
  padding: 1rem; 
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.kano-delight  { color: #f0c040; } /* 魅力需求 */
.kano-expected { color: #4a9eff; } /* 期望需求 */
.kano-basic    { color: #94a3b8; } /* 基础需求 */
```

### 4.10 导航栏
```css
.report-nav {
  position: sticky; top: 0; z-index: 100;
  background: rgba(10,14,26,0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(240,192,64,0.15);
  padding: 0.75rem 2rem;
  display: flex; gap: 1.5rem; align-items: center;
}
.nav-link {
  color: var(--text-secondary); text-decoration: none; font-size: 0.85rem;
  padding: 0.3rem 0.75rem; border-radius: 20px;
  transition: all 0.2s;
}
.nav-link:hover, .nav-link.active {
  color: var(--accent-gold);
  background: rgba(240,192,64,0.1);
}
```

---

## 5. 页面结构模板

### MarketingInsight.html
```
<nav> — 固定导航（报告名 + 各章节锚点）
<header> — 报告头 + 战略定性标签
#diagnosis — 款式诊断卡（每款式一个 card）
#matrix — 波士顿矩阵 + 款式趋势动能 TABLE A
#features — 卖点战略角色矩阵
#market-map — 市场地图（价格带×款式 表格）
#concentration — 市场集中度分析（HHI/CR/NPRS/NETI/Bd/CI 指标卡 + 文字分析）
#competition — 分款式竞争强度全览
#opportunity — 机会款式判断表 + 分析结论
```

### ConsumerInsight.html
```
<nav>
<header> — 品类 + 数据口径标注
#data-scope — 数据说明（样本量/来源/口径）
#ecosystem — 三圈层信息生态模型
#core-layer — 核心圈分析
#middle-layer — 中间圈分析
#outer-layer — 外围圈分析
#personas — 关键人群（每 Persona 一个 section）
#key-findings — 关键洞察 Key Findings
```

### ProductSolution.html
```
<nav>
<header> — LUXEPET PRO 品牌头 + 5 模块预览
#scheme-a — 方案A Essential
  #scheme-a-def — 产品定义
  #scheme-a-persona — 人群画像
  #scheme-a-jtbd — JTBD 映射
  #scheme-a-journey — 用户旅程
  #scheme-a-proof — 成功论证
  #scheme-a-entry — 市场进入策略
  #scheme-a-product — 产品实现
  #scheme-a-biz — 商业可行性
  #scheme-a-gtm — GTM 推广
#scheme-b — 方案B Pro（同结构）
#scheme-c — 方案C Designer（同结构）
```

---

## 6. 响应式断点

```css
/* Mobile */
@media (max-width: 768px) {
  .grid-2col { grid-template-columns: 1fr; }
  .data-table-wrap { overflow-x: auto; }
  .bcg-grid { grid-template-columns: 1fr; }
  .report-nav { overflow-x: auto; }
}
/* Tablet */
@media (max-width: 1024px) {
  .grid-3col { grid-template-columns: repeat(2, 1fr); }
}
```

---

## 7. 特殊组件

### 7.1 战场定性徽章（战略类型标签）
```html
<span class="battle-badge battle-war">⚔️ 乱世争霸赛</span>
<span class="battle-badge battle-niche">🔻 利基衰退</span>
<span class="battle-badge battle-star">🌟 新星爆发</span>
<span class="battle-badge battle-cash">💰 成熟存量</span>
```

### 7.2 机会判断标记
```html
<span class="opportunity yes">✅ 机会款式</span>
<span class="opportunity no">❌ 非机会款式</span>
```

### 7.3 KANO 需求星级
```
⭐⭐⭐⭐⭐ (必备/期望需求)
⭐⭐⭐⭐  (期望需求/魅力需求)
⭐⭐⭐   (观察)
```

### 7.4 供应链壁垒标签
```html
<span class="barrier hard">🔩 硬件壁垒</span>
<span class="barrier soft">💻 软件/组装</span>
<span class="barrier design">🎨 设计策略</span>
```