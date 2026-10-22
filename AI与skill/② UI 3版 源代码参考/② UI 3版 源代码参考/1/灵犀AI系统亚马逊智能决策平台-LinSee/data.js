// ==================================================================
//  LinSee · CDQv3 完整评分细则 · 细化版 v4
//  - 每个维度都有 公式 / 子规则 / 等级阶梯 / 红旗清单 / 命中明细
//  - 每个子规则都有：公式、阈值、加扣分逻辑、A/B/C 阈值、示例
// ==================================================================

window.LS_I18N = {
  zh: {
    appName: "LinSee 灵犀", appSub: "亚马逊 Listing 智能诊断",
    navDashboard: "仪表盘", navDiagnose: "单条诊断", navCompare: "对比分析",
    navHistory: "历史记录", navKnowledge: "知识库", navTeam: "团队与批注",
    navMember: "会员中心", navNew: "新建诊断",
    searchPlaceholder: "搜索 ASIN、标题或类目…",
    runDiagnosis: "运行诊断", export: "导出", share: "分享", addAnno: "添加批注",
  },
  en: {
    appName: "LinSee", appSub: "Amazon Listing Intelligence",
    navDashboard: "Dashboard", navDiagnose: "Diagnose", navCompare: "Compare",
    navHistory: "History", navKnowledge: "Knowledge", navTeam: "Team & Notes",
    navMember: "Membership", navNew: "New audit",
    searchPlaceholder: "Search ASIN, title or category…",
    runDiagnosis: "Run diagnosis", export: "Export", share: "Share", addAnno: "Add note",
  }
};

// ------------------------------------------------------------------
// CDQv3 六大组件 — 完整细则 (权重合计 100%)
// ------------------------------------------------------------------
window.LS_RUBRIC = [
  // ============================================================
  //  1. 标题质量 25%  · TQS = Σ(子项权重 × 子项达成率)
  // ============================================================
  {
    key: "title", name: "标题质量", nameEn: "Title Quality", weight: 25,
    desc: "TQS 标题质量分：完整性、冗余度、篇幅（二段式 75+125）、大小写、管套分隔、特殊字符、受限词与促销词、品牌前置八项加权。",
    descEn: "TQS: completeness, redundancy, two-part length (75+125), casing, pipe separators, charset, restricted/promo words, brand-lead.",
    formula: "TQS = 完整性·20 + 冗余度·15 + 篇幅·10 + 大小写·10 + 管套·10 + 字符·10 + 受限·15 + 品牌·10",
    maxHint: "满分 100 · 权重 25%",
    subs: [
      { k: "complete",  n: "标题完整性", nEn: "Completeness", weight: 20,
        rule: "含品牌名 + 主关键词 + ≥3 项核心属性 + 适用人群/场景，无语法错误",
        formula: "complete = min(1, 标注属性数 / 3)",
        ladder: [{g:"A",cond:"≥0.6",hint:"≥3 项属性"},{g:"B",cond:"0.4–0.6",hint:"2 项"},{g:"C",cond:"<0.4",hint:"<2 项 → U 级"}],
        eg: "✓ 'Anker 240W USB-C Cable, 6ft, Bio-Nylon'（品牌+功率+类型+长度+材质 = 5 项）" },
      { k: "redundant", n: "关键词冗余度", nEn: "Redundancy", weight: 15,
        rule: "同语境同词重复 ≤2 次；品牌名不可出现 2 次；介词/冠词/连词不受限",
        formula: "redundant = 1 − (重复词次数 / 总词数)",
        ladder: [{g:"A",cond:"=1.0",hint:"无冗余"},{g:"B",cond:">0.6",hint:"轻度"},{g:"C",cond:"≤0.6",hint:"同词 >2 次 → U 级"}],
        eg: "✗ 'Baby Boy Outfits Baby Boy Clothes Baby Boy Sets' — Baby Boy 重复 3 次" },
      { k: "length",    n: "篇幅（二段式）", nEn: "Length (two-part)", weight: 10,
        rule: "主标题 ≤75 字符 + HIGHLIGHT ≤125 字符，总长 ≤200；建议 75–200，移动端友好 ≤80",
        formula: "length = 1 (75≤L≤200) | 0.5 (60≤L<75) | 0 (L>200)",
        ladder: [{g:"A",cond:"75–200",hint:"主标题≤75为佳"},{g:"B",cond:"60–75",hint:"略短"},{g:"C",cond:">200",hint:"政策违规 → U 级"}],
        eg: "二段式测试中：前段放产品基本信息，后段 HIGHLIGHT 放差异点" },
      { k: "casing",    n: "大小写规范", nEn: "Casing", weight: 10,
        rule: "每词首字母大写；介词/连词/冠词小写；禁止全大写；数字用阿拉伯数字",
        formula: "casing = 合规词数 / 总词数",
        ladder: [{g:"A",cond:">0.95",hint:"全合规"},{g:"B",cond:">0.8",hint:"少量错误"},{g:"C",cond:"≤0.6",hint:"违规"}],
        eg: "✓ 'USB-C to USB-C Cable for iPhone 15' · 用 '2' 不用 'two'  ✗ 'USB-C TO USB-C CABLE'" },
      { k: "pipe",      n: "管套评分（分隔符）", nEn: "Pipe separators", weight: 10,
        rule: "至少 1 个管道符（|）或分隔符，清晰分隔信息段（A 级必要条件：管套评分 >0）",
        formula: "pipe = 分隔符数 ≥1 ? 1 : 0",
        ladder: [{g:"A",cond:">0",hint:"有分隔符"},{g:"C",cond:"=0",hint:"无分隔 → 无法达 A"}],
        eg: "✓ 'Anker USB-C Cable | 240W Fast Charging | 6ft Bio-Nylon'" },
      { k: "charset",   n: "特殊字符", nEn: "Charset", weight: 10,
        rule: "禁用 ! $ ? _ { } ^ ¬ ¦；~ # < > * 仅限编码/测量语境；禁止装饰性符号与 emoji",
        formula: "charset = 1 (无违规字符) | 0",
        ladder: [{g:"A",cond:"=1.0",hint:"洁净"},{g:"C",cond:"<1.0",hint:"含违规字符 → Poor"}],
        eg: "✓ '款式 #4301' '<10 磅'（合法语境） ✗ '<< Size Kids XXS >>'（装饰性）" },
      { k: "restricted",n: "受限与促销词", nEn: "Restricted & promo", weight: 15,
        rule: "无促销词（Best/Free Shipping/#1/Top Rated/Gift/Warranty）、无健康医疗声明（Antibacterial/Sanitize/Anti-Mites/UV Sterilize）、无竞品品牌词",
        formula: "restricted = 1 (无命中) | 0 (任一命中 → U 级)",
        ladder: [{g:"A",cond:"=1",hint:"清洁"},{g:"C",cond:"=0",hint:"含违禁词 → 评分 0 / U 级"}],
        eg: "✗ 'Best Seller' 'FSA/HSA Eligible' '100% Quality Guaranteed' 'Antimicrobial'" },
      { k: "brandLead", n: "品牌前置 + 不堆砌", nEn: "Brand-lead + No stuffing", weight: 10,
        rule: "品牌名作为标题第一词；结构 = 品牌 + 核心产品名 + 关键属性；无关键词堆砌",
        formula: "brandLead = brandFirst·0.5 + noStuff·0.5",
        ladder: [{g:"A",cond:"=1",hint:"前置且无堆砌"},{g:"B",cond:"=0.5",hint:"二者居其一"},{g:"C",cond:"=0",hint:"未前置且堆砌"}],
        eg: "✓ 'Amazon Basics 60W USB-C Cable...'  ✗ 'USB Cable Type C Cord Charger USBC...'" },
    ],
    tiers: [
      { g: "A", label: "高质量", cond: "完整性≥0.6 且 冗余度=1 且 长度≤200 且 管套>0 且 字符=1 且 受限=1 → TQS=100%", score: [100, 100] },
      { g: "B", label: "合格",   cond: "未违反政策，但 ≥1 项未达高质量标准（TQS ≥50%）", score: [50, 99] },
      { g: "C", label: "违规 → U 级", cond: "完整性<0.4 或 冗余度≤0.6 或 长度>200 或 含受限短语 → TQS=0%，CDQv3 等级 U，评分 N/A", score: [0, 0] },
    ],
  },

  // ============================================================
  //  2. 结构化属性 30%  · 评分 = Σ(完整性 × 正确性 × 权重)
  // ============================================================
  {
    key: "attr", name: "结构化属性", nameEn: "Structured Attributes", weight: 30,
    desc: "RAI 前 6 项 + Band A 转化属性 + Band B 体验属性，三层权重叠加。正确性优先于完整性；IAI ≥ 0.4 解锁 +10。",
    descEn: "RAI Top 6 + Band A/B (Depth Widget). Correctness > completeness. IAI ≥ 0.4 unlocks +10.",
    formula: "score = Σ (weight × completeness_i × correctness_i) + IAI≥0.4 ? 10 : 0 + Top4最优 ? 5 : 0 【正确性 > 完整性】",
    maxHint: "满分 100 · 权重 30%",
    subs: [
      { k: "rai_title", n: "RAI · 标题",       nEn: "RAI · Title", band: "RAI", weight: 10,
        rule: "品牌+核心词+功能+尺寸结构完整，无堆砌、无违禁",
        formula: "rai_title = 标题完整性 × 标题正确性",
        ladder: [{g:"A",cond:"≥0.9"},{g:"B",cond:"≥0.7"},{g:"C",cond:"<0.7"}],
        eg: "权重最高的 RAI 字段。补全可一次性拉动 IAI 上限" },
      { k: "rai_brand", n: "RAI · 品牌",       nEn: "RAI · Brand", band: "RAI", weight: 8,
        rule: "与品牌备案一致（大小写敏感），不可为 Generic",
        formula: "rai_brand = 备案匹配 ? 1 : 0",
        ladder: [{g:"A",cond:"=1"},{g:"C",cond:"=0",hint:"将触发品牌违规"}],
        eg: "✓ 'Amazon Basics'  ✗ 'amazon basics' / 'Generic'" },
      { k: "rai_cat",   n: "RAI · 分类叶节点", nEn: "RAI · Leaf node", band: "RAI", weight: 12,
        rule: "落在最相关叶子节点，不能停在中间分类",
        formula: "rai_cat = 是否叶子节点 ? 1 : 0.3",
        ladder: [{g:"A",cond:"叶子",hint:"+10 可发现性奖励"},{g:"C",cond:"非叶子"}],
        eg: "Electronics › Cables › USB Cables › USB-C to USB-C  ← 叶节点" },
      { k: "rai_bul",   n: "RAI · 五点",       nEn: "RAI · Bullets", band: "RAI", weight: 8,
        rule: "前两点必须覆盖核心卖点 + 使用场景",
        formula: "rai_bul = (前两点完整性 + 0-1-3 命中) / 2",
        ladder: [{g:"A",cond:"≥0.9"},{g:"B",cond:"≥0.7"},{g:"C",cond:"<0.7"}],
        eg: "Bullet 1 = 主卖点（功率/速度），Bullet 2 = 场景（设备兼容）" },
      { k: "rai_pt",    n: "RAI · Product Type", nEn: "RAI · Product Type", band: "RAI", weight: 10,
        rule: "精确叶级 PT，禁止家族泛化值",
        formula: "rai_pt = 是否叶级 ? 1 : 0.4",
        ladder: [{g:"A",cond:"叶级 PT"},{g:"C",cond:"家族 PT",hint:"扣 60%"}],
        eg: "✓ CABLE_USB_C_TO_C  ✗ CABLE (家族级)" },
      { k: "rai_main",  n: "RAI · 主图",       nEn: "RAI · Main image", band: "RAI", weight: 10,
        rule: "纯白底 (#FFFFFF) · 产品占比 ≥85% · 无水印/边框",
        formula: "rai_main = 0.4·白底 + 0.4·占比 + 0.2·无水印",
        ladder: [{g:"A",cond:"≥0.9"},{g:"B",cond:"≥0.7"},{g:"C",cond:"<0.7"}],
        eg: "白底通过 RGB 阈值检测 (R>250 & G>250 & B>250)" },
      { k: "a_size",    n: "Band A · 规格/颜色/材质", nEn: "A · Size/Color/Material", band: "A", weight: 8,
        rule: "通过 variation 正确表达；与实物一致",
        formula: "a_size = (规格·色·料) 三项平均完整性",
        ladder: [{g:"A",cond:"≥0.9"},{g:"B",cond:"≥0.6"},{g:"C",cond:"<0.6"}],
        eg: "Band A 字段直接驱动转化，缺失 = 退货率上升 1.8x" },
      { k: "a_weight",  n: "Band A · 重量/尺寸", nEn: "A · Weight & Dims", band: "A", weight: 6,
        rule: "与物流实测误差 ≤2%",
        formula: "a_weight = 1 − |填报 − 实测| / 实测",
        ladder: [{g:"A",cond:"≥0.98"},{g:"B",cond:"≥0.9"},{g:"C",cond:"<0.9"}],
        eg: "尺寸误差 >5% 将触发 FBA 计费纠纷" },
      { k: "a_model",   n: "Band A · 型号/风格", nEn: "A · Model & Style", band: "A", weight: 6,
        rule: "用于亚马逊 AI 相似产品识别和广告同类匹配",
        formula: "a_model = (型号填写 ? 1 : 0) × 0.5 + (风格枚举 ? 1 : 0) × 0.5",
        ladder: [{g:"A",cond:"=1"},{g:"B",cond:"=0.5"},{g:"C",cond:"=0"}],
        eg: "✓ Model: AB-USBC60-6FT  ✓ Style: Braided" },
      { k: "b_feat",    n: "Band B · 特殊功能", nEn: "B · Special features", band: "B", weight: 6,
        rule: "Portable / Auto-shutoff / Fast-charging 等枚举值",
        formula: "b_feat = 命中枚举数 / 推荐枚举数",
        ladder: [{g:"A",cond:"≥0.8"},{g:"B",cond:"≥0.5"},{g:"C",cond:"<0.5"}],
        eg: "影响左侧筛选栏可见性，每填一项 = 一个流量入口" },
      { k: "b_aud",     n: "Band B · 目标人群", nEn: "B · Target audience", band: "B", weight: 8,
        rule: "Professional / Beginner / Travel 等枚举",
        formula: "b_aud = 人群枚举命中 / 推荐人群数",
        ladder: [{g:"A",cond:"≥0.8"},{g:"B",cond:"≥0.5"},{g:"C",cond:"<0.5"}],
        eg: "驱动 Posts / Brand Story 个性化推送" },
      { k: "b_use",     n: "Band B · 使用场景", nEn: "B · Usage scenario", band: "B", weight: 8,
        rule: "Indoor / Travel / Office 等场景枚举",
        formula: "b_use = 场景枚举命中 / 推荐场景数",
        ladder: [{g:"A",cond:"≥0.8"},{g:"B",cond:"≥0.5"},{g:"C",cond:"<0.5"}],
        eg: "✓ Indoor + Travel + Office 三场景全填" },
    ],
    flags: [
      { k: "iai", n: "IAI ≥ 0.4 +10", rule: "属性综合指数 IAI = Σ完整正确率 ≥ 0.4 时全维加 10" },
      { k: "top4", n: "Top 4 相关属性最优 +5", rule: "RAI Top 4 (品牌/分类/PT/主图) 全 A 时加 5" },
    ],
    criticals: [
      "大多数 PT 中前 6 项相关属性错误 → 立即影响等级",
      "前 10 项相关属性完整性 < 50% → 立即降级 D",
      "误导性属性值（文字与图片/实物冲突）→ 触发买家投诉",
    ],
  },

  // ============================================================
  //  3. 变体质量 20%  · 主题一致 + 属性正确 + 子项去重
  // ============================================================
  {
    key: "vari", name: "变体质量", nameEn: "Variation Quality", weight: 20,
    desc: "变体主题一致性、属性枚举正确性、子项去重；严重缺陷立即降级。孤儿 ASIN（无变体家族）此项 N/A，20% 权重重新分配至其它维度（如图片升至 18.75%）。",
    descEn: "Theme consistency, enum correctness, de-dup. Orphan ASINs: N/A, weight redistributed (Image → 18.75%).",
    formula: "score = Σ(子项权重 × 达成率) − 严重缺陷·25 − 软缺陷·8",
    maxHint: "满分 100 · 权重 20%",
    subs: [
      { k: "theme_ok",  n: "变体主题一致性", nEn: "Theme consistency", weight: 25,
        rule: "父子变体主题完全一致（不可父 Color、子 Size）",
        formula: "theme_ok = 父子主题完全匹配 ? 1 : 0",
        ladder: [{g:"A",cond:"=1"},{g:"C",cond:"=0",hint:"立即扣 25"}],
        eg: "父：Color × Length；所有子 SKU 均带 Color + Length 字段" },
      { k: "attr_ok",   n: "变体属性正确性", nEn: "Attribute correctness", weight: 25,
        rule: "Size/Color 必须为亚马逊枚举值，不可自创",
        formula: "attr_ok = 枚举命中数 / 总属性数",
        ladder: [{g:"A",cond:"=1"},{g:"B",cond:"≥0.85"},{g:"C",cond:"<0.85"}],
        eg: "✓ Color: Black / White / Navy   ✗ Color: 'midnight obsidian'" },
      { k: "no_dup",    n: "子项去重", nEn: "No child duplication", weight: 20,
        rule: "不同 SKU 属性组合不可完全重复",
        formula: "no_dup = 1 − (重复 SKU 数 / 总 SKU 数)",
        ladder: [{g:"A",cond:"=1"},{g:"B",cond:"≥0.9"},{g:"C",cond:"<0.9"}],
        eg: "✗ 6ft·Black 出现 2 个 SKU，会被合并并降权" },
      { k: "family",    n: "变体家族 ≥2", nEn: "Family ≥ 2", weight: 15,
        rule: "至少 2 个子变体才进入评分",
        formula: "family = 子 SKU 数 ≥ 2 ? 1 : 0",
        ladder: [{g:"A",cond:"≥2"},{g:"C",cond:"=1",hint:"无变体"}],
        eg: "1 个变体的 listing 仅按 SP 计分" },
      { k: "rich",      n: "丰富属性", nEn: "Rich attributes", weight: 15,
        rule: "≥3 个变体维度（Color × Length × Pack 等）",
        formula: "rich = min(1, 变体维度 / 3)",
        ladder: [{g:"A",cond:"≥3"},{g:"B",cond:"=2"},{g:"C",cond:"=1"}],
        eg: "Color × Length × Pack 三维 = 满分" },
    ],
    criticalsStrict: [
      "错误的属性值（非枚举）",
      "单位制混用（cm / inch、ft / Foot 同时出现）",
      "变体信息冗余（父子描述字段重复 ≥60%）",
      "本地化错误（en-US 翻译错）",
      "子项完全重复（属性组合一致）",
    ],
    criticalsSoft: [
      "未标准化的属性值（如 '6ft' vs '6 Foot'）",
      "格式不匹配（数字 vs 字符串）",
      "变体主题错误（应该 Size 实际填 Color）",
    ],
  },

  // ============================================================
  //  4. 图片与 A+ 15%
  // ============================================================
  {
    key: "img", name: "图片质量", nameEn: "Image Quality", weight: 15,
    desc: "四象限矩阵：数量≥4 × 无缺陷为核心判定；另含 IAI、主图缩放、有效像素占比 ≥85%、alt 属性完整性。孤儿 ASIN 权重 18.75%。",
    descEn: "Count×defect matrix core; plus IAI, zoom, ≥85% effective pixels, alt completeness. 18.75% for orphans.",
    formula: "score = matrix(数量, 缺陷) × 60 + IAI·15 + 缩放·15 + 信息完善·10",
    maxHint: "满分 100 · 权重 15%（孤儿 18.75%）",
    matrix: [
      { cond: "图片数 ≥4 且 无图片缺陷", score: "1.0 (100%)", tone: "pass" },
      { cond: "图片数 ≥4 但 存在图片缺陷", score: "0.4 (40%)", tone: "warn" },
      { cond: "图片数 <4 且 无缺陷", score: "0.6 (60%)", tone: "warn" },
      { cond: "图片数 <4 且 存在缺陷", score: "0.0 (0%)", tone: "fail" },
    ],
    subs: [
      { k: "count",     n: "图像数量 ≥4", nEn: "Images ≥ 4", weight: 20,
        rule: "主图 + 副图（结构 / 特写 / 场景 / 尺寸 / 包装 / 对比），≥4 张 +5%",
        formula: "count = 图片数 ≥4 ? 1 : 0.6（无缺陷时）",
        ladder: [{g:"A",cond:"≥6"},{g:"B",cond:"≥4"},{g:"C",cond:"<4"}],
        eg: "四象限矩阵：≥4+无缺陷=100% · ≥4+有缺陷=40% · <4+无缺陷=60% · <4+有缺陷=0%" },
      { k: "iai",       n: "IAI ≥0.4", nEn: "IAI ≥ 0.4", weight: 20,
        rule: "Imaging Attribute Index：对比同类目相似产品的图像完整度与元数据质量",
        formula: "iai = f(图像元数据, 属性完整度, 同类对比)",
        ladder: [{g:"A",cond:"≥0.7"},{g:"B",cond:"≥0.4",hint:"解锁 +10"},{g:"C",cond:"<0.4"}],
        eg: "IAI 按产品类型汇总评估图像元数据与属性" },
      { k: "pixel85",   n: "有效像素 ≥85%", nEn: "Effective pixels ≥ 85%", weight: 20,
        rule: "产品在整张图片上的占比 ≥85%（亚马逊 S3 图库系统标准）",
        formula: "pixel85 = 产品像素面积 / 图片总面积 ≥ 0.85",
        ladder: [{g:"A",cond:"≥85%"},{g:"B",cond:"70–85%"},{g:"C",cond:"<70%"}],
        eg: "第一要点：产品占比；其次打标签让系统收录关键词并匹配产品" },
      { k: "alt_attr",  n: "图片 alt 属性完整", nEn: "Alt attributes", weight: 20,
        rule: "图片 alt 标签具有相关属性的完整性，帮助系统收录关键词",
        formula: "alt_attr = 已标注图片 / 总图片",
        ladder: [{g:"A",cond:"=1"},{g:"B",cond:"≥0.6"},{g:"C",cond:"<0.6"}],
        eg: "alt 标签 = 系统关键词收录入口，影响搜索匹配" },
      { k: "zoom",      n: "主图缩放", nEn: "Main image zoom", weight: 20,
        rule: "分辨率 ≥1000px（推荐 ≥2000px）启用 zoom",
        formula: "zoom = 长边 px ≥1000 ? 1 : 0",
        ladder: [{g:"A",cond:"≥2000"},{g:"B",cond:"≥1000"},{g:"C",cond:"<1000"}],
        eg: "推荐 2400×2400 px，JPG 压缩率 ≤90%" },
    ],
  },

  // ============================================================
  //  5. 五点与描述 5%  · 0-1-3 卖点分布原则
  // ============================================================
  {
    key: "bul", name: "五点与描述", nameEn: "Bullets & Description", weight: 5,
    desc: "Bullet 数量 + 0-1-3 卖点分布（0 遗漏 / 1 主打 / ≥3 魅力）+ 关键属性覆盖。",
    descEn: "Count + 0-1-3 distribution rule + key attribute coverage.",
    formula: "score = 数量·30 + 卖点·20 + 关键属性·20 + 0-1-3·30",
    maxHint: "满分 100 · 权重 5%",
    subs: [
      { k: "count3",    n: "Bullet 数量", nEn: "Bullet count", weight: 30,
        rule: "≥3 条 = 100% · ≥1 条 = 50% · 无 = 0%",
        formula: "count3 = 数量 ≥3 ? 1 : 数量 ≥1 ? 0.5 : 0",
        ladder: [{g:"A",cond:"≥5"},{g:"B",cond:"=3-4"},{g:"C",cond:"<3"}],
        eg: "亚马逊允许最多 5 条 Bullet" },
      { k: "count5",    n: "≥3 条商品要点", nEn: "3+ selling points", weight: 20,
        rule: "其中至少 3 条聚焦在不同卖点维度",
        formula: "count5 = 不同维度卖点数 / 3",
        ladder: [{g:"A",cond:"≥3"},{g:"B",cond:"=2"},{g:"C",cond:"<2"}],
        eg: "三个维度示例：性能 + 兼容性 + 耐用性" },
      { k: "key_attr",  n: "关键属性 100%", nEn: "Key attrs 100%", weight: 20,
        rule: "Bullet 中需明确出现核心属性数值",
        formula: "key_attr = Bullet 中命中关键字 / 关键字总数",
        ladder: [{g:"A",cond:"=1"},{g:"B",cond:"≥0.7"},{g:"C",cond:"<0.7"}],
        eg: "USB 类目关键字：功率 / 长度 / 速率 / 兼容设备" },
      { k: "rule013",   n: "0-1-3 原则", nEn: "0-1-3 rule", weight: 30,
        rule: "0 遗漏核心 + 1 个主打卖点 + ≥3 个魅力卖点",
        formula: "rule013 = 0_miss·0.4 + 1_hero·0.2 + 3_charm·0.4",
        ladder: [{g:"A",cond:"=1"},{g:"B",cond:"≥0.7"},{g:"C",cond:"<0.7"}],
        eg: "主打：功率（60W 快充）；魅力：编织、长度、设备适配" },
    ],
  },

  // ============================================================
  //  6. A+ 内容 5%
  // ============================================================
  {
    key: "aplus", name: "A+ 内容", nameEn: "A+ Content", weight: 5,
    desc: "二元判定：存在 = 100%，不存在 = 0%，无部分得分。A+ 内容质量评估计划于 2026 年上线。",
    descEn: "Binary: present = 1.0, absent = 0. Content-quality scoring planned for 2026.",
    formula: "score = A+ 存在 ? 100 : 0（二元，无部分得分）",
    maxHint: "满分 100 · 权重 5%",
    subs: [
      { k: "exist",     n: "A+ 存在（二元）", nEn: "A+ exists (binary)", weight: 100,
        rule: "存在任意 A+ 内容 → 1.0；不存在 → 0.0；当前不评估内容好坏",
        formula: "exist = hasAPlus ? 1 : 0",
        ladder: [{g:"A",cond:"存在",hint:"100%"},{g:"C",cond:"不存在",hint:"0%"}],
        eg: "2026 起将评估 A+ 内容质量；目前仅检查存在与否。Premium A+ 在图片维度另有加分" },
    ],
  },

  // ============================================================
  //  7. 产品类型分类 / 可发现性 0–20% · 加分项（总分 100–120）
  // ============================================================
  {
    key: "ptc", name: "产品类型分类（可发现性）", nameEn: "PT Classification (Discoverability)", weight: 20, bonus: true,
    desc: "评估组：Discoverability。权重 0–20% 加分项，总分可达 120。要求有准确、详细的叶节点 Node ID，包含搜索关键词与类目词。部分站点（如 IE）尚未上线。",
    descEn: "Discoverability group. 0–20% bonus (total up to 120). Requires accurate leaf Node ID + search keywords.",
    formula: "bonus = 叶节点·10 + 搜索关键词·5 + 类目词匹配·5（计入总分 100–120）",
    maxHint: "加分 0–20 · 不计入 100 基础盘",
    subs: [
      { k: "leaf",      n: "分类叶节点 Node ID", nEn: "Leaf Node ID", weight: 50,
        rule: "具有准确且详细的类目细分节点，正确且相关",
        formula: "leaf = 叶节点正确相关 ? 1 : 0",
        ladder: [{g:"A",cond:"叶节点",hint:"+10"},{g:"C",cond:"非叶/错误",hint:"0"}],
        eg: "Electronics › Cables › USB Cables › USB-C to USB-C ← Node ID 精确到叶级" },
      { k: "kw",        n: "搜索关键词", nEn: "Search keywords", weight: 25,
        rule: "后台 Search Terms 已填写，含类目词与节点词",
        formula: "kw = 已填写且命中类目词 ? 1 : 0.5 (部分) : 0",
        ladder: [{g:"A",cond:"完整",hint:"+5"},{g:"B",cond:"部分"},{g:"C",cond:"未填"}],
        eg: "DART 工具可识别需要 enrich 的属性与搜索词" },
      { k: "funnel",    n: "NPL 漏斗指标", nEn: "NPL funnel metrics", weight: 25,
        rule: "Traffic (GV/100k) · 加购率 (ATC/GV) · 转化率 (Units/GV) 追踪中",
        formula: "funnel = 监控中指标数 / 3",
        ladder: [{g:"A",cond:"3/3",hint:"+5"},{g:"B",cond:"≥1"},{g:"C",cond:"0"}],
        eg: "新品 NPL：提前 6–12 个月提交计划，提前 4–6 周上 A+ 并加入 Vine" },
    ],
  },
];

// ------------------------------------------------------------------
// 红旗 / 可发现性
// ------------------------------------------------------------------
window.LS_FLAGS = [
  {
    key: "policy", name: "策略违规", nameEn: "Policy violation",
    desc: "一票否决：触发后 Listing 被索引 / 网站抑制。",
    items: [
      "索引 / 网站抑制（搜索结果不展示）",
      "标题政策违规（不完整、冗余、受限关键词、长度或大小写错误）",
      "严重缺陷 — 大多数 PT 中前 6 项相关属性错误，或前 10 项相关属性完整性 <50%",
      "变异严重缺陷（错误属性值、单位混用、子项重复）",
    ],
  },
  {
    key: "find", name: "可发现性（2026.05.01 推出）", nameEn: "Findability (2026-05-01)",
    desc: "即将作为独立加分通道上线，目前为预览。当前 ASIN 命中 6/7。",
    items: [
      { t: "pass", text: "具有叶节点 +10" },
      { t: "pass", text: "有搜索关键词 +5" },
      { t: "pass", text: "标题含品牌名 +5" },
      { t: "pass", text: "A+ 页面存在 +12.5" },
      { t: "pass", text: "标题完整性、有品牌名称 +5" },
      { t: "pass", text: "有商品要点 +5（遵循 0-1-3）· 1 个核心卖点 +5 · 3 个魅力卖点 +10" },
      { t: "pass", text: "3 条或以上商品要点 +5 · 关键属性全都填写 +2.5" },
    ],
    note: "* 部分 Softline PT 遵循不同的相关属性排序逻辑",
  },
];

// ------------------------------------------------------------------
// 等级规则
// ------------------------------------------------------------------
window.LS_GRADE_RULES = {
  letter: [
    { g: "A++", label: "极高 · 加分", min: 100.01, color: "grade-a", note: "总分 >100（100–120），含可发现性加分。" },
    { g: "A+", label: "高质量", min: 92, color: "grade-a", note: "85–100 区间高段，六维核心规则全部满足。" },
    { g: "A", label: "尚可", min: 85, color: "grade-a", note: ">85，仍有优化空间。" },
    { g: "B", label: "低质量 · 无缺陷", min: 70, color: "grade-b", note: "70–85，未违反政策但未达最佳。" },
    { g: "C", label: "低质量 · 非严重缺陷", min: 0.01, color: "grade-c", note: "0–69.99，存在可修复缺陷。" },
    { g: "D", label: "低质量 · 严重缺陷", min: 0, color: "grade-d", note: "=0，存在严重缺陷，需立即处理。" },
    { g: "U", label: "政策违规", min: null, color: "grade-u", note: "n/a，索引/网站抑制或标题政策违规。" },
  ],
};

// ------------------------------------------------------------------
// 产品池
// ------------------------------------------------------------------
window.LS_PRODUCTS = {
  "B09GTRVJQM": {
    asin: "B09GTRVJQM", brand: "Amazon Basics",
    title: "Amazon Basics 60W USB-C to USB-C Fast Charger Cable, USB 2.0, 6 Foot, Black",
    titleLen: 82,
    category: "Electronics › Cables & Accessories › USB Cables",
    price: "$7.99", reviews: 18244, stars: 4.6, marketplace: "US", updated: "2026-04-16",
    scores: { title: 76, attr: 88, vari: 72, img: 82, bul: 90, aplus: 100, ptc: 90 },
    sub: {
      title: { complete: 66, redundant: 72, length: 95, casing: 95, pipe: 0, charset: 100, restricted: 100, brandLead: 80, tier: "B", tqs: 78 },
      attr: {
        rai_title: 86, rai_brand: 100, rai_cat: 100, rai_bul: 82, rai_pt: 92, rai_main: 95,
        a_size: 90, a_weight: 95, a_model: 80,
        b_feat: 72, b_aud: 58, b_use: 62,
        iai: 0.48, top4: true,
      },
      vari: { theme_ok: 80, attr_ok: 70, no_dup: 55, family: 100, rich: 66,
        hitStrict: ["变体信息冗余（父子描述字段重复 ≥60%）"], hitSoft: ["未标准化的属性值（如 '6ft' vs '6 Foot'）"] },
      img: { count: 100, iai: 80, pixel85: 88, alt_attr: 60, zoom: 100 },
      bul: { count3: 100, count5: 100, key_attr: 70, rule013: 80 },
      aplus: { exist: 100 },
      ptc: { leaf: 100, kw: 80, funnel: 66 },
    },
    checks: {
      title: [
        { type: "pass", text: "长度 82 字符，二段式总长处于推荐区间 75–200" },
        { type: "pass", text: "Title Case 规范，特殊字符检测通过，无促销词/敏感词" },
        { type: "pass", text: "以品牌 'Amazon Basics' 开头" },
        { type: "fail", text: "管套评分 = 0：无管道符/分隔符，无法达 A 级" },
        { type: "warn", text: "完整性评分 0.66（建议补适用人群/场景描述）" },
        { type: "warn", text: "未覆盖高转化词：PD 3.0 / Type-C / iPhone 15" },
        { type: "fail", text: "末尾颜色冗余（变体层已有颜色维度）" },
      ],
      attr: [
        { type: "pass", text: "RAI 前 6 项已全部结构化（品牌/分类/PT/主图/标题/Bullet）" },
        { type: "pass", text: "分类落在 USB Cables 叶节点（+10）" },
        { type: "pass", text: "IAI = 0.48（≥0.4 达标，+10）" },
        { type: "warn", text: "Compatible Devices 仅填 1 个泛化值，建议补 6 个" },
        { type: "warn", text: "Target Audience / Usage Scenario 覆盖率仅 60%" },
        { type: "fail", text: "Data Transfer Rate 未填（应为 480 Mbps）" },
      ],
      vari: [
        { type: "pass", text: "变体家族 Color × Length 共 6 个子 SKU" },
        { type: "warn", text: "3 Foot 子变体标题缺少 'Fast Charger' 关键词" },
        { type: "fail", text: "严重缺陷：变体信息冗余（父子描述字段重复度 68%）" },
        { type: "warn", text: "非严重缺陷：属性值未标准化（1 处 '6ft' vs '6 Foot'）" },
      ],
      img: [
        { type: "pass", text: "共 7 张图 ≥4 且无图片缺陷 → 矩阵得分 1.0 (100%)" },
        { type: "pass", text: "主图白底合规，分辨率 2400px 支持缩放" },
        { type: "pass", text: "有效像素占比 88%（≥ 85% 达标，S3 图库标准）" },
        { type: "warn", text: "图片 alt 属性仅标注 60%，影响关键词收录" },
        { type: "warn", text: "缺少 2 张应用场景实拍（办公/出行）" },
      ],
      bul: [
        { type: "pass", text: "共 5 条 Bullet，满足 ≥3 条 → 100%" },
        { type: "pass", text: "检测到 1 条主打卖点（+5），无违禁关键词" },
        { type: "warn", text: "魅力卖点仅 2 条（0-1-3 原则要求 ≥3）" },
        { type: "warn", text: "关键属性在 Bullet 中覆盖 70%（目标 100%）" },
      ],
      aplus: [
        { type: "pass", text: "A+ 存在 → 二元判定 1.0 (100%)，Basic A+ 模块 × 3" },
        { type: "warn", text: "2026 起将评估 A+ 内容质量；建议提前升级 Premium A+" },
      ],
      ptc: [
        { type: "pass", text: "叶节点 Node ID 正确：USB-C to USB-C Cables（+10）" },
        { type: "pass", text: "Search Terms 已填写，含类目词与节点词（+5）" },
        { type: "warn", text: "NPL 漏斗仅监控 Traffic + 转化，加购率 (ATC/GV) 未接入" },
      ],
    },
    suggestions: {
      title: "去掉末尾冗余颜色，改用二段式结构：'Amazon Basics USB-C Cable | 60W PD Fast Charging | 6 Foot' — 补管道符使管套评分 >0，同时前置关键词，可触发 A 级。",
      attr: "补全 Compatible Devices（iPhone 15 / iPad Pro / MacBook Air / Galaxy S24 / Pixel 8 / Switch）+ Data Transfer Rate(480 Mbps) + Target Audience，可解锁 IAI ≥0.6。",
      vari: "同步父子模板，统一单位制（全部写 '6 Foot'），重写 2-Pack 的 Bullet 继承，解决变体信息冗余。",
      img: "补 2 张场景实拍并为全部图片补齐 alt 属性标注；保持无图片缺陷即可维持矩阵 100%。",
      bul: "按 0-1-3 原则重组 Bullet：第 1 条主卖点（PD 3.0 60W 快充），2–4 条分别放 1 个魅力点（编织 / 长度 / 适配），第 5 条合规声明。",
      aplus: "A+ 已存在得满分；2026 内容质量评估上线前建议升级 Premium A+（需 Brand Registry）。",
      ptc: "接入加购率监控，补齐 NPL 三漏斗；可发现性加分可从 +18 提升至满幅 +20。",
    },
  },
  "B0CHX2F5QN": { asin: "B0CHX2F5QN", brand: "Anker",
    title: "Anker USB C to USB C Cable (240W, 6ft), Bio-Nylon Cable for iPhone 15 / MacBook Pro",
    titleLen: 93, category: "Electronics › Cables & Accessories › USB Cables",
    price: "$12.99", reviews: 34120, stars: 4.7, marketplace: "US", updated: "2026-04-15",
    scores: { title: 94, attr: 96, vari: 90, img: 92, bul: 100, aplus: 100, ptc: 100 },
    sub: { title: { tqs: 100, tier: "A" }, attr: { iai: 0.72, top4: true } } },
  "B08L5WRWNW": { asin: "B08L5WRWNW", brand: "UGREEN",
    title: "UGREEN USB C Cable 100W, Type C Fast Charging Nylon Braided Cord",
    titleLen: 68, category: "Electronics › Cables & Accessories › USB Cables",
    price: "$9.99", reviews: 12088, stars: 4.6, marketplace: "US", updated: "2026-04-12",
    scores: { title: 70, attr: 82, vari: 65, img: 78, bul: 80, aplus: 0, ptc: 60 },
    sub: { title: { tqs: 62, tier: "B" }, attr: { iai: 0.38, top4: false } } },
  "B0CR6V4T8H": { asin: "B0CR6V4T8H", brand: "Syncwire",
    title: "Syncwire USB Type-C Cable 6ft (Black)",
    titleLen: 39, category: "Electronics › Cables & Accessories › USB Cables",
    price: "$5.49", reviews: 1822, stars: 4.3, marketplace: "US", updated: "2026-04-09",
    scores: { title: 42, attr: 48, vari: 0, img: 55, bul: 60, aplus: 0, ptc: 0 },
    sub: { title: { tqs: 35, tier: "C" }, attr: { iai: 0.22, top4: false } } },
  "B0B2D77YB8": { asin: "B0B2D77YB8", brand: "JSAUX",
    title: "JSAUX USB C to USB C Cable 100W 6.6ft, PD 3.0 Fast Charging",
    titleLen: 58, category: "Electronics › Cables & Accessories › USB Cables",
    price: "$8.99", reviews: 8440, stars: 4.5, marketplace: "US", updated: "2026-04-10",
    scores: { title: 80, attr: 76, vari: 70, img: 72, bul: 90, aplus: 100, ptc: 80 },
    sub: { title: { tqs: 82, tier: "B" }, attr: { iai: 0.44, top4: true } } },
};

window.LS_PORTFOLIO = ["B09GTRVJQM", "B0B2D77YB8", "B08L5WRWNW", "B0CR6V4T8H"];

window.LS_TREND = [
  { d: "03-01", s: 72 }, { d: "03-08", s: 74 }, { d: "03-15", s: 73 },
  { d: "03-22", s: 78 }, { d: "03-29", s: 79 }, { d: "04-05", s: 81 },
  { d: "04-12", s: 83 }, { d: "04-16", s: 84 },
];

window.LS_ACTIVITY = [
  { t: "2026-04-16 14:32", a: "Maya Chen",  msg: "为 <b>B09GTRVJQM</b> 运行了 CDQv3 诊断，总分 <b>84</b>（+2）" },
  { t: "2026-04-16 11:08", a: "Ryan Wu",    msg: "在 <b>标题质量</b> 添加了批注：已排期下周更新文案" },
  { t: "2026-04-15 20:15", a: "Maya Chen",  msg: "对比了 <b>B09GTRVJQM</b> 与 <b>Anker B0CHX2F5QN</b>" },
  { t: "2026-04-14 09:44", a: "系统",        msg: "周度批量诊断完成，覆盖 <b>4 个 ASIN</b>" },
  { t: "2026-04-13 17:30", a: "Ling Zhao",  msg: "将 <b>B0B2D77YB8</b> 的诊断报告分享给供应链团队" },
];

window.LS_KB = [
  { cat: "评分规则", title: "CDQv3 六大组件权重与计算细则", excerpt: "标题 25 / 属性 30 / 变体 20 / 图片 15 / Bullet 5 / A+ 5；含 TQS、IAI、0-1-3 全公式拆解。" },
  { cat: "标题优化", title: "TQS 评级：A/B/C 的精确触发条件", excerpt: "完整性 ≥0.6、冗余度 =1、长度 ≤200、大小写 >0、特殊字符 =1、受限短语 =1 — 六项同时满足即 A 级。" },
  { cat: "结构化属性", title: "RAI Top 6 与 Band A/B 的权重地图", excerpt: "品牌/叶节点/PT/主图为硬性通道；Band A 驱动退货率，Band B 决定筛选栏可见性。" },
  { cat: "变体策略", title: "变体严重缺陷：5 类立即停摆情况", excerpt: "错误属性值、单位制混用、变体信息冗余、本地化错误、子项完全重复。" },
  { cat: "合规与安全", title: "2026 年受限关键词 · 中英映射", excerpt: "FDA / CPSC / EPA 更新清单，与 TQS 'restricted_score < 1' 的触发机制。" },
  { cat: "即将推出", title: "可发现性加分通道（2026-05-01 上线）", excerpt: "叶节点 +10、搜索关键词 +5、A+ 页面 +12.5、Bullet 0-1-3 原则 +15 — 四大通道详解。" },
];

window.LS_TEAM = [
  { name: "Maya Chen",  role: "运营负责人", init: "MC", color: "#c06138" },
  { name: "Ryan Wu",    role: "文案",       init: "RW", color: "#2f5d5a" },
  { name: "Ling Zhao",  role: "供应链",     init: "LZ", color: "#b08339" },
  { name: "Oscar King", role: "美工",       init: "OK", color: "#2f4f87" },
];

window.LS_COMMENTS = {
  title: [
    { who: "Maya Chen", init: "MC", color: "#c06138", when: "2 小时前",
      text: "末尾颜色冗余这点同意，我下周一会走一版去掉颜色、前置 PD 3.0 的标题。@Ryan Wu 请帮忙出 3 个备选。" },
    { who: "Ryan Wu",   init: "RW", color: "#2f5d5a", when: "1 小时前",
      text: "收到，晚上给到三版，都会控制在 180 字符内，保留 iPhone 15 / MacBook 的高转化词。" },
  ],
  vari: [
    { who: "Ling Zhao", init: "LZ", color: "#b08339", when: "昨天",
      text: "2-Pack 的 Bullet 下周供应链盘点时一起核对，先把单位制 '6ft / 6 Foot' 的问题解掉。" },
  ],
};
