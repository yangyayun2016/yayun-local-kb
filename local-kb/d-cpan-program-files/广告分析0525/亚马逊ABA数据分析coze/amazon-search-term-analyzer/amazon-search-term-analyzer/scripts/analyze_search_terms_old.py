#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
亚马逊搜索词报告分析脚本（通用版）
适用于任何类目的搜索词报告分析
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
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置绘图风格
sns.set_style('whitegrid')
sns.set_palette('husl')

# 停用词列表（用于词频分析）
STOP_WORDS = {
    'for', 'with', 'and', 'the', 'of', 'in', 'to', 'a', 'an',
    'on', 'at', 'by', 'from', 'up', 'about', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'between',
    'under', 'again', 'further', 'then', 'once', '&', '-', '/'
}

class AmazonSearchAnalyzer:
    """亚马逊搜索词报告分析器（通用版）"""

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.all_data = []
        self.df = None
        self.output_dir = data_dir

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
                # 跳过第一行（元数据），从第二行开始读取
                df = pd.read_csv(file, skiprows=1, encoding='utf-8-sig')
                self.all_data.append(df)
            except Exception as e:
                print(f"   ⚠️  Error loading {file}: {e}")

        # 合并所有数据
        if self.all_data:
            self.df = pd.concat(self.all_data, ignore_index=True)
            print(f"\n✅ 总记录数: {len(self.df)}")
            return True
        return False

    def clean_data(self):
        """数据清洗"""
        print("\n🧹 数据清洗中...")

        # 转换数值列
        self.df['搜索频率排名'] = pd.to_numeric(self.df['搜索频率排名'], errors='coerce')

        # 转换日期
        self.df['报告日期'] = pd.to_datetime(self.df['报告日期'])
        self.df['月份'] = self.df['报告日期'].dt.to_period('M')

        # 转换点击和转化份额
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

        # 获取TOP 15品牌
        top_brands = dict(brand_counts.most_common(15))

        # 创建品牌排位分布数据
        brand_position_data = []
        for brand in top_brands.keys():
            brand_position_data.append({
                'Brand': brand,
                'Position_1': brand_positions[1][brand],
                'Position_2': brand_positions[2][brand],
                'Position_3': brand_positions[3][brand],
                'Total': brand_counts[brand]
            })

        brand_df = pd.DataFrame(brand_position_data).sort_values('Total', ascending=False)
        print(f"   ✓ 识别到 {len(brand_counts)} 个品牌，TOP品牌: {brand_df.iloc[0]['Brand']}")

        return brand_df

    def analyze_categories(self):
        """类别趋势分析"""
        print("\n📊 2/8 类别趋势分析...")

        category_counts = Counter()

        for i in range(1, 4):
            col = f'点击量最高的类别 #{i}'
            categories = self.df[col].dropna()
            category_counts.update(categories)

        top_categories = dict(category_counts.most_common(10))
        print(f"   ✓ 识别到 {len(category_counts)} 个类别，TOP类别: {list(top_categories.keys())[0]}")

        return top_categories

    def analyze_search_trends(self):
        """搜索词热度分析"""
        print("\n📊 3/8 搜索词热度分析...")

        # 计算每个搜索词的平均排名和趋势
        search_stats = self.df.groupby('搜索词').agg({
            '搜索频率排名': ['mean', 'std', 'min', 'max', 'count']
        }).round(0)

        search_stats.columns = ['平均排名', '排名标准差', '最佳排名', '最差排名', '出现次数']
        search_stats = search_stats.sort_values('平均排名')

        # 识别排名上升最快的搜索词
        trend_data = []
        for term in self.df['搜索词'].unique():
            term_data = self.df[self.df['搜索词'] == term].sort_values('报告日期')
            if len(term_data) >= 2:
                first_rank = term_data.iloc[0]['搜索频率排名']
                last_rank = term_data.iloc[-1]['搜索频率排名']
                change = first_rank - last_rank  # 正值表示排名上升
                trend_data.append({
                    '搜索词': term,
                    '初始排名': first_rank,
                    '最终排名': last_rank,
                    '排名变化': change
                })

        trend_df = pd.DataFrame(trend_data).sort_values('排名变化', ascending=False)
        print(f"   ✓ 分析了 {len(search_stats)} 个搜索词的热度趋势")

        return search_stats, trend_df

    def analyze_word_frequency(self):
        """搜索词词频统计和分析 ⭐"""
        print("\n📊 4/8 搜索词词频统计分析...")

        # 拆解所有搜索词
        all_words = []
        word_to_searches = {}  # 记录每个词对应的搜索词

        for _, row in self.df.iterrows():
            search_term = str(row['搜索词']).lower()
            rank = row['搜索频率排名']

            # 按空格和常见分隔符拆分
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

        # 统计词频
        word_freq = Counter(all_words)

        # 创建词频统计表
        word_freq_data = []
        for word, count in word_freq.most_common(50):
            # 找出包含该词的搜索排名最靠前的搜索词
            searches = word_to_searches[word]
            best_search = min(searches, key=lambda x: x['rank'])
            avg_rank = np.mean([s['rank'] for s in searches])

            # 词汇分类
            word_type = self._classify_word(word)

            word_freq_data.append({
                '排名': len(word_freq_data) + 1,
                '单词': word,
                '出现次数': count,
                '词汇类型': word_type,
                '最佳搜索词示例': best_search['search_term'],
                '该搜索词排名': int(best_search['rank']),
                '平均搜索排名': int(avg_rank)
            })

        word_freq_df = pd.DataFrame(word_freq_data)

        # 按类型汇总
        type_summary = word_freq_df.groupby('词汇类型')['单词'].apply(list).to_dict()

        print(f"   ✓ 识别到 {len(word_freq)} 个高频词汇")
        print(f"   ✓ 人群词: {len([w for w in word_freq_data if w['词汇类型'] == '人群词'])} 个")
        print(f"   ✓ 场景词: {len([w for w in word_freq_data if w['词汇类型'] == '场景词'])} 个")
        print(f"   ✓ 属性词: {len([w for w in word_freq_data if w['词汇类型'] == '属性词'])} 个")

        return word_freq_df, type_summary

    def _classify_word(self, word):
        """词汇分类"""
        # 人群词
        audience_words = ['women', 'men', 'man', 'woman', 'kids', 'kid', 'children', 'child',
                         'boys', 'boy', 'girls', 'girl', 'college', 'student', 'business',
                         'professional', 'teen', 'adult', 'ladies', 'lady', 'mens', 'womens']

        # 场景词
        scene_words = ['travel', 'work', 'school', 'gaming', 'outdoor', 'hiking', 'camping',
                      'office', 'gym', 'sports', 'running', 'cycling', 'commute', 'daily',
                      'casual', 'business', 'professional', 'weekend', 'vacation']

        # 属性词（尺寸、材质、特性）
        attribute_words = ['large', 'small', 'big', 'mini', 'slim', 'lightweight', 'heavy',
                          'waterproof', 'leather', 'canvas', 'nylon', 'durable', 'portable',
                          'foldable', 'expandable', 'anti', 'theft', 'resistant', 'proof',
                          'inch', '15', '16', '17', '18', 'capacity', 'compartment']

        # 品牌词（常见品牌，会根据实际数据动态识别）
        # 这里只列举一些通用的，实际会从数据中提取

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
                        'Name': row[name_col][:50] if pd.notna(row[name_col]) else '',
                        'Click_Share': row[click_col],
                        'Conv_Share': row[conv_col],
                        'Search_Term': row['搜索词'],
                        'Position': i
                    })

        product_df = pd.DataFrame(product_data)

        # 统计每个ASIN的出现频率和平均表现
        product_stats = product_df.groupby('ASIN').agg({
            'Click_Share': ['mean', 'count'],
            'Conv_Share': 'mean',
            'Name': 'first',
            'Search_Term': 'nunique'
        }).round(2)

        product_stats.columns = ['平均点击份额', '出现次数', '平均转化份额', '商品名称', '覆盖搜索词数']
        product_stats = product_stats.sort_values('出现次数', ascending=False)

        print(f"   ✓ 分析了 {len(product_stats)} 个商品，TOP商品出现 {int(product_stats.iloc[0]['出现次数'])} 次")

        return product_df, product_stats

    def analyze_conversion_efficiency(self, product_df):
        """ASIN转化效率分析"""
        print("\n📊 6/8 ASIN转化效率分析...")

        # 计算转化效率比
        product_df['Conv_Efficiency'] = product_df['Conv_Share'] / (product_df['Click_Share'] + 0.001)

        # 分类商品
        high_click = product_df['Click_Share'] >= product_df['Click_Share'].median()
        high_conv = product_df['Conv_Share'] >= product_df['Conv_Share'].median()

        product_df['Category'] = 'Low Traffic Low Conv'
        product_df.loc[high_click & high_conv, 'Category'] = 'Star Products (High Click High Conv)'
        product_df.loc[~high_click & high_conv, 'Category'] = 'Hidden Gems (Low Click High Conv)'
        product_df.loc[high_click & ~high_conv, 'Category'] = 'Traffic Trap (High Click Low Conv)'

        category_counts = product_df['Category'].value_counts()
        print(f"   ✓ 明星商品: {category_counts.get('Star Products (High Click High Conv)', 0)} 个")
        print(f"   ✓ 潜力商品: {category_counts.get('Hidden Gems (Low Click High Conv)', 0)} 个")

        return product_df

    def analyze_keyword_conversion(self):
        """基于关键词的转化效率分析 ⭐"""
        print("\n📊 7/8 基于关键词的转化效率分析...")

        keyword_data = []

        for search_term in self.df['搜索词'].unique():
            term_data = self.df[self.df['搜索词'] == search_term]

            # 计算TOP3点击份额和转化份额合计
            click_total = 0
            conv_total = 0
            avg_rank = term_data['搜索频率排名'].mean()

            for i in range(1, 4):
                click_col = f'点击量最高的商品 #{i}：点击份额'
                conv_col = f'点击量最高的商品 #{i}：转化份额'
                click_total += term_data[click_col].fillna(0).mean()
                conv_total += term_data[conv_col].fillna(0).mean()

            # 计算转化效率比
            conv_efficiency = conv_total / (click_total + 0.001)

            # 判断垄断程度
            if click_total > 40:
                monopoly = '高垄断'
            elif click_total > 20:
                monopoly = '中等垄断'
            else:
                monopoly = '低垄断'

            # 四象限分类
            if monopoly == '低垄断' and conv_efficiency > 0.8:
                category = '黄金关键词'
            elif monopoly == '高垄断' and conv_efficiency > 0.8:
                category = '红海关键词'
            elif monopoly == '低垄断' and conv_efficiency <= 0.8:
                category = '潜力关键词'
            else:
                category = '避坑关键词'

            keyword_data.append({
                '搜索词': search_term,
                '搜索排名': int(avg_rank),
                '点击份额合计': round(click_total, 2),
                '转化份额合计': round(conv_total, 2),
                '转化效率比': round(conv_efficiency, 2),
                '垄断程度': monopoly,
                '关键词分类': category
            })

        keyword_df = pd.DataFrame(keyword_data).sort_values('搜索排名')

        # 统计各类关键词数量
        category_counts = keyword_df['关键词分类'].value_counts()
        print(f"   ✓ 黄金关键词: {category_counts.get('黄金关键词', 0)} 个")
        print(f"   ✓ 红海关键词: {category_counts.get('红海关键词', 0)} 个")
        print(f"   ✓ 潜力关键词: {category_counts.get('潜力关键词', 0)} 个")

        return keyword_df

    def analyze_time_series(self):
        """时间序列分析"""
        print("\n📊 8/8 时间序列分析...")

        # 按月统计平均排名
        monthly_avg = self.df.groupby('月份').agg({
            '搜索频率排名': 'mean'
        }).round(0)

        print(f"   ✓ 分析了 {len(monthly_avg)} 个月的数据")

        return monthly_avg

    def generate_visualizations(self, brand_df, categories, product_df, word_freq_df, keyword_df):
        """生成可视化图表"""
        print("\n📈 生成可视化图表...")

        output_dir = os.path.join(self.output_dir, 'analysis_charts')
        os.makedirs(output_dir, exist_ok=True)

        # 1. 品牌竞争分布图
        fig, ax = plt.subplots(figsize=(12, 6))
        brand_df_plot = brand_df.head(10).set_index('Brand')
        brand_df_plot[['Position_1', 'Position_2', 'Position_3']].plot(
            kind='bar', stacked=True, ax=ax,
            color=['#FF6B6B', '#4ECDC4', '#95E1D3']
        )
        ax.set_title('Top 10 Brands - Position Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Brand', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.legend(['Position #1', 'Position #2', 'Position #3'])
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '01_brand_competition.png'), dpi=300, bbox_inches='tight')
        plt.close()

        print(f"   ✓ 品牌竞争分布图")

        # 2. 类别分布饼图
        fig, ax = plt.subplots(figsize=(10, 8))
        cat_items = list(categories.items())[:8]
        labels = [c[0] for c in cat_items]
        sizes = [c[1] for c in cat_items]
        colors = sns.color_palette('pastel', len(labels))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title('Top 8 Categories Distribution', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '02_category_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()

        print(f"   ✓ 类别分布饼图")

        return output_dir

    def save_results(self, word_freq_df, keyword_df):
        """保存分析结果为CSV"""
        print("\n💾 保存分析结果...")

        # 保存词频统计表
        word_freq_path = os.path.join(self.output_dir, '词频统计表.csv')
        word_freq_df.to_csv(word_freq_path, index=False, encoding='utf-8-sig')
        print(f"   ✓ 词频统计表.csv")

        # 保存关键词转化效率表
        keyword_path = os.path.join(self.output_dir, '关键词转化效率表.csv')
        keyword_df.to_csv(keyword_path, index=False, encoding='utf-8-sig')
        print(f"   ✓ 关键词转化效率表.csv")

        return word_freq_path, keyword_path


def main():
    """主函数"""
    import sys

    # 获取数据目录
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        data_dir = os.getcwd()

    print("=" * 60)
    print("🚀 亚马逊搜索词报告分析器（通用版）")
    print("=" * 60)
    print(f"\n📁 数据目录: {data_dir}")

    # 创建分析器
    analyzer = AmazonSearchAnalyzer(data_dir)

    # 加载数据
    if not analyzer.load_all_data():
        print("\n❌ 未找到有效的CSV文件")
        return

    # 清洗数据
    analyzer.clean_data()

    # 执行8维度分析
    print("\n" + "=" * 60)
    print("📊 开始8维度分析")
    print("=" * 60)

    brand_df = analyzer.analyze_brands()
    categories = analyzer.analyze_categories()
    search_stats, trend_df = analyzer.analyze_search_trends()
    word_freq_df, type_summary = analyzer.analyze_word_frequency()
    product_df, product_stats = analyzer.analyze_products()
    product_df = analyzer.analyze_conversion_efficiency(product_df)
    keyword_df = analyzer.analyze_keyword_conversion()
    monthly_avg = analyzer.analyze_time_series()

    # 生成可视化
    print("\n" + "=" * 60)
    print("📈 生成可视化和报告")
    print("=" * 60)

    chart_dir = analyzer.generate_visualizations(brand_df, categories, product_df, word_freq_df, keyword_df)

    # 保存结果
    word_freq_path, keyword_path = analyzer.save_results(word_freq_df, keyword_df)

    # 完成
    print("\n" + "=" * 60)
    print("✅ 分析完成！")
    print("=" * 60)
    print(f"\n📊 生成的文件：")
    print(f"   - 词频统计表: {word_freq_path}")
    print(f"   - 关键词转化效率表: {keyword_path}")
    print(f"   - 可视化图表: {chart_dir}/")
    print(f"\n💡 提示：查看 02_分析角度和方法.md 了解如何应用这些分析结果")


if __name__ == '__main__':
    main()

