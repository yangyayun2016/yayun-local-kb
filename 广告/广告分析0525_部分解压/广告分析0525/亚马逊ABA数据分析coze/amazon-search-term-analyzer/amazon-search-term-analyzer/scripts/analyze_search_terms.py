#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
亚马逊搜索词报告分析脚本（完整版）
为每个分析维度生成独立的输出文件
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os
import glob
import warnings
import re
from datetime import datetime
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置绘图风格
sns.set_style('whitegrid')
sns.set_palette('husl')

# 停用词列表
STOP_WORDS = {
    'for', 'with', 'and', 'the', 'of', 'in', 'to', 'a', 'an',
    'on', 'at', 'by', 'from', 'up', 'about', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'between',
    'under', 'again', 'further', 'then', 'once', '&', '-', '/'
}

class AmazonSearchAnalyzer:
    """亚马逊搜索词报告分析器（完整版）"""

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.all_data = []
        self.df = None
        self.output_dir = data_dir
        self.reports_dir = os.path.join(data_dir, 'analysis_reports')
        os.makedirs(self.reports_dir, exist_ok=True)

    def load_all_data(self):
        """加载所有CSV文件"""
        csv_files = sorted(glob.glob(os.path.join(self.data_dir, '*.csv')))

        if not csv_files:
            print(f"❌ 未找到CSV文件: {self.data_dir}")
            return False

        print(f"\n📂 找到 {len(csv_files)} 个CSV文件")

        for file in csv_files:
            print(f"   Loading: {os.path.basename(file)}")
            try:
                df = pd.read_csv(file, skiprows=1, encoding='utf-8-sig')
                self.all_data.append(df)
            except Exception as e:
                print(f"   ⚠️  Error loading {file}: {e}")

        if self.all_data:
            self.df = pd.concat(self.all_data, ignore_index=True)
            print(f"\n✅ 总记录数: {len(self.df)}")
            return True
        return False

    def clean_data(self):
        """数据清洗"""
        print("\n🧹 数据清洗中...")

        self.df['搜索频率排名'] = pd.to_numeric(self.df['搜索频率排名'], errors='coerce')
        self.df['报告日期'] = pd.to_datetime(self.df['报告日期'])
        self.df['月份'] = self.df['报告日期'].dt.to_period('M')

        for i in range(1, 4):
            click_col = f'点击量最高的商品 #{i}：点击份额'
            conv_col = f'点击量最高的商品 #{i}：转化份额'
            self.df[click_col] = pd.to_numeric(self.df[click_col], errors='coerce')
            self.df[conv_col] = pd.to_numeric(self.df[conv_col], errors='coerce')

        print(f"   数据维度: {self.df.shape}")
        print(f"   时间范围: {self.df['报告日期'].min()} 至 {self.df['报告日期'].max()}")
        print(f"   独特搜索词: {self.df['搜索词'].nunique()}")

    def analyze_brands(self):
        """品牌竞争分析"""
        print("\n📊 1/8 品牌竞争分析...")

        brand_counts = Counter()
        brand_positions = {1: Counter(), 2: Counter(), 3: Counter()}

        for i in range(1, 4):
            col = f'点击量最高的品牌 #{i}'
            brands = self.df[col].dropna()
            brand_counts.update(brands)
            brand_positions[i].update(brands)

        # 创建品牌排位分布数据
        brand_data = []
        for brand, total in brand_counts.most_common(30):
            brand_data.append({
                '排名': len(brand_data) + 1,
                '品牌': brand,
                '#1位次数': brand_positions[1][brand],
                '#2位次数': brand_positions[2][brand],
                '#3位次数': brand_positions[3][brand],
                '总出现次数': total,
                '市场占有率': f"{total / sum(brand_counts.values()) * 100:.2f}%"
            })

        brand_df = pd.DataFrame(brand_data)

        # 保存CSV
        csv_path = os.path.join(self.reports_dir, '01_品牌竞争分析.csv')
        brand_df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        # 生成Markdown报告
        self._generate_brand_report(brand_df)

        print(f"   ✓ 识别到 {len(brand_counts)} 个品牌")
        print(f"   ✓ 输出文件: 01_品牌竞争分析.csv + .md")

        return brand_df

    def _generate_brand_report(self, brand_df):
        """生成品牌分析Markdown报告"""
        md_path = os.path.join(self.reports_dir, '01_品牌竞争分析.md')

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# 品牌竞争分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # 执行摘要
            f.write("## 📊 执行摘要\n\n")
            top3_brands = brand_df.head(3)
            f.write(f"- **市场领导者**: {top3_brands.iloc[0]['品牌']}（出现{top3_brands.iloc[0]['总出现次数']}次）\n")
            f.write(f"- **TOP 3品牌**: {', '.join(top3_brands['品牌'].tolist())}\n")
            f.write(f"- **TOP 3市场占有率**: {sum([float(x.strip('%')) for x in top3_brands['市场占有率']]):.2f}%\n")
            f.write(f"- **总品牌数**: {len(brand_df)}\n\n")

            # TOP 10品牌表格
            f.write("## 🏆 TOP 10 品牌排名\n\n")
            f.write("| 排名 | 品牌 | #1位 | #2位 | #3位 | 总次数 | 市场占有率 |\n")
            f.write("|------|------|------|------|------|--------|------------|\n")
            for _, row in brand_df.head(10).iterrows():
                f.write(f"| {row['排名']} | {row['品牌']} | {row['#1位次数']} | {row['#2位次数']} | {row['#3位次数']} | {row['总出现次数']} | {row['市场占有率']} |\n")

            # 品牌分类
            f.write("\n## 📈 品牌分类\n\n")
            f.write("### 头部品牌（TOP 5）\n")
            f.write("市场主导者，占据绝对优势，新品难以直接竞争。\n\n")
            for _, row in brand_df.head(5).iterrows():
                f.write(f"- **{row['品牌']}**: {row['总出现次数']}次出现，占据{row['市场占有率']}市场份额\n")

            f.write("\n### 腰部品牌（6-15名）\n")
            f.write("有一定市场影响力，有成长空间。\n\n")
            for _, row in brand_df.iloc[5:15].iterrows():
                f.write(f"- **{row['品牌']}**: {row['总出现次数']}次\n")

            # 实操建议
            f.write("\n## 💡 实操建议\n\n")
            f.write("### 针对新入局卖家\n")
            f.write(f"- ❌ 避开TOP 3品牌（{', '.join(top3_brands['品牌'].tolist())}）的正面竞争\n")
            f.write("- ✅ 考虑差异化定位或细分市场\n")
            f.write("- ✅ 可以关注腰部品牌的策略，学习他们如何在头部品牌夹缝中生存\n\n")

            f.write("### 针对现有卖家\n")
            f.write("- 如果你的品牌在TOP 10，重点防御，维护市场地位\n")
            f.write("- 如果你的品牌在10名之外，考虑品牌升级或重新定位\n\n")

            f.write("### 广告投放策略\n")
            f.write(f"- 对头部品牌词（如'{top3_brands.iloc[0]['品牌']}'）进行防御性投放\n")
            f.write("- 避免直接竞价头部品牌词（ROI低）\n")
            f.write("- 关注腰部品牌词，可能有更好的转化\n\n")

            f.write("---\n\n")
            f.write("**数据说明**: 基于搜索词报告中TOP 3品牌位置统计\n")

    def analyze_categories(self):
        """类别趋势分析"""
        print("\n📊 2/8 类别趋势分析...")

        category_counts = Counter()
        category_positions = {1: Counter(), 2: Counter(), 3: Counter()}

        for i in range(1, 4):
            col = f'点击量最高的类别 #{i}'
            categories = self.df[col].dropna()
            category_counts.update(categories)
            category_positions[i].update(categories)

        # 创建类别数据
        category_data = []
        for category, total in category_counts.most_common(20):
            category_data.append({
                '排名': len(category_data) + 1,
                '类别': category,
                '#1位次数': category_positions[1][category],
                '#2位次数': category_positions[2][category],
                '#3位次数': category_positions[3][category],
                '总出现次数': total,
                '占比': f"{total / sum(category_counts.values()) * 100:.2f}%"
            })

        category_df = pd.DataFrame(category_data)

        # 保存CSV
        csv_path = os.path.join(self.reports_dir, '02_类别趋势分析.csv')
        category_df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        # 生成Markdown报告
        self._generate_category_report(category_df)

        print(f"   ✓ 识别到 {len(category_counts)} 个类别")
        print(f"   ✓ 输出文件: 02_类别趋势分析.csv + .md")

        return category_df

    def _generate_category_report(self, category_df):
        """生成类别分析Markdown报告"""
        md_path = os.path.join(self.reports_dir, '02_类别趋势分析.md')

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# 类别趋势分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # 执行摘要
            f.write("## 📊 执行摘要\n\n")
            top_category = category_df.iloc[0]
            f.write(f"- **主导类别**: {top_category['类别']}（占比{top_category['占比']}）\n")
            f.write(f"- **TOP 3类别**: {', '.join(category_df.head(3)['类别'].tolist())}\n")
            f.write(f"- **类别集中度**: TOP 3占比{sum([float(x.strip('%')) for x in category_df.head(3)['占比']]):.2f}%\n")
            f.write(f"- **总类别数**: {len(category_df)}\n\n")

            # 类别排名表格
            f.write("## 🏆 TOP 10 类别排名\n\n")
            f.write("| 排名 | 类别 | #1位 | #2位 | #3位 | 总次数 | 占比 |\n")
            f.write("|------|------|------|------|------|--------|------|\n")
            for _, row in category_df.head(10).iterrows():
                f.write(f"| {row['排名']} | {row['类别']} | {row['#1位次数']} | {row['#2位次数']} | {row['#3位次数']} | {row['总出现次数']} | {row['占比']} |\n")

            # 类别洞察
            f.write("\n## 🔍 类别洞察\n\n")
            if len(category_df) >= 3:
                f.write("### 主导类别\n")
                for _, row in category_df.head(3).iterrows():
                    f.write(f"- **{row['类别']}**: 用户主要搜索意图集中在此类别\n")

            if len(category_df) > 3:
                f.write("\n### 次要类别\n")
                f.write("用户也会在这些类别下搜索，存在跨类别销售机会：\n\n")
                for _, row in category_df.iloc[3:8].iterrows():
                    f.write(f"- {row['类别']} ({row['占比']})\n")

            # 实操建议
            f.write("\n## 💡 实操建议\n\n")
            f.write("### 产品分类优化\n")
            f.write(f"- 确保你的产品主分类选择在 **{category_df.iloc[0]['类别']}**\n")
            f.write("- 考虑添加次要类别，增加曝光渠道\n\n")

            f.write("### Listing文案优化\n")
            f.write("- 在产品描述中融入多个类别的关键词\n")
            f.write(f"- 例如：同时强调产品在 {', '.join(category_df.head(3)['类别'].tolist())} 的应用场景\n\n")

            f.write("### A+内容设计\n")
            f.write("- 针对不同类别用户设计差异化模块\n")
            for _, row in category_df.head(3).iterrows():
                f.write(f"  - **{row['类别']}用户**: 强调相关卖点\n")

            f.write("\n---\n\n")
            f.write("**数据说明**: 基于搜索词报告中TOP 3类别位置统计\n")

    def analyze_search_trends(self):
        """搜索词热度分析"""
        print("\n📊 3/8 搜索词热度分析...")

        # 计算搜索词统计
        search_stats = self.df.groupby('搜索词').agg({
            '搜索频率排名': ['mean', 'std', 'min', 'max', 'count']
        }).round(0)

        search_stats.columns = ['平均排名', '排名标准差', '最佳排名', '最差排名', '出现月数']
        search_stats = search_stats.reset_index().sort_values('平均排名')

        # 识别排名变化
        trend_data = []
        for term in self.df['搜索词'].unique():
            term_data = self.df[self.df['搜索词'] == term].sort_values('报告日期')
            if len(term_data) >= 2:
                first_rank = term_data.iloc[0]['搜索频率排名']
                last_rank = term_data.iloc[-1]['搜索频率排名']
                change = first_rank - last_rank
                trend_data.append({
                    '搜索词': term,
                    '初始排名': int(first_rank),
                    '最终排名': int(last_rank),
                    '排名变化': int(change),
                    '变化趋势': '⬆️上升' if change > 0 else ('⬇️下降' if change < 0 else '→持平')
                })

        trend_df = pd.DataFrame(trend_data)

        # 合并数据
        search_full = search_stats.merge(trend_df, on='搜索词', how='left')
        search_full['排名变化'] = search_full['排名变化'].fillna(0).astype(int)
        search_full['变化趋势'] = search_full['变化趋势'].fillna('→持平')

        # 保存CSV
        csv_path = os.path.join(self.reports_dir, '03_搜索词热度分析.csv')
        search_full.to_csv(csv_path, index=False, encoding='utf-8-sig')

        # 生成Markdown报告
        self._generate_search_trends_report(search_full)

        print(f"   ✓ 分析了 {len(search_stats)} 个搜索词")
        print(f"   ✓ 输出文件: 03_搜索词热度分析.csv + .md")

        return search_full

    def _generate_search_trends_report(self, search_df):
        """生成搜索词热度分析Markdown报告"""
        md_path = os.path.join(self.reports_dir, '03_搜索词热度分析.md')

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# 搜索词热度分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # 执行摘要
            f.write("## 📊 执行摘要\n\n")
            f.write(f"- **总搜索词数**: {len(search_df)}\n")
            f.write(f"- **热度最高**: {search_df.iloc[0]['搜索词']}（排名{int(search_df.iloc[0]['平均排名'])}）\n")

            rising = search_df[search_df['排名变化'] > 0].sort_values('排名变化', ascending=False)
            if len(rising) > 0:
                f.write(f"- **增长最快**: {rising.iloc[0]['搜索词']}（上升{int(rising.iloc[0]['排名变化'])}位）\n")

            # TOP 20热门搜索词
            f.write("\n## 🔥 TOP 20 热门搜索词\n\n")
            f.write("| 排名 | 搜索词 | 平均排名 | 最佳排名 | 最差排名 | 出现月数 | 变化趋势 |\n")
            f.write("|------|--------|----------|----------|----------|----------|----------|\n")
            for idx, row in search_df.head(20).iterrows():
                f.write(f"| {idx+1} | {row['搜索词']} | {int(row['平均排名'])} | {int(row['最佳排名'])} | {int(row['最差排名'])} | {int(row['出现月数'])} | {row['变化趋势']} |\n")

            # 增长最快搜索词
            f.write("\n## 📈 增长最快搜索词 TOP 10\n\n")
            if len(rising) > 0:
                f.write("| 排名 | 搜索词 | 排名提升 | 初始排名 | 最终排名 |\n")
                f.write("|------|--------|----------|----------|----------|\n")
                for idx, row in rising.head(10).iterrows():
                    f.write(f"| {idx+1} | {row['搜索词']} | +{int(row['排名变化'])} | {row['初始排名']} | {row['最终排名']} |\n")
            else:
                f.write("暂无数据（需要多月数据才能分析趋势）\n")

            # 实操建议
            f.write("\n## 💡 实操建议\n\n")
            f.write("### 广告投放关键词选择\n")
            f.write("#### 高优先级（热度高且稳定）\n")
            stable = search_df[search_df['排名标准差'] < search_df['排名标准差'].median()].head(5)
            for _, row in stable.iterrows():
                f.write(f"- `{row['搜索词']}`（平均排名{int(row['平均排名'])}）\n")

            if len(rising) > 0:
                f.write("\n#### 潜力关键词（快速增长）\n")
                for _, row in rising.head(5).iterrows():
                    f.write(f"- `{row['搜索词']}`（上升{int(row['排名变化'])}位）\n")

            f.write("\n### Listing标题优化\n")
            f.write(f"- 将 `{search_df.iloc[0]['搜索词']}` 作为核心关键词放在标题前部\n")
            f.write("- 覆盖TOP 5搜索词的主要词根\n\n")

            f.write("---\n\n")
            f.write("**数据说明**: 基于搜索频率排名统计，排名数字越小表示热度越高\n")

    def analyze_word_frequency(self):
        """搜索词词频统计分析"""
        print("\n📊 4/8 搜索词词频统计分析...")

        all_words = []
        word_to_searches = {}

        for _, row in self.df.iterrows():
            search_term = str(row['搜索词']).lower()
            rank = row['搜索频率排名']

            words = re.findall(r'\b\w+\b', search_term)

            for word in words:
                if word not in STOP_WORDS and len(word) > 1:
                    all_words.append(word)
                    if word not in word_to_searches:
                        word_to_searches[word] = []
                    word_to_searches[word].append({
                        'search_term': search_term,
                        'rank': rank
                    })

        word_freq = Counter(all_words)

        # 创建词频统计表
        word_freq_data = []
        for word, count in word_freq.most_common(100):
            searches = word_to_searches[word]
            best_search = min(searches, key=lambda x: x['rank'])
            avg_rank = np.mean([s['rank'] for s in searches])

            word_type = self._classify_word(word)

            word_freq_data.append({
                '排名': len(word_freq_data) + 1,
                '单词': word,
                '出现次数': count,
                '词汇类型': word_type,
                '最佳搜索词示例': best_search['search_term'],
                '该搜索词排名': int(best_search['rank']) if pd.notna(best_search['rank']) else 0,
                '平均搜索排名': int(avg_rank) if pd.notna(avg_rank) else 0
            })

        word_freq_df = pd.DataFrame(word_freq_data)

        # 保存CSV
        csv_path = os.path.join(self.reports_dir, '04_词频统计分析.csv')
        word_freq_df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        # 生成Markdown报告
        self._generate_word_freq_report(word_freq_df)

        print(f"   ✓ 识别到 {len(word_freq)} 个高频词汇")
        print(f"   ✓ 输出文件: 04_词频统计分析.csv + .md")

        return word_freq_df

    def _classify_word(self, word):
        """词汇分类"""
        audience_words = ['women', 'men', 'man', 'woman', 'kids', 'kid', 'children', 'child',
                         'boys', 'boy', 'girls', 'girl', 'college', 'student', 'business',
                         'professional', 'teen', 'adult', 'ladies', 'lady', 'mens', 'womens']

        scene_words = ['travel', 'work', 'school', 'gaming', 'outdoor', 'hiking', 'camping',
                      'office', 'gym', 'sports', 'running', 'cycling', 'commute', 'daily',
                      'casual', 'weekend', 'vacation']

        attribute_words = ['large', 'small', 'big', 'mini', 'slim', 'lightweight', 'heavy',
                          'waterproof', 'leather', 'canvas', 'nylon', 'durable', 'portable',
                          'foldable', 'expandable', 'anti', 'theft', 'resistant', 'proof',
                          'inch', '15', '16', '17', '18', 'capacity', 'compartment']

        if word in audience_words:
            return '人群词'
        elif word in scene_words:
            return '场景词'
        elif word in attribute_words or word.isdigit():
            return '属性词'
        elif word[0].isupper() or word in self._get_brand_list():
            return '品牌词'
        else:
            return '核心词'

    def _get_brand_list(self):
        """从数据中提取品牌列表"""
        brands = set()
        for i in range(1, 4):
            col = f'点击量最高的品牌 #{i}'
            brands.update(self.df[col].dropna().str.lower().unique())
        return brands

    def _generate_word_freq_report(self, word_freq_df):
        """生成词频分析Markdown报告"""
        md_path = os.path.join(self.reports_dir, '04_词频统计分析.md')

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# 搜索词词频统计分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # 执行摘要
            f.write("## 📊 执行摘要\n\n")
            f.write(f"- **总词汇数**: {len(word_freq_df)}\n")
            f.write(f"- **最高频词**: {word_freq_df.iloc[0]['单词']}（出现{word_freq_df.iloc[0]['出现次数']}次）\n")

            type_counts = word_freq_df['词汇类型'].value_counts()
            f.write(f"- **人群词**: {type_counts.get('人群词', 0)} 个\n")
            f.write(f"- **场景词**: {type_counts.get('场景词', 0)} 个\n")
            f.write(f"- **属性词**: {type_counts.get('属性词', 0)} 个\n")
            f.write(f"- **品牌词**: {type_counts.get('品牌词', 0)} 个\n\n")

            # TOP 30高频词
            f.write("## 🔤 TOP 30 高频词汇\n\n")
            f.write("| 排名 | 单词 | 出现次数 | 类型 | 最佳搜索词示例 | 该词排名 |\n")
            f.write("|------|------|----------|------|----------------|----------|\n")
            for _, row in word_freq_df.head(30).iterrows():
                f.write(f"| {row['排名']} | **{row['单词']}** | {row['出现次数']} | {row['词汇类型']} | {row['最佳搜索词示例'][:40]}... | {row['该搜索词排名']} |\n")

            # 按类型分类
            f.write("\n## 🏷️ 词汇分类汇总\n\n")

            for word_type in ['人群词', '场景词', '属性词', '品牌词', '核心词']:
                type_words = word_freq_df[word_freq_df['词汇类型'] == word_type]
                if len(type_words) > 0:
                    f.write(f"### {word_type} TOP 10\n\n")
                    for _, row in type_words.head(10).iterrows():
                        f.write(f"- **{row['单词']}** ({row['出现次数']}次)\n")
                    f.write("\n")

            # 实操建议
            f.write("## 💡 实操建议\n\n")

            f.write("### 1. 广告关键词选词\n\n")
            f.write("#### 精准匹配广告\n")
            f.write("使用高频核心词组合：\n")
            core_words = word_freq_df[word_freq_df['词汇类型'] == '核心词'].head(3)
            if len(core_words) > 0:
                f.write("```\n")
                for _, row in core_words.iterrows():
                    f.write(f"{row['单词']} + [属性词] + [人群词]\n")
                f.write("```\n\n")

            f.write("#### 广泛匹配广告\n")
            audience = word_freq_df[word_freq_df['词汇类型'] == '人群词'].head(2)
            scene = word_freq_df[word_freq_df['词汇类型'] == '场景词'].head(2)
            if len(audience) > 0 and len(scene) > 0:
                f.write("使用人群词+场景词组合扩大流量：\n")
                f.write("```\n")
                for _, a in audience.iterrows():
                    for _, s in scene.iterrows():
                        f.write(f"[核心词] + {a['单词']} + {s['单词']}\n")
                f.write("```\n\n")

            f.write("### 2. Listing标题编写\n\n")
            f.write("**推荐标题结构**:\n")
            f.write("```\n")
            f.write("[品牌词] + [核心词] + [属性词1] + [属性词2] + [人群词] + [场景词]\n")
            f.write("```\n\n")

            f.write("**示例**:\n")
            brand = word_freq_df[word_freq_df['词汇类型'] == '品牌词'].head(1)
            core = word_freq_df[word_freq_df['词汇类型'] == '核心词'].head(2)
            attr = word_freq_df[word_freq_df['词汇类型'] == '属性词'].head(2)
            aud = word_freq_df[word_freq_df['词汇类型'] == '人群词'].head(1)
            sc = word_freq_df[word_freq_df['词汇类型'] == '场景词'].head(1)

            if len(brand) > 0 and len(core) >= 2:
                f.write("```\n")
                title_parts = []
                if len(brand) > 0:
                    title_parts.append(brand.iloc[0]['单词'].upper())
                if len(core) >= 2:
                    title_parts.append(' '.join([core.iloc[i]['单词'] for i in range(min(2, len(core)))]))
                if len(attr) >= 2:
                    title_parts.append(' '.join([attr.iloc[i]['单词'] for i in range(min(2, len(attr)))]))
                if len(aud) > 0:
                    title_parts.append(f"for {aud.iloc[0]['单词']}")
                if len(sc) > 0:
                    title_parts.append(sc.iloc[0]['单词'])

                f.write(' '.join(title_parts).title())
                f.write("\n```\n\n")

            f.write("### 3. 五点描述优化\n\n")
            if len(scene) > 0:
                f.write("每个bullet point针对一个场景词展开：\n\n")
                for _, row in scene.head(3).iterrows():
                    f.write(f"- **Perfect for {row['单词'].title()}**: [具体卖点]\n")

            f.write("\n---\n\n")
            f.write("**数据说明**: 基于搜索词拆解统计，过滤了常见停用词\n")

    # 继续添加其他分析方法...
    # 由于字符限制，我会在下一个文件中继续

    def analyze_products(self):
        """商品竞争力分析"""
        print("\n📊 5/8 商品竞争力分析...")

        product_data = []

        for i in range(1, 4):
            asin_col = f'点击量最高的商品 #{i}：ASIN'
            name_col = f'点击量最高的商品 #{i}：商品名称'
            click_col = f'点击量最高的商品 #{i}：点击份额'
            conv_col = f'点击量最高的商品 #{i}：转化份额'

            for _, row in self.df.iterrows():
                if pd.notna(row[asin_col]):
                    product_data.append({
                        'ASIN': row[asin_col],
                        'Name': row[name_col][:100] if pd.notna(row[name_col]) else '',
                        'Click_Share': row[click_col],
                        'Conv_Share': row[conv_col],
                        'Search_Term': row['搜索词'],
                        'Position': i
                    })

        product_df = pd.DataFrame(product_data)

        # 统计每个ASIN
        product_stats = product_df.groupby('ASIN').agg({
            'Click_Share': ['mean', 'count'],
            'Conv_Share': 'mean',
            'Name': 'first',
            'Search_Term': 'nunique'
        }).round(2)

        product_stats.columns = ['平均点击份额', '出现次数', '平均转化份额', '商品名称', '覆盖搜索词数']
        product_stats = product_stats.reset_index().sort_values('出现次数', ascending=False)

        # 保存CSV
        csv_path = os.path.join(self.reports_dir, '05_商品竞争力分析.csv')
        product_stats.head(50).to_csv(csv_path, index=False, encoding='utf-8-sig')

        # 生成Markdown
        self._generate_product_report(product_stats)

        print(f"   ✓ 分析了 {len(product_stats)} 个商品")
        print(f"   ✓ 输出文件: 05_商品竞争力分析.csv + .md")

        return product_df, product_stats

    def _generate_product_report(self, product_stats):
        """生成商品竞争力Markdown报告"""
        md_path = os.path.join(self.reports_dir, '05_商品竞争力分析.md')

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# 商品竞争力分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # 执行摘要
            f.write("## 📊 执行摘要\n\n")
            top_product = product_stats.iloc[0]
            f.write(f"- **明星商品**: {top_product['ASIN']}（出现{int(top_product['出现次数'])}次）\n")
            f.write(f"- **总商品数**: {len(product_stats)}\n")
            f.write(f"- **TOP商品平均点击份额**: {top_product['平均点击份额']:.2f}%\n")
            f.write(f"- **TOP商品覆盖搜索词**: {int(top_product['覆盖搜索词数'])}个\n\n")

            # TOP 20商品表格
            f.write("## 🏆 TOP 20 明星商品\n\n")
            f.write("| 排名 | ASIN | 商品名称 | 出现次数 | 平均点击份额 | 平均转化份额 | 覆盖搜索词数 |\n")
            f.write("|------|------|----------|----------|--------------|--------------|---------------|\n")
            for idx, row in product_stats.head(20).iterrows():
                name_short = row['商品名称'][:40] + '...' if len(row['商品名称']) > 40 else row['商品名称']
                f.write(f"| {idx+1} | {row['ASIN']} | {name_short} | {int(row['出现次数'])} | {row['平均点击份额']:.2f}% | {row['平均转化份额']:.2f}% | {int(row['覆盖搜索词数'])} |\n")

            # 实操建议
            f.write("\n## 💡 实操建议\n\n")
            f.write("### 竞品分析\n")
            f.write(f"重点研究TOP 3商品（{', '.join(product_stats.head(3)['ASIN'].tolist())}）：\n\n")
            f.write("- 分析他们的标题结构和关键词布局\n")
            f.write("- 查看主图风格和A+内容设计\n")
            f.write("- 研究价格策略和促销活动\n")
            f.write("- 分析评论中的高频词汇（用户关注点）\n\n")

            f.write("### Listing优化\n")
            f.write("学习明星商品的标题特征：\n\n")
            for _, row in product_stats.head(3).iterrows():
                f.write(f"- **{row['ASIN']}**: {row['商品名称']}\n")

            f.write("\n### 广告ASIN定向\n")
            f.write("针对TOP商品进行ASIN定向投放：\n")
            f.write("```\n")
            for _, row in product_stats.head(5).iterrows():
                f.write(f"{row['ASIN']} - 出现{int(row['出现次数'])}次\n")
            f.write("```\n\n")

            f.write("---\n\n")
            f.write("**数据说明**: 基于TOP 3商品位置统计\n")

    def analyze_conversion_efficiency(self, product_df):
        """ASIN转化效率分析"""
        print("\n📊 6/8 ASIN转化效率分析...")

        # 计算转化效率
        product_df['Conv_Efficiency'] = product_df['Conv_Share'] / (product_df['Click_Share'] + 0.001)

        # 四象限分类
        high_click = product_df['Click_Share'] >= product_df['Click_Share'].median()
        high_conv = product_df['Conv_Share'] >= product_df['Conv_Share'].median()

        product_df['Category'] = 'Low Traffic Low Conv'
        product_df.loc[high_click & high_conv, 'Category'] = 'Star Products'
        product_df.loc[~high_click & high_conv, 'Category'] = 'Hidden Gems'
        product_df.loc[high_click & ~high_conv, 'Category'] = 'Traffic Trap'

        # 按ASIN汇总分类
        asin_category = product_df.groupby('ASIN').agg({
            'Click_Share': 'mean',
            'Conv_Share': 'mean',
            'Conv_Efficiency': 'mean',
            'Category': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0],
            'Name': 'first'
        }).round(2)

        asin_category = asin_category.reset_index().sort_values('Conv_Efficiency', ascending=False)

        # 保存CSV
        csv_path = os.path.join(self.reports_dir, '06_ASIN转化效率分析.csv')
        asin_category.head(100).to_csv(csv_path, index=False, encoding='utf-8-sig')

        # 生成Markdown
        self._generate_conversion_report(asin_category)

        print(f"   ✓ 四象限分类完成")
        print(f"   ✓ 输出文件: 06_ASIN转化效率分析.csv + .md")

        return product_df

    def _generate_conversion_report(self, asin_category):
        """生成ASIN转化效率Markdown报告"""
        md_path = os.path.join(self.reports_dir, '06_ASIN转化效率分析.md')

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# ASIN转化效率分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # 执行摘要
            f.write("## 📊 执行摘要\n\n")
            category_counts = asin_category['Category'].value_counts()
            f.write(f"- **明星商品**: {category_counts.get('Star Products', 0)} 个\n")
            f.write(f"- **潜力商品**: {category_counts.get('Hidden Gems', 0)} 个\n")
            f.write(f"- **流量陷阱**: {category_counts.get('Traffic Trap', 0)} 个\n")
            f.write(f"- **问题商品**: {category_counts.get('Low Traffic Low Conv', 0)} 个\n\n")

            # 四象限说明
            f.write("## 🎯 四象限分类说明\n\n")
            f.write("| 分类 | 特征 | 优化策略 |\n")
            f.write("|------|------|----------|\n")
            f.write("| ⭐ 明星商品 | 高点击+高转化 | 保持优势，持续投入 |\n")
            f.write("| 💎 潜力商品 | 低点击+高转化 | 增加广告预算，优化主图标题 |\n")
            f.write("| ⚠️ 流量陷阱 | 高点击+低转化 | 优化详情页、价格、评论 |\n")
            f.write("| ❌ 问题商品 | 低点击+低转化 | 全面改进或考虑下架 |\n\n")

            # 各类商品TOP 10
            for category in ['Star Products', 'Hidden Gems', 'Traffic Trap']:
                cat_data = asin_category[asin_category['Category'] == category]
                if len(cat_data) > 0:
                    icon = '⭐' if category == 'Star Products' else ('💎' if category == 'Hidden Gems' else '⚠️')
                    f.write(f"## {icon} {category} TOP 10\n\n")
                    f.write("| 排名 | ASIN | 平均点击份额 | 平均转化份额 | 转化效率比 |\n")
                    f.write("|------|------|--------------|--------------|------------|\n")
                    for idx, row in cat_data.head(10).iterrows():
                        f.write(f"| {idx+1} | {row['ASIN']} | {row['Click_Share']:.2f}% | {row['Conv_Share']:.2f}% | {row['Conv_Efficiency']:.2f} |\n")
                    f.write("\n")

            # 实操建议
            f.write("## 💡 实操建议\n\n")

            f.write("### 明星商品策略\n")
            stars = asin_category[asin_category['Category'] == 'Star Products'].head(3)
            if len(stars) > 0:
                f.write("保持竞争力，防御竞争对手：\n")
                for _, row in stars.iterrows():
                    f.write(f"- {row['ASIN']}: 持续优化，监控竞品\n")

            f.write("\n### 潜力商品策略\n")
            gems = asin_category[asin_category['Category'] == 'Hidden Gems'].head(3)
            if len(gems) > 0:
                f.write("加大广告投入，提升曝光：\n")
                for _, row in gems.iterrows():
                    f.write(f"- {row['ASIN']}: 转化好但曝光不足，增加广告预算\n")

            f.write("\n### 流量陷阱策略\n")
            traps = asin_category[asin_category['Category'] == 'Traffic Trap'].head(3)
            if len(traps) > 0:
                f.write("优化详情页，提升转化：\n")
                for _, row in traps.iterrows():
                    f.write(f"- {row['ASIN']}: 检查价格、评论、A+内容\n")

            f.write("\n---\n\n")
            f.write("**数据说明**: 基于点击份额和转化份额的中位数进行分类\n")

    def analyze_keyword_conversion(self):
        """关键词转化效率分析"""
        print("\n📊 7/8 关键词转化效率分析...")

        keyword_data = []

        for search_term in self.df['搜索词'].unique():
            term_data = self.df[self.df['搜索词'] == search_term]

            click_total = 0
            conv_total = 0
            avg_rank = term_data['搜索频率排名'].mean()

            for i in range(1, 4):
                click_col = f'点击量最高的商品 #{i}：点击份额'
                conv_col = f'点击量最高的商品 #{i}：转化份额'
                click_total += term_data[click_col].fillna(0).mean()
                conv_total += term_data[conv_col].fillna(0).mean()

            conv_efficiency = conv_total / (click_total + 0.001)

            if click_total > 40:
                monopoly = '高垄断'
            elif click_total > 20:
                monopoly = '中等垄断'
            else:
                monopoly = '低垄断'

            if monopoly == '低垄断' and conv_efficiency > 0.8:
                category = '⭐黄金关键词'
            elif monopoly == '高垄断' and conv_efficiency > 0.8:
                category = '🔥红海关键词'
            elif monopoly == '低垄断':
                category = '💡潜力关键词'
            else:
                category = '⚠️避坑关键词'

            keyword_data.append({
                '搜索词': search_term,
                '搜索排名': int(avg_rank),
                '点击份额合计%': round(click_total, 2),
                '转化份额合计%': round(conv_total, 2),
                '转化效率比': round(conv_efficiency, 2),
                '垄断程度': monopoly,
                '关键词分类': category
            })

        keyword_df = pd.DataFrame(keyword_data).sort_values('搜索排名')

        # 保存CSV
        csv_path = os.path.join(self.reports_dir, '07_关键词转化效率分析.csv')
        keyword_df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        # 生成Markdown
        self._generate_keyword_report(keyword_df)

        print(f"   ✓ 分析了 {len(keyword_df)} 个关键词")
        print(f"   ✓ 输出文件: 07_关键词转化效率分析.csv + .md")

        return keyword_df

    def _generate_keyword_report(self, keyword_df):
        """生成关键词转化效率Markdown报告"""
        md_path = os.path.join(self.reports_dir, '07_关键词转化效率分析.md')

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# 关键词转化效率分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # 执行摘要
            f.write("## 📊 执行摘要\n\n")
            category_counts = keyword_df['关键词分类'].value_counts()
            f.write(f"- **黄金关键词**: {category_counts.get('⭐黄金关键词', 0)} 个（优先投放）\n")
            f.write(f"- **红海关键词**: {category_counts.get('🔥红海关键词', 0)} 个（谨慎投放）\n")
            f.write(f"- **潜力关键词**: {category_counts.get('💡潜力关键词', 0)} 个（优化后投放）\n")
            f.write(f"- **避坑关键词**: {category_counts.get('⚠️避坑关键词', 0)} 个（不建议）\n\n")

            # 分类说明
            f.write("## 🎯 分类说明\n\n")
            f.write("| 分类 | 垄断程度 | 转化效率 | 投放建议 |\n")
            f.write("|------|----------|----------|----------|\n")
            f.write("| ⭐黄金关键词 | 低垄断(<20%) | 高转化(>0.8) | 立即投放，重点监控 |\n")
            f.write("| 🔥红海关键词 | 高垄断(>40%) | 高转化(>0.8) | 谨慎投放，需要高预算 |\n")
            f.write("| 💡潜力关键词 | 低垄断(<20%) | 低转化(<0.8) | 优化Listing后测试 |\n")
            f.write("| ⚠️避坑关键词 | 高垄断(>40%) | 低转化(<0.8) | 不建议投放 |\n\n")

            # 各类关键词列表
            for category in ['⭐黄金关键词', '🔥红海关键词', '💡潜力关键词']:
                cat_data = keyword_df[keyword_df['关键词分类'] == category]
                if len(cat_data) > 0:
                    f.write(f"## {category}\n\n")
                    f.write("| 排名 | 搜索词 | 搜索排名 | 点击份额合计 | 转化份额合计 | 转化效率比 | 垄断程度 |\n")
                    f.write("|------|--------|----------|--------------|--------------|------------|----------|\n")
                    for idx, row in cat_data.head(20).iterrows():
                        f.write(f"| {idx+1} | {row['搜索词']} | {row['搜索排名']} | {row['点击份额合计%']:.2f}% | {row['转化份额合计%']:.2f}% | {row['转化效率比']:.2f} | {row['垄断程度']} |\n")
                    f.write("\n")

            # 实操建议
            f.write("## 💡 实操建议\n\n")

            gold = keyword_df[keyword_df['关键词分类'] == '⭐黄金关键词']
            if len(gold) > 0:
                f.write("### 黄金关键词投放计划\n")
                f.write("**优先级最高，立即投放**：\n\n")
                f.write("| 搜索词 | 建议出价 | 匹配类型 | 备注 |\n")
                f.write("|--------|----------|----------|------|\n")
                for _, row in gold.head(10).iterrows():
                    f.write(f"| {row['搜索词']} | 中高出价 | 精准+广泛 | 低垄断高转化 |\n")

            red = keyword_df[keyword_df['关键词分类'] == '🔥红海关键词']
            if len(red) > 0:
                f.write("\n### 红海关键词投放计划\n")
                f.write("**需要评估预算和产品竞争力**：\n\n")
                f.write("| 搜索词 | 建议出价 | 匹配类型 | 备注 |\n")
                f.write("|--------|----------|----------|------|\n")
                for _, row in red.head(5).iterrows():
                    f.write(f"| {row['搜索词']} | 高出价 | 精准 | 高垄断，需要高预算 |\n")

            potential = keyword_df[keyword_df['关键词分类'] == '💡潜力关键词']
            if len(potential) > 0:
                f.write("\n### 潜力关键词优化计划\n")
                f.write("**先优化Listing，再测试投放**：\n\n")
                for _, row in potential.head(5).iterrows():
                    f.write(f"- `{row['搜索词']}`: 优化标题和主图后，低出价测试\n")

            f.write("\n---\n\n")
            f.write("**数据说明**: 基于TOP 3商品的点击和转化份额合计计算\n")

    def analyze_time_series(self):
        """时间序列分析"""
        print("\n📊 8/8 时间序列分析...")

        # 按月统计
        monthly_stats = self.df.groupby('月份').agg({
            '搜索频率排名': ['mean', 'min', 'max'],
            '搜索词': 'nunique'
        }).round(0)

        monthly_stats.columns = ['平均搜索排名', '最佳排名', '最差排名', '搜索词数量']
        monthly_stats = monthly_stats.reset_index()
        monthly_stats['月份'] = monthly_stats['月份'].astype(str)

        # 保存CSV
        csv_path = os.path.join(self.reports_dir, '08_时间序列分析.csv')
        monthly_stats.to_csv(csv_path, index=False, encoding='utf-8-sig')

        # 生成Markdown
        self._generate_time_series_report(monthly_stats)

        print(f"   ✓ 分析了 {len(monthly_stats)} 个月的数据")
        print(f"   ✓ 输出文件: 08_时间序列分析.csv + .md")

        return monthly_stats

    def _generate_time_series_report(self, monthly_stats):
        """生成时间序列Markdown报告"""
        md_path = os.path.join(self.reports_dir, '08_时间序列分析.md')

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# 时间序列分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # 执行摘要
            f.write("## 📊 执行摘要\n\n")
            f.write(f"- **分析周期**: {monthly_stats['月份'].min()} 至 {monthly_stats['月份'].max()}\n")
            f.write(f"- **数据月数**: {len(monthly_stats)} 个月\n")

            if len(monthly_stats) >= 2:
                first_month = monthly_stats.iloc[0]
                last_month = monthly_stats.iloc[-1]
                rank_change = first_month['平均搜索排名'] - last_month['平均搜索排名']
                trend = "⬆️上升" if rank_change > 0 else ("⬇️下降" if rank_change < 0 else "→持平")
                f.write(f"- **整体趋势**: {trend}（从{int(first_month['平均搜索排名'])}到{int(last_month['平均搜索排名'])}）\n\n")

            # 月度数据表格
            f.write("## 📈 月度趋势数据\n\n")
            f.write("| 月份 | 平均搜索排名 | 最佳排名 | 最差排名 | 搜索词数量 | 环比变化 |\n")
            f.write("|------|--------------|----------|----------|------------|----------|\n")

            for idx, row in monthly_stats.iterrows():
                if idx > 0:
                    prev_rank = monthly_stats.iloc[idx-1]['平均搜索排名']
                    change = prev_rank - row['平均搜索排名']
                    change_str = f"+{int(change)}" if change > 0 else f"{int(change)}" if change < 0 else "-"
                else:
                    change_str = "-"

                f.write(f"| {row['月份']} | {int(row['平均搜索排名'])} | {int(row['最佳排名'])} | {int(row['最差排名'])} | {int(row['搜索词数量'])} | {change_str} |\n")

            # 季节性分析
            if len(monthly_stats) >= 6:
                f.write("\n## 🔍 趋势洞察\n\n")

                # 找出最好和最差月份
                best_month = monthly_stats.loc[monthly_stats['平均搜索排名'].idxmin()]
                worst_month = monthly_stats.loc[monthly_stats['平均搜索排名'].idxmax()]

                f.write(f"- **最佳月份**: {best_month['月份']}（平均排名{int(best_month['平均搜索排名'])}）\n")
                f.write(f"- **最差月份**: {worst_month['月份']}（平均排名{int(worst_month['平均搜索排名'])}）\n\n")

            # 实操建议
            f.write("## 💡 实操建议\n\n")

            f.write("### 备货计划\n")
            if len(monthly_stats) >= 6:
                f.write(f"- 根据历史数据，{best_month['月份']}前后是旺季，提前备货\n")
                f.write(f"- {worst_month['月份']}前后是淡季，控制库存\n\n")

            f.write("### 广告预算分配\n")
            f.write("- 旺季（搜索排名上升期）增加30-50%广告预算\n")
            f.write("- 淡季（搜索排名下降期）降低预算或测试新关键词\n\n")

            f.write("### 促销活动策划\n")
            f.write("- 在搜索热度上升前1-2个月开始促销预热\n")
            f.write("- 旺季高峰期配合LD、BD等大促活动\n\n")

            f.write("---\n\n")
            f.write("**数据说明**: 基于每月搜索频率排名统计，排名数字越小表示热度越高\n")


def main():
    """主函数"""
    import sys

    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        data_dir = os.getcwd()

    print("=" * 60)
    print("🚀 亚马逊搜索词报告分析器（完整版）")
    print("=" * 60)
    print(f"\n📁 数据目录: {data_dir}")

    analyzer = AmazonSearchAnalyzer(data_dir)

    if not analyzer.load_all_data():
        print("\n❌ 未找到有效的CSV文件")
        return

    analyzer.clean_data()

    print("\n" + "=" * 60)
    print("📊 开始8维度分析")
    print("=" * 60)

    # 执行所有分析
    brand_df = analyzer.analyze_brands()
    category_df = analyzer.analyze_categories()
    search_df = analyzer.analyze_search_trends()
    word_freq_df = analyzer.analyze_word_frequency()
    product_df, product_stats = analyzer.analyze_products()
    product_df = analyzer.analyze_conversion_efficiency(product_df)
    keyword_df = analyzer.analyze_keyword_conversion()
    monthly_stats = analyzer.analyze_time_series()

    # 完成
    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print("=" * 60)
    print(f"\n📊 生成的报告文件（{analyzer.reports_dir}/）：")
    print("   1. 01_品牌竞争分析.csv + .md")
    print("   2. 02_类别趋势分析.csv + .md")
    print("   3. 03_搜索词热度分析.csv + .md")
    print("   4. 04_词频统计分析.csv + .md")
    print("   5. 05_商品竞争力分析.csv + .md")
    print("   6. 06_ASIN转化效率分析.csv + .md")
    print("   7. 07_关键词转化效率分析.csv + .md")
    print("   8. 08_时间序列分析.csv + .md")
    print(f"\n💡 提示：所有报告已保存到 {analyzer.reports_dir} 目录")


if __name__ == '__main__':
    main()
