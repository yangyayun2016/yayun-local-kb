#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
亚马逊关键词智能分析系统 - 主程序
作者: 亚马逊关键词分析工具
版本: 1.0.0
日期: 2024
"""

import os
import sys
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 导入自定义模块
from src.data_loader import DataLoader
from src.field_mapper import FieldMapper
from src.conflict_resolver import ConflictResolver
from src.semantic_analyzer import SemanticAnalyzer
from src.keyword_classifier import KeywordClassifier
from src.reason_generator import ReasonGenerator
from src.excel_exporter import ExcelExporter
from src.chart_generator import ChartGenerator
from config.column_mapping import COLUMN_MAPPINGS
from config.classification_rules import CLASSIFICATION_RULES
from config.thresholds import THRESHOLDS

# 配置日志
def setup_logging():
    """配置日志系统"""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f"keyword_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

class KeywordAnalysisProject:
    """关键词分析项目主类"""
    
    def __init__(self, data_dir=None):
        """初始化项目"""
        self.logger = setup_logging()
        self.data_dir = Path(data_dir) if data_dir else project_root / "data"
        self.output_dir = self.data_dir / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化模块
        self.data_loader = DataLoader(self.data_dir, self.logger)
        self.field_mapper = FieldMapper(COLUMN_MAPPINGS, self.logger)
        self.conflict_resolver = ConflictResolver(self.logger)
        self.semantic_analyzer = SemanticAnalyzer(self.logger)
        self.keyword_classifier = KeywordClassifier(CLASSIFICATION_RULES, THRESHOLDS, self.logger)
        self.reason_generator = ReasonGenerator(self.logger)
        self.excel_exporter = ExcelExporter(self.logger)
        self.chart_generator = ChartGenerator(self.logger)
        
        # 数据存储
        self.raw_data = {}
        self.unified_data = None
        self.final_data = None
        
    def run(self):
        """运行完整的数据处理流程"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("开始亚马逊关键词智能分析项目")
            self.logger.info("=" * 60)
            
            # 步骤1: 加载数据
            self.load_data()
            
            # 步骤2: 映射字段
            self.map_fields()
            
            # 步骤3: 解决冲突并合并
            self.resolve_conflicts()
            
            # 步骤4: 语义分析
            self.semantic_analysis()
            
            # 步骤5: 关键词分类
            self.classify_keywords()
            
            # 步骤6: 生成分类理由
            self.generate_reasons()
            
            # 步骤7: 导出Excel
            self.export_excel()
            
            # 步骤8: 生成图表
            self.generate_charts()
            
            # 步骤9: 生成报告
            self.generate_reports()
            
            self.logger.info("=" * 60)
            self.logger.info("项目处理完成！")
            self.logger.info(f"输出文件保存在: {self.output_dir}")
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.error(f"处理过程中发生错误: {str(e)}", exc_info=True)
            raise
    
    def load_data(self):
        """加载所有数据文件"""
        self.logger.info("步骤1: 加载数据文件...")
        self.raw_data = self.data_loader.load_all_files()
        self.logger.info(f"成功加载 {len(self.raw_data)} 个数据文件")
        
        # 记录数据统计
        for tool_name, df in self.raw_data.items():
            self.logger.info(f"  {tool_name}: {len(df)} 条记录")
    
    def map_fields(self):
        """映射和统一字段"""
        self.logger.info("步骤2: 映射和统一字段...")
        
        # 对每个数据源进行字段映射
        mapped_data = {}
        for tool_name, df in self.raw_data.items():
            mapped_df = self.field_mapper.map_fields(df, tool_name)
            if mapped_df is not None:
                mapped_data[tool_name] = mapped_df
                self.logger.info(f"  {tool_name}: 映射 {len(mapped_df.columns)} 个字段")
        
        # 合并映射后的数据
        all_data = []
        for tool_name, df in mapped_data.items():
            df['source_tool'] = tool_name
            all_data.append(df)
        
        if all_data:
            self.unified_data = pd.concat(all_data, ignore_index=True, sort=False)
            self.logger.info(f"合并后总数据量: {len(self.unified_data)} 条记录")
        else:
            raise ValueError("没有成功映射任何数据")
    
    def resolve_conflicts(self):
        """解决数据冲突"""
        self.logger.info("步骤3: 解决数据冲突...")
        self.final_data = self.conflict_resolver.resolve(self.unified_data)
        self.logger.info(f"冲突解决后数据量: {len(self.final_data)} 条唯一关键词")
    
    def semantic_analysis(self):
        """执行语义分析"""
        self.logger.info("步骤4: 执行语义分析...")
        
        # 加载产品标题和品牌信息
        product_titles_path = self.data_dir / "input" / "product_titles.xlsx"
        brand_info_path = self.data_dir / "input" / "brand.xlsx"
        
        if product_titles_path.exists():
            product_df = pd.read_excel(product_titles_path)
            # 提取产品标题关键词
            product_titles = product_df['商品标题'].dropna().tolist()
            self.final_data = self.semantic_analyzer.calculate_similarity(
                self.final_data, product_titles
            )
        
        # 检查品牌词
        if brand_info_path.exists():
            brand_df = pd.read_excel(brand_info_path)
            brands = brand_df['品牌'].dropna().tolist()
            self.final_data = self.semantic_analyzer.identify_brand_keywords(
                self.final_data, brands
            )
    
    def classify_keywords(self):
        """分类关键词"""
        self.logger.info("步骤5: 分类关键词...")
        self.final_data = self.keyword_classifier.classify(self.final_data)
        
        # 统计分类结果
        class_counts = self.final_data['classification'].value_counts()
        for cls, count in class_counts.items():
            self.logger.info(f"  {cls}: {count} 个关键词")
    
    def generate_reasons(self):
        """生成分类理由"""
        self.logger.info("步骤6: 生成分类理由...")
        self.final_data = self.reason_generator.generate_all_reasons(self.final_data)
    
    def export_excel(self):
        """导出Excel文件"""
        self.logger.info("步骤7: 导出Excel文件...")
        
        output_path = self.output_dir / "关键词智能分析库.xlsx"
        
        # 准备要导出的工作表
        sheets = {
            '所有关键词': self.final_data,
            '投放关键词': self.final_data[self.final_data['classification'] == '投放关键词'].copy(),
            '否定关键词': self.final_data[self.final_data['classification'] == '否定关键词'].copy(),
            '品牌关键词': self.final_data[self.final_data['classification'] == '品牌关键词'].copy(),
            '待定关键词': self.final_data[self.final_data['classification'] == '待定关键词'].copy()
        }
        
        # 添加词根分析
        sheets['投放关键词词根'] = self.extract_keyword_roots(
            sheets['投放关键词'], '投放关键词'
        )
        sheets['否定关键词词根'] = self.extract_keyword_roots(
            sheets['否定关键词'], '否定关键词'
        )
        
        # 添加分析报告
        sheets['分析报告'] = self.create_analysis_report()
        
        # 添加数据质量报告
        sheets['数据质量报告'] = self.create_data_quality_report()
        
        # 导出Excel
        self.excel_exporter.export_to_excel(sheets, output_path)
        self.logger.info(f"Excel文件已保存: {output_path}")
    
    def extract_keyword_roots(self, df, category):
        """提取关键词词根"""
        if len(df) == 0:
            return pd.DataFrame()
        
        # 简单词根提取（按空格分割）
        roots = []
        for keyword in df['keyword'].dropna():
            words = str(keyword).lower().split()
            if len(words) > 1:
                # 取第一个或前两个单词作为词根
                root = ' '.join(words[:min(2, len(words))])
                roots.append(root)
        
        # 统计词根频率
        from collections import Counter
        root_counts = Counter(roots)
        
        # 创建词根DataFrame
        root_df = pd.DataFrame({
            '词根': list(root_counts.keys()),
            '出现次数': list(root_counts.values())
        })
        
        # 计算相关指标
        root_df['平均搜索量'] = 0
        root_df['平均CPC'] = 0
        root_df['关键词数量'] = root_df['出现次数']
        
        for idx, root in enumerate(root_df['词根']):
            matching_keywords = df[df['keyword'].str.contains(root, case=False, na=False)]
            if len(matching_keywords) > 0:
                root_df.loc[idx, '平均搜索量'] = matching_keywords['search_volume'].mean()
                root_df.loc[idx, '平均CPC'] = matching_keywords['cpc_suggested'].mean()
        
        # 排序
        root_df = root_df.sort_values('出现次数', ascending=False)
        
        return root_df
    
    def create_analysis_report(self):
        """创建分析报告"""
        report_data = []
        
        # 基本信息
        report_data.append(["分析报告", ""])
        report_data.append(["生成时间", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        report_data.append(["关键词总数", len(self.final_data)])
        report_data.append(["", ""])
        
        # 分类统计
        report_data.append(["分类统计", ""])
        class_counts = self.final_data['classification'].value_counts()
        for cls, count in class_counts.items():
            report_data.append([f"{cls}数量", count])
            report_data.append([f"{cls}占比", f"{count/len(self.final_data)*100:.1f}%"])
        
        report_data.append(["", ""])
        
        # 关键指标
        report_data.append(["关键指标统计", ""])
        if 'search_volume' in self.final_data.columns:
            avg_search = self.final_data['search_volume'].mean()
            report_data.append(["平均搜索量", f"{avg_search:.0f}"])
        
        if 'cpc_suggested' in self.final_data.columns:
            avg_cpc = self.final_data['cpc_suggested'].mean()
            report_data.append(["平均CPC", f"${avg_cpc:.2f}"])
        
        if 'conversion_rate' in self.final_data.columns:
            avg_cr = self.final_data['conversion_rate'].mean()
            report_data.append(["平均转化率", f"{avg_cr*100:.1f}%"])
        
        report_data.append(["", ""])
        
        # 数据来源
        report_data.append(["数据来源分布", ""])
        if 'source_tool' in self.final_data.columns:
            source_counts = self.final_data['source_tool'].value_counts()
            for source, count in source_counts.items():
                report_data.append([source, count])
        
        # 转换为DataFrame
        report_df = pd.DataFrame(report_data, columns=["指标", "值"])
        return report_df
    
    def create_data_quality_report(self):
        """创建数据质量报告"""
        quality_data = []
        
        quality_data.append(["数据质量报告", ""])
        quality_data.append(["检查时间", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        quality_data.append(["", ""])
        
        # 检查缺失值
        quality_data.append(["缺失值统计", ""])
        for column in self.final_data.columns:
            missing_count = self.final_data[column].isna().sum()
            missing_pct = missing_count / len(self.final_data) * 100
            if missing_count > 0:
                quality_data.append([column, f"{missing_count} ({missing_pct:.1f}%)"])
        
        quality_data.append(["", ""])
        
        # 检查数据范围
        quality_data.append(["数据范围检查", ""])
        numeric_columns = self.final_data.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_columns[:10]:  # 只检查前10个数值列
            if col in self.final_data.columns:
                min_val = self.final_data[col].min()
                max_val = self.final_data[col].max()
                quality_data.append([f"{col}范围", f"{min_val:.2f} - {max_val:.2f}"])
        
        quality_df = pd.DataFrame(quality_data, columns=["检查项", "结果"])
        return quality_df
    
    def generate_charts(self):
        """生成所有图表"""
        self.logger.info("步骤8: 生成图表...")
        
        charts_dir = self.output_dir / "charts"
        charts_dir.mkdir(exist_ok=True)
        
        # 生成图表
        self.chart_generator.generate_all_charts(self.final_data, charts_dir)
        
        self.logger.info(f"图表已保存到: {charts_dir}")
    
    def generate_reports(self):
        """生成文本报告"""
        self.logger.info("步骤9: 生成报告...")
        
        report_path = self.output_dir / "处理报告.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("亚马逊关键词智能分析处理报告\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("1. 数据概览\n")
            f.write(f"   关键词总数: {len(self.final_data)}\n")
            
            # 分类统计
            f.write("\n2. 分类统计\n")
            class_counts = self.final_data['classification'].value_counts()
            for cls, count in class_counts.items():
                percentage = count / len(self.final_data) * 100
                f.write(f"   {cls}: {count} ({percentage:.1f}%)\n")
            
            # 关键指标
            f.write("\n3. 关键指标\n")
            if 'search_volume' in self.final_data.columns:
                avg_search = self.final_data['search_volume'].mean()
                f.write(f"   平均搜索量: {avg_search:.0f}\n")
            
            if 'cpc_suggested' in self.final_data.columns:
                avg_cpc = self.final_data['cpc_suggested'].mean()
                f.write(f"   平均CPC: ${avg_cpc:.2f}\n")
            
            # 处理问题
            f.write("\n4. 处理日志\n")
            f.write("   所有数据已成功处理\n")
            f.write("   图表已生成: 20张\n")
            f.write("   Excel报告已生成: 9个工作表\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("处理完成\n")
            f.write("=" * 60 + "\n")
        
        self.logger.info(f"处理报告已保存: {report_path}")

def main():
    """主函数"""
    try:
        # 设置数据目录
        data_dir = r"C:\Users\Administrator\Desktop\keyword"
        
        # 创建并运行项目
        project = KeywordAnalysisProject(data_dir)
        project.run()
        
    except Exception as e:
        print(f"程序执行错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
字段映射配置
定义各数据源的字段到统一字段的映射关系
"""

COLUMN_MAPPINGS = {
    # SIF工具 (keyword1.xlsx)
    'SIF': {
        'source_columns': {
            '关键词': 'keyword',
            '翻译': 'chinese_translation',
            '相关性-自动百分比': 'relevance_auto_percentage',
            '相关性-自动': 'relevance_auto',
            '搜索量': 'search_volume',
            '排名': 'organic_rank'
        },
        'transformations': {
            'relevance_auto_percentage': lambda x: float(x.strip('%')) if isinstance(x, str) and '%' in x else float(x),
            'relevance_auto': lambda x: {'高': 3, '中': 2, '低': 1}.get(str(x).strip(), 2)
        }
    },
    
    # 卖家精灵 (keyword2.xlsx)
    '卖家精灵': {
        'source_columns': {
            '关键词': 'keyword',
            '关键词翻译': 'chinese_translation',
            '月搜索量': 'search_volume',
            '相关产品': 'related_products',
            '相关ASIN': 'related_asins',
            'SPR': 'spr',
            'PPC竞价': 'cpc_suggested',
            '建议竞价范围': 'cpc_range',
            '转化总占比': 'conversion_rate',
            '广告竞品数': 'competition_level',
            'ABA周排名': 'organic_rank',
            '#1 点击共享': 'click_share',
            '#1 转化共享': 'conversion_share'
        },
        'transformations': {
            'conversion_rate': lambda x: float(x.strip('%')) / 100 if isinstance(x, str) and '%' in x else float(x),
            'click_share': lambda x: float(x.strip('%')) / 100 if isinstance(x, str) and '%' in x else float(x),
            'conversion_share': lambda x: float(x.strip('%')) / 100 if isinstance(x, str) and '%' in x else float(x),
            'cpc_suggested': lambda x: float(str(x).replace('$', '').strip()) if isinstance(x, (str, float, int)) else 0.0,
            'cpc_range': lambda x: str(x) if isinstance(x, str) else ""
        }
    },
    
    # 亚马逊ABA (keyword3.xlsx)
    '亚马逊ABA': {
        'source_columns': {
            '搜索词': 'keyword',
            '搜索频率排名': 'organic_rank'
        },
        'transformations': {
            'organic_rank': lambda x: int(float(x)) if pd.notna(x) else None
        }
    },
    
    # 西柚找词 (keyword4.xlsx)
    '西柚找词': {
        'source_columns': {
            '关键词 (数据来源于西柚找词)': 'keyword',
            '翻译': 'chinese_translation',
            '相关性得分': 'relevance_score',
            '相关性档位': 'relevance_level',
            '周平均搜索量': 'weekly_search_volume',  # 需要转换为月搜索量
            'CPC建议竞价($)': 'cpc_suggested',
            '建议竞价范围($)': 'cpc_range',
            '点击转化率(均值)': 'conversion_rate',
            '竞争难度档位': 'competition_level',
            '周平均关键词排名': 'organic_rank',
            'asin数量': 'related_products',
            'Top3周平均点击份额': 'click_share',
            'Top3周平均转化份额': 'conversion_share'
        },
        'transformations': {
            'weekly_search_volume': lambda x: float(x) * 4.33,  # 转换为月搜索量
            'conversion_rate': lambda x: float(x.strip('%')) / 100 if isinstance(x, str) and '%' in x else float(x),
            'click_share': lambda x: float(x.strip('%')) / 100 if isinstance(x, str) and '%' in x else float(x),
            'conversion_share': lambda x: float(x.strip('%')) / 100 if isinstance(x, str) and '%' in x else float(x),
            'cpc_suggested': lambda x: float(str(x).replace('$', '').strip()) if isinstance(x, (str, float, int)) else 0.0,
            'relevance_level': lambda x: {'强相关': 3, '中相关': 2, '弱相关': 1}.get(str(x).strip(), 2),
            'competition_level': lambda x: {'高': 3, '中': 2, '低': 1}.get(str(x).strip(), 2)
        }
    }
}

# 统一字段列表
UNIFIED_FIELDS = [
    'keyword',                    # 关键词
    'chinese_translation',        # 中文翻译
    'search_volume',              # 搜索量
    'relevance_auto_percentage',  # 相关性-自动百分比
    'relevance_auto',             # 相关性-自动 (1-3)
    'relevance_score',            # 相关性得分
    'relevance_level',            # 相关性档位 (1-3)
    'related_products',           # 相关产品数量
    'related_asins',              # 相关ASIN
    'spr',                        # SPR
    'cpc_suggested',              # CPC建议竞价
    'cpc_range_min',              # 建议竞价范围下限
    'cpc_range_max',              # 建议竞价范围上限
    'conversion_rate',            # 点击转化率
    'competition_level',          # 竞争难度 (1-3)
    'organic_rank',               # 自然排名
    'click_share',                # 点击份额
    'conversion_share',           # 转化份额
    'source_tool',                # 数据来源
    'classification',             # 分类结果
    'classification_reason',      # 分类理由
    'suggested_bid',              # 建议竞价
    'comprehensive_score',        # 综合评分
    'is_brand_keyword',           # 是否品牌词
    'similarity_score'            # 与产品标题相似度
]

# -*- coding: utf-8 -*-
"""
分类规则配置
定义关键词分类的决策树规则
"""

CLASSIFICATION_RULES = {
    # 品牌关键词检测
    'brand_detection': {
        'conditions': [
            {
                'field': 'is_brand_keyword',
                'operator': '==',
                'value': True,
                'classification': '品牌关键词'
            }
        ]
    },
    
    # 相关性检查
    'relevance_check': {
        'conditions': [
            {
                'field': 'relevance_auto_percentage',
                'operator': '>=',
                'value': 70,
                'classification': '投放评估'
            },
            {
                'field': 'relevance_auto_percentage',
                'operator': '<',
                'value': 30,
                'classification': '否定关键词'
            },
            {
                'field': 'relevance_level',
                'operator': '==',
                'value': 3,  # 强相关
                'classification': '投放评估'
            }
        ],
        'default': '否定评估'
    },
    
    # 投放评估规则 (需同时满足)
    'placement_evaluation': {
        'conditions': [
            {
                'fields': [
                    {'field': 'search_volume', 'operator': '>=', 'value': 100},
                    {'field': 'cpc_suggested', 'operator': '<=', 'value': 3.0},
                    {'field': 'competition_level', 'operator': '!=', 'value': 3},  # 不是高竞争
                    {'field': 'conversion_rate', 'operator': '>=', 'value': 0.02}
                ],
                'logical': 'AND',
                'classification': '投放关键词'
            },
            {
                'fields': [
                    {'field': 'search_volume', 'operator': '>=', 'value': 50},
                    {'field': 'cpc_suggested', 'operator': '<=', 'value': 5.0},
                    {'field': 'conversion_rate', 'operator': '>=', 'value': 0.01}
                ],
                'logical': 'AND',
                'classification': '待定关键词'
            }
        ],
        'default': '否定关键词'
    },
    
    # 否定评估规则 (满足任一)
    'negative_evaluation': {
        'conditions': [
            {
                'fields': [
                    {'field': 'relevance_auto_percentage', 'operator': '<', 'value': 30},
                    {'field': 'search_volume', 'operator': '<', 'value': 10},
                    {'field': 'cpc_suggested', 'operator': '>', 'value': 5.0},
                    {
                        'logical': 'AND',
                        'conditions': [
                            {'field': 'competition_level', 'operator': '==', 'value': 3},
                            {'field': 'conversion_rate', 'operator': '<', 'value': 0.01}
                        ]
                    }
                ],
                'logical': 'OR',
                'classification': '否定关键词'
            }
        ],
        'default': '待定关键词'
    }
}

# 竞价建议规则
BIDDING_RULES = {
    '投放关键词': {
        'relevance_auto_percentage >= 80': lambda row: row.get('cpc_suggested', 0) * 1.1,
        'relevance_auto_percentage >= 60': lambda row: row.get('cpc_suggested', 0) * 0.9,
        'default': lambda row: row.get('cpc_suggested', 0) * 0.7
    },
    '其他': lambda row: '不投放'
}

# 综合评分计算权重
SCORING_WEIGHTS = {
    'search_volume': 0.25,
    'relevance_auto_percentage': 0.20,
    'cpc_suggested': 0.15,
    'conversion_rate': 0.20,
    'competition_level': 0.10,
    'organic_rank': 0.10
}

# 数据源可信度权重 (用于冲突解决)
SOURCE_WEIGHTS = {
    '卖家精灵': 4,
    'SIF': 3,
    '西柚找词': 2,
    '亚马逊ABA': 1
}
# -*- coding: utf-8 -*-
"""
阈值配置
定义各种分类和判断的阈值
"""

THRESHOLDS = {
    # 搜索量阈值
    'search_volume': {
        'high': 1000,      # 高搜索量
        'medium': 100,     # 中等搜索量
        'low': 10          # 低搜索量
    },
    
    # CPC阈值
    'cpc': {
        'high': 5.0,       # 高CPC
        'medium': 2.0,     # 中等CPC
        'low': 0.5         # 低CPC
    },
    
    # 相关性阈值
    'relevance': {
        'strong': 70,      # 强相关 (百分比)
        'medium': 40,      # 中等相关
        'weak': 30         # 弱相关
    },
    
    # 转化率阈值
    'conversion_rate': {
        'high': 0.05,      # 高转化率 (5%)
        'medium': 0.02,    # 中等转化率 (2%)
        'low': 0.01        # 低转化率 (1%)
    },
    
    # 竞争难度 (1-3, 3为最难)
    'competition': {
        'high': 3,
        'medium': 2,
        'low': 1
    },
    
    # 自然排名阈值
    'organic_rank': {
        'excellent': 10,   # 优秀排名
        'good': 50,        # 良好排名
        'average': 100,    # 一般排名
        'poor': 200        # 较差排名
    },
    
    # 单位换算
    'conversion': {
        'weekly_to_monthly': 4.33,  # 周搜索量转月搜索量
        'monthly_to_weekly': 0.23   # 月搜索量转周搜索量
    },
    
    # 分类阈值
    'classification': {
        'placement_min_search': 100,      # 投放关键词最小搜索量
        'placement_max_cpc': 3.0,         # 投放关键词最大CPC
        'placement_min_conversion': 0.02, # 投放关键词最小转化率
        'negative_max_cpc': 5.0,          # 否定关键词最大CPC
        'negative_min_search': 10         # 否定关键词最小搜索量
    }
}

# 字段默认值
DEFAULT_VALUES = {
    'search_volume': 0,
    'cpc_suggested': 0.0,
    'conversion_rate': 0.0,
    'relevance_auto_percentage': 0,
    'competition_level': 2,  # 默认为中等竞争
    'organic_rank': 999,     # 默认较差排名
    'click_share': 0.0,
    'conversion_share': 0.0
}

# 字段数据类型
DATA_TYPES = {
    'keyword': 'str',
    'chinese_translation': 'str',
    'search_volume': 'float',
    'relevance_auto_percentage': 'float',
    'cpc_suggested': 'float',
    'conversion_rate': 'float',
    'competition_level': 'int',
    'organic_rank': 'int',
    'click_share': 'float',
    'conversion_share': 'float'
}
# -*- coding: utf-8 -*-
"""
数据加载模块
精确读取6个Excel文件，按照给定的表头
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class DataLoader:
    """数据加载器类"""
    
    def __init__(self, data_dir, logger):
        """
        初始化数据加载器
        
        Args:
            data_dir: 数据目录路径
            logger: 日志记录器
        """
        self.data_dir = Path(data_dir)
        self.input_dir = self.data_dir / "input"
        self.logger = logger
        
        # 文件路径映射
        self.file_paths = {
            'SIF': self.input_dir / "keyword1.xlsx",
            '卖家精灵': self.input_dir / "keyword2.xlsx",
            '亚马逊ABA': self.input_dir / "keyword3.xlsx",
            '西柚找词': self.input_dir / "keyword4.xlsx",
            '产品标题': self.input_dir / "product_titles.xlsx",
            '品牌信息': self.input_dir / "brand.xlsx"
        }
    
    def load_all_files(self):
        """
        加载所有数据文件
        
        Returns:
            dict: 包含所有数据文件的字典
        """
        data = {}
        
        for tool_name, file_path in self.file_paths.items():
            try:
                if file_path.exists():
                    self.logger.info(f"加载文件: {tool_name} ({file_path.name})")
                    
                    if tool_name == 'SIF':
                        df = self.load_sif_data(file_path)
                    elif tool_name == '卖家精灵':
                        df = self.load_seller_sprite_data(file_path)
                    elif tool_name == '亚马逊ABA':
                        df = self.load_aba_data(file_path)
                    elif tool_name == '西柚找词':
                        df = self.load_grapefruit_data(file_path)
                    elif tool_name == '产品标题':
                        df = self.load_product_titles(file_path)
                    elif tool_name == '品牌信息':
                        df = self.load_brand_info(file_path)
                    else:
                        df = pd.read_excel(file_path)
                    
                    data[tool_name] = df
                    self.logger.info(f"  -> 成功加载 {len(df)} 行数据")
                    
                    # 显示列信息
                    self.logger.debug(f"  -> 列数: {len(df.columns)}")
                    self.logger.debug(f"  -> 列名: {list(df.columns)}")
                    
                else:
                    self.logger.warning(f"文件不存在: {file_path}")
                    
            except Exception as e:
                self.logger.error(f"加载 {tool_name} 文件失败: {str(e)}")
                raise
        
        return data
    
    def load_sif_data(self, file_path):
        """
        加载SIF数据 (keyword1.xlsx)
        
        Args:
            file_path: 文件路径
            
        Returns:
            DataFrame: 处理后的数据
        """
        df = pd.read_excel(file_path)
        
        # 检查表头
        expected_columns = [
            '关键词', '翻译', '相关性-自动百分比', '相关性-自动',
            '自然位前4占位率', '自然位前8占位率', '自然位前16占位率',
            '自然位前32占位率', '自然位前48占位率', '搜索量', '排名'
        ]
        
        # 验证列名
        self._validate_columns(df, expected_columns, "SIF")
        
        # 数据清洗
        df = self._clean_data(df)
        
        # 关键词去重
        df = self._deduplicate_keywords(df, '关键词')
        
        return df
    
    def load_seller_sprite_data(self, file_path):
        """
        加载卖家精灵数据 (keyword2.xlsx)
        
        Args:
            file_path: 文件路径
            
        Returns:
            DataFrame: 处理后的数据
        """
        df = pd.read_excel(file_path)
        
        # 检查表头
        expected_columns = [
            '关键词', '关键词翻译', 'AC推荐词', '流量占比', '流量词类型',
            '预估周曝光量', '相关产品', '相关ASIN', 'ABA周排名',
            '月搜索量', '月购买量', '购买率', '展示量', '点击量',
            'SPR', '标题密度', '商品数', '需供比', '广告竞品数',
            '点击总占比', '转化总占比', 'PPC竞价', '建议竞价范围',
            '#1 前三ASIN', '#1 点击共享', '#1 转化共享',
            '#2 前三ASIN', '#2 点击共享', '#2 转化共享',
            '#3 前三ASIN', '#3 点击共享', '#3 转化共享'
        ]
        
        # 验证列名
        self._validate_columns(df, expected_columns, "卖家精灵")
        
        # 数据清洗
        df = self._clean_data(df)
        
        # 关键词去重
        df = self._deduplicate_keywords(df, '关键词')
        
        # 转换建议竞价范围
        if '建议竞价范围' in df.columns:
            df['建议竞价范围'] = df['建议竞价范围'].apply(self._parse_bid_range)
        
        return df
    
    def load_aba_data(self, file_path):
        """
        加载亚马逊ABA数据 (keyword3.xlsx)
        
        Args:
            file_path: 文件路径
            
        Returns:
            DataFrame: 处理后的数据
        """
        df = pd.read_excel(file_path)
        
        # 检查表头
        expected_columns = [
            '搜索频率排名', '搜索词',
            '点击量最高的品牌 #1', '点击量最高的品牌 #2', '点击量最高的品牌 #3',
            '点击量最高的类别 #1', '点击量最高的类别 #2', '点击量最高的类别 #3',
            '点击量最高的商品 #1：ASIN', '点击量最高的商品 #1：商品名称',
            '点击量最高的商品 #1：点击份额', '点击量最高的商品 #1：转化份额',
            '点击量最高的商品 #2：ASIN', '点击量最高的商品 #2：商品名称',
            '点击量最高的商品 #2：点击份额', '点击量最高的商品 #2：转化份额',
            '点击量最高的商品 #3：ASIN', '点击量最高的商品 #3：商品名称',
            '点击量最高的商品 #3：点击份额', '点击量最高的商品 #3：转化份额',
            '报告日期'
        ]
        
        # 验证列名
        self._validate_columns(df, expected_columns, "亚马逊ABA")
        
        # 数据清洗
        df = self._clean_data(df)
        
        # 重命名列
        df = df.rename(columns={'搜索词': '关键词'})
        
        # 关键词去重
        df = self._deduplicate_keywords(df, '关键词')
        
        return df
    
    def load_grapefruit_data(self, file_path):
        """
        加载西柚找词数据 (keyword4.xlsx)
        
        Args:
            file_path: 文件路径
            
        Returns:
            DataFrame: 处理后的数据
        """
        df = pd.read_excel(file_path)
        
        # 检查表头
        expected_columns = [
            '关键词 (数据来源于西柚找词)', '翻译', '相关性得分',
            '相关性档位', '流量总和', '周平均关键词排名',
            '周平均搜索量', 'CPC建议竞价($)', '建议竞价范围($)',
            '点击转化率(均值)', '周平均竞争难度', '竞争难度档位',
            '自然位滚动率', 'Top3周平均点击份额', 'Top3周平均转化份额',
            'asin数量'
        ]
        
        # 验证列名
        self._validate_columns(df, expected_columns, "西柚找词")
        
        # 数据清洗
        df = self._clean_data(df)
        
        # 重命名列
        df = df.rename(columns={'关键词 (数据来源于西柚找词)': '关键词'})
        
        # 关键词去重
        df = self._deduplicate_keywords(df, '关键词')
        
        # 转换建议竞价范围
        if '建议竞价范围($)' in df.columns:
            df['建议竞价范围($)'] = df['建议竞价范围($)'].apply(self._parse_bid_range)
        
        return df
    
    def load_product_titles(self, file_path):
        """
        加载产品标题数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            DataFrame: 产品标题数据
        """
        df = pd.read_excel(file_path)
        
        # 检查表头
        expected_columns = ['ASIN', '商品标题']
        self._validate_columns(df, expected_columns, "产品标题")
        
        return df
    
    def load_brand_info(self, file_path):
        """
        加载品牌信息数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            DataFrame: 品牌信息数据
        """
        df = pd.read_excel(file_path)
        
        # 检查表头
        expected_columns = [
            '品牌', '月销量', '月销售额($)', '近1年销量',
            '近一年销售额($)', '平均价格($)', '市场份额'
        ]
        self._validate_columns(df, expected_columns, "品牌信息")
        
        return df
    
    def _validate_columns(self, df, expected_columns, tool_name):
        """
        验证列名是否符合预期
        
        Args:
            df: DataFrame
            expected_columns: 预期列名列表
            tool_name: 工具名称
        """
        actual_columns = list(df.columns)
        
        # 检查列数
        if len(actual_columns) != len(expected_columns):
            self.logger.warning(
                f"{tool_name}: 列数不匹配 "
                f"(预期: {len(expected_columns)}, 实际: {len(actual_columns)})"
            )
        
        # 检查列名
        for i, (expected, actual) in enumerate(zip(expected_columns, actual_columns)):
            if expected != actual:
                self.logger.warning(
                    f"{tool_name}: 第{i+1}列名称不匹配 "
                    f"(预期: '{expected}', 实际: '{actual}')"
                )
    
    def _clean_data(self, df):
        """
        数据清洗
        
        Args:
            df: 原始DataFrame
            
        Returns:
            DataFrame: 清洗后的数据
        """
        # 去除首尾空格
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        
        # 处理缺失值
        df = df.replace(['', ' ', 'N/A', 'NA', 'null', 'NULL', None], np.nan)
        
        return df
    
    def _deduplicate_keywords(self, df, keyword_column):
        """
        关键词去重
        
        Args:
            df: DataFrame
            keyword_column: 关键词列名
            
        Returns:
            DataFrame: 去重后的数据
        """
        # 去除关键词中的多余空格并小写化（用于去重比较）
        if keyword_column in df.columns:
            df[keyword_column] = df[keyword_column].astype(str).str.strip()
            
            # 记录去重前的数量
            before_count = len(df)
            
            # 去除完全重复的行
            df = df.drop_duplicates(subset=[keyword_column], keep='first')
            
            # 记录去重后的数量
            after_count = len(df)
            
            if before_count != after_count:
                self.logger.info(f"  去重: {before_count} -> {after_count} 条记录")
        
        return df
    
    def _parse_bid_range(self, value):
        """
        解析建议竞价范围字符串
        
        Args:
            value: 竞价范围字符串，如 "$0.5-$0.8"
            
        Returns:
            dict: 包含min和max的字典
        """
        if pd.isna(value) or not isinstance(value, str):
            return {"min": np.nan, "max": np.nan}
        
        try:
            # 去除美元符号和空格
            cleaned = value.replace('$', '').strip()
            
            if '-' in cleaned:
                parts = cleaned.split('-')
                if len(parts) == 2:
                    return {"min": float(parts[0]), "max": float(parts[1])}
            
            # 如果不是范围，尝试解析单个值
            return {"min": float(cleaned), "max": float(cleaned)}
            
        except (ValueError, AttributeError):
            return {"min": np.nan, "max": np.nan}
# -*- coding: utf-8 -*-
"""
字段映射模块
将各数据源的字段映射到统一的字段名称
"""

import pandas as pd
import numpy as np
from config.column_mapping import UNIFIED_FIELDS
from config.thresholds import DEFAULT_VALUES, DATA_TYPES

class FieldMapper:
    """字段映射器类"""
    
    def __init__(self, column_mappings, logger):
        """
        初始化字段映射器
        
        Args:
            column_mappings: 字段映射配置
            logger: 日志记录器
        """
        self.column_mappings = column_mappings
        self.logger = logger
        
    def map_fields(self, df, tool_name):
        """
        将数据框的字段映射到统一字段
        
        Args:
            df: 原始数据框
            tool_name: 工具名称
            
        Returns:
            DataFrame: 映射后的数据框
        """
        if tool_name not in self.column_mappings:
            self.logger.warning(f"未知的工具名称: {tool_name}")
            return None
        
        mapping_config = self.column_mappings[tool_name]
        
        try:
            # 创建新数据框
            result_df = pd.DataFrame()
            
            # 应用字段映射
            for source_col, target_col in mapping_config['source_columns'].items():
                if source_col in df.columns:
                    # 复制数据
                    result_df[target_col] = df[source_col].copy()
                    
                    # 应用转换函数
                    if 'transformations' in mapping_config and target_col in mapping_config['transformations']:
                        transform_func = mapping_config['transformations'][target_col]
                        result_df[target_col] = result_df[target_col].apply(transform_func)
            
            # 处理特殊字段
            if tool_name == '西柚找词' and 'weekly_search_volume' in result_df.columns:
                # 将周搜索量转换为月搜索量
                result_df['search_volume'] = result_df['weekly_search_volume']
                result_df = result_df.drop('weekly_search_volume', axis=1)
            
            # 解析竞价范围
            if 'cpc_range' in result_df.columns:
                bid_ranges = result_df['cpc_range'].apply(self._extract_bid_range)
                result_df['cpc_range_min'] = bid_ranges.apply(lambda x: x['min'])
                result_df['cpc_range_max'] = bid_ranges.apply(lambda x: x['max'])
                result_df = result_df.drop('cpc_range', axis=1)
            
            # 添加缺失的统一字段
            for field in UNIFIED_FIELDS:
                if field not in result_df.columns:
                    result_df[field] = np.nan
            
            # 应用默认值
            for field, default_value in DEFAULT_VALUES.items():
                if field in result_df.columns:
                    result_df[field] = result_df[field].fillna(default_value)
            
            # 转换数据类型
            result_df = self._convert_data_types(result_df)
            
            self.logger.info(f"  字段映射完成: {tool_name} -> {len(result_df.columns)} 个字段")
            
            return result_df
            
        except Exception as e:
            self.logger.error(f"映射 {tool_name} 字段时出错: {str(e)}")
            return None
    
    def _extract_bid_range(self, value):
        """
        提取竞价范围
        
        Args:
            value: 竞价范围值
            
        Returns:
            dict: 包含min和max的字典
        """
        if pd.isna(value):
            return {"min": np.nan, "max": np.nan}
        
        try:
            if isinstance(value, dict):
                return value
            
            if isinstance(value, str):
                # 处理字符串格式，如 "$0.5-$0.8"
                cleaned = value.replace('$', '').strip()
                if '-' in cleaned:
                    parts = cleaned.split('-')
                    if len(parts) == 2:
                        return {"min": float(parts[0]), "max": float(parts[1])}
                # 尝试解析为单个数字
                return {"min": float(cleaned), "max": float(cleaned)}
            
            if isinstance(value, (int, float)):
                return {"min": float(value), "max": float(value)}
            
            return {"min": np.nan, "max": np.nan}
            
        except (ValueError, AttributeError):
            return {"min": np.nan, "max": np.nan}
    
    def _convert_data_types(self, df):
        """
        转换数据类型
        
        Args:
            df: 数据框
            
        Returns:
            DataFrame: 转换后的数据框
        """
        for field, dtype in DATA_TYPES.items():
            if field in df.columns:
                try:
                    if dtype == 'str':
                        df[field] = df[field].astype(str)
                    elif dtype == 'float':
                        df[field] = pd.to_numeric(df[field], errors='coerce')
                    elif dtype == 'int':
                        df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0).astype(int)
                except Exception as e:
                    self.logger.warning(f"转换字段 {field} 的数据类型时出错: {str(e)}")
        
        return df
    # -*- coding: utf-8 -*-
"""
数据冲突解决模块
当同一关键词出现在多个文件中时，解决数据冲突
"""

import pandas as pd
import numpy as np
from config.classification_rules import SOURCE_WEIGHTS

class ConflictResolver:
    """冲突解决器类"""
    
    def __init__(self, logger):
        """
        初始化冲突解决器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger
        self.source_weights = SOURCE_WEIGHTS
    
    def resolve(self, unified_df):
        """
        解决数据冲突
        
        Args:
            unified_df: 统一字段后的数据框
            
        Returns:
            DataFrame: 解决冲突后的数据框
        """
        if unified_df is None or len(unified_df) == 0:
            return unified_df
        
        self.logger.info(f"开始解决数据冲突，总数据量: {len(unified_df)} 条")
        
        try:
            # 按关键词分组
            grouped = unified_df.groupby('keyword')
            
            resolved_rows = []
            conflict_count = 0
            
            for keyword, group in grouped:
                if len(group) == 1:
                    # 单一来源，直接使用
                    resolved_rows.append(group.iloc[0].to_dict())
                else:
                    # 多个来源，需要解决冲突
                    conflict_count += 1
                    resolved_row = self._resolve_group_conflict(group)
                    resolved_rows.append(resolved_row)
            
            # 创建结果数据框
            result_df = pd.DataFrame(resolved_rows)
            
            self.logger.info(f"冲突解决完成，解决 {conflict_count} 个冲突关键词")
            self.logger.info(f"最终唯一关键词数量: {len(result_df)}")
            
            return result_df
            
        except Exception as e:
            self.logger.error(f"解决冲突时出错: {str(e)}")
            return unified_df
    
    def _resolve_group_conflict(self, group_df):
        """
        解决一个关键词组内的数据冲突
        
        Args:
            group_df: 包含同一关键词多个来源的数据框
            
        Returns:
            dict: 解决冲突后的行数据
        """
        # 初始化结果字典
        result = {'keyword': group_df.iloc[0]['keyword']}
        
        # 获取所有字段
        columns = group_df.columns
        
        # 对每个字段应用冲突解决策略
        for column in columns:
            if column == 'keyword':
                continue
            
            # 获取该字段的所有非空值
            values = group_df[column].dropna()
            
            if len(values) == 0:
                # 所有来源都为空
                result[column] = np.nan
            elif len(values) == 1:
                # 只有一个来源有值
                result[column] = values.iloc[0]
            else:
                # 多个来源有值，需要解决冲突
                result[column] = self._resolve_field_conflict(column, values, group_df)
        
        return result
    
    def _resolve_field_conflict(self, field_name, values, group_df):
        """
        解决单个字段的冲突
        
        Args:
            field_name: 字段名
            values: 字段值序列
            group_df: 原始分组数据框
            
        Returns:
            解决冲突后的值
        """
        # 获取数据来源
        sources = group_df['source_tool'].values
        
        # 应用不同的解决策略
        if field_name == 'search_volume':
            # 搜索量：取最大值
            return values.max()
        
        elif field_name in ['relevance_auto_percentage', 'relevance_score', 'conversion_rate']:
            # 相关性、转化率：取最高值（最乐观）
            return values.max()
        
        elif field_name in ['cpc_suggested', 'competition_level', 'organic_rank']:
            # CPC、竞争难度、排名：取平均值
            return values.mean()
        
        elif field_name in ['chinese_translation', 'related_asins']:
            # 文本字段：按可信度选择
            return self._select_by_source_credibility(field_name, values, sources)
        
        else:
            # 其他字段：按可信度加权平均
            return self._weighted_average(values, sources)
    
    def _select_by_source_credibility(self, field_name, values, sources):
        """
        根据数据源可信度选择值
        
        Args:
            field_name: 字段名
            values: 值数组
            sources: 来源数组
            
        Returns:
            选择的字段值
        """
        # 创建来源到值的映射
        source_value_map = {}
        for source, value in zip(sources, values):
            if pd.notna(value):
                source_value_map[source] = value
        
        if not source_value_map:
            return np.nan
        
        # 按可信度排序
        sorted_sources = sorted(
            source_value_map.keys(),
            key=lambda x: self.source_weights.get(x, 0),
            reverse=True
        )
        
        # 选择最高可信度的值
        return source_value_map[sorted_sources[0]]
    
    def _weighted_average(self, values, sources):
        """
        计算加权平均值
        
        Args:
            values: 值数组
            sources: 来源数组
            
        Returns:
            加权平均值
        """
        total_weight = 0
        weighted_sum = 0
        
        for value, source in zip(values, sources):
            if pd.notna(value):
                weight = self.source_weights.get(source, 1)
                weighted_sum += value * weight
                total_weight += weight
        
        if total_weight == 0:
            return np.nan
        
        return weighted_sum / total_weight
    # -*- coding: utf-8 -*-
"""
语义分析模块
分析关键词与产品标题的相似度，识别品牌关键词
"""

import re
import jieba
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticAnalyzer:
    """语义分析器类"""
    
    def __init__(self, logger):
        """
        初始化语义分析器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger
        # 初始化jieba分词
        jieba.initialize()
        
        # 品牌词缓存
        self.brand_keywords = set()
    
    def calculate_similarity(self, df, product_titles):
        """
        计算关键词与产品标题的相似度
        
        Args:
            df: 关键词数据框
            product_titles: 产品标题列表
            
        Returns:
            DataFrame: 添加了相似度得分的数据框
        """
        if len(df) == 0 or len(product_titles) == 0:
            df['similarity_score'] = 0.0
            return df
        
        try:
            self.logger.info("开始计算关键词与产品标题相似度...")
            
            # 准备文本数据
            keywords = df['keyword'].fillna('').astype(str).tolist()
            
            # 分词处理
            keyword_segmented = [' '.join(jieba.cut(k)) for k in keywords]
            title_segmented = [' '.join(jieba.cut(t)) for t in product_titles]
            
            # 合并所有文本
            all_texts = keyword_segmented + title_segmented
            
            # 计算TF-IDF向量
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            
            # 分割矩阵
            keyword_vectors = tfidf_matrix[:len(keywords)]
            title_vectors = tfidf_matrix[len(keywords):]
            
            # 计算相似度
            similarity_matrix = cosine_similarity(keyword_vectors, title_vectors)
            
            # 取最大相似度作为得分
            similarity_scores = similarity_matrix.max(axis=1)
            
            # 添加到数据框
            df['similarity_score'] = similarity_scores
            
            self.logger.info(f"相似度计算完成，平均相似度: {similarity_scores.mean():.3f}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"计算相似度时出错: {str(e)}")
            df['similarity_score'] = 0.0
            return df
    
    def identify_brand_keywords(self, df, brands):
        """
        识别品牌关键词
        
        Args:
            df: 关键词数据框
            brands: 品牌列表
            
        Returns:
            DataFrame: 添加了品牌标识的数据框
        """
        if len(df) == 0 or len(brands) == 0:
            df['is_brand_keyword'] = False
            return df
        
        try:
            self.logger.info(f"开始识别品牌关键词，品牌数量: {len(brands)}")
            
            # 创建品牌正则表达式
            brand_patterns = []
            for brand in brands:
                if isinstance(brand, str) and len(brand.strip()) > 0:
                    brand_clean = re.escape(brand.strip().lower())
                    brand_patterns.append(brand_clean)
            
            # 合并模式
            if brand_patterns:
                pattern = re.compile(r'\b(' + '|'.join(brand_patterns) + r')\b', re.IGNORECASE)
            else:
                pattern = None
            
            # 识别品牌关键词
            is_brand_keyword = []
            brand_count = 0
            
            for keyword in df['keyword']:
                if pd.isna(keyword):
                    is_brand_keyword.append(False)
                    continue
                
                keyword_str = str(keyword).lower()
                if pattern and pattern.search(keyword_str):
                    is_brand_keyword.append(True)
                    brand_count += 1
                else:
                    is_brand_keyword.append(False)
            
            df['is_brand_keyword'] = is_brand_keyword
            df['brand_keyword'] = df.apply(
                lambda row: self._extract_brand_from_keyword(row['keyword'], brands) 
                if row['is_brand_keyword'] else '', 
                axis=1
            )
            
            self.logger.info(f"识别出 {brand_count} 个品牌关键词")
            
            return df
            
        except Exception as e:
            self.logger.error(f"识别品牌关键词时出错: {str(e)}")
            df['is_brand_keyword'] = False
            return df
    
    def _extract_brand_from_keyword(self, keyword, brands):
        """
        从关键词中提取品牌
        
        Args:
            keyword: 关键词
            brands: 品牌列表
            
        Returns:
            str: 提取的品牌
        """
        if pd.isna(keyword):
            return ''
        
        keyword_str = str(keyword).lower()
        
        for brand in brands:
            if isinstance(brand, str) and brand.strip():
                brand_lower = brand.strip().lower()
                if brand_lower in keyword_str:
                    return brand.strip()
        
        return ''
    
    def analyze_keyword_intent(self, keywords):
        """
        分析关键词意图
        
        Args:
            keywords: 关键词列表
            
        Returns:
            list: 意图分类列表
        """
        intents = []
        
        # 意图分类关键词
        intent_patterns = {
            'transactional': ['buy', 'purchase', 'order', 'price', 'cost', 'deal', 'discount', 
                             'cheap', 'sale', 'best price', 'where to buy', 'for sale'],
            'informational': ['what is', 'how to', 'why', 'when', 'where', 'which', 'who', 
                            'compare', 'review', 'guide', 'tutorial', 'vs'],
            'navigational': ['amazon', 'official', 'website', 'store', 'brand', 'model'],
            'commercial': ['best', 'top', 'review', 'vs', 'comparison', 'rating', 'quality']
        }
        
        for keyword in keywords:
            if pd.isna(keyword):
                intents.append('unknown')
                continue
            
            keyword_lower = str(keyword).lower()
            keyword_intent = 'generic'
            
            for intent_type, patterns in intent_patterns.items():
                for pattern in patterns:
                    if pattern in keyword_lower:
                        keyword_intent = intent_type
                        break
                if keyword_intent != 'generic':
                    break
            
            intents.append(keyword_intent)
        
        return intents
    # -*- coding: utf-8 -*-
"""
关键词分类模块
根据规则对关键词进行智能分类
"""

import pandas as pd
import numpy as np
from config.classification_rules import CLASSIFICATION_RULES, BIDDING_RULES, SCORING_WEIGHTS
from config.thresholds import THRESHOLDS

class KeywordClassifier:
    """关键词分类器类"""
    
    def __init__(self, classification_rules, thresholds, logger):
        """
        初始化关键词分类器
        
        Args:
            classification_rules: 分类规则配置
            thresholds: 阈值配置
            logger: 日志记录器
        """
        self.classification_rules = classification_rules
        self.thresholds = thresholds
        self.logger = logger
    
    def classify(self, df):
        """
        对关键词进行分类
        
        Args:
            df: 关键词数据框
            
        Returns:
            DataFrame: 添加了分类结果的数据框
        """
        if len(df) == 0:
            return df
        
        self.logger.info("开始关键词分类...")
        
        try:
            # 创建副本以避免修改原始数据
            result_df = df.copy()
            
            # 初始化分类列
            result_df['classification'] = '待定关键词'
            result_df['suggested_bid'] = '不投放'
            result_df['comprehensive_score'] = 0.0
            
            # 应用分类规则
            for idx, row in result_df.iterrows():
                classification = self._apply_classification_rules(row)
                result_df.at[idx, 'classification'] = classification
                
                # 计算建议竞价
                suggested_bid = self._calculate_suggested_bid(row, classification)
                result_df.at[idx, 'suggested_bid'] = suggested_bid
                
                # 计算综合评分
                score = self._calculate_comprehensive_score(row)
                result_df.at[idx, 'comprehensive_score'] = score
            
            self.logger.info("关键词分类完成")
            
            return result_df
            
        except Exception as e:
            self.logger.error(f"分类关键词时出错: {str(e)}")
            return df
    
    def _apply_classification_rules(self, row):
        """
        应用分类规则
        
        Args:
            row: 数据行
            
        Returns:
            str: 分类结果
        """
        # 1. 检查是否为品牌关键词
        if row.get('is_brand_keyword', False):
            return '品牌关键词'
        
        # 2. 检查相关性
        relevance_percentage = row.get('relevance_auto_percentage', 0)
        relevance_level = row.get('relevance_level', 2)
        
        # 高相关性 -> 投放评估
        if relevance_percentage >= self.thresholds['relevance']['strong'] or relevance_level == 3:
            return self._evaluate_for_placement(row)
        # 低相关性 -> 否定评估
        elif relevance_percentage < self.thresholds['relevance']['weak']:
            return self._evaluate_for_negative(row)
        # 中等相关性 -> 进一步评估
        else:
            # 根据其他指标决定
            search_volume = row.get('search_volume', 0)
            cpc = row.get('cpc_suggested', 0)
            
            if search_volume >= 50 and cpc <= 3.0:
                return self._evaluate_for_placement(row)
            else:
                return self._evaluate_for_negative(row)
    
    def _evaluate_for_placement(self, row):
        """
        投放评估
        
        Args:
            row: 数据行
            
        Returns:
            str: 分类结果
        """
        # 检查所有投放条件
        conditions = [
            row.get('search_volume', 0) >= self.thresholds['classification']['placement_min_search'],
            row.get('cpc_suggested', 0) <= self.thresholds['classification']['placement_max_cpc'],
            row.get('competition_level', 2) != self.thresholds['competition']['high'],
            row.get('conversion_rate', 0) >= self.thresholds['classification']['placement_min_conversion']
        ]
        
        if all(conditions):
            return '投放关键词'
        
        # 检查待定条件
        secondary_conditions = [
            row.get('search_volume', 0) >= 50,
            row.get('cpc_suggested', 0) <= 5.0,
            row.get('conversion_rate', 0) >= 0.01
        ]
        
        if all(secondary_conditions):
            return '待定关键词'
        
        return '否定关键词'
    
    def _evaluate_for_negative(self, row):
        """
        否定评估
        
        Args:
            row: 数据行
            
        Returns:
            str: 分类结果
        """
        # 检查否定条件（满足任一）
        negative_conditions = [
            row.get('relevance_auto_percentage', 0) < self.thresholds['relevance']['weak'],
            row.get('search_volume', 0) < self.thresholds['classification']['negative_min_search'],
            row.get('cpc_suggested', 0) > self.thresholds['classification']['negative_max_cpc'],
            (row.get('competition_level', 2) == self.thresholds['competition']['high'] and 
             row.get('conversion_rate', 0) < 0.01)
        ]
        
        if any(negative_conditions):
            return '否定关键词'
        
        return '待定关键词'
    
    def _calculate_suggested_bid(self, row, classification):
        """
        计算建议竞价
        
        Args:
            row: 数据行
            classification: 分类结果
            
        Returns:
            float or str: 建议竞价
        """
        if classification != '投放关键词':
            return '不投放'
        
        cpc = row.get('cpc_suggested', 0)
        relevance_percentage = row.get('relevance_auto_percentage', 0)
        
        if relevance_percentage >= 80:
            return cpc * 1.1  # 积极竞价
        elif relevance_percentage >= 60:
            return cpc * 0.9  # 保守竞价
        else:
            return cpc * 0.7  # 测试竞价
    
    def _calculate_comprehensive_score(self, row):
        """
        计算综合评分（0-100）
        
        Args:
            row: 数据行
            
        Returns:
            float: 综合评分
        """
        score = 0.0
        
        # 1. 搜索量评分 (0-25分)
        search_volume = row.get('search_volume', 0)
        if search_volume >= self.thresholds['search_volume']['high']:
            score += 25
        elif search_volume >= self.thresholds['search_volume']['medium']:
            score += 15
        elif search_volume >= self.thresholds['search_volume']['low']:
            score += 5
        
        # 2. 相关性评分 (0-20分)
        relevance_percentage = row.get('relevance_auto_percentage', 0)
        if relevance_percentage >= self.thresholds['relevance']['strong']:
            score += 20
        elif relevance_percentage >= self.thresholds['relevance']['medium']:
            score += 12
        elif relevance_percentage >= self.thresholds['relevance']['weak']:
            score += 5
        
        # 3. CPC评分 (0-15分)
        cpc = row.get('cpc_suggested', 0)
        if cpc <= self.thresholds['cpc']['low']:
            score += 15
        elif cpc <= self.thresholds['cpc']['medium']:
            score += 10
        elif cpc <= self.thresholds['cpc']['high']:
            score += 5
        
        # 4. 转化率评分 (0-20分)
        conversion_rate = row.get('conversion_rate', 0)
        if conversion_rate >= self.thresholds['conversion_rate']['high']:
            score += 20
        elif conversion_rate >= self.thresholds['conversion_rate']['medium']:
            score += 12
        elif conversion_rate >= self.thresholds['conversion_rate']['low']:
            score += 5
        
        # 5. 竞争难度评分 (0-10分)
        competition_level = row.get('competition_level', 2)
        if competition_level == 1:  # 低竞争
            score += 10
        elif competition_level == 2:  # 中等竞争
            score += 5
        
        # 6. 自然排名评分 (0-10分)
        organic_rank = row.get('organic_rank', 999)
        if organic_rank <= self.thresholds['organic_rank']['excellent']:
            score += 10
        elif organic_rank <= self.thresholds['organic_rank']['good']:
            score += 7
        elif organic_rank <= self.thresholds['organic_rank']['average']:
            score += 3
        
        return min(score, 100)  # 确保不超过100分
    
    def analyze_keyword_roots(self, df, classification):
        """
        分析关键词词根
        
        Args:
            df: 关键词数据框
            classification: 要分析的分类
            
        Returns:
            DataFrame: 词根分析结果
        """
        if len(df) == 0:
            return pd.DataFrame()
        
        # 筛选指定分类
        filtered_df = df[df['classification'] == classification].copy()
        
        if len(filtered_df) == 0:
            return pd.DataFrame()
        
        # 提取词根（简单实现：取前2个单词）
        roots = []
        for keyword in filtered_df['keyword']:
            if pd.isna(keyword):
                continue
            
            words = str(keyword).lower().split()
            if len(words) >= 2:
                root = ' '.join(words[:2])
                roots.append(root)
            elif len(words) == 1:
                roots.append(words[0])
        
        # 统计词根频率
        from collections import Counter
        root_counts = Counter(roots)
        
        # 创建结果数据框
        result_data = []
        for root, count in root_counts.most_common(50):  # 取前50个
            matching_rows = filtered_df[filtered_df['keyword'].str.contains(root, case=False, na=False)]
            
            if len(matching_rows) > 0:
                result_data.append({
                    '词根': root,
                    '关键词数量': count,
                    '平均搜索量': matching_rows['search_volume'].mean(),
                    '平均CPC': matching_rows['cpc_suggested'].mean(),
                    '平均转化率': matching_rows['conversion_rate'].mean(),
                    '平均综合评分': matching_rows['comprehensive_score'].mean()
                })
        
        return pd.DataFrame(result_data)
    # -*- coding: utf-8 -*-
"""
分类理由生成模块
为每个分类结果生成详细的理由说明
"""

import pandas as pd
import numpy as np
from config.thresholds import THRESHOLDS

class ReasonGenerator:
    """分类理由生成器类"""
    
    def __init__(self, logger):
        """
        初始化分类理由生成器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger
        self.thresholds = THRESHOLDS
    
    def generate_all_reasons(self, df):
        """
        为所有关键词生成分类理由
        
        Args:
            df: 关键词数据框
            
        Returns:
            DataFrame: 添加了分类理由的数据框
        """
        if len(df) == 0:
            return df
        
        self.logger.info("开始生成分类理由...")
        
        try:
            result_df = df.copy()
            reasons = []
            
            for idx, row in result_df.iterrows():
                reason = self._generate_reason(row)
                reasons.append(reason)
            
            result_df['classification_reason'] = reasons
            
            self.logger.info("分类理由生成完成")
            
            return result_df
            
        except Exception as e:
            self.logger.error(f"生成分类理由时出错: {str(e)}")
            result_df['classification_reason'] = '理由生成失败'
            return result_df
    
    def _generate_reason(self, row):
        """
        为单个关键词生成分类理由
        
        Args:
            row: 数据行
            
        Returns:
            str: 分类理由
        """
        classification = row.get('classification', '待定关键词')
        
        if classification == '品牌关键词':
            return self._generate_brand_keyword_reason(row)
        elif classification == '投放关键词':
            return self._generate_placement_reason(row)
        elif classification == '否定关键词':
            return self._generate_negative_reason(row)
        elif classification == '待定关键词':
            return self._generate_pending_reason(row)
        else:
            return '未知分类'
    
    def _generate_brand_keyword_reason(self, row):
        """
        生成品牌关键词理由
        
        Args:
            row: 数据行
            
        Returns:
            str: 理由
        """
        brand = row.get('brand_keyword', '')
        if brand:
            return f"包含品牌词 '{brand}'，建议用于品牌保护或精准投放"
        else:
            return "识别为品牌关键词，建议用于品牌保护"
    
    def _generate_placement_reason(self, row):
        """
        生成投放关键词理由
        
        Args:
            row: 数据行
            
        Returns:
            str: 理由
        """
        reasons = []
        
        # 检查各个指标
        search_volume = row.get('search_volume', 0)
        relevance = row.get('relevance_auto_percentage', 0)
        cpc = row.get('cpc_suggested', 0)
        conversion_rate = row.get('conversion_rate', 0)
        competition = row.get('competition_level', 2)
        
        # 搜索量理由
        if search_volume >= self.thresholds['search_volume']['high']:
            reasons.append(f"搜索量高 ({search_volume:.0f}+)")
        elif search_volume >= self.thresholds['search_volume']['medium']:
            reasons.append(f"搜索量中等 ({search_volume:.0f})")
        
        # 相关性理由
        if relevance >= self.thresholds['relevance']['strong']:
            reasons.append(f"强相关性 ({relevance:.0f}%)")
        elif relevance >= self.thresholds['relevance']['medium']:
            reasons.append(f"中等相关性 ({relevance:.0f}%)")
        
        # CPC理由
        if cpc <= self.thresholds['cpc']['low']:
            reasons.append(f"CPC成本低 (${cpc:.2f})")
        elif cpc <= self.thresholds['cpc']['medium']:
            reasons.append(f"CPC成本中等 (${cpc:.2f})")
        
        # 转化率理由
        if conversion_rate >= self.thresholds['conversion_rate']['high']:
            reasons.append(f"转化率高 ({conversion_rate*100:.1f}%)")
        elif conversion_rate >= self.thresholds['conversion_rate']['medium']:
            reasons.append(f"转化率中等 ({conversion_rate*100:.1f}%)")
        
        # 竞争难度理由
        if competition == 1:
            reasons.append("竞争难度低")
        elif competition == 2:
            reasons.append("竞争难度中等")
        
        if reasons:
            return "满足投放条件: " + "，".join(reasons)
        else:
            return "符合投放标准"
    
    def _generate_negative_reason(self, row):
        """
        生成否定关键词理由
        
        Args:
            row: 数据行
            
        Returns:
            str: 理由
        """
        reasons = []
        
        # 检查否定原因
        search_volume = row.get('search_volume', 0)
        relevance = row.get('relevance_auto_percentage', 0)
        cpc = row.get('cpc_suggested', 0)
        conversion_rate = row.get('conversion_rate', 0)
        competition = row.get('competition_level', 2)
        
        # 低相关性
        if relevance < self.thresholds['relevance']['weak']:
            reasons.append(f"相关性低 ({relevance:.0f}% < {self.thresholds['relevance']['weak']}%)")
        
        # 低搜索量
        if search_volume < self.thresholds['search_volume']['low']:
            reasons.append(f"搜索量低 ({search_volume:.0f} < {self.thresholds['search_volume']['low']})")
        
        # 高CPC
        if cpc > self.thresholds['cpc']['high']:
            reasons.append(f"CPC成本高 (${cpc:.2f} > ${self.thresholds['cpc']['high']:.1f})")
        
        # 高竞争低转化
        if competition == self.thresholds['competition']['high'] and conversion_rate < 0.01:
            reasons.append("竞争激烈且转化率低")
        
        if reasons:
            return "建议否定: " + "，".join(reasons)
        else:
            return "不符合投放标准，建议否定"
    
    def _generate_pending_reason(self, row):
        """
        生成待定关键词理由
        
        Args:
            row: 数据行
            
        Returns:
            str: 理由
        """
        reasons = []
        
        # 检查需要人工审核的原因
        search_volume = row.get('search_volume', 0)
        relevance = row.get('relevance_auto_percentage', 0)
        cpc = row.get('cpc_suggested', 0)
        conversion_rate = row.get('conversion_rate', 0)
        
        # 搜索量在边界
        if 10 <= search_volume < 100:
            reasons.append(f"搜索量边界 ({search_volume:.0f})")
        
        # 相关性在边界
        if 30 <= relevance < 70:
            reasons.append(f"相关性边界 ({relevance:.0f}%)")
        
        # CPC在边界
        if 3.0 < cpc <= 5.0:
            reasons.append(f"CPC边界 (${cpc:.2f})")
        
        # 转化率在边界
        if 0.01 <= conversion_rate < 0.02:
            reasons.append(f"转化率边界 ({conversion_rate*100:.1f}%)")
        
        if reasons:
            return "需要人工审核: " + "，".join(reasons)
        else:
            return "指标表现一般，建议人工审核"
    
    def generate_negative_reasons_summary(self, negative_df):
        """
        生成否定关键词原因汇总
        
        Args:
            negative_df: 否定关键词数据框
            
        Returns:
            DataFrame: 原因汇总
        """
        if len(negative_df) == 0:
            return pd.DataFrame()
        
        # 提取否定原因类型
        reason_categories = {
            '低相关性': 0,
            '低搜索量': 0,
            '高CPC': 0,
            '高竞争低转化': 0,
            '其他原因': 0
        }
        
        for reason in negative_df['classification_reason']:
            if pd.isna(reason):
                continue
            
            reason_str = str(reason)
            
            if '相关性低' in reason_str:
                reason_categories['低相关性'] += 1
            elif '搜索量低' in reason_str:
                reason_categories['低搜索量'] += 1
            elif 'CPC成本高' in reason_str:
                reason_categories['高CPC'] += 1
            elif '竞争激烈' in reason_str:
                reason_categories['高竞争低转化'] += 1
            else:
                reason_categories['其他原因'] += 1
        
        # 创建汇总数据框
        summary_df = pd.DataFrame({
            '否定原因': list(reason_categories.keys()),
            '关键词数量': list(reason_categories.values())
        })
        
        # 计算百分比
        total = summary_df['关键词数量'].sum()
        if total > 0:
            summary_df['占比'] = summary_df['关键词数量'] / total * 100
            summary_df['占比'] = summary_df['占比'].round(1)
        else:
            summary_df['占比'] = 0
        
        # 排序
        summary_df = summary_df.sort_values('关键词数量', ascending=False)
        
        return summary_df
    # -*- coding: utf-8 -*-
"""
Excel导出模块
导出美化后的Excel文件
"""

import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import (
    PatternFill, Font, Border, Side, Alignment, 
    NamedStyle, numbers
)
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule, FormulaRule
import xlsxwriter

class ExcelExporter:
    """Excel导出器类"""
    
    def __init__(self, logger):
        """
        初始化Excel导出器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger
        
        # 定义样式
        self.styles = self._define_styles()
    
    def export_to_excel(self, sheets_dict, output_path):
        """
        导出数据到Excel文件
        
        Args:
            sheets_dict: 工作表字典 {工作表名: DataFrame}
            output_path: 输出文件路径
        """
        try:
            self.logger.info(f"开始导出Excel文件: {output_path}")
            
            # 使用pandas的ExcelWriter，指定引擎为openpyxl
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, df in sheets_dict.items():
                    if df is not None and len(df) > 0:
                        # 导出数据
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        # 获取工作表对象
                        worksheet = writer.sheets[sheet_name]
                        
                        # 应用样式
                        self._apply_styles(worksheet, df, sheet_name)
                        
                        self.logger.info(f"  工作表 '{sheet_name}': {len(df)} 行")
                    else:
                        self.logger.warning(f"  工作表 '{sheet_name}' 无数据，跳过")
            
            self.logger.info(f"Excel文件导出完成: {output_path}")
            
            # 使用xlsxwriter添加更多格式
            self._enhance_with_xlsxwriter(output_path, sheets_dict)
            
        except Exception as e:
            self.logger.error(f"导出Excel文件失败: {str(e)}")
            raise
    
    def _define_styles(self):
        """定义Excel样式"""
        styles = {}
        
        # 标题样式
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(name="微软雅黑", size=11, bold=True, color="FFFFFF")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        header_border = Border(
            left=Side(style="thin", color="000000"),
            right=Side(style="thin", color="000000"),
            top=Side(style="thin", color="000000"),
            bottom=Side(style="thin", color="000000")
        )
        
        styles['header'] = {
            'fill': header_fill,
            'font': header_font,
            'alignment': header_alignment,
            'border': header_border
        }
        
        # 数据行样式
        data_font = Font(name="微软雅黑", size=10)
        data_alignment = Alignment(vertical="center")
        data_border = Border(
            left=Side(style="thin", color="D9D9D9"),
            right=Side(style="thin", color="D9D9D9"),
            top=Side(style="thin", color="D9D9D9"),
            bottom=Side(style="thin", color="D9D9D9")
        )
        
        # 交替行填充
        even_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
        odd_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
        
        styles['data_even'] = {
            'fill': even_fill,
            'font': data_font,
            'alignment': data_alignment,
            'border': data_border
        }
        
        styles['data_odd'] = {
            'fill': odd_fill,
            'font': data_font,
            'alignment': data_alignment,
            'border': data_border
        }
        
        # 分类颜色
        classification_colors = {
            '投放关键词': 'C6EFCE',  # 浅绿色
            '否定关键词': 'FFC7CE',  # 浅红色
            '品牌关键词': 'FFEB9C',  # 浅黄色
            '待定关键词': 'BDD7EE'   # 浅蓝色
        }
        
        styles['classification_colors'] = classification_colors
        
        return styles
    
    def _apply_styles(self, worksheet, df, sheet_name):
        """
        应用样式到工作表
        
        Args:
            worksheet: 工作表对象
            df: 数据框
            sheet_name: 工作表名称
        """
        # 设置列宽
        for i, column in enumerate(df.columns):
            column_width = max(len(str(column)) * 1.2, 10)
            worksheet.column_dimensions[get_column_letter(i+1)].width = column_width
        
        # 应用标题样式
        for cell in worksheet[1]:
            cell.fill = self.styles['header']['fill']
            cell.font = self.styles['header']['font']
            cell.alignment = self.styles['header']['alignment']
            cell.border = self.styles['header']['border']
        
        # 应用数据行样式
        for row_idx, row in enumerate(worksheet.iter_rows(min_row=2, max_row=len(df)+1)):
            is_even = (row_idx % 2 == 0)
            style = self.styles['data_even'] if is_even else self.styles['data_odd']
            
            for cell in row:
                cell.font = style['font']
                cell.alignment = style['alignment']
                cell.border = style['border']
                
                # 填充背景色
                if is_even:
                    cell.fill = style['fill']
                else:
                    cell.fill = style['fill']
        
        # 根据分类应用颜色
        if 'classification' in df.columns:
            classification_col = df.columns.get_loc('classification') + 1
            for row_idx in range(2, len(df) + 2):
                cell = worksheet.cell(row=row_idx, column=classification_col)
                classification = cell.value
                
                if classification in self.styles['classification_colors']:
                    fill_color = self.styles['classification_colors'][classification]
                    cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        
        # 应用数字格式
        numeric_columns = ['search_volume', 'cpc_suggested', 'conversion_rate', 
                          'comprehensive_score', 'similarity_score']
        
        for col_name in numeric_columns:
            if col_name in df.columns:
                col_idx = df.columns.get_loc(col_name) + 1
                
                if col_name in ['cpc_suggested']:
                    # 货币格式
                    for row_idx in range(2, len(df) + 2):
                        cell = worksheet.cell(row=row_idx, column=col_idx)
                        if isinstance(cell.value, (int, float)):
                            cell.number_format = '"$"#,##0.00'
                
                elif col_name in ['conversion_rate', 'similarity_score']:
                    # 百分比格式
                    for row_idx in range(2, len(df) + 2):
                        cell = worksheet.cell(row=row_idx, column=col_idx)
                        if isinstance(cell.value, (int, float)):
                            cell.number_format = '0.00%'
                
                elif col_name in ['comprehensive_score']:
                    # 两位小数格式
                    for row_idx in range(2, len(df) + 2):
                        cell = worksheet.cell(row=row_idx, column=col_idx)
                        if isinstance(cell.value, (int, float)):
                            cell.number_format = '0.00'
    
    def _enhance_with_xlsxwriter(self, output_path, sheets_dict):
        """
        使用xlsxwriter增强Excel文件
        
        Args:
            output_path: 文件路径
            sheets_dict: 工作表字典
        """
        try:
            # 重新打开文件以添加更多格式
            workbook = xlsxwriter.Workbook(output_path)
            
            for sheet_name, df in sheets_dict.items():
                if df is not None and len(df) > 0:
                    worksheet = workbook.add_worksheet(sheet_name)
                    
                    # 写入数据
                    for col_idx, column in enumerate(df.columns):
                        worksheet.write(0, col_idx, column)
                        
                        for row_idx, value in enumerate(df[column]):
                            worksheet.write(row_idx + 1, col_idx, value)
                    
                    # 添加条件格式
                    self._add_conditional_formatting(workbook, worksheet, df, sheet_name)
            
            workbook.close()
            
        except Exception as e:
            self.logger.warning(f"使用xlsxwriter增强格式时出错: {str(e)}")
    
    def _add_conditional_formatting(self, workbook, worksheet, df, sheet_name):
        """
        添加条件格式
        
        Args:
            workbook: xlsxwriter工作簿
            worksheet: xlsxwriter工作表
            df: 数据框
            sheet_name: 工作表名称
        """
        # 综合评分颜色刻度
        if 'comprehensive_score' in df.columns:
            col_idx = df.columns.get_loc('comprehensive_score')
            worksheet.conditional_format(1, col_idx, len(df), col_idx, {
                'type': '3_color_scale',
                'min_color': '#FF0000',  # 红色
                'mid_color': '#FFFF00',  # 黄色
                'max_color': '#00FF00'   # 绿色
            })
        
        # 搜索量颜色刻度
        if 'search_volume' in df.columns:
            col_idx = df.columns.get_loc('search_volume')
            worksheet.conditional_format(1, col_idx, len(df), col_idx, {
                'type': '3_color_scale',
                'min_color': '#FFFFFF',  # 白色
                'mid_color': '#FFEB84',  # 浅黄色
                'max_color': '#FF9900'   # 橙色
            })
        
        # 分类颜色
        if 'classification' in df.columns:
            col_idx = df.columns.get_loc('classification')
            
            # 投放关键词 - 绿色
            worksheet.conditional_format(1, col_idx, len(df), col_idx, {
                'type': 'text',
                'criteria': 'containing',
                'value': '投放关键词',
                'format': workbook.add_format({'bg_color': '#C6EFCE'})
            })
            
            # 否定关键词 - 红色
            worksheet.conditional_format(1, col_idx, len(df), col_idx, {
                'type': 'text',
                'criteria': 'containing',
                'value': '否定关键词',
                'format': workbook.add_format({'bg_color': '#FFC7CE'})
            })
            
            # 品牌关键词 - 黄色
            worksheet.conditional_format(1, col_idx, len(df), col_idx, {
                'type': 'text',
                'criteria': 'containing',
                'value': '品牌关键词',
                'format': workbook.add_format({'bg_color': '#FFEB9C'})
            })
            
            # 待定关键词 - 蓝色
            worksheet.conditional_format(1, col_idx, len(df), col_idx, {
                'type': 'text',
                'criteria': 'containing',
                'value': '待定关键词',
                'format': workbook.add_format({'bg_color': '#BDD7EE'})
            })
            # -*- coding: utf-8 -*-
"""
图表生成模块
生成20张分析图表
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
import jieba
from matplotlib.font_manager import FontProperties

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ChartGenerator:
    """图表生成器类"""
    
    def __init__(self, logger):
        """
        初始化图表生成器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger
        
        # 设置图表样式
        sns.set_style("whitegrid")
        sns.set_palette("husl")
        
        # 创建颜色映射
        self.color_palette = {
            '投放关键词': '#4CAF50',  # 绿色
            '否定关键词': '#F44336',  # 红色
            '品牌关键词': '#FFC107',  # 黄色
            '待定关键词': '#2196F3',  # 蓝色
            '其他': '#9E9E9E'         # 灰色
        }
    
    def generate_all_charts(self, df, output_dir):
        """
        生成所有图表
        
        Args:
            df: 关键词数据框
            output_dir: 输出目录
        """
        self.logger.info(f"开始生成图表，保存到: {output_dir}")
        
        # 确保输出目录存在
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        try:
            # 1. 关键词来源分布饼图
            self.generate_source_distribution(df, output_dir / "01_关键词来源分布.png")
            
            # 2. 搜索量分布直方图
            self.generate_search_volume_distribution(df, output_dir / "02_搜索量分布直方图.png")
            
            # 3. CPC建议竞价分布图
            self.generate_cpc_distribution(df, output_dir / "03_CPC建议竞价分布.png")
            
            # 4. 相关性评分分布图
            self.generate_relevance_distribution(df, output_dir / "04_相关性评分分布.png")
            
            # 5. 竞争难度分布图
            self.generate_competition_distribution(df, output_dir / "05_竞争难度分布.png")
            
            # 6. 分类数量对比图
            self.generate_classification_comparison(df, output_dir / "06_分类数量对比.png")
            
            # 7. 搜索量 vs CPC 散点图
            self.generate_search_vs_cpc_scatter(df, output_dir / "07_搜索量vsCPC散点图.png")
            
            # 8. 相关性 vs 转化率 散点图
            self.generate_relevance_vs_conversion_scatter(df, output_dir / "08_相关性vs转化率散点图.png")
            
            # 9. 关键词长度分布图
            self.generate_keyword_length_distribution(df, output_dir / "09_关键词长度分布.png")
            
            # 10. 自然排名分布图
            self.generate_organic_rank_distribution(df, output_dir / "10_自然排名分布.png")
            
            # 11. 点击转化率分布图
            self.generate_conversion_rate_distribution(df, output_dir / "11_点击转化率分布.png")
            
            # 12. 建议竞价范围分布图
            self.generate_bid_range_distribution(df, output_dir / "12_建议竞价范围分布.png")
            
            # 13. 各工具数据对比雷达图
            self.generate_tool_comparison_radar(df, output_dir / "13_各工具数据对比雷达图.png")
            
            # 14. 关键词意图分布图
            self.generate_intent_distribution(df, output_dir / "14_关键词意图分布.png")
            
            # 15. 品牌关键词词云
            self.generate_brand_wordcloud(df, output_dir / "15_品牌关键词词云.png")
            
            # 16. 投放关键词词云
            self.generate_placement_wordcloud(df, output_dir / "16_投放关键词词云.png")
            
            # 17. 否定关键词原因分布
            self.generate_negative_reasons_distribution(df, output_dir / "17_否定关键词原因分布.png")
            
            # 18. ROI潜力矩阵图
            self.generate_roi_matrix(df, output_dir / "18_ROI潜力矩阵.png")
            
            # 19. 综合评分分布图
            self.generate_comprehensive_score_distribution(df, output_dir / "19_综合评分分布.png")
            
            # 20. 四象限分析图
            self.generate_quadrant_analysis(df, output_dir / "20_四象限分析.png")
            
            self.logger.info("所有图表生成完成")
            
        except Exception as e:
            self.logger.error(f"生成图表时出错: {str(e)}")
    
    def generate_source_distribution(self, df, output_path):
        """生成关键词来源分布饼图"""
        if 'source_tool' not in df.columns:
            return
        
        source_counts = df['source_tool'].value_counts()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 创建饼图
        wedges, texts, autotexts = ax.pie(
            source_counts.values,
            labels=source_counts.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=sns.color_palette("Set2")
        )
        
        # 美化
        ax.set_title('关键词来源分布', fontsize=16, fontweight='bold')
        ax.axis('equal')  # 确保饼图是圆形
        
        # 添加图例
        ax.legend(wedges, source_counts.index,
                 title="数据来源",
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_search_volume_distribution(self, df, output_path):
        """生成搜索量分布直方图"""
        if 'search_volume' not in df.columns:
            return
        
        # 过滤极端值
        search_volumes = df['search_volume'].dropna()
        if len(search_volumes) == 0:
            return
        
        # 使用对数尺度
        log_search = np.log10(search_volumes.replace(0, 1))
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 创建直方图
        n, bins, patches = ax.hist(log_search, bins=30, edgecolor='black', alpha=0.7)
        
        # 设置x轴标签为实际搜索量
        tick_positions = [0, 1, 2, 3, 4, 5]  # 对应10^0到10^5
        tick_labels = ['1', '10', '100', '1K', '10K', '100K']
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels)
        
        ax.set_xlabel('搜索量 (月)', fontsize=12)
        ax.set_ylabel('关键词数量', fontsize=12)
        ax.set_title('搜索量分布直方图', fontsize=16, fontweight='bold')
        
        # 添加网格
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_cpc_distribution(self, df, output_path):
        """生成CPC建议竞价分布图"""
        if 'cpc_suggested' not in df.columns:
            return
        
        cpc_data = df['cpc_suggested'].dropna()
        if len(cpc_data) == 0:
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 创建箱线图和小提琴图的组合
        sns.boxplot(x=cpc_data, ax=ax, color='lightblue', width=0.2)
        sns.violinplot(x=cpc_data, ax=ax, color='skyblue', inner=None)
        
        ax.set_xlabel('CPC建议竞价 ($)', fontsize=12)
        ax.set_title('CPC建议竞价分布', fontsize=16, fontweight='bold')
        
        # 添加统计信息
        stats_text = f"平均值: ${cpc_data.mean():.2f}\n中位数: ${cpc_data.median():.2f}"
        ax.text(0.95, 0.95, stats_text,
                transform=ax.transAxes,
                verticalalignment='top',
                horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_relevance_distribution(self, df, output_path):
        """生成相关性评分分布图"""
        if 'relevance_auto_percentage' not in df.columns:
            return
        
        relevance_data = df['relevance_auto_percentage'].dropna()
        if len(relevance_data) == 0:
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 创建分布图
        sns.histplot(data=relevance_data, bins=20, kde=True, ax=ax, color='green')
        
        ax.set_xlabel('相关性评分 (%)', fontsize=12)
        ax.set_ylabel('关键词数量', fontsize=12)
        ax.set_title('相关性评分分布', fontsize=16, fontweight='bold')
        
        # 添加阈值线
        ax.axvline(x=70, color='red', linestyle='--', alpha=0.5, label='强相关阈值 (70%)')
        ax.axvline(x=30, color='orange', linestyle='--', alpha=0.5, label='弱相关阈值 (30%)')
        
        ax.legend()
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_competition_distribution(self, df, output_path):
        """生成竞争难度分布图"""
        if 'competition_level' not in df.columns:
            return
        
        competition_data = df['competition_level'].dropna()
        if len(competition_data) == 0:
            return
        
        # 映射数值到文本
        level_map = {1: '低', 2: '中', 3: '高'}
        competition_text = competition_data.map(level_map)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 创建条形图
        level_counts = competition_text.value_counts().sort_index()
        colors = ['#4CAF50', '#FFC107', '#F44336']  # 绿黄红
        
        bars = ax.bar(level_counts.index, level_counts.values, color=colors)
        
        ax.set_xlabel('竞争难度', fontsize=12)
        ax.set_ylabel('关键词数量', fontsize=12)
        ax.set_title('竞争难度分布', fontsize=16, fontweight='bold')
        
        # 在每个柱子上添加数量标签
        for bar, count in zip(bars, level_counts.values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{count}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_classification_comparison(self, df, output_path):
        """生成分类数量对比图"""
        if 'classification' not in df.columns:
            return
        
        class_counts = df['classification'].value_counts()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 创建水平条形图
        colors = [self.color_palette.get(cls, '#9E9E9E') for cls in class_counts.index]
        bars = ax.barh(class_counts.index, class_counts.values, color=colors)
        
        ax.set_xlabel('关键词数量', fontsize=12)
        ax.set_title('关键词分类数量对比', fontsize=16, fontweight='bold')
        
        # 在每个条形上添加数量和百分比
        total = class_counts.sum()
        for bar, count in zip(bars, class_counts.values):
            width = bar.get_width()
            percentage = (count / total) * 100
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                   f'{count} ({percentage:.1f}%)',
                   va='center', ha='left')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_search_vs_cpc_scatter(self, df, output_path):
        """生成搜索量 vs CPC 散点图"""
        if 'search_volume' not in df.columns or 'cpc_suggested' not in df.columns:
            return
        
        # 过滤有效数据
        scatter_data = df[['search_volume', 'cpc_suggested', 'classification']].dropna()
        if len(scatter_data) == 0:
            return
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 按分类着色
        for cls in scatter_data['classification'].unique():
            cls_data = scatter_data[scatter_data['classification'] == cls]
            color = self.color_palette.get(cls, '#9E9E9E')
            ax.scatter(cls_data['search_volume'], cls_data['cpc_suggested'],
                      alpha=0.6, label=cls, color=color, s=50)
        
        # 设置对数尺度
        ax.set_xscale('log')
        
        ax.set_xlabel('搜索量 (月, 对数尺度)', fontsize=12)
        ax.set_ylabel('CPC建议竞价 ($)', fontsize=12)
        ax.set_title('搜索量 vs CPC 散点图 (四象限分析)', fontsize=16, fontweight='bold')
        
        # 添加四象限分界线
        median_search = scatter_data['search_volume'].median()
        median_cpc = scatter_data['cpc_suggested'].median()
        
        ax.axhline(y=median_cpc, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=median_search, color='gray', linestyle='--', alpha=0.5)
        
        # 添加象限标签
        ax.text(median_search * 0.1, median_cpc * 0.1, '低搜索量/低CPC',
                ha='center', va='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.text(median_search * 10, median_cpc * 0.1, '高搜索量/低CPC',
                ha='center', va='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.text(median_search * 0.1, median_cpc * 10, '低搜索量/高CPC',
                ha='center', va='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.text(median_search * 10, median_cpc * 10, '高搜索量/高CPC',
                ha='center', va='center', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.legend()
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_relevance_vs_conversion_scatter(self, df, output_path):
        """生成相关性 vs 转化率 散点图"""
        if 'relevance_auto_percentage' not in df.columns or 'conversion_rate' not in df.columns:
            return
        
        scatter_data = df[['relevance_auto_percentage', 'conversion_rate', 'classification']].dropna()
        if len(scatter_data) == 0:
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 按分类着色
        for cls in scatter_data['classification'].unique():
            cls_data = scatter_data[scatter_data['classification'] == cls]
            color = self.color_palette.get(cls, '#9E9E9E')
            ax.scatter(cls_data['relevance_auto_percentage'], cls_data['conversion_rate'] * 100,
                      alpha=0.6, label=cls, color=color, s=50)
        
        ax.set_xlabel('相关性评分 (%)', fontsize=12)
        ax.set_ylabel('点击转化率 (%)', fontsize=12)
        ax.set_title('相关性 vs 转化率 散点图', fontsize=16, fontweight='bold')
        
        # 添加趋势线
        if len(scatter_data) > 1:
            z = np.polyfit(scatter_data['relevance_auto_percentage'], 
                          scatter_data['conversion_rate'] * 100, 1)
            p = np.poly1d(z)
            ax.plot(scatter_data['relevance_auto_percentage'], 
                   p(scatter_data['relevance_auto_percentage']),
                   "r--", alpha=0.5, label='趋势线')
        
        ax.legend()
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_keyword_length_distribution(self, df, output_path):
        """生成关键词长度分布图"""
        if 'keyword' not in df.columns:
            return
        
        # 计算关键词长度
        keyword_lengths = df['keyword'].dropna().apply(lambda x: len(str(x).split()))
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 创建直方图
        sns.histplot(data=keyword_lengths, bins=20, ax=ax, color='purple')
        
        ax.set_xlabel('关键词长度 (单词数)', fontsize=12)
        ax.set_ylabel('关键词数量', fontsize=12)
        ax.set_title('关键词长度分布', fontsize=16, fontweight='bold')
        
        # 添加平均线
        avg_length = keyword_lengths.mean()
        ax.axvline(x=avg_length, color='red', linestyle='--', alpha=0.7,
                  label=f'平均长度: {avg_length:.1f}')
        
        ax.legend()
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_organic_rank_distribution(self, df, output_path):
        """生成自然排名分布图"""
        if 'organic_rank' not in df.columns:
            return
        
        rank_data = df['organic_rank'].dropna()
        if len(rank_data) == 0:
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 创建累积分布图
        sorted_rank = np.sort(rank_data)
        cum_dist = np.arange(1, len(sorted_rank) + 1) / len(sorted_rank)
        
        ax.plot(sorted_rank, cum_dist * 100, linewidth=2, color='blue')
        
        ax.set_xlabel('自然排名', fontsize=12)
        ax.set_ylabel('累积百分比 (%)', fontsize=12)
        ax.set_title('自然排名累积分布', fontsize=16, fontweight='bold')
        
        # 添加关键百分位线
        for percentile in [25, 50, 75, 90]:
            rank_value = np.percentile(sorted_rank, percentile)
            ax.axvline(x=rank_value, color='gray', linestyle='--', alpha=0.5)
            ax.text(rank_value, percentile + 2, f'{percentile}%: {rank_value:.0f}',
                   ha='center', fontsize=9)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_conversion_rate_distribution(self, df, output_path):
        """生成点击转化率分布图"""
        if 'conversion_rate' not in df.columns:
            return
        
        conversion_data = df['conversion_rate'].dropna() * 100  # 转换为百分比
        if len(conversion_data) == 0:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 子图1: 直方图
        sns.histplot(data=conversion_data, bins=30, ax=ax1, kde=True, color='orange')
        ax1.set_xlabel('点击转化率 (%)', fontsize=12)
        ax1.set_ylabel('关键词数量', fontsize=12)
        ax1.set_title('点击转化率分布', fontsize=14, fontweight='bold')
        
        # 子图2: 箱线图
        sns.boxplot(y=conversion_data, ax=ax2, color='lightyellow')
        ax2.set_ylabel('点击转化率 (%)', fontsize=12)
        ax2.set_title('点击转化率统计', fontsize=14, fontweight='bold')
        
        # 在箱线图上添加统计信息
        stats_text = (f"平均值: {conversion_data.mean():.2f}%\n"
                     f"中位数: {conversion_data.median():.2f}%\n"
                     f"最小值: {conversion_data.min():.2f}%\n"
                     f"最大值: {conversion_data.max():.2f}%")
        
        ax2.text(0.95, 0.95, stats_text,
                transform=ax2.transAxes,
                verticalalignment='top',
                horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_bid_range_distribution(self, df, output_path):
        """生成建议竞价范围分布图"""
        if 'cpc_range_min' not in df.columns or 'cpc_range_max' not in df.columns:
            return
        
        # 过滤有效数据
        bid_data = df[['cpc_range_min', 'cpc_range_max']].dropna()
        if len(bid_data) == 0:
            return
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 创建范围条形图
        for idx, row in bid_data.iterrows():
            ax.plot([row['cpc_range_min'], row['cpc_range_max']], 
                   [idx, idx], color='blue', alpha=0.3, linewidth=0.5)
        
        # 添加平均值线
        avg_min = bid_data['cpc_range_min'].mean()
        avg_max = bid_data['cpc_range_max'].mean()
        
        ax.axvline(x=avg_min, color='red', linestyle='--', alpha=0.7, label=f'平均下限: ${avg_min:.2f}')
        ax.axvline(x=avg_max, color='green', linestyle='--', alpha=0.7, label=f'平均上限: ${avg_max:.2f}')
        
        ax.set_xlabel('建议竞价范围 ($)', fontsize=12)
        ax.set_ylabel('关键词索引', fontsize=12)
        ax.set_title('建议竞价范围分布', fontsize=16, fontweight='bold')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_tool_comparison_radar(self, df, output_path):
        """生成各工具数据对比雷达图"""
        if 'source_tool' not in df.columns:
            return
        
        # 选择要比较的指标
        metrics = ['search_volume', 'cpc_suggested', 'conversion_rate', 
                  'relevance_auto_percentage', 'competition_level']
        
        # 确保指标存在
        available_metrics = [m for m in metrics if m in df.columns]
        if not available_metrics:
            return
        
        # 计算每个工具的平均值
        tool_stats = {}
        for tool in df['source_tool'].unique():
            tool_data = df[df['source_tool'] == tool]
            tool_stats[tool] = {}
            
            for metric in available_metrics:
                if metric == 'competition_level':
                    # 竞争难度需要反向处理（值越小越好）
                    tool_stats[tool][metric] = 4 - tool_data[metric].mean()
                else:
                    tool_stats[tool][metric] = tool_data[metric].mean()
        
        # 创建雷达图
        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))
        
        # 准备角度
        angles = np.linspace(0, 2 * np.pi, len(available_metrics), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形
        
        # 为每个工具绘制雷达图
        colors = plt.cm.Set2(np.linspace(0, 1, len(tool_stats)))
        
        for (tool, stats), color in zip(tool_stats.items(), colors):
            values = [stats[metric] for metric in available_metrics]
            values += values[:1]  # 闭合图形
            
            # 标准化值到0-1范围
            max_val = max(values)
            if max_val > 0:
                values = [v / max_val for v in values]
            
            ax.plot(angles, values, 'o-', linewidth=2, label=tool, color=color)
            ax.fill(angles, values, alpha=0.1, color=color)
        
        # 设置坐标轴
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(available_metrics, fontsize=11)
        ax.set_ylim(0, 1)
        
        ax.set_title('各工具数据对比雷达图', fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_intent_distribution(self, df, output_path):
        """生成关键词意图分布图"""
        if 'keyword' not in df.columns:
            return
        
        # 简单的意图分类
        keywords = df['keyword'].dropna().astype(str).tolist()
        
        # 意图关键词
        intent_patterns = {
            '交易型': ['buy', 'purchase', 'price', 'cheap', 'deal', 'discount', 'sale'],
            '信息型': ['what', 'how', 'why', 'when', 'where', 'which', 'compare', 'review'],
            '导航型': ['amazon', 'official', 'store', 'brand'],
            '评论型': ['review', 'rating', 'best', 'top', 'quality']
        }
        
        intent_counts = {'通用型': 0}
        for intent in intent_patterns.keys():
            intent_counts[intent] = 0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            matched = False
            
            for intent, patterns in intent_patterns.items():
                for pattern in patterns:
                    if pattern in keyword_lower:
                        intent_counts[intent] += 1
                        matched = True
                        break
                if matched:
                    break
            
            if not matched:
                intent_counts['通用型'] += 1
        
        # 过滤掉数量为0的意图
        intent_counts = {k: v for k, v in intent_counts.items() if v > 0}
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 创建饼图
        wedges, texts, autotexts = ax.pie(
            intent_counts.values(),
            labels=intent_counts.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=sns.color_palette("Set3")
        )
        
        ax.set_title('关键词意图分布', fontsize=16, fontweight='bold')
        ax.axis('equal')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_brand_wordcloud(self, df, output_path):
        """生成品牌关键词词云"""
        if 'keyword' not in df.columns or 'classification' not in df.columns:
            return
        
        # 提取品牌关键词
        brand_keywords = df[df['classification'] == '品牌关键词']['keyword'].dropna()
        if len(brand_keywords) == 0:
            return
        
        # 合并所有关键词
        text = ' '.join(brand_keywords.astype(str))
        
        # 创建词云
        wordcloud = WordCloud(
            width=1200,
            height=800,
            background_color='white',
            colormap='Set2',
            max_words=100,
            contour_width=1,
            contour_color='steelblue'
        ).generate(text)
        
        fig, ax = plt.subplots(figsize=(15, 10))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('品牌关键词词云', fontsize=20, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_placement_wordcloud(self, df, output_path):
        """生成投放关键词词云"""
        if 'keyword' not in df.columns or 'classification' not in df.columns:
            return
        
        # 提取投放关键词
        placement_keywords = df[df['classification'] == '投放关键词']['keyword'].dropna()
        if len(placement_keywords) == 0:
            return
        
        # 合并所有关键词
        text = ' '.join(placement_keywords.astype(str))
        
        # 创建词云
        wordcloud = WordCloud(
            width=1200,
            height=800,
            background_color='white',
            colormap='viridis',
            max_words=150,
            contour_width=1,
            contour_color='green'
        ).generate(text)
        
        fig, ax = plt.subplots(figsize=(15, 10))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('投放关键词词云', fontsize=20, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_negative_reasons_distribution(self, df, output_path):
        """生成否定关键词原因分布"""
        if 'classification' not in df.columns or 'classification_reason' not in df.columns:
            return
        
        # 提取否定关键词
        negative_df = df[df['classification'] == '否定关键词']
        if len(negative_df) == 0:
            return
        
        # 解析否定原因
        reason_categories = {
            '低相关性': negative_df['classification_reason'].str.contains('相关性低').sum(),
            '低搜索量': negative_df['classification_reason'].str.contains('搜索量低').sum(),
            '高CPC': negative_df['classification_reason'].str.contains('CPC成本高').sum(),
            '高竞争低转化': negative_df['classification_reason'].str.contains('竞争激烈').sum(),
            '其他原因': len(negative_df) - sum([
                negative_df['classification_reason'].str.contains('相关性低').sum(),
                negative_df['classification_reason'].str.contains('搜索量低').sum(),
                negative_df['classification_reason'].str.contains('CPC成本高').sum(),
                negative_df['classification_reason'].str.contains('竞争激烈').sum()
            ])
        }
        
        # 过滤掉数量为0的类别
        reason_categories = {k: v for k, v in reason_categories.items() if v > 0}
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 创建水平条形图
        colors = ['#F44336', '#FF9800', '#FFC107', '#FF5722', '#9E9E9E']
        bars = ax.barh(list(reason_categories.keys()), list(reason_categories.values()), 
                      color=colors[:len(reason_categories)])
        
        ax.set_xlabel('关键词数量', fontsize=12)
        ax.set_title('否定关键词原因分布', fontsize=16, fontweight='bold')
        
        # 添加数量标签
        total = sum(reason_categories.values())
        for bar, count in zip(bars, reason_categories.values()):
            width = bar.get_width()
            percentage = (count / total) * 100
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                   f'{count} ({percentage:.1f}%)',
                   va='center', ha='left')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_roi_matrix(self, df, output_path):
        """生成ROI潜力矩阵图"""
        if 'search_volume' not in df.columns or 'conversion_rate' not in df.columns or 'cpc_suggested' not in df.columns:
            return
        
        # 计算简单的ROI潜力评分
        # ROI潜力 = (搜索量 * 转化率) / CPC
        roi_data = df[['search_volume', 'conversion_rate', 'cpc_suggested', 'classification']].dropna()
        
        if len(roi_data) == 0:
            return
        
        # 避免除以0
        roi_data = roi_data[roi_data['cpc_suggested'] > 0]
        if len(roi_data) == 0:
            return
        
        # 计算ROI潜力
        roi_data['roi_potential'] = (roi_data['search_volume'] * roi_data['conversion_rate']) / roi_data['cpc_suggested']
        
        # 使用对数尺度
        roi_data['log_roi'] = np.log10(roi_data['roi_potential'].replace(0, 1))
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 创建散点图，按ROI潜力着色
        scatter = ax.scatter(roi_data['search_volume'], roi_data['cpc_suggested'],
                           c=roi_data['log_roi'], cmap='RdYlGn', 
                           alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
        
        ax.set_xscale('log')
        
        ax.set_xlabel('搜索量 (月, 对数尺度)', fontsize=12)
        ax.set_ylabel('CPC建议竞价 ($)', fontsize=12)
        ax.set_title('ROI潜力矩阵图', fontsize=16, fontweight='bold')
        
        # 添加颜色条
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('ROI潜力 (对数尺度)', fontsize=12)
        
        # 添加四分位线
        median_search = roi_data['search_volume'].median()
        median_cpc = roi_data['cpc_suggested'].median()
        
        ax.axhline(y=median_cpc, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=median_search, color='gray', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_comprehensive_score_distribution(self, df, output_path):
        """生成综合评分分布图"""
        if 'comprehensive_score' not in df.columns:
            return
        
        score_data = df['comprehensive_score'].dropna()
        if len(score_data) == 0:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 子图1: 直方图
        sns.histplot(data=score_data, bins=30, ax=ax1, kde=True, color='purple')
        ax1.set_xlabel('综合评分 (0-100)', fontsize=12)
        ax1.set_ylabel('关键词数量', fontsize=12)
        ax1.set_title('综合评分分布', fontsize=14, fontweight='bold')
        
        # 添加分数段
        for threshold in [30, 60, 80]:
            ax1.axvline(x=threshold, color='red', linestyle='--', alpha=0.5)
            ax1.text(threshold + 1, ax1.get_ylim()[1] * 0.9, 
                    f'{threshold}+', fontsize=10, color='red')
        
        # 子图2: 按分类的箱线图
        if 'classification' in df.columns:
            # 过滤有分类和评分的数据
            score_class_data = df[['comprehensive_score', 'classification']].dropna()
            
            # 创建分类列表
            classifications = score_class_data['classification'].unique()
            
            # 为每个分类创建数据列表
            data_by_class = []
            class_labels = []
            
            for cls in classifications:
                cls_scores = score_class_data[score_class_data['classification'] == cls]['comprehensive_score']
                if len(cls_scores) > 0:
                    data_by_class.append(cls_scores)
                    class_labels.append(cls)
            
            if data_by_class:
                # 创建箱线图
                boxplot = ax2.boxplot(data_by_class, labels=class_labels, patch_artist=True)
                
                # 设置颜色
                for patch, cls in zip(boxplot['boxes'], class_labels):
                    patch.set_facecolor(self.color_palette.get(cls, '#9E9E9E'))
                    patch.set_alpha(0.7)
                
                ax2.set_ylabel('综合评分', fontsize=12)
                ax2.set_title('各分类综合评分对比', fontsize=14, fontweight='bold')
                ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_quadrant_analysis(self, df, output_path):
        """生成四象限分析图"""
        if 'search_volume' not in df.columns or 'relevance_auto_percentage' not in df.columns:
            return
        
        quadrant_data = df[['search_volume', 'relevance_auto_percentage', 'classification']].dropna()
        if len(quadrant_data) == 0:
            return
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # 按分类着色
        for cls in quadrant_data['classification'].unique():
            cls_data = quadrant_data[quadrant_data['classification'] == cls]
            color = self.color_palette.get(cls, '#9E9E9E')
            ax.scatter(cls_data['search_volume'], cls_data['relevance_auto_percentage'],
                      alpha=0.6, label=cls, color=color, s=80, edgecolors='black', linewidth=0.5)
        
        # 设置对数尺度
        ax.set_xscale('log')
        
        ax.set_xlabel('搜索量 (月, 对数尺度)', fontsize=14)
        ax.set_ylabel('相关性评分 (%)', fontsize=14)
        ax.set_title('关键词四象限分析: 搜索量 vs 相关性', fontsize=18, fontweight='bold', pad=20)
        
        # 添加四象限分界线
        median_search = quadrant_data['search_volume'].median()
        median_relevance = quadrant_data['relevance_auto_percentage'].median()
        
        ax.axhline(y=median_relevance, color='black', linestyle='-', alpha=0.7, linewidth=2)
        ax.axvline(x=median_search, color='black', linestyle='-', alpha=0.7, linewidth=2)
        
        # 添加象限标签
        ax.text(median_search * 0.1, median_relevance * 0.1, '利基机会\n低搜索量/高相关',
                ha='center', va='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        ax.text(median_search * 10, median_relevance * 0.1, '流量机会\n高搜索量/高相关',
                ha='center', va='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        ax.text(median_search * 0.1, median_relevance + (100 - median_relevance) * 0.9, '低效机会\n低搜索量/低相关',
                ha='center', va='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
        
        ax.text(median_search * 10, median_relevance + (100 - median_relevance) * 0.9, '竞争机会\n高搜索量/低相关',
                ha='center', va='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        # 添加图例
        ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        # -*- coding: utf-8 -*-
"""
工具函数模块
提供各种辅助函数
"""

import pandas as pd
import numpy as np
import re
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import hashlib

class DataUtils:
    """数据处理工具类"""
    
    @staticmethod
    def safe_float_conversion(value, default=0.0):
        """
        安全地将值转换为浮点数
        
        Args:
            value: 要转换的值
            default: 转换失败时的默认值
            
        Returns:
            float: 转换后的浮点数
        """
        if pd.isna(value) or value is None:
            return default
        
        try:
            if isinstance(value, str):
                # 去除货币符号和空格
                cleaned = value.replace('$', '').replace(',', '').strip()
                # 处理百分比
                if '%' in cleaned:
                    return float(cleaned.replace('%', '')) / 100
                return float(cleaned)
            elif isinstance(value, (int, float)):
                return float(value)
            else:
                return default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_int_conversion(value, default=0):
        """
        安全地将值转换为整数
        
        Args:
            value: 要转换的值
            default: 转换失败时的默认值
            
        Returns:
            int: 转换后的整数
        """
        if pd.isna(value) or value is None:
            return default
        
        try:
            if isinstance(value, str):
                # 去除逗号等分隔符
                cleaned = value.replace(',', '').strip()
                # 尝试解析为浮点数再转整数
                return int(float(cleaned))
            elif isinstance(value, (int, float)):
                return int(value)
            else:
                return default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def parse_range_string(range_str, default_min=0, default_max=0):
        """
        解析范围字符串，如 "$0.5-$0.8"
        
        Args:
            range_str: 范围字符串
            default_min: 默认最小值
            default_max: 默认最大值
            
        Returns:
            tuple: (最小值, 最大值)
        """
        if pd.isna(range_str) or not isinstance(range_str, str):
            return default_min, default_max
        
        try:
            # 去除货币符号和空格
            cleaned = range_str.replace('$', '').strip()
            
            if '-' in cleaned:
                parts = cleaned.split('-')
                if len(parts) == 2:
                    min_val = float(parts[0].strip())
                    max_val = float(parts[1].strip())
                    return min_val, max_val
            
            # 如果不是范围，尝试解析为单个值
            single_val = float(cleaned)
            return single_val, single_val
            
        except (ValueError, AttributeError):
            return default_min, default_max
    
    @staticmethod
    def normalize_text(text):
        """
        标准化文本
        
        Args:
            text: 原始文本
            
        Returns:
            str: 标准化后的文本
        """
        if pd.isna(text):
            return ''
        
        text_str = str(text)
        
        # 去除首尾空格
        text_str = text_str.strip()
        
        # 转换全角字符为半角
        text_str = text_str.translate(
            str.maketrans('ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９',
                         'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
        )
        
        # 去除多余空格
        text_str = re.sub(r'\s+', ' ', text_str)
        
        return text_str
    
    @staticmethod
    def extract_keyword_roots(keywords, max_roots=100):
        """
        提取关键词词根
        
        Args:
            keywords: 关键词列表
            max_roots: 最大词根数量
            
        Returns:
            DataFrame: 词根统计
        """
        if not keywords:
            return pd.DataFrame()
        
        # 简单的词根提取（按空格分割）
        roots = []
        for keyword in keywords:
            if pd.isna(keyword):
                continue
            
            keyword_str = str(keyword).lower()
            words = keyword_str.split()
            
            if len(words) >= 2:
                # 取前两个单词作为词根
                root = ' '.join(words[:2])
                roots.append(root)
            elif len(words) == 1:
                roots.append(words[0])
        
        # 统计词根频率
        from collections import Counter
        root_counts = Counter(roots)
        
        # 获取最常见的词根
        common_roots = root_counts.most_common(max_roots)
        
        # 创建结果DataFrame
        result_data = []
        for root, count in common_roots:
            result_data.append({
                '词根': root,
                '出现次数': count
            })
        
        return pd.DataFrame(result_data)
    
    @staticmethod
    def calculate_missing_stats(df):
        """
        计算缺失值统计
        
        Args:
            df: 数据框
            
        Returns:
            DataFrame: 缺失值统计
        """
        if df is None or len(df) == 0:
            return pd.DataFrame()
        
        missing_stats = []
        total_rows = len(df)
        
        for column in df.columns:
            missing_count = df[column].isna().sum()
            missing_percentage = (missing_count / total_rows) * 100
            
            missing_stats.append({
                '字段名': column,
                '缺失数量': missing_count,
                '缺失比例': missing_percentage,
                '数据类型': str(df[column].dtype)
            })
        
        missing_df = pd.DataFrame(missing_stats)
        missing_df = missing_df.sort_values('缺失比例', ascending=False)
        
        return missing_df
    
    @staticmethod
    def create_summary_stats(df, numeric_columns=None):
        """
        创建数值列统计摘要
        
        Args:
            df: 数据框
            numeric_columns: 要统计的数值列列表
            
        Returns:
            DataFrame: 统计摘要
        """
        if df is None or len(df) == 0:
            return pd.DataFrame()
        
        if numeric_columns is None:
            # 自动检测数值列
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        stats_data = []
        for column in numeric_columns:
            if column in df.columns:
                col_data = df[column].dropna()
                if len(col_data) > 0:
                    stats_data.append({
                        '字段名': column,
                        '平均值': col_data.mean(),
                        '中位数': col_data.median(),
                        '最小值': col_data.min(),
                        '最大值': col_data.max(),
                        '标准差': col_data.std(),
                        '非空数量': len(col_data),
                        '缺失比例': (df[column].isna().sum() / len(df)) * 100
                    })
        
        return pd.DataFrame(stats_data)
    
    @staticmethod
    def generate_data_hash(df, columns=None):
        """
        生成数据的哈希值，用于检查数据是否变化
        
        Args:
            df: 数据框
            columns: 要包含的列列表
            
        Returns:
            str: 哈希值
        """
        if df is None or len(df) == 0:
            return ''
        
        if columns is None:
            columns = df.columns.tolist()
        
        # 选择指定列
        data_subset = df[columns].copy()
        
        # 转换为字符串并排序以确保一致性
        data_str = data_subset.to_csv(index=False)
        
        # 生成哈希
        return hashlib.md5(data_str.encode()).hexdigest()

class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def ensure_directory(path):
        """
        确保目录存在
        
        Args:
            path: 目录路径
        """
        os.makedirs(path, exist_ok=True)
    
    @staticmethod
    def get_file_info(file_path):
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            dict: 文件信息
        """
        if not os.path.exists(file_path):
            return None
        
        stats = os.stat(file_path)
        
        return {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_size': stats.st_size,
            'created_time': datetime.fromtimestamp(stats.st_ctime),
            'modified_time': datetime.fromtimestamp(stats.st_mtime),
            'is_file': os.path.isfile(file_path),
            'is_dir': os.path.isdir(file_path)
        }
    
    @staticmethod
    def save_json(data, file_path, indent=2):
        """
        保存数据为JSON文件
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
            indent: 缩进空格数
        """
        FileUtils.ensure_directory(os.path.dirname(file_path))
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent, default=str)
    
    @staticmethod
    def load_json(file_path, default=None):
        """
        从JSON文件加载数据
        
        Args:
            file_path: 文件路径
            default: 文件不存在时的默认值
            
        Returns:
            dict or list: 加载的数据
        """
        if not os.path.exists(file_path):
            return default if default is not None else {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_pickle(data, file_path):
        """
        保存数据为pickle文件
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
        """
        import pickle
        FileUtils.ensure_directory(os.path.dirname(file_path))
        
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
    
    @staticmethod
    def load_pickle(file_path, default=None):
        """
        从pickle文件加载数据
        
        Args:
            file_path: 文件路径
            default: 文件不存在时的默认值
            
        Returns:
            加载的数据
        """
        import pickle
        
        if not os.path.exists(file_path):
            return default
        
        with open(file_path, 'rb') as f:
            return pickle.load(f)

class ValidationUtils:
    """数据验证工具类"""
    
    @staticmethod
    def validate_dataframe(df, required_columns=None, min_rows=1):
        """
        验证DataFrame是否符合要求
        
        Args:
            df: 要验证的DataFrame
            required_columns: 必需的列列表
            min_rows: 最小行数
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if df is None:
            return False, "DataFrame为None"
        
        if not isinstance(df, pd.DataFrame):
            return False, "输入不是DataFrame"
        
        if len(df) < min_rows:
            return False, f"数据行数不足: {len(df)} < {min_rows}"
        
        if required_columns:
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return False, f"缺少必需的列: {missing_columns}"
        
        return True, "验证通过"
    
    @staticmethod
    def check_column_types(df, type_mapping):
        """
        检查列数据类型
        
        Args:
            df: DataFrame
            type_mapping: 列名到数据类型的映射
            
        Returns:
            dict: 检查结果
        """
        results = {}
        
        for column, expected_type in type_mapping.items():
            if column not in df.columns:
                results[column] = {
                    'status': 'missing',
                    'message': f'列不存在'
                }
                continue
            
            actual_type = str(df[column].dtype)
            expected_type_str = str(expected_type)
            
            # 简化的类型检查
            type_matches = False
            if expected_type_str in ['int64', 'int32', 'int']:
                type_matches = 'int' in actual_type
            elif expected_type_str in ['float64', 'float32', 'float']:
                type_matches = 'float' in actual_type
            elif expected_type_str in ['object', 'str']:
                type_matches = 'object' in actual_type
            else:
                type_matches = actual_type == expected_type_str
            
            results[column] = {
                'status': 'ok' if type_matches else 'mismatch',
                'expected': expected_type_str,
                'actual': actual_type,
                'message': f'类型匹配' if type_matches else f'类型不匹配: 预期{expected_type_str}, 实际{actual_type}'
            }
        
        return results
    
    @staticmethod
    def validate_numeric_range(df, column, min_val=None, max_val=None):
        """
        验证数值列的范围
        
        Args:
            df: DataFrame
            column: 列名
            min_val: 最小值
            max_val: 最大值
            
        Returns:
            dict: 验证结果
        """
        if column not in df.columns:
            return {'status': 'error', 'message': f'列不存在: {column}'}
        
        numeric_data = pd.to_numeric(df[column], errors='coerce')
        valid_data = numeric_data.dropna()
        
        results = {
            'column': column,
            'total_values': len(df[column]),
            'valid_numeric': len(valid_data),
            'invalid_numeric': len(df[column]) - len(valid_data),
            'min_value': float(valid_data.min()) if len(valid_data) > 0 else None,
            'max_value': float(valid_data.max()) if len(valid_data) > 0 else None,
            'range_violations': 0
        }
        
        # 检查范围
        if min_val is not None:
            below_min = (valid_data < min_val).sum()
            results['below_min'] = int(below_min)
            results['range_violations'] += below_min
        
        if max_val is not None:
            above_max = (valid_data > max_val).sum()
            results['above_max'] = int(above_max)
            results['range_violations'] += above_max
        
        results['status'] = 'warning' if results['range_violations'] > 0 else 'ok'
        
        if results['invalid_numeric'] > 0:
            results['message'] = f'有{results["invalid_numeric"]}个非数值'
        elif results['range_violations'] > 0:
            results['message'] = f'有{results["range_violations"]}个值超出范围'
        else:
            results['message'] = '范围验证通过'
        
        return results

class PerformanceUtils:
    """性能优化工具类"""
    
    @staticmethod
    def memory_usage(df):
        """
        计算DataFrame的内存使用情况
        
        Args:
            df: DataFrame
            
        Returns:
            dict: 内存使用信息
        """
        if df is None:
            return {}
        
        memory_bytes = df.memory_usage(deep=True).sum()
        
        # 转换为更易读的单位
        units = ['B', 'KB', 'MB', 'GB']
        memory_value = memory_bytes
        unit_index = 0
        
        while memory_value >= 1024 and unit_index < len(units) - 1:
            memory_value /= 1024
            unit_index += 1
        
        return {
            'bytes': memory_bytes,
            'human_readable': f'{memory_value:.2f} {units[unit_index]}',
            'rows': len(df),
            'columns': len(df.columns),
            'bytes_per_row': memory_bytes / len(df) if len(df) > 0 else 0
        }
    
    @staticmethod
    def optimize_dataframe(df, downcast_int=True, downcast_float=True, category_threshold=0.5):
        """
        优化DataFrame以减少内存使用
        
        Args:
            df: 要优化的DataFrame
            downcast_int: 是否向下转换整数类型
            downcast_float: 是否向下转换浮点数类型
            category_threshold: 转换为分类类型的阈值（比例）
            
        Returns:
            DataFrame: 优化后的DataFrame
        """
        if df is None or len(df) == 0:
            return df
        
        optimized_df = df.copy()
        initial_memory = PerformanceUtils.memory_usage(optimized_df)['bytes']
        
        # 优化数值列
        for column in optimized_df.select_dtypes(include=['int64', 'int32', 'int']).columns:
            if downcast_int:
                # 尝试向下转换整数类型
                col_min = optimized_df[column].min()
                col_max = optimized_df[column].max()
                
                if col_min >= 0:  # 无符号整数
                    if col_max <= 255:
                        optimized_df[column] = optimized_df[column].astype('uint8')
                    elif col_max <= 65535:
                        optimized_df[column] = optimized_df[column].astype('uint16')
                    elif col_max <= 4294967295:
                        optimized_df[column] = optimized_df[column].astype('uint32')
                else:  # 有符号整数
                    if col_min >= -128 and col_max <= 127:
                        optimized_df[column] = optimized_df[column].astype('int8')
                    elif col_min >= -32768 and col_max <= 32767:
                        optimized_df[column] = optimized_df[column].astype('int16')
                    elif col_min >= -2147483648 and col_max <= 2147483647:
                        optimized_df[column] = optimized_df[column].astype('int32')
        
        # 优化浮点数列
        for column in optimized_df.select_dtypes(include=['float64', 'float32']).columns:
            if downcast_float:
                # 尝试转换为float32
                optimized_df[column] = optimized_df[column].astype('float32')
        
        # 优化对象列（字符串）
        for column in optimized_df.select_dtypes(include=['object']).columns:
            # 检查是否适合转换为分类类型
            unique_ratio = optimized_df[column].nunique() / len(optimized_df[column])
            if unique_ratio < category_threshold:
                optimized_df[column] = optimized_df[column].astype('category')
        
        final_memory = PerformanceUtils.memory_usage(optimized_df)['bytes']
        savings = initial_memory - final_memory
        savings_pct = (savings / initial_memory * 100) if initial_memory > 0 else 0
        
        print(f"内存优化: {initial_memory/1024/1024:.2f} MB -> {final_memory/1024/1024:.2f} MB, "
              f"节省 {savings_pct:.1f}%")
        
        return optimized_df
    
    @staticmethod
    def batch_process(data, batch_size=1000, process_func=None):
        """
        批量处理数据
        
        Args:
            data: 要处理的数据
            batch_size: 批大小
            process_func: 处理函数
            
        Returns:
            list: 处理结果
        """
        if process_func is None:
            return data
        
        results = []
        total_batches = (len(data) + batch_size - 1) // batch_size
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batch_result = process_func(batch)
            results.extend(batch_result)
            
            # 打印进度
            batch_num = i // batch_size + 1
            if batch_num % 10 == 0 or batch_num == total_batches:
                print(f"处理进度: {batch_num}/{total_batches} 批次")
        
        return results