# Listing Generator Skill

## 用途

自动生成亚马逊产品Listing的各个组件，包括标题、五点描述、A+内容等。

## 支持的内容类型

| 类型 | 字符限制 | 说明 |
|------|---------|------|
| 标题（Title） | 200字符 | 产品核心信息，SEO最重要位置 |
| 五点描述（Bullet Points） | 5条x 500字符 | 产品卖点，转化关键 |
| 产品描述（Description） | 2000字符 | 补充说明，可含HTML |
| A+页面 | 模块化 | 品牌故事+产品详情 |
| 搜索关键词 | 250字节 | 后台隐藏关键词 |
| 后台关键词 | 249字节 | 五组，每组49字节 |

## 生成流程

```
输入产品信息 → 关键词研究 → 文案撰写 → SEO优化 → 合规检查 → 输出
```

## 标题撰写规范

### 黄金法则
```
品牌名 + 核心关键词 + 核心卖点 + 材质/颜色 + 尺寸 + 数量
```

### 字符分配建议
- 前80字符：核心关键词（移动端可见）
- 80-120字符：次要关键词
- 120-200字符：补充信息

### 正确示例
```
JOYOSO Stainless Steel mixing bowls Set of 3 - Non-slip Bottom,
Dishwasher Safe, Measurement Lines, Shatter Resistant for Kitchen
```

### 错误示例
```
Best Amazing Awesome Fantastic 5-Piece Kitchen Bowls Set - Beautiful
Colors and Great Quality You Will Love!!! (Click to Buy Now!)
```

## 五点描述策略

### 痛点→解决方案结构
```
1. 开篇吸引 + 核心卖点
2. 材质/工艺优势
3. 使用场景/便利性
4. 解决的问题
5. 品牌/售后承诺
```

### 关键词布局
- 每点1-2个核心关键词
- 自然融入，非堆砌
- 大小写正确

## A+内容模块

### 推荐模块组合
1. 品牌故事模块
2. 对比图模块
3. 功能特性模块
4. 产品细节模块
5. 使用场景模块

## 关键词研究

### 来源
- 竞品标题
- 亚马逊搜索下拉框
- 广告报告
- 第三方工具（Helium10、Jungle Scout）
- 客户评论

### 筛选标准
- 相关性（与产品相关）
- 搜索量（有足够搜索）
- 竞争度（适中竞争）
- 转化率（有购买意图）

## 违禁词清单

### 严禁使用的词
- 最（Best、#1、Number 1）
- 便宜（Cheap）
- 保证（Guarantee、Promise）
- 绝对（Absolutely）
- 免费（Free）
- 最好（Better than）

### 特殊符号
- ! ? $ % * 不建议使用
- 全部使用大写字母开头

## 使用示例

### 示例1：生成新品Listing
```
用户：帮我生成一个厨房量杯的Listing
助手：
1. 收集产品信息：
   - 产品：不锈钢量杯套装
   - 包含：3个尺寸
   - 特点：防滑底、刻度清晰
   - 用途：烘焙、烹饪

2. 生成标题：
   JOYOSO Stainless Steel Measuring Cups Set of 3 - Stackable Design,
   Laser Etched Measurement Lines, Anti-slip Base, Dishwasher Safe

3. 生成五点：
   ✓ Premium Stainless Steel -...
   ✓ Space-Saving Stackable...
   ✓ Clear Measurement Lines...
   ✓ Stable Anti-slip Base...
   ✓ Dishwasher Safe & Easy to Clean

4. 生成关键词：
   measuring cups, stainless steel measuring cups, cooking measuring cups...
```

### 示例2：优化现有Listing
```
用户：帮我优化这个标题
原标题：KITCHEN BOWLS SET - 5 PIECES MIXING BOWLS STAINLESS STEEL
优化后：
5-Piece Stainless Steel Mixing Bowls Set - Non-slip Base,
Graduated Measurement Lines, Dishwasher Safe for Kitchen & Baking
```

## 批量生成

支持Excel导入产品列表，批量生成多国语言版本：

```python
输入：products.csv（产品信息表）
输出：listings.xlsx（标题、五点、描述）
```

## 最佳实践

1. **移动端优先** - 优化前80字符
2. **关键词自然** - 避免生硬堆砌
3. **突出差异化** - 与竞品形成对比
4. **持续优化** - 根据广告数据调整
5. **合规第一** - 严格遵守亚马逊规则
6. **多版本测试** - A/B测试不同文案
