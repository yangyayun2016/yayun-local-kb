// CDQ 评估维度定义
window.CDQ_DIMENSIONS = [
  {
    key: 'structured',
    name: '结构化属性',
    nameEn: 'Structured Attributes',
    weight: 30,
    group: '详情页',
    desc: '产品概述前6项RAI属性 + 深度信息Band A/B 完整且正确',
  },
  {
    key: 'title',
    name: '标题质量',
    nameEn: 'Title Quality',
    weight: 25,
    group: '详情页',
    desc: 'TQS评分 · 完整性/长度/大小写/关键词/冗余/限制内容',
  },
  {
    key: 'bullets',
    name: '五点描述',
    nameEn: 'Bullet Points',
    weight: 5,
    group: '详情页',
    desc: '≥3条 · 0-1-3原则 · 无违禁/敏感词',
  },
  {
    key: 'images',
    name: '图片质量',
    nameEn: 'Image Quality',
    weight: 15,
    group: '详情页',
    desc: '≥4张 · IAI≥0.4 · 主图缩放 · 无质量缺陷',
  },
  {
    key: 'aplus',
    name: 'A+ 内容',
    nameEn: 'A+ Content',
    weight: 5,
    group: '详情页',
    desc: '存在 A+ 详情页内容（推荐高级 A+）',
  },
  {
    key: 'variation',
    name: '变体质量',
    nameEn: 'Variation Quality',
    weight: 20,
    group: '详情页',
    desc: '变体主题一致 · 属性正确 · 无重复 · 数量≥2 · Orphan ASIN 不适用 (N/A 权重重新分配)',
  },
  {
    key: 'classification',
    name: '产品分类',
    nameEn: 'Product Type Classification',
    weight: 20,
    group: '可搜索性',
    desc: '权重 0–20% 浮动 · 叶节点 Node ID 准确 · PT 精确 · 包含关键词（部分市场未上线，如 IE）',
  },
];

// 等级
window.CDQ_GRADES = [
  { grade: 'A++', min: 100, max: 120, label: '极高质量', tone: 'emerald' },
  { grade: 'A+',  min: 85,  max: 100, label: '高质量',   tone: 'teal'    },
  { grade: 'A',   min: 85,  max: 85,  label: '尚可',     tone: 'sky'     },
  { grade: 'B',   min: 70,  max: 85,  label: '低质量·无缺陷',   tone: 'amber'   },
  { grade: 'C',   min: 0,   max: 69.99,  label: '低质量·非严重',   tone: 'orange'  },
  { grade: 'D',   min: 0,   max: 0,   label: '低质量·严重缺陷', tone: 'rose'    },
  { grade: 'U',   min: 0,   max: 0,   label: '政策违规',        tone: 'zinc'    },
];

window.scoreToGrade = function(total) {
  if (total > 100) return 'A++';
  if (total >= 85) return 'A+';
  if (total > 70)  return 'B';
  if (total > 0)   return 'C';
  return 'D';
};

// Mock ASIN 数据集
window.ASINS = [
  {
    asin: 'B09GTRVJQM', sku: 'STQ-OXF-2401',
    title: 'STQSHOES Men\'s Classic Leather Oxford Dress Shoes | Genuine Cowhide | Cushioned Insole | Wide Width Available | Size 7-13',
    pt: 'SHOES', cat: 'Men\'s Oxfords / Dress Shoes',
    market: 'US', brand: 'STQSHOES',
    image: '#e8d8c4',
    pv30: 24819, sales30: '$18,420',
    scores: { structured: 26, title: 22, bullets: 5, images: 14, aplus: 5, variation: 18, classification: 20 },
    titleTQS: 'A',
    flags: { quarantined: false, indexed: true, websiteActive: true, leafNode: true, keywords: true, image: true, brand: true, titleStartsBrand: true, titleLengthCorrect: true, bulletPoint: true, description: true, mainImageZoom: true, racTop4: true, racTop10: false },
    defects: [
      { type: 'minor', cat: 'RAC', detail: 'Relevant attributes ranked [5..10] are incomplete', action: 'Fill in missing relevant attributes ranked [5..10]: maximum_current, item_weight', status: 'pending' },
    ],
    bullets: [
      { text: 'PREMIUM GENUINE LEATHER — handcrafted full-grain cowhide upper with breathable lining for all-day comfort', flag: 'core' },
      { text: 'CLASSIC OXFORD SILHOUETTE — versatile lace-up dress shoe pairs with suits, business casual & formalwear', flag: 'charm' },
      { text: 'CUSHIONED MEMORY-FOAM INSOLE — anatomical arch support reduces foot fatigue on long workdays', flag: 'charm' },
      { text: 'DURABLE NON-SLIP OUTSOLE — flexible rubber tread with stitched welt construction for long wear', flag: 'charm' },
      { text: 'WIDE WIDTH OPTIONS · TRUE-TO-SIZE FIT — refer to size chart, half sizes available 7–13 (D & 2E)', flag: 'charm' },
    ],
    attributes: {
      'Brand Name': { val: 'STQSHOES', ok: true, band: 'RAI' },
      'Product Type': { val: 'SHOES', ok: true, band: 'RAI' },
      'Category Node': { val: 'Men › Shoes › Oxfords (Node 679288011)', ok: true, band: 'RAI' },
      'Title': { val: '已填写', ok: true, band: 'RAI' },
      'Bullet Points': { val: '5 条', ok: true, band: 'RAI' },
      'Main Image': { val: '纯白底 · 1500×1500', ok: true, band: 'RAI' },
      'Outer Material': { val: 'Leather', ok: true, band: 'A' },
      'Sole Material': { val: 'Rubber', ok: true, band: 'A' },
      'Closure Type': { val: 'Lace-Up', ok: true, band: 'A' },
      'Item Weight': { val: '—', ok: false, band: 'A' },
      'Heel Type': { val: 'Block', ok: true, band: 'A' },
      'Shoe Width': { val: 'Medium', ok: true, band: 'A' },
      'Special Feature': { val: 'Cushioned', ok: true, band: 'B' },
      'Target Audience': { val: 'Men', ok: true, band: 'B' },
      'Occasion': { val: '—', ok: false, band: 'B' },
      'Style': { val: 'Classic', ok: true, band: 'B' },
      'maximum_current': { val: '—', ok: false, band: 'B' },
    },
    images: [
      { kind: 'main', ok: true, note: '主图 · 纯白底 · 缩放✓' },
      { kind: 'lifestyle', ok: true, note: '侧面 · 商务场景' },
      { kind: 'detail', ok: true, note: '材质特写' },
      { kind: 'detail', ok: true, note: '鞋底纹路' },
      { kind: 'sizing', ok: true, note: '尺码图' },
      { kind: 'lifestyle', ok: true, note: '上脚效果' },
    ],
    aplus: { has: true, advanced: true, modules: 7, hasComparison: true },
    variation: { count: 14, themes: ['Color', 'Size'], consistent: true, duplicates: 0 },
    titleAnalysis: {
      length: 144, integrity: 0.65, redundancy: 1.0, pipeScore: 0.9,
      special: 1.0, restricted: 1.0, brandStart: true, attrCount: 4,
      issues: [],
    },
  },
  {
    asin: 'B0C4HX7TY9', sku: 'STQ-LOAFER-118',
    title: 'Mens Penny Loafers Slip On Casual Dress Shoes Comfortable Walking Loafer Best Seller for Office & Wedding!',
    pt: 'SHOES', cat: 'Men\'s Loafers',
    market: 'US', brand: 'STQSHOES',
    image: '#3a2a20',
    pv30: 12305, sales30: '$6,210',
    scores: { structured: 18, title: 0, bullets: 5, images: 10, aplus: 0, variation: 14, classification: 18 },
    titleTQS: 'C',
    flags: { quarantined: false, indexed: true, websiteActive: true, leafNode: true, keywords: true, image: true, brand: true, titleStartsBrand: false, titleLengthCorrect: true, bulletPoint: true, description: false, mainImageZoom: false, racTop4: false, racTop10: false },
    defects: [
      { type: 'severe', cat: 'Title', detail: '标题政策违规：包含促销语 "Best Seller"、特殊字符 "!"', action: '移除促销语与特殊字符，以品牌名开头', status: 'pending' },
      { type: 'minor', cat: 'A+', detail: 'Missing A+', action: 'Add A+', status: 'reference' },
      { type: 'minor', cat: 'Image', detail: '主图未启用缩放', action: '主图分辨率提升至 1600px+ 启用 zoom', status: 'pending' },
    ],
    titleAnalysis: { length: 102, integrity: 0.4, redundancy: 0.8, pipeScore: 0, special: 0, restricted: 0.6, brandStart: false, attrCount: 2, issues: ['含促销词 Best Seller', '含特殊字符 !', '未以品牌名开头', '缺少分隔符 |'] },
  },
  {
    asin: 'B0DFNQM4ZK', sku: 'STQ-SNK-507',
    title: 'STQSHOES Men Running Shoes | Lightweight Mesh Sneakers | Memory Foam | Athletic Walking Tennis Casual',
    pt: 'SHOES', cat: 'Men\'s Athletic / Running',
    market: 'US', brand: 'STQSHOES',
    image: '#1f2a44',
    pv30: 38120, sales30: '$24,860',
    scores: { structured: 28, title: 24, bullets: 5, images: 15, aplus: 5, variation: 19, classification: 20 },
    titleTQS: 'A',
    flags: { quarantined: false, indexed: true, websiteActive: true, leafNode: true, keywords: true, image: true, brand: true, titleStartsBrand: true, titleLengthCorrect: true, bulletPoint: true, description: true, mainImageZoom: true, racTop4: true, racTop10: true },
    defects: [],
    titleAnalysis: { length: 118, integrity: 0.7, redundancy: 1, pipeScore: 1, special: 1, restricted: 1, brandStart: true, attrCount: 5, issues: [] },
  },
  {
    asin: 'B0BX2GCWPL', sku: 'STQ-BOOT-302',
    title: 'STQSHOES Womens Chelsea Boots Antimicrobial Lining Ankle Boot Block Heel Booties',
    pt: 'BOOTS', cat: 'Women\'s Chelsea Boots',
    market: 'US', brand: 'STQSHOES',
    image: '#5a3a2a',
    pv30: 9812, sales30: '$4,920',
    scores: { structured: 22, title: 0, bullets: 3, images: 12, aplus: 0, variation: 16, classification: 18 },
    titleTQS: 'C',
    flags: { quarantined: false, indexed: false, websiteActive: true, leafNode: true, keywords: true, image: true, brand: true, titleStartsBrand: true, titleLengthCorrect: true, bulletPoint: true, description: false, mainImageZoom: false, racTop4: true, racTop10: false },
    defects: [
      { type: 'severe', cat: 'Restricted', detail: '标题包含敏感词 "Antimicrobial"（健康/医疗类违禁）', action: '移除敏感词并替换为合规描述', status: 'pending' },
      { type: 'minor', cat: 'Index', detail: 'Is Not Search Indexed', action: '修复违禁词后等待重新收录', status: 'pending' },
      { type: 'minor', cat: 'A+', detail: 'Missing A+', action: 'Add A+', status: 'pending' },
    ],
    titleAnalysis: { length: 89, integrity: 0.5, redundancy: 1, pipeScore: 0, special: 1, restricted: 0, brandStart: true, attrCount: 3, issues: ['含敏感词 Antimicrobial', '缺少分隔符 |'] },
  },
  {
    asin: 'B0D8K9TXP1', sku: 'STQ-SAND-89',
    title: 'STQSHOES Women\'s Slide Sandals | Memory Foam Footbed | Adjustable Strap | Beach Pool Summer',
    pt: 'SANDALS', cat: 'Women\'s Slides',
    market: 'US', brand: 'STQSHOES',
    image: '#c89b6a',
    pv30: 15620, sales30: '$8,310',
    scores: { structured: 24, title: 22, bullets: 5, images: 13, aplus: 5, variation: 17, classification: 18 },
    titleTQS: 'A',
    flags: { quarantined: false, indexed: true, websiteActive: true, leafNode: true, keywords: true, image: true, brand: true, titleStartsBrand: true, titleLengthCorrect: true, bulletPoint: true, description: true, mainImageZoom: true, racTop4: true, racTop10: false },
    defects: [
      { type: 'minor', cat: 'RAC', detail: 'Top 10 RAI 完整性 < 80%', action: '补全 footbed_material, strap_type', status: 'benchmark' },
    ],
    titleAnalysis: { length: 96, integrity: 0.62, redundancy: 1, pipeScore: 1, special: 1, restricted: 1, brandStart: true, attrCount: 4, issues: [] },
  },
  {
    asin: 'B0CMR5LX8K', sku: 'STQ-HEEL-44',
    title: 'STQSHOES Pump Heel Shoes Pump Heel Shoes Ladies Pump Heel Pumps Office',
    pt: 'PUMPS', cat: 'Women\'s Pumps',
    market: 'US', brand: 'STQSHOES',
    image: '#7a1a3a',
    pv30: 4210, sales30: '$1,820',
    scores: { structured: 14, title: 0, bullets: 2, images: 8, aplus: 0, variation: 10, classification: 16 },
    titleTQS: 'C',
    flags: { quarantined: false, indexed: true, websiteActive: true, leafNode: true, keywords: false, image: true, brand: true, titleStartsBrand: true, titleLengthCorrect: true, bulletPoint: true, description: false, mainImageZoom: false, racTop4: false, racTop10: false },
    defects: [
      { type: 'severe', cat: 'Title', detail: '关键词堆砌：Pump Heel 出现 4 次（同语境>2次）', action: '重写标题，去除重复词', status: 'pending' },
      { type: 'minor', cat: 'Bullet', detail: '五点描述仅 2 条', action: '补充至 ≥3 条，遵循 0-1-3 原则', status: 'pending' },
      { type: 'minor', cat: 'A+', detail: 'Missing A+', action: 'Add A+', status: 'pending' },
    ],
    titleAnalysis: { length: 73, integrity: 0.35, redundancy: 0.4, pipeScore: 0, special: 1, restricted: 1, brandStart: true, attrCount: 2, issues: ['Pump Heel 重复 4 次', '长度不足 80 字符', '缺少分隔符'] },
  },
  {
    asin: 'B0EXM2NKLR', sku: 'STQ-KIDS-66',
    title: 'STQSHOES Kids Sneaker Boys Girls Lightweight Breathable School Sport Shoe | Hook & Loop | Toddler-Big Kid',
    pt: 'SHOES', cat: 'Kids\' Athletic',
    market: 'US', brand: 'STQSHOES',
    image: '#3c8fb8',
    pv30: 18205, sales30: '$11,640',
    scores: { structured: 27, title: 23, bullets: 5, images: 14, aplus: 5, variation: 18, classification: 20 },
    titleTQS: 'A',
    flags: { quarantined: false, indexed: true, websiteActive: true, leafNode: true, keywords: true, image: true, brand: true, titleStartsBrand: true, titleLengthCorrect: true, bulletPoint: true, description: true, mainImageZoom: true, racTop4: true, racTop10: true },
    defects: [],
    titleAnalysis: { length: 113, integrity: 0.68, redundancy: 1, pipeScore: 1, special: 1, restricted: 1, brandStart: true, attrCount: 5, issues: [] },
  },
  {
    asin: 'B0F5LJD2MX', sku: 'STQ-SLIP-21',
    title: 'STQSHOES Mens Slip On Walking Shoes',
    pt: 'SHOES', cat: 'Men\'s Slip-On',
    market: 'US', brand: 'STQSHOES',
    image: '#2b2b2b',
    orphan: true,
    pv30: 6021, sales30: '$2,940',
    scores: { structured: 12, title: 12, bullets: 3, images: 6, aplus: 0, variation: null, classification: 14 },
    titleTQS: 'B',
    flags: { quarantined: false, indexed: true, websiteActive: true, leafNode: true, keywords: false, image: true, brand: true, titleStartsBrand: true, titleLengthCorrect: false, bulletPoint: true, description: false, mainImageZoom: false, racTop4: false, racTop10: false },
    defects: [
      { type: 'minor', cat: 'Title', detail: '标题长度仅 35 字符（建议 80–200）', action: '扩充材质/规格/场景关键词', status: 'pending' },
      { type: 'minor', cat: 'RAC', detail: 'Top 4 RAI 完整性 < 50%', action: '补全 outer_material, sole_material, closure_type', status: 'pending' },
      { type: 'minor', cat: 'Image', detail: '仅 3 张图片（要求≥4）', action: '补充使用场景与细节图', status: 'pending' },
      { type: 'minor', cat: 'A+', detail: 'Missing A+', action: 'Add A+', status: 'pending' },
    ],
    titleAnalysis: { length: 35, integrity: 0.3, redundancy: 1, pipeScore: 0, special: 1, restricted: 1, brandStart: true, attrCount: 2, issues: ['长度过短', '缺少分隔符'] },
  },
];

// 算各 ASIN total（Orphan ASIN：变体质量 N/A，权重重新分配 → 按有效权重折算到 120 分制）
window.ASINS.forEach(a => {
  const raw = Object.values(a.scores).reduce((s, n) => s + (n || 0), 0);
  if (a.orphan) {
    const effWeight = window.CDQ_DIMENSIONS.filter(d => a.scores[d.key] != null).reduce((s, d) => s + d.weight, 0);
    a.total = Math.round(raw / effWeight * 120);
  } else {
    a.total = raw;
  }
  a.grade = window.scoreToGrade(a.total);
});

// 词频/词根统计示例
window.KEYWORD_FREQ = [
  { word: 'leather', freq: 6, places: ['Title', 'BP1', 'BP2', 'A+', 'Image-Alt', 'Search-Term'], type: '核心', density: 1.8 },
  { word: 'oxford', freq: 5, places: ['Title', 'BP2', 'A+', 'Image-Alt', 'Search-Term'], type: '核心', density: 1.5 },
  { word: 'dress shoes', freq: 4, places: ['Title', 'BP3', 'A+', 'Search-Term'], type: '核心', density: 1.2 },
  { word: 'cushioned', freq: 3, places: ['Title', 'BP3', 'A+'], type: '功能', density: 0.9 },
  { word: 'business', freq: 3, places: ['BP2', 'A+', 'Search-Term'], type: '场景', density: 0.9 },
  { word: 'wide width', freq: 2, places: ['Title', 'BP5'], type: '规格', density: 0.6 },
  { word: 'memory foam', freq: 2, places: ['BP3', 'A+'], type: '功能', density: 0.6 },
  { word: 'wedding', freq: 1, places: ['A+'], type: '场景', density: 0.3 },
];

// 违禁/敏感词字典
window.RESTRICTED_DICT = [
  { word: 'Best Seller', cat: '促销/主观', risk: 'high' },
  { word: 'Top Rated',   cat: '促销/主观', risk: 'high' },
  { word: '#1 Best',     cat: '促销/主观', risk: 'high' },
  { word: 'Free Shipping', cat: '物流/促销', risk: 'high' },
  { word: '100% Quality Guaranteed', cat: '促销', risk: 'high' },
  { word: 'Antimicrobial', cat: '健康/医疗', risk: 'severe' },
  { word: 'Antibacterial', cat: '健康/医疗', risk: 'severe' },
  { word: 'Antifungal',    cat: '健康/医疗', risk: 'severe' },
  { word: 'Pesticides',    cat: '杀虫剂声明', risk: 'severe' },
  { word: 'Insecticide',   cat: '杀虫剂声明', risk: 'severe' },
  { word: 'Drugs',         cat: '药物/管制', risk: 'severe' },
  { word: 'Marijuana',     cat: '药物/管制', risk: 'severe' },
  { word: 'Anti-Mites',    cat: '健康/医疗', risk: 'severe' },
  { word: 'Sanitize',      cat: '健康/医疗', risk: 'severe' },
  { word: 'Detoxify',      cat: '健康/医疗', risk: 'severe' },
  { word: 'UV Sterilizes', cat: '健康/医疗', risk: 'severe' },
  { word: 'Cheapest',      cat: '价格/促销', risk: 'high' },
  { word: 'Hot Item',      cat: '主观', risk: 'high' },
  { word: 'Gift',          cat: '建议规避', risk: 'low' },
  { word: 'Warranty',      cat: '建议规避', risk: 'low' },
];
