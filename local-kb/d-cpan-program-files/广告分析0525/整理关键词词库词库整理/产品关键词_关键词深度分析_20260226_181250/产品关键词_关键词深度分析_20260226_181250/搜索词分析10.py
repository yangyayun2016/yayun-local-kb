# -*- coding: utf-8 -*-
"""
Created on Sun Jan  4 15:06:40 2026

@author: Administrator
"""

import pandas as pd
import numpy as np
import re
import os
import sys
from pathlib import Path
from collections import Counter, defaultdict
import warnings
import time
import traceback
from itertools import combinations
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment, NamedStyle
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import seaborn as sns

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 忽略警告
warnings.filterwarnings('ignore')

# 全局配置 - 增加更多可能的列名
COLUMN_MAPPINGS = {
    'campaign': ['campaign', '广告组合', '广告活动', '广告系列', '广告组合名称', 'campaign name'],
    'ad_group': ['ad group', '广告组', '广告小组', '广告组名称', 'ad group name'],
    'keyword': ['search term', '搜索词', 'customer search term', '查询', '客户搜索词'],
    'match_type': ['match type', '匹配类型', '匹配方式', '匹配方式'],
    'date': ['date', '日期', 'day', '开始日期', '结束日期'],
    'orders': ['orders', '订单', '7天总订单数', 'total orders', '7天总订单数(#)'],
    'impressions': ['impressions', '展示量', '曝光量'],
    'clicks': ['clicks', '点击量', '点击数', '点击量(#)'],
    'sales': ['sales', '销售额', '7天总销售额', 'total sales'],
    'cpc': ['cpc', '每次点击成本', 'cost per click', '每次点击成本(CPC)'],
    'asin': ['asin', '子asin', '子商品asin', 'parent asin', 'ASIN', '广告ASIN'],
    'sku': ['sku', '子sku', '子商品sku', '广告SKU', '7天内广告SKU销售量(#)'],
    'targeting': ['targeting', '投放方式', '定向方式'],
    'placement': ['placement', '展示位置', '广告位'],
    'product_name': ['product', 'product name', '商品名称', '产品名称']
}

# 颜色方案 - 为不同工作表设置不同的标签颜色
SHEET_COLORS = [
    'FFE6B3',  # 淡橙色
    'C6E0B4',  # 淡绿色
    'BDD7EE',  # 淡蓝色
    'F8CBAD',  # 淡桃色
    'E2EFDA',  # 淡青色
    'FFF2CC',  # 淡黄色
    'DDEBF7',  # 淡天蓝色
    'FCE4D6',  # 淡粉色
    'EDEDED',  # 淡灰色
    'D9E1F2',  # 淡紫色
]

# 字体配置
DEFAULT_FONT = Font(name='微软雅黑', size=12)
HEADER_FONT = Font(name='微软雅黑', size=12, bold=True, color='FFFFFF')
TITLE_FONT = Font(name='微软雅黑', size=14, bold=True, color='1F4E79')
NUMBER_FONT = Font(name='微软雅黑', size=11)
PERCENT_FONT = Font(name='微软雅黑', size=11, color='C00000')
POSITIVE_FONT = Font(name='微软雅黑', size=11, color='00B050')
NEGATIVE_FONT = Font(name='微软雅黑', size=11, color='FF0000')

# 填充颜色
HEADER_FILL = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
TITLE_FILL = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
HIGHLIGHT_FILL = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')
POSITIVE_FILL = PatternFill(start_color='C6E0B4', end_color='C6E0B4', fill_type='solid')
NEGATIVE_FILL = PatternFill(start_color='F8CBAD', end_color='F8CBAD', fill_type='solid')

# 边框
THIN_BORDER = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

# 对齐方式
CENTER_ALIGN = Alignment(horizontal='center', vertical='center')
LEFT_ALIGN = Alignment(horizontal='left', vertical='center')
RIGHT_ALIGN = Alignment(horizontal='right', vertical='center')

# 增加停用词和产品核心词保护列表
STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'of', 'for', 'in', 'on', 'with', 'to', 'by', 
    'it', 'as', 'at', 'this', 'that', 'from', 'your', 'you', 'my', 'me', 'we', 
    'our', 'they', 'their', 'them', 'what', 'which', 'who', 'how', 'when', 'where', 
    'why', 'can', 'could', 'would', 'should', 'will', 'shall', 'must', 'might', 'may',
    'have', 'has', 'had', 'do', 'does', 'did', 'not', 'no', 'yes', 'but', 'if', 'then',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing', 'for', 'from', 'of', 'off', 'on', 'out', 'over',
    'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
    'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
    'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
}

# 产品核心词保护列表 - 这些词不应该被否定
PROTECTED_WORDS = {
    # 椭圆机相关核心词
    'elliptical', 'ellipticals', 'ellipitcal', 'ellip', 'elliptic',
    'machine', 'machines', 'equipment', 'trainer', 'trainers',
    'desk', 'under', 'pedal', 'pedals', 'exercise', 'exerciser',
    'foot', 'feet', 'leg', 'legs', 'senior', 'seniors', 'electric',
    'underdesk', 'underdesks', 'under-desk', 'under desk',
    
    # 通用运动设备词
    'fitness', 'workout', 'cardio', 'gym', 'home', 'office',
    'compact', 'portable', 'quiet', 'silent', 'low', 'impact'
}

# 亚马逊广告算法优化参数
AMAZON_OPTIMIZATION_PARAMS = {
    'ctr_weight': 0.35,  # CTR权重提高
    'conversion_weight': 0.45,  # 转化率权重提高
    'relevance_weight': 0.20,  # 相关性权重
    'min_ctr_threshold': 0.001,  # 最低CTR阈值
    'min_conversion_threshold': 0.01,  # 最低转化率阈值
    'quality_score_high': 70,  # 高质量关键词阈值
    'quality_score_medium': 50,  # 中等质量关键词阈值
    'waste_spend_threshold': 0.5,  # 浪费花费阈值
    'high_roas_threshold': 3.0,  # 高ROAS阈值
    'low_roas_threshold': 1.0,  # 低ROAS阈值
}

def read_data_file(file_path):
    """读取数据文件 - 增强容错性"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext == '.csv':
            # 尝试多种编码
            for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb18030', 'big5', 'latin1', 'cp1252']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
                    print(f"✅ 使用编码: {encoding}")
                    return df
                except Exception as e:
                    continue
            
            # 如果所有编码都失败，尝试自动检测
            try:
                import chardet
                with open(file_path, 'rb') as f:
                    result = chardet.detect(f.read(10000))
                encoding = result['encoding']
                df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
                print(f"✅ 自动检测编码: {encoding}")
                return df
            except:
                return pd.read_csv(file_path, encoding='utf-8', errors='ignore', low_memory=False)
                
        elif file_ext in ['.xls', '.xlsx']:
            try:
                # 尝试读取Excel
                df = pd.read_excel(file_path, engine='openpyxl')
                print("✅ Excel文件读取成功")
                return df
            except Exception as e:
                print(f"⚠️ 使用openpyxl读取失败，尝试其他引擎: {str(e)}")
                try:
                    if file_ext == '.xls':
                        df = pd.read_excel(file_path, engine='xlrd')
                    else:
                        df = pd.read_excel(file_path, engine='openpyxl')
                    return df
                except:
                    # 最后尝试所有引擎
                    return pd.read_excel(file_path, engine=None)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")
            
    except Exception as e:
        print(f"❌ 读取文件时出错: {str(e)}")
        traceback.print_exc()
        return None

def detect_column(df, possible_names):
    """智能检测数据列 - 增强容错性"""
    if df is None or df.empty:
        return None
    
    try:
        # 尝试精确匹配列名
        for col in df.columns:
            col_lower = str(col).lower().strip()
            for name in possible_names:
                if name == col_lower or name.replace(' ', '_') == col_lower.replace(' ', '_'):
                    return col
        
        # 尝试部分匹配列名
        for col in df.columns:
            col_lower = str(col).lower().strip()
            for name in possible_names:
                if name in col_lower or col_lower in name:
                    return col
        
        # 检查列内容是否包含ASIN（以b0或B0开头）
        if 'asin' in str(possible_names).lower():
            for col in df.columns:
                # 检查前几行数据是否包含ASIN格式
                sample_values = df[col].dropna().astype(str).head(10)
                asin_pattern = re.compile(r'^B0[0-9A-Z]{8,9}$', re.IGNORECASE)
                if any(asin_pattern.match(value.strip()) for value in sample_values):
                    return col
        
        return None
    except Exception as e:
        print(f"检测列时出错: {str(e)}")
        return None

def extract_asins_from_keyword(keyword):
    """从关键词/搜索词中提取ASIN（以b0或B0开头）- 增强版"""
    if not isinstance(keyword, str):
        return []
    
    try:
        # 查找以b0或B0开头的10位ASIN（不区分大小写）
        # 匹配模式：b0或B0后跟8个字母数字字符，总共10位
        asin_pattern = re.compile(r'\b(B0[0-9A-Z]{8,9})\b', re.IGNORECASE)
        matches = asin_pattern.findall(keyword.upper())
        
        # 过滤掉长度不等于10的（标准ASIN长度）
        valid_asins = []
        for asin in matches:
            # 标准化ASIN：转为大写，去除空格
            asin_clean = asin.upper().strip()
            if len(asin_clean) == 10 and asin_clean.startswith('B0'):
                valid_asins.append(asin_clean)
        
        return list(set(valid_asins))  # 去重
    except Exception as e:
        print(f"提取ASIN时出错: {str(e)}")
        return []

def clean_data(df, report_type=None):
    """数据清洗函数 - 增强容错性，增加从搜索词提取ASIN的功能"""
    try:
        print(f"原始数据形状: {df.shape}")
        print(f"原始列名: {list(df.columns)}")
        
        # 移除完全空的行
        df = df.dropna(how='all')
        print(f"清理空行后形状: {df.shape}")
        
        # 自动检测报告类型
        if report_type is None:
            keyword_col = detect_column(df, COLUMN_MAPPINGS['keyword'])
            if keyword_col:
                report_type = 'search_term' if 'search' in str(keyword_col).lower() else 'keyword'
                print(f"检测到{report_type}报告")
            else:
                report_type = 'keyword'
                print("使用默认报告类型: keyword")
        
        # 应用列名映射
        renamed_cols = {}
        for target_col, possible_names in COLUMN_MAPPINGS.items():
            detected_col = detect_column(df, possible_names)
            if detected_col:
                renamed_cols[detected_col] = target_col
        
        if renamed_cols:
            df = df.rename(columns=renamed_cols)
            print(f"重命名列: {renamed_cols}")
        
        print(f"重命名后列名: {list(df.columns)}")
        
        # 确保必要列存在
        required_cols = ['campaign', 'ad_group', 'keyword']
        for col in required_cols:
            if col not in df.columns:
                if col == 'keyword':
                    # 尝试使用第一列作为关键词
                    if len(df.columns) > 0:
                        first_col = df.columns[0]
                        if first_col not in ['date', 'campaign', 'ad_group']:
                            df = df.rename(columns={first_col: 'keyword'})
                            print(f"将第一列 '{first_col}' 重命名为 'keyword'")
                else:
                    df[col] = f'默认{col}'
                    print(f"创建默认列: {col}")
        
        # 处理日期列
        if 'date' in df.columns:
            try:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                if df['date'].isna().all():
                    print("警告: 日期列转换失败，创建虚拟日期")
                    df['date'] = datetime.now()
            except:
                df['date'] = datetime.now()
        
        # 数值列处理 - 增强容错性
        num_cols = ['orders', 'impressions', 'clicks', 'sales', 'cpc']
        for col in num_cols:
            if col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        df[col] = df[col].astype(str).replace(r'[^\d\.-]', '', regex=True)
                    except:
                        pass
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0
        
        # 处理ASIN列 - 增强ASIN提取功能
        if 'asin' in df.columns:
            # 标准化ASIN格式（转为大写，去除空格）
            df['asin'] = df['asin'].astype(str).str.upper().str.strip()
            # 提取有效的ASIN（以B0开头且长度至少为10位）
            asin_pattern = re.compile(r'^B0[0-9A-Z]{8,9}$')
            df['asin'] = df['asin'].apply(lambda x: x if asin_pattern.match(str(x)) else None)
        
        # 新增：从搜索词中提取ASIN
        print("从搜索词中提取ASIN...")
        if 'keyword' in df.columns:
            # 创建提取的ASIN列表列
            df['extracted_asins'] = df['keyword'].apply(extract_asins_from_keyword)
            
            # 统计提取情况
            asin_extracted_count = df[df['extracted_asins'].apply(len) > 0].shape[0]
            total_extracted_asins = sum(df['extracted_asins'].apply(len))
            print(f"从{asin_extracted_count}个搜索词中提取到{total_extracted_asins}个ASIN")
            
            # 如果有ASIN列为空，尝试用提取的第一个ASIN填充
            if 'asin' in df.columns:
                for idx, row in df.iterrows():
                    if pd.isna(row['asin']) or str(row['asin']).strip() == '' or str(row['asin']).strip().lower() == 'nan':
                        extracted = row['extracted_asins']
                        if extracted:
                            df.at[idx, 'asin'] = extracted[0]  # 使用第一个提取的ASIN
            else:
                # 如果原本没有ASIN列，创建新列
                df['asin'] = df['extracted_asins'].apply(lambda x: x[0] if x else None)
            
            # 创建商品ASIN分析标志列
            df['contains_asin'] = df['extracted_asins'].apply(lambda x: len(x) > 0)
            
            # 提取ASIN作为单独列（第一个ASIN）
            df['primary_asin'] = df['extracted_asins'].apply(lambda x: x[0] if x else None)
        
        # 添加关键指标
        df['spend'] = df['cpc'] * df['clicks']
        
        # 使用安全的计算方式
        def safe_div(a, b):
            return a / b if b != 0 else 0
        
        df['conversion_rate'] = df.apply(lambda x: safe_div(x['orders'], x['clicks']), axis=1)
        df['ctr'] = df.apply(lambda x: safe_div(x['clicks'], x['impressions']), axis=1)
        df['acos'] = df.apply(lambda x: safe_div(x['spend'], x['sales']) if x['sales'] > 0 else 0, axis=1)
        df['roas'] = df.apply(lambda x: safe_div(x['sales'], x['spend']) if x['spend'] > 0 else 0, axis=1)
        
        # 添加分析占位符
        df['negation_suggestion'] = "保留"
        df['grouping_suggestion'] = "未分组"
        df['quality_score'] = 0
        df['optimization_priority'] = "低"
        df['bid_suggestion'] = "维持"
        df['relevance_score'] = 0
        df['match_type_suggestion'] = ""
        df['campaign_recommendation'] = ""
        df['asin_related_suggestion'] = ""
        df['keyword_trend'] = "稳定"
        
        print(f"最终数据形状: {df.shape}")
        print(f"包含ASIN的数据行数: {df['asin'].notna().sum()}")
        return df, report_type
        
    except Exception as e:
        print(f"数据清洗错误: {str(e)}")
        traceback.print_exc()
        # 返回基本数据
        return df, report_type or 'unknown'

def extract_roots(keyword, min_length=3):
    """从关键词中提取有效词根 - 智能版"""
    if not isinstance(keyword, str):
        return []
    
    try:
        # 清理关键词，移除特殊字符
        keyword_clean = re.sub(r'[^\w\s]', ' ', str(keyword).lower())
        
        # 提取词根
        words = re.findall(r'\b\w{%d,}\b' % min_length, keyword_clean)
        
        # 过滤停用词
        filtered_words = []
        for word in words:
            if word not in STOP_WORDS:
                # 检查是否受保护的核心词
                if word in PROTECTED_WORDS:
                    filtered_words.append(word)
                elif len(word) >= min_length:  # 确保最小长度
                    filtered_words.append(word)
        
        return filtered_words
    except:
        return []

def is_protected_word(word):
    """检查是否是受保护的核心词"""
    word_lower = word.lower()
    
    # 直接匹配
    if word_lower in PROTECTED_WORDS:
        return True
    
    # 部分匹配检查
    for protected in PROTECTED_WORDS:
        if protected in word_lower or word_lower in protected:
            return True
    
    return False

def calculate_keyword_quality(row):
    """计算关键词质量得分 - 优化版"""
    try:
        score = 0
        
        # 基础分
        base_score = 30
        score += base_score
        
        # CTR权重
        if row['impressions'] > 0:
            ctr = row['ctr']
            if ctr > 0.01:
                ctr_score = 25
            elif ctr > 0.005:
                ctr_score = 15
            elif ctr > 0.002:
                ctr_score = 5
            else:
                ctr_score = 0
            score += ctr_score
        
        # 转化率权重
        if row['clicks'] > 0:
            cr = row['conversion_rate']
            if cr > 0.1:
                cr_score = 25
            elif cr > 0.05:
                cr_score = 15
            elif cr > 0.02:
                cr_score = 8
            elif cr > 0.01:
                cr_score = 3
            else:
                cr_score = 0
            score += cr_score
        
        # ROAS权重
        if row['spend'] > 0:
            roas = row['roas']
            if roas > 5:
                roas_score = 25
            elif roas > 3:
                roas_score = 15
            elif roas > 2:
                roas_score = 10
            elif roas > 1:
                roas_score = 5
            else:
                roas_score = 0
            score += roas_score
        
        # 订单权重
        orders = row['orders']
        if orders >= 5:
            orders_score = 20
        elif orders >= 3:
            orders_score = 15
        elif orders >= 2:
            orders_score = 10
        elif orders >= 1:
            orders_score = 5
        else:
            orders_score = 0
        score += orders_score
        
        # 相关性加分
        keyword = str(row['keyword']).lower()
        relevance_bonus = calculate_relevance_bonus(keyword)
        score += relevance_bonus
        
        # 限制在0-100分之间
        return min(100, max(0, score))
    except:
        return 30  # 基础分

def calculate_relevance_bonus(keyword):
    """计算相关性加分"""
    bonus = 0
    keyword_lower = keyword.lower()
    
    # 检查是否包含产品核心词
    for word in PROTECTED_WORDS:
        if word in keyword_lower:
            bonus += 3
            if word in ['elliptical', 'ellipticals', 'machine', 'trainer']:
                bonus += 2  # 核心产品词额外加分
    
    # 检查关键词长度
    words = keyword_lower.split()
    if 2 <= len(words) <= 5:
        bonus += 5  # 适中长度的关键词更好
    
    # 检查是否包含购买意图词
    intent_words = ['buy', 'purchase', 'shop', 'order', 'cheap', 'best', 'review', 'price']
    for word in intent_words:
        if word in keyword_lower:
            bonus += 2
    
    return min(15, bonus)  # 限制最大加分
def get_optimization_suggestion(row):
    """根据关键词表现返回优化建议"""
    if row['orders'] == 0 and row['spend'] > 1:
        return "否定（高花费无转化）"
    elif row['roas'] < 0.5 and row['spend'] > 0.5:
        return "降低出价（ROAS过低）"
    elif row['ctr'] < 0.001 and row['impressions'] > 100:
        return "优化广告文案或调整匹配类型（CTR过低）"
    elif row['conversion_rate'] < 0.01 and row['clicks'] > 10:
        return "优化落地页（转化率过低）"
    elif row['quality_score'] < 40:
        return "优化关键词质量得分"
    else:
        return "其他优化"
def get_poor_performing_keywords(campaign_df):
    """
    找出表现差的关键词：
    1. 花费高不出单
    2. ACOS 高
    3. ROAS 低
    4. CTR 低但花费高
    5. 转化率低但点击多
    """

    if campaign_df.empty:
        return pd.DataFrame()

    conditions = (
        # 高花费无订单
        ((campaign_df['orders'] == 0) & (campaign_df['spend'] > 1)) |

        # 高 ACOS
        ((campaign_df['acos'] > 0.6) & (campaign_df['spend'] > 0.5)) |

        # 有单但 ROAS 低
        ((campaign_df['orders'] > 0) & (campaign_df['roas'] < 1.5) & (campaign_df['spend'] > 0.5)) |

        # CTR 低 + 花费高
        ((campaign_df['ctr'] < 0.002) & (campaign_df['spend'] > 0.5) & (campaign_df['impressions'] > 100)) |

        # 转化率低 + 点击多
        ((campaign_df['conversion_rate'] < 0.01) & (campaign_df['clicks'] > 10))
    )

    poor_df = campaign_df.loc[conditions].copy()

    if poor_df.empty:
        return pd.DataFrame()

    # 标记原因
    def mark_reason(row):
        reasons = []
        if row['orders'] == 0 and row['spend'] > 1:
            reasons.append("高花费无订单")
        if row['acos'] > 0.6:
            reasons.append(f"ACOS高({row['acos']:.0%})")
        if row['roas'] < 1.5 and row['orders'] > 0:
            reasons.append(f"ROAS低({row['roas']:.2f})")
        if row['ctr'] < 0.002:
            reasons.append("CTR低")
        if row['conversion_rate'] < 0.01 and row['clicks'] > 10:
            reasons.append("转化率低")

        return "｜".join(reasons)

    poor_df['表现差原因'] = poor_df.apply(mark_reason, axis=1)

    return poor_df.sort_values('spend', ascending=False)[[
        'keyword', 'impressions', 'clicks', 'orders',
        'spend', 'sales', 'acos', 'roas',
        'ctr', 'conversion_rate', '表现差原因'
    ]]


# 在 analyze_campaign 函数中添加以下新功能
def analyze_campaign(df, campaign_name):
    """分析单个广告组合 - 增强版，增加ASIN分析和高级分析模块"""
    try:
        campaign_df = df[df['campaign'] == campaign_name].copy()
        
        if len(campaign_df) == 0:
            print(f"警告: 广告组合 {campaign_name} 无数据")
            return {
                'campaign_name': campaign_name,
                'top_keywords': pd.DataFrame(),
                'waste_keywords': pd.DataFrame(),
                'top_converting_roots': [],
                'top_non_converting_roots': [],
                'asin_analysis': pd.DataFrame(),
                'keyword_trends': pd.DataFrame(),
                'campaign_df': campaign_df,
                'campaign_recommendations': [],
                'campaign_stats': {},
                'summary_stats': get_campaign_summary_stats(campaign_df),
                'search_term_asin_analysis': pd.DataFrame(),  # 新增：搜索词ASIN分析
                'competitor_asins': pd.DataFrame(),
                'budget_recommendations': [],
                'ad_copy_suggestions': [],
                'time_performance_analysis': pd.DataFrame(),
                'keyword_expansion_suggestions': [],
                'targeting_optimizations': [],
                # 新增：高级分析模块
                'market_analysis': {},
                'customer_analysis': {},
                'competition_analysis': {},
                'forecast_analysis': {},
                'optimization_analysis': {},
                'risk_analysis': {},
                'growth_analysis': {},
                'seasonal_analysis': {},
                # 新增：表现差的关键词
                'poor_performing_keywords': pd.DataFrame()
            }
        
        print(f"分析广告组合: {campaign_name} ({len(campaign_df)}个关键词)")
        
        # 1. 计算质量得分
        campaign_df['quality_score'] = campaign_df.apply(calculate_keyword_quality, axis=1)
        
        # 2. 计算相关性得分
        campaign_df['relevance_score'] = campaign_df['keyword'].apply(lambda x: calculate_relevance_bonus(x))
        
        # 3. 综合得分排序
        campaign_df['composite_score'] = campaign_df['quality_score'] * 0.7 + campaign_df['relevance_score'] * 0.3
        top_keywords = campaign_df.sort_values('composite_score', ascending=False).head(15)
        
        # 4. 应否定关键词
        waste_conditions = (
            (campaign_df['orders'] == 0) & 
            (campaign_df['spend'] > 0.5) &
            (campaign_df['ctr'] < 0.001) &
            (~campaign_df['keyword'].apply(lambda x: contains_protected_words(str(x))))
        )
        
        waste_keywords = campaign_df[waste_conditions].copy()
        waste_keywords['negation_reason'] = waste_keywords.apply(get_negation_reason_enhanced, axis=1)
        waste_keywords = waste_keywords.sort_values('spend', ascending=False).head(20)
        
        # ================ 新增：找出所有表现差的关键词 ================
        # 条件1: 高花费无转化
        condition_high_spend_no_orders = (
            (campaign_df['orders'] == 0) & 
            (campaign_df['spend'] > 1.0)
        )
        
        # 条件2: 高ACOS（>60%）
        condition_high_acos = (
            (campaign_df['acos'] > 0.6) & 
            (campaign_df['spend'] > 0.5)
        )
        
        # 条件3: 高花费低ROAS（ROAS < 1.5）
        condition_low_roas = (
            (campaign_df['roas'] < 1.5) & 
            (campaign_df['spend'] > 0.5) &
            (campaign_df['orders'] > 0)  # 有订单但ROAS低
        )
        
        # 条件4: 低CTR高花费（CTR < 0.002 且花费 > 0.5）
        condition_low_ctr_high_spend = (
            (campaign_df['ctr'] < 0.002) & 
            (campaign_df['spend'] > 0.5) &
            (campaign_df['impressions'] > 100)
        )
        
        # 条件5: 低转化率高点击（转化率 < 0.01 且点击 > 10）
        condition_low_cr_high_clicks = (
            (campaign_df['conversion_rate'] < 0.01) & 
            (campaign_df['clicks'] > 10) &
            (campaign_df['spend'] > 0.5)
        )
        
        # 组合所有条件
        poor_conditions = (
            condition_high_spend_no_orders | 
            condition_high_acos | 
            condition_low_roas | 
            condition_low_ctr_high_spend | 
            condition_low_cr_high_clicks
        )
        
        # 获取表现差的关键词
        poor_performing = campaign_df[poor_conditions].copy()
        
        
        if not poor_performing.empty:
            # 添加表现差的原因
            def get_poor_performance_reason(row):
                reasons = []
                
                if row['orders'] == 0 and row['spend'] > 1.0:
                    reasons.append(f"高花费无转化(¥{row['spend']:.2f})")
                
                if row['acos'] > 0.6 and row['spend'] > 0.5:
                    reasons.append(f"高ACOS({row['acos']:.1%})")
                
                if row['roas'] < 1.5 and row['spend'] > 0.5 and row['orders'] > 0:
                    reasons.append(f"低ROAS({row['roas']:.2f})")
                
                if row['ctr'] < 0.002 and row['spend'] > 0.5 and row['impressions'] > 100:
                    reasons.append(f"低CTR({row['ctr']:.3%})")
                
                if row['conversion_rate'] < 0.01 and row['clicks'] > 10 and row['spend'] > 0.5:
                    reasons.append(f"低转化率({row['conversion_rate']:.2%})")
                
                return " | ".join(reasons) if reasons else "表现不佳"
            
            poor_performing['poor_reason'] = poor_performing.apply(get_poor_performance_reason, axis=1)
            
            # 按花费排序
            poor_performing = poor_performing.sort_values('spend', ascending=False)
            
            # 选择最重要的列
            poor_columns = [
                'keyword', 'impressions', 'clicks', 'orders', 'spend', 
                'sales', 'roas', 'acos', 'ctr', 'conversion_rate', 
                'quality_score', 'poor_reason'
            ]
            
            # 只保留存在的列
            poor_columns = [col for col in poor_columns if col in poor_performing.columns]
            poor_performing_keywords = poor_performing[poor_columns].copy()
            
            # 限制数量
            poor_performing_keywords = poor_performing_keywords.head(30)
            
            print(f"发现 {len(poor_performing_keywords)} 个表现差的关键词")
        else:
            poor_performing_keywords = pd.DataFrame()
        # ================ 新增结束 ================
        
        # 5. 高效词根分析
        converting_keywords = campaign_df[campaign_df['orders'] > 0]
        converting_roots = []
        if len(converting_keywords) > 0:
            for keyword in converting_keywords['keyword']:
                roots = extract_roots(keyword)
                for root in roots:
                    keyword_orders = converting_keywords[converting_keywords['keyword'] == keyword]['orders'].values[0]
                    keyword_relevance = calculate_relevance_bonus(str(keyword))
                    weight = keyword_orders * 3 + keyword_relevance
                    converting_roots.append((root, weight))
        
        if converting_roots:
            root_counter = Counter()
            for root, weight in converting_roots:
                root_counter[root] += weight
            
            top_converting_roots = root_counter.most_common(15)
        else:
            top_converting_roots = []
        
        # 6. 无效词根分析
        non_converting_keywords = campaign_df[campaign_df['orders'] == 0]
        non_converting_roots = []
        if len(non_converting_keywords) > 0:
            for keyword in non_converting_keywords['keyword']:
                roots = extract_roots(keyword)
                filtered_roots = []
                for root in roots:
                    if not is_protected_word(root):
                        in_efficient_roots = any(r[0] == root for r in top_converting_roots)
                        if not in_efficient_roots:
                            filtered_roots.append(root)
                non_converting_roots.extend(filtered_roots)
            
            non_converting_root_counter = Counter(non_converting_roots)
            top_non_converting_roots = [(root, count) for root, count in non_converting_root_counter.most_common(20) 
                                       if count >= 2 and not is_protected_word(root)]
        else:
            top_non_converting_roots = []
        
        # 7. ASIN分析（包括从搜索词提取的ASIN）
        asin_analysis = pd.DataFrame()
        if 'asin' in campaign_df.columns and campaign_df['asin'].notna().any():
            asin_analysis = analyze_campaign_asins(campaign_df)
        
        # 8. 新增：搜索词中的ASIN分析
        search_term_asin_analysis = pd.DataFrame()
        if 'extracted_asins' in campaign_df.columns:
            search_term_asin_analysis = analyze_search_term_asins(campaign_df)
        
        # 9. 关键词趋势分析
        keyword_trends = analyze_keyword_trends(campaign_df)
        
        # 10. 添加智能否定词建议
        campaign_df = add_intelligent_negation_suggestions(campaign_df, top_converting_roots, top_non_converting_roots)
        
        # 11. 添加分组建议
        campaign_df = add_intelligent_grouping_suggestions(campaign_df, top_converting_roots)
        
        # 12. 添加匹配类型建议
        campaign_df = add_match_type_suggestions(campaign_df)
        
        # 13. 添加出价建议
        campaign_df = add_intelligent_bid_suggestions(campaign_df)
        
        # 14. 添加ASIN相关建议
        campaign_df = add_asin_related_suggestions(campaign_df, asin_analysis)
        
        # 15. 添加关键词趋势标签
        campaign_df = add_keyword_trend_labels(campaign_df)
        
        # 16. 生成广告组合建议
        campaign_recommendations = generate_campaign_recommendations(campaign_df, top_converting_roots, 
                                                                   waste_keywords, asin_analysis)
        
        # 17. 计算广告组合统计
        campaign_stats = calculate_campaign_statistics(campaign_df, asin_analysis)
        
        # 18. 新增：竞争对手ASIN分析
        competitor_asins = analyze_competitor_asins(campaign_df)
        
        # 19. 新增：预算分配建议
        budget_recommendations = generate_budget_recommendations(campaign_df, asin_analysis, competitor_asins)
        
        # 20. 新增：广告文案建议
        ad_copy_suggestions = generate_ad_copy_suggestions(campaign_df, top_converting_roots)
        
        # 21. 新增：时间段表现分析
        time_performance_analysis = analyze_time_performance(campaign_df)
        
        # 22. 新增：关键词扩展建议
        keyword_expansion_suggestions = generate_keyword_expansion_suggestions(campaign_df, top_converting_roots)
        
        # 23. 新增：投放策略优化
        targeting_optimizations = generate_targeting_optimizations(campaign_df)
        
        # 24. 新增：高级分析模块
        print(f"执行高级分析模块: {campaign_name}")
        
        # 市场分析
        market_analysis = perform_market_analysis(campaign_df)
        
        # 客户分析
        customer_analysis = perform_customer_analysis(campaign_df)
        
        # 竞争分析 - 使用已计算的competitor_asins
        competition_analysis = perform_competition_analysis(campaign_df, competitor_asins)
        
        # 预测分析
        forecast_analysis = perform_forecast_analysis(campaign_df)
        
        # 优化分析
        optimization_analysis = perform_optimization_analysis(campaign_df)
        
        # 风险分析
        risk_analysis = perform_risk_analysis(campaign_df, asin_analysis, competitor_asins)
        
        # 增长分析
        growth_analysis = perform_growth_analysis(campaign_df, search_term_asin_analysis)
        
        # 季节性分析
        seasonal_analysis = perform_seasonal_analysis(campaign_df)
        
        print(f"广告组合 {campaign_name} 分析完成: 推荐{len(top_keywords)}个关键词, 否定{len(waste_keywords)}个关键词")
        if not search_term_asin_analysis.empty:
            print(f"从搜索词中分析出{len(search_term_asin_analysis)}个商品ASIN")
        if not poor_performing_keywords.empty:
            print(f"发现{len(poor_performing_keywords)}个表现差的关键词")
        
        return {
            'campaign_name': campaign_name,
            'top_keywords': top_keywords,
            'waste_keywords': waste_keywords,
            'top_converting_roots': top_converting_roots,
            'top_non_converting_roots': top_non_converting_roots,
            'asin_analysis': asin_analysis,
            'search_term_asin_analysis': search_term_asin_analysis,
            'keyword_trends': keyword_trends,
            'campaign_df': campaign_df,
            'campaign_recommendations': campaign_recommendations,
            'campaign_stats': campaign_stats,
            'summary_stats': get_campaign_summary_stats(campaign_df),
            'competitor_asins': competitor_asins,
            'budget_recommendations': budget_recommendations,
            'ad_copy_suggestions': ad_copy_suggestions,
            'time_performance_analysis': time_performance_analysis,
            'keyword_expansion_suggestions': keyword_expansion_suggestions,
            'targeting_optimizations': targeting_optimizations,
            # 高级分析模块
            'market_analysis': market_analysis,
            'customer_analysis': customer_analysis,
            'competition_analysis': competition_analysis,
            'forecast_analysis': forecast_analysis,
            'optimization_analysis': optimization_analysis,
            'risk_analysis': risk_analysis,
            'growth_analysis': growth_analysis,
            'seasonal_analysis': seasonal_analysis,
            # 新增：表现差的关键词
            'poor_performing_keywords': poor_performing_keywords
        }
        
    except Exception as e:
        print(f"分析广告组合 {campaign_name} 时出错: {str(e)}")
        traceback.print_exc()
        return {
            'campaign_name': campaign_name,
            'top_keywords': pd.DataFrame(),
            'waste_keywords': pd.DataFrame(),
            'top_converting_roots': [],
            'top_non_converting_roots': [],
            'asin_analysis': pd.DataFrame(),
            'search_term_asin_analysis': pd.DataFrame(),
            'keyword_trends': pd.DataFrame(),
            'campaign_df': df[df['campaign'] == campaign_name].copy() if 'campaign' in df.columns else pd.DataFrame(),
            'campaign_recommendations': [],
            'campaign_stats': {},
            'competitor_asins': pd.DataFrame(),
            'budget_recommendations': [],
            'ad_copy_suggestions': [],
            'time_performance_analysis': pd.DataFrame(),
            'keyword_expansion_suggestions': [],
            'targeting_optimizations': [],
            # 高级分析模块
            'market_analysis': {},
            'customer_analysis': {},
            'competition_analysis': {},
            'forecast_analysis': {},
            'optimization_analysis': {},
            'risk_analysis': {},
            'growth_analysis': {},
            'seasonal_analysis': {},
            # 新增：表现差的关键词
            'poor_performing_keywords': pd.DataFrame()
        }
            
            # 保存其他分析
categories = ['搜索词分析', '广告活动分析']
for category in categories:
                if category in data:
                    analysis_data = data[category]
                    
                    # 处理字典类型的分析结果
                    if isinstance(analysis_data, dict):
                        for sheet_idx, (sheet_key, df_section) in enumerate(analysis_data.items()):
                            if isinstance(df_section, pd.DataFrame) and not df_section.empty:
                                base_sheet_name = f"{category}_{sheet_key}" if sheet_key else category
                                sheet_name = get_unique_sheet_name(base_sheet_name)
                                df_section.to_excel(writer, sheet_name=sheet_name, index=False)
                                apply_excel_formatting(writer.sheets[sheet_name], len(used_sheet_names))
                    
                    # 处理DataFrame类型的分析结果
                    elif isinstance(analysis_data, pd.DataFrame) and not analysis_data.empty:
                        sheet_name = get_unique_sheet_name(category)
                        analysis_data.to_excel(writer, sheet_name=sheet_name, index=False)
                        apply_excel_formatting(writer.sheets[sheet_name], len(used_sheet_names))
            
            # 保存关键洞察
           if '关键洞察' in data and data['关键洞察']:
                sheet_name = get_unique_sheet_name('关键洞察')
                insights_df = pd.DataFrame(data['关键洞察'], columns=['洞察内容'])
                insights_df.to_excel(writer, sheet_name=sheet_name, index=False)
                apply_excel_formatting(writer.sheets[sheet_name], len(used_sheet_names))
        
        print(f"✅ Excel文件保存成功: {output_file}")
        
        # 添加可视化分析
        generate_visual_analysis(data['原始数据'], output_file)
        
        return True
        
    except Exception as e:
        print(f"❌ 保存Excel文件时出错: {str(e)}")
        traceback.print_exc()
        return False
def find_poor_performing_keywords(df):
    """找出表现差的关键词：花费多不出单或ACOS高"""
    try:
        # 条件1: 高花费无转化
        condition_high_spend_no_orders = (
            (df['orders'] == 0) & 
            (df['spend'] > 1.0)
        )
        
        # 条件2: 高ACOS（>60%）
        condition_high_acos = (
            (df['acos'] > 0.6) & 
            (df['spend'] > 0.5)
        )
        
        # 条件3: 高花费低ROAS（ROAS < 1.5）
        condition_low_roas = (
            (df['roas'] < 1.5) & 
            (df['spend'] > 0.5) &
            (df['orders'] > 0)  # 有订单但ROAS低
        )
        
        # 条件4: 低CTR高花费（CTR < 0.002 且花费 > 0.5）
        condition_low_ctr_high_spend = (
            (df['ctr'] < 0.002) & 
            (df['spend'] > 0.5) &
            (df['impressions'] > 100)
        )
        
        # 组合所有条件
        poor_conditions = (
            condition_high_spend_no_orders | 
            condition_high_acos | 
            condition_low_roas | 
            condition_low_ctr_high_spend
        )
        
        # 获取表现差的关键词
        poor_performing = df[poor_conditions].copy()
        
        if not poor_performing.empty:
            # 添加表现差的原因
            def get_poor_performance_reason(row):
                reasons = []
                
                if row['orders'] == 0 and row['spend'] > 1.0:
                    reasons.append(f"高花费无转化(¥{row['spend']:.2f})")
                
                if row['acos'] > 0.6 and row['spend'] > 0.5:
                    reasons.append(f"高ACOS({row['acos']:.1%})")
                
                if row['roas'] < 1.5 and row['spend'] > 0.5 and row['orders'] > 0:
                    reasons.append(f"低ROAS({row['roas']:.2f})")
                
                if row['ctr'] < 0.002 and row['spend'] > 0.5 and row['impressions'] > 100:
                    reasons.append(f"低CTR({row['ctr']:.3%})")
                
                return " | ".join(reasons) if reasons else "表现不佳"
            
            poor_performing['poor_reason'] = poor_performing.apply(get_poor_performance_reason, axis=1)
            
            # 按花费排序
            poor_performing = poor_performing.sort_values('spend', ascending=False)
            
            # 选择最重要的列
            poor_columns = [
                'keyword', 'impressions', 'clicks', 'orders', 'spend', 
                'sales', 'roas', 'acos', 'ctr', 'conversion_rate', 
                'quality_score', 'poor_reason'
            ]
            
            # 只保留存在的列
            poor_columns = [col for col in poor_columns if col in poor_performing.columns]
            poor_performing_keywords = poor_performing[poor_columns].copy()
            
            # 限制数量
            poor_performing_keywords = poor_performing_keywords.head(30)
            
            print(f"发现 {len(poor_performing_keywords)} 个表现差的关键词")
            return poor_performing_keywords
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"查找表现差关键词时出错: {str(e)}")
        return pd.DataFrame()
def get_poor_performing_keywords(campaign_df):
    """
    找出表现差的关键词：
    1. 花费高不出单
    2. ACOS 高
    3. ROAS 低
    4. CTR 低但花费高
    5. 转化率低但点击多
    """
    if campaign_df.empty:
        return pd.DataFrame()
    
    conditions = (
        # 高花费无订单
        ((campaign_df['orders'] == 0) & (campaign_df['spend'] > 1)) |
        
        # 高 ACOS
        ((campaign_df['acos'] > 0.6) & (campaign_df['spend'] > 0.5)) |
        
        # 有单但 ROAS 低
        ((campaign_df['orders'] > 0) & (campaign_df['roas'] < 1.5) & (campaign_df['spend'] > 0.5)) |
        
        # CTR 低 + 花费高
        ((campaign_df['ctr'] < 0.002) & (campaign_df['spend'] > 0.5) & (campaign_df['impressions'] > 100)) |
        
        # 转化率低 + 点击多
        ((campaign_df['conversion_rate'] < 0.01) & (campaign_df['clicks'] > 10))
    )
    
    poor_df = campaign_df.loc[conditions].copy()
    
    if poor_df.empty:
        return pd.DataFrame()
    
    # 标记原因
    def mark_reason(row):
        reasons = []
        if row['orders'] == 0 and row['spend'] > 1:
            reasons.append("高花费无订单")
        if row['acos'] > 0.6:
            reasons.append(f"ACOS高({row['acos']:.0%})")
        if row['roas'] < 1.5 and row['orders'] > 0:
            reasons.append(f"ROAS低({row['roas']:.2f})")
        if row['ctr'] < 0.002:
            reasons.append("CTR低")
        if row['conversion_rate'] < 0.01 and row['clicks'] > 10:
            reasons.append("转化率低")
        
        return " | ".join(reasons)
    
    poor_df['表现差原因'] = poor_df.apply(mark_reason, axis=1)
    
    return poor_df.sort_values('spend', ascending=False)[[
        'keyword', 'impressions', 'clicks', 'orders',
        'spend', 'sales', 'acos', 'roas',
        'ctr', 'conversion_rate', '表现差原因'
    ]]


# 在 analyze_campaign 函数中添加调用
# 在 analyze_campaign 函数的顶部，添加表现差关键词的分析

def analyze_campaign(df, campaign_name):
    """分析单个广告组合 - 增强版，增加ASIN分析和高级分析模块"""
    try:
        campaign_df = df[df['campaign'] == campaign_name].copy()
        
        if len(campaign_df) == 0:
            print(f"警告: 广告组合 {campaign_name} 无数据")
            return {
                'campaign_name': campaign_name,
                'top_keywords': pd.DataFrame(),
                'waste_keywords': pd.DataFrame(),
                'poor_performing_keywords': pd.DataFrame(),  # 新增
                'top_converting_roots': [],
                'top_non_converting_roots': [],
                'asin_analysis': pd.DataFrame(),
                'keyword_trends': pd.DataFrame(),
                'campaign_df': campaign_df,
                'campaign_recommendations': [],
                'campaign_stats': {},
                'summary_stats': get_campaign_summary_stats(campaign_df),
                'search_term_asin_analysis': pd.DataFrame(),
                'competitor_asins': pd.DataFrame(),
                'budget_recommendations': [],
                'ad_copy_suggestions': [],
                'time_performance_analysis': pd.DataFrame(),
                'keyword_expansion_suggestions': [],
                'targeting_optimizations': [],
            }
        
        print(f"分析广告组合: {campaign_name} ({len(campaign_df)}个关键词)")
        
        # 1. 计算质量得分
        campaign_df['quality_score'] = campaign_df.apply(calculate_keyword_quality, axis=1)
        
        # 2. 计算相关性得分
        campaign_df['relevance_score'] = campaign_df['keyword'].apply(lambda x: calculate_relevance_bonus(x))
        
        # 3. 综合得分排序
        campaign_df['composite_score'] = campaign_df['quality_score'] * 0.7 + campaign_df['relevance_score'] * 0.3
        top_keywords = campaign_df.sort_values('composite_score', ascending=False).head(15)
        
        # 4. 应否定关键词
        waste_conditions = (
            (campaign_df['orders'] == 0) & 
            (campaign_df['spend'] > 0.5) &
            (campaign_df['ctr'] < 0.001) &
            (~campaign_df['keyword'].apply(lambda x: contains_protected_words(str(x))))
        )
        
        waste_keywords = campaign_df[waste_conditions].copy()
        waste_keywords['negation_reason'] = waste_keywords.apply(get_negation_reason_enhanced, axis=1)
        waste_keywords = waste_keywords.sort_values('spend', ascending=False).head(20)
        
        # 5. 新增：找出表现差的关键词
       poor_performing_keywords = get_poor_performing_keywords(campaign_df)
        
        # 6. 高效词根分析
        converting_keywords = campaign_df[campaign_df['orders'] > 0]
        converting_roots = []
        if len(converting_keywords) > 0:
            for keyword in converting_keywords['keyword']:
                roots = extract_roots(keyword)
                for root in roots:
                    keyword_orders = converting_keywords[converting_keywords['keyword'] == keyword]['orders'].values[0]
                    keyword_relevance = calculate_relevance_bonus(str(keyword))
                    weight = keyword_orders * 3 + keyword_relevance
                    converting_roots.append((root, weight))
        
        if converting_roots:
            root_counter = Counter()
            for root, weight in converting_roots:
                root_counter[root] += weight
            
            top_converting_roots = root_counter.most_common(15)
        else:
            top_converting_roots = []
        
        # 7. 无效词根分析
        non_converting_keywords = campaign_df[campaign_df['orders'] == 0]
        non_converting_roots = []
        if len(non_converting_keywords) > 0:
            for keyword in non_converting_keywords['keyword']:
                roots = extract_roots(keyword)
                filtered_roots = []
                for root in roots:
                    if not is_protected_word(root):
                        in_efficient_roots = any(r[0] == root for r in top_converting_roots)
                        if not in_efficient_roots:
                            filtered_roots.append(root)
                non_converting_roots.extend(filtered_roots)
            
            non_converting_root_counter = Counter(non_converting_roots)
            top_non_converting_roots = [(root, count) for root, count in non_converting_root_counter.most_common(20) 
                                       if count >= 2 and not is_protected_word(root)]
        else:
            top_non_converting_roots = []
        
        # 8. ASIN分析
        asin_analysis = pd.DataFrame()
        if 'asin' in campaign_df.columns and campaign_df['asin'].notna().any():
            asin_analysis = analyze_campaign_asins(campaign_df)
        
        # 9. 搜索词中的ASIN分析
        search_term_asin_analysis = pd.DataFrame()
        if 'extracted_asins' in campaign_df.columns:
            search_term_asin_analysis = analyze_search_term_asins(campaign_df)
        
        # 10. 关键词趋势分析
        keyword_trends = analyze_keyword_trends(campaign_df)
        
        # 11. 添加智能否定词建议
        campaign_df = add_intelligent_negation_suggestions(campaign_df, top_converting_roots, top_non_converting_roots)
        
        # 12. 添加分组建议
        campaign_df = add_intelligent_grouping_suggestions(campaign_df, top_converting_roots)
        
        # 13. 添加匹配类型建议
        campaign_df = add_match_type_suggestions(campaign_df)
        
        # 14. 添加出价建议
        campaign_df = add_intelligent_bid_suggestions(campaign_df)
        
        # 15. 添加ASIN相关建议
        campaign_df = add_asin_related_suggestions(campaign_df, asin_analysis)
        
        # 16. 添加关键词趋势标签
        campaign_df = add_keyword_trend_labels(campaign_df)
        
        # 17. 生成广告组合建议
        campaign_recommendations = generate_campaign_recommendations(campaign_df, top_converting_roots, 
                                                                   waste_keywords, asin_analysis)
        
        # 18. 计算广告组合统计
        campaign_stats = calculate_campaign_statistics(campaign_df, asin_analysis)
        
        # 19. 竞争对手ASIN分析
        competitor_asins = analyze_competitor_asins(campaign_df)
        
        # 20. 预算分配建议
        budget_recommendations = generate_budget_recommendations(campaign_df, asin_analysis, competitor_asins)
        
        # 21. 广告文案建议
        ad_copy_suggestions = generate_ad_copy_suggestions(campaign_df, top_converting_roots)
        
        # 22. 时间段表现分析
        time_performance_analysis = analyze_time_performance(campaign_df)
        
        # 23. 关键词扩展建议
        keyword_expansion_suggestions = generate_keyword_expansion_suggestions(campaign_df, top_converting_roots)
        
        # 24. 投放策略优化
        targeting_optimizations = generate_targeting_optimizations(campaign_df)
        
        print(f"广告组合 {campaign_name} 分析完成: 推荐{len(top_keywords)}个关键词, 否定{len(waste_keywords)}个关键词")
        print(f"发现{len(poor_performing_keywords)}个表现差的关键词")
        # 新增：找出表现差的关键词
        poor_performing_keywords = get_poor_performing_keywords(campaign_df)
        
        print(f"广告组合 {campaign_name} 分析完成: 推荐{len(top_keywords)}个关键词, 否定{len(waste_keywords)}个关键词")
        if not poor_performing_keywords.empty:
            print(f"发现{len(poor_performing_keywords)}个表现差的关键词")
        
        return {
            'campaign_name': campaign_name,
            'top_keywords': top_keywords,
            'waste_keywords': waste_keywords,
            'poor_performing_keywords': poor_performing_keywords,  # 新增
            'top_converting_roots': top_converting_roots,
            'top_non_converting_roots': top_non_converting_roots,
            'asin_analysis': asin_analysis,
            'search_term_asin_analysis': search_term_asin_analysis,
            'keyword_trends': keyword_trends,
            'campaign_df': campaign_df,
            'campaign_recommendations': campaign_recommendations,
            'campaign_stats': campaign_stats,
            'summary_stats': get_campaign_summary_stats(campaign_df),
            'competitor_asins': competitor_asins,
            'budget_recommendations': budget_recommendations,
            'ad_copy_suggestions': ad_copy_suggestions,
            'time_performance_analysis': time_performance_analysis,
            'keyword_expansion_suggestions': keyword_expansion_suggestions,
            'targeting_optimizations': targeting_optimizations,'
            'poor_performing_keywords': poor_performing_keywords,
        }
        
    except Exception as e:
        print(f"分析广告组合 {campaign_name} 时出错: {str(e)}")
        traceback.print_exc()
        return {
            'campaign_name': campaign_name,
            'top_keywords': pd.DataFrame(),
            'waste_keywords': pd.DataFrame(),
            'poor_performing_keywords': pd.DataFrame(),
            'top_converting_roots': [],
            'top_non_converting_roots': [],
            'asin_analysis': pd.DataFrame(),
            'search_term_asin_analysis': pd.DataFrame(),
            'keyword_trends': pd.DataFrame(),
            'campaign_df': df[df['campaign'] == campaign_name].copy() if 'campaign' in df.columns else pd.DataFrame(),
            'campaign_recommendations': [],
            'campaign_stats': {},
            'competitor_asins': pd.DataFrame(),
            'budget_recommendations': [],
            'ad_copy_suggestions': [],
            'time_performance_analysis': pd.DataFrame(),
            'keyword_expansion_suggestions': [],
            'targeting_optimizations': [],
            'poor_performing_keywords': poor_performing_keywords,
        }


# 修改 save_to_excel 函数，在保存广告组合分析时添加表现差的关键词
def save_to_excel(data, output_file):
    """将所有分析结果保存到Excel文件"""
    # 跟踪已使用的工作表名称，避免重复
    used_sheet_names = set()
    
    def get_unique_sheet_name(base_name):
        """获取唯一的工作表名称"""
        cleaned_name = clean_sheet_name(base_name)
        if cleaned_name not in used_sheet_names:
            used_sheet_names.add(cleaned_name)
            return cleaned_name
        else:
            # 如果名称已存在，添加数字后缀
            counter = 1
            while True:
                new_name = f"{cleaned_name[:28]}_{counter}" if len(cleaned_name) >= 28 else f"{cleaned_name}_{counter}"
                if new_name not in used_sheet_names:
                    used_sheet_names.add(new_name)
                    return new_name
                counter += 1
    
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            workbook = writer.book
            
            # 保存原始数据
            if '原始数据' in data and isinstance(data['原始数据'], pd.DataFrame) and not data['原始数据'].empty:
                sheet_name = get_unique_sheet_name('原始数据')
                data['原始数据'].to_excel(writer, sheet_name=sheet_name, index=False)
                apply_excel_formatting(writer.sheets[sheet_name], 0)
            
            # 保存广告组合分析 - 每个广告组合一个工作表
            if 'campaign_analysis' in data and data['campaign_analysis']:
                for idx, (campaign, analysis) in enumerate(data['campaign_analysis'].items()):
                    if analysis is None:
                        continue
                    
                    sheet_name = get_unique_sheet_name(campaign)
                    
                    # 创建主工作表
                    start_row = 0
                    
                    # 1. 写入广告组合建议
                    if 'campaign_recommendations' in analysis and analysis['campaign_recommendations']:
                        recommendations_df = pd.DataFrame(analysis['campaign_recommendations'], columns=['广告组合建议'])
                        recommendations_df.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
                        start_row += len(recommendations_df) + 3
                    
                    # 2. 写入摘要统计
                    if 'summary_stats' in analysis and analysis['summary_stats']:
                        summary_df = pd.DataFrame([analysis['summary_stats']])
                        summary_df.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
                        start_row += len(summary_df) + 3
                    
                    # 3. 写入TOP关键词
                    if not analysis['top_keywords'].empty:
                        analysis['top_keywords'].to_excel(writer, sheet_name=sheet_name, 
                                                         startrow=start_row, index=False)
                        start_row += len(analysis['top_keywords']) + 3
                    
                    # 4. 新增：写入表现差的关键词
                    if 'poor_performing_keywords' in analysis and not analysis['poor_performing_keywords'].empty:
                        # 添加标题
                        ws = writer.sheets[sheet_name]
                        title_cell = ws.cell(row=start_row+1, column=1, value="⚠️ 表现差的关键词（花费多、不出单、ACOS高）")
                        title_cell.font = Font(name='微软雅黑', size=12, bold=True, color='FF0000')
                        title_cell.fill = PatternFill(start_color='FFE6B3', end_color='FFE6B3', fill_type='solid')
                        start_row += 2
                        
                        analysis['poor_performing_keywords'].to_excel(writer, sheet_name=sheet_name, 
                                                                     startrow=start_row, index=False)
                        start_row += len(analysis['poor_performing_keywords']) + 3
                    
        
                    
                    # 5. 写入否定关键词
                    if not analysis['waste_keywords'].empty:
                        analysis['waste_keywords'].to_excel(writer, sheet_name=sheet_name, 
                                                           startrow=start_row, index=False)
                        start_row += len(analysis['waste_keywords']) + 3
                    
                    # 6. 写入高效词根
                    if analysis['top_converting_roots']:
                        converting_roots_df = pd.DataFrame(analysis['top_converting_roots'], 
                                                          columns=['高效词根', '加权得分'])
                        converting_roots_df.to_excel(writer, sheet_name=sheet_name, 
                                                    startrow=start_row, index=False)
                        start_row += len(converting_roots_df) + 3
                    
                    # 7. 写入无效词根
                    if analysis['top_non_converting_roots']:
                        non_converting_roots_df = pd.DataFrame(analysis['top_non_converting_roots'], 
                                                              columns=['无效词根', '出现次数'])
                        non_converting_roots_df.to_excel(writer, sheet_name=sheet_name, 
                                                        startrow=start_row, index=False)
                        start_row += len(non_converting_roots_df) + 3
                    
                    # 8. 写入ASIN分析
                    if not analysis['asin_analysis'].empty:
                        asin_analysis_df = analysis['asin_analysis']
                        asin_analysis_df.to_excel(writer, sheet_name=sheet_name, 
                                                 startrow=start_row, index=False)
                        start_row += len(asin_analysis_df) + 3
                    
                    # 9. 写入搜索词ASIN分析
                    if 'search_term_asin_analysis' in analysis and not analysis['search_term_asin_analysis'].empty:
                        search_asin_df = analysis['search_term_asin_analysis']
                        search_asin_df.to_excel(writer, sheet_name=sheet_name, 
                                               startrow=start_row, index=False)
                        start_row += len(search_asin_df) + 3
                    
                    # 10. 写入竞争对手ASIN分析
                    if isinstance(analysis['competitor_asins'], pd.DataFrame) and not analysis['competitor_asins'].empty:
                        competitor_df = analysis['competitor_asins']
                        competitor_df.to_excel(writer, sheet_name=sheet_name, 
                                              startrow=start_row, index=False)
                        start_row += len(competitor_df) + 3
                    
                    # 11. 写入预算分配建议
                    if 'budget_recommendations' in analysis and analysis['budget_recommendations']:
                        budget_df = pd.DataFrame(analysis['budget_recommendations'], columns=['预算分配建议'])
                        budget_df.to_excel(writer, sheet_name=sheet_name, 
                                          startrow=start_row, index=False)
                        start_row += len(budget_df) + 3
                    
                    # 12. 写入广告文案建议
                    if 'ad_copy_suggestions' in analysis and analysis['ad_copy_suggestions']:
                        ad_copy_df = pd.DataFrame(analysis['ad_copy_suggestions'], columns=['广告文案建议'])
                        ad_copy_df.to_excel(writer, sheet_name=sheet_name, 
                                           startrow=start_row, index=False)
                        start_row += len(ad_copy_df) + 3
                    
                    # 13. 写入时间段表现分析
                    if isinstance(analysis['time_performance_analysis'], pd.DataFrame) and not analysis['time_performance_analysis'].empty:
                        time_df = analysis['time_performance_analysis']
                        time_df.to_excel(writer, sheet_name=sheet_name, 
                                        startrow=start_row, index=False)
                        start_row += len(time_df) + 3
                    
                    # 14. 写入关键词扩展建议
                    if 'keyword_expansion_suggestions' in analysis and analysis['keyword_expansion_suggestions']:
                        expansion_df = pd.DataFrame(analysis['keyword_expansion_suggestions'], columns=['关键词扩展建议'])
                        expansion_df.to_excel(writer, sheet_name=sheet_name, 
                                             startrow=start_row, index=False)
                        start_row += len(expansion_df) + 3
                    
                    # 15. 写入投放策略优化
                    if 'targeting_optimizations' in analysis and analysis['targeting_optimizations']:
                        targeting_df = pd.DataFrame(analysis['targeting_optimizations'], columns=['投放策略优化建议'])
                        targeting_df.to_excel(writer, sheet_name=sheet_name, 
                                             startrow=start_row, index=False)
                    
                    # 应用格式化
                    apply_excel_formatting(writer.sheets[sheet_name], idx + 1)
            
            # 保存其他分析
            categories = ['搜索词分析', '广告活动分析']
            
            for category in categories:
                if category in data:
                    analysis_data = data[category]
                    
                    # 处理字典类型的分析结果
                    if isinstance(analysis_data, dict):
                        for sheet_idx, (sheet_key, df_section) in enumerate(analysis_data.items()):
                            if isinstance(df_section, pd.DataFrame) and not df_section.empty:
                                base_sheet_name = f"{category}_{sheet_key}" if sheet_key else category
                                sheet_name = get_unique_sheet_name(base_sheet_name)
                                df_section.to_excel(writer, sheet_name=sheet_name, index=False)
                                apply_excel_formatting(writer.sheets[sheet_name], len(used_sheet_names))
                    
                    # 处理DataFrame类型的分析结果
                    elif isinstance(analysis_data, pd.DataFrame) and not analysis_data.empty:
                        sheet_name = get_unique_sheet_name(category)
                        analysis_data.to_excel(writer, sheet_name=sheet_name, index=False)
                        apply_excel_formatting(writer.sheets[sheet_name], len(used_sheet_names))
            
            # 保存关键洞察
            if '关键洞察' in data and data['关键洞察']:
                sheet_name = get_unique_sheet_name('关键洞察')
                insights_df = pd.DataFrame(data['关键洞察'], columns=['洞察内容'])
                insights_df.to_excel(writer, sheet_name=sheet_name, index=False)
                apply_excel_formatting(writer.sheets[sheet_name], len(used_sheet_names))
        
        print(f"✅ Excel文件保存成功: {output_file}")
        
        # 添加可视化分析
        generate_visual_analysis(data['原始数据'], output_file)
        
        return True
        
    except Exception as e:
        print(f"❌ 保存Excel文件时出错: {str(e)}")
        traceback.print_exc()
        return False


# 在 generate_key_insights 函数中添加表现差关键词的概览
def generate_key_insights(df, campaign_analyses, search_term_analysis):
    """生成关键洞察与建议 - 增强版，增加ASIN分析和表现差关键词分析"""
    insights = []
    
    # 总体表现
    total = df.agg({
        'spend': 'sum',
        'sales': 'sum',
        'orders': 'sum',
        'impressions': 'sum',
        'clicks': 'sum'
    })
    
    overall_roas = total['sales'] / total['spend'] if total['spend'] > 0 else 0
    overall_acos = total['spend'] / total['sales'] if total['sales'] > 0 else 0
    overall_ctr = total['clicks'] / total['impressions'] if total['impressions'] > 0 else 0
    overall_cr = total['orders'] / total['clicks'] if total['clicks'] > 0 else 0
    
    insights.append("=" * 80)
    insights.append("📊 亚马逊广告智能分析报告")
    insights.append("=" * 80)
    insights.append("")
    insights.append("🎯 核心表现指标")
    insights.append(f"总花费: ¥{total['spend']:.2f}")
    insights.append(f"总销售额: ¥{total['sales']:.2f}")
    insights.append(f"总订单: {int(total['orders'])}")
    insights.append(f"总体ROAS: {overall_roas:.2f} | ACOS: {overall_acos:.1%}")
    insights.append(f"总体CTR: {overall_ctr:.2%} | 转化率: {overall_cr:.2%}")
    
    # 表现差关键词总览
    insights.append("")
    insights.append("⚠️ 表现差关键词总览")
    
    total_poor_keywords = 0
    total_poor_spend = 0
    
    for campaign_name, analysis in campaign_analyses.items():
        if analysis is None or 'poor_performing_keywords' not in analysis:
            continue
        
        poor_keywords = analysis['poor_performing_keywords']
        if isinstance(poor_keywords, pd.DataFrame) and not poor_keywords.empty:
            poor_keywords_count = len(poor_keywords)
            poor_spend = poor_keywords['spend'].sum()
            
            total_poor_keywords += poor_keywords_count
            total_poor_spend += poor_spend
    
    insights.append(f"表现差关键词总数: {total_poor_keywords}个")
    insights.append(f"表现差关键词总花费: ¥{total_poor_spend:.2f}")
    insights.append(f"预计优化后每月可节省: ¥{total_poor_spend * 4:.2f}")
    
    # 关键词质量分析
    high_quality = len(df[df['quality_score'] >= 70])
    medium_quality = len(df[(df['quality_score'] >= 50) & (df['quality_score'] < 70)])
    low_quality = len(df[df['quality_score'] < 50])
    
    insights.append("")
    insights.append("📈 关键词质量分析")
    insights.append(f"高质量关键词(≥70分): {high_quality}个 ({high_quality/len(df)*100:.1f}%)")
    insights.append(f"中等质量关键词(50-69分): {medium_quality}个 ({medium_quality/len(df)*100:.1f}%)")
    insights.append(f"低质量关键词(<50分): {low_quality}个 ({low_quality/len(df)*100:.1f}%)")
    
    # 相关性分析
    core_keywords = len(df[df['keyword'].apply(contains_protected_words)])
    insights.append(f"核心产品关键词: {core_keywords}个 ({core_keywords/len(df)*100:.1f}%)")
    
    # ASIN分析
    if 'asin' in df.columns and df['asin'].notna().any():
        asin_count = df['asin'].nunique()
        insights.append(f"关联ASIN数量: {asin_count}个")
    
    # 搜索词中的ASIN分析
    if 'extracted_asins' in df.columns:
        asin_search_terms = df[df['extracted_asins'].apply(lambda x: len(x) > 0)]
        insights.append(f"包含商品ASIN的搜索词: {len(asin_search_terms)}个 ({len(asin_search_terms)/len(df)*100:.1f}%)")
    
    # 否定词分析
    negation_keywords = len(df[df['negation_suggestion'].str.contains('否定', na=False)])
    if negation_keywords > 0:
        waste_spend = df[df['negation_suggestion'].str.contains('否定', na=False)]['spend'].sum()
        insights.append("")
        insights.append("💰 否定词优化机会")
        insights.append(f"建议否定关键词: {negation_keywords}个")
        insights.append(f"潜在节省花费: ¥{waste_spend:.2f}")
    
    # 广告组合表现概览
    insights.append("")
    insights.append("📊 广告组合表现概览")
    for campaign_name, analysis in campaign_analyses.items():
        if analysis and 'summary_stats' in analysis:
            stats = analysis['summary_stats']
            if '总花费' in stats and '总订单数' in stats:
                spend_str = stats['总花费']
                orders_str = stats['总订单数']
                
                # 添加表现差关键词信息
                poor_info = ""
                if 'poor_performing_keywords' in analysis and isinstance(analysis['poor_performing_keywords'], pd.DataFrame):
                    poor_count = len(analysis['poor_performing_keywords'])
                    if poor_count > 0:
                        poor_spend = analysis['poor_performing_keywords']['spend'].sum()
                        poor_info = f", 表现差:{poor_count}个(¥{poor_spend:.2f})"
                
                insights.append(f"• {campaign_name}: {spend_str}, 订单{orders_str}{poor_info}")
    
    # 最佳表现关键词
    if '最佳关键词分析' in search_term_analysis:
        best_df = search_term_analysis['最佳关键词分析']
        if not best_df.empty:
            insights.append("")
            insights.append("🏆 各广告组合最佳关键词")
            for _, row in best_df.head(5).iterrows():
                insights.append(f"• {row['广告组合']}: {row['最佳关键词']} (得分:{row['综合得分']:.1f}, ROAS:{row['ROAS']:.2f})")
    
    # 表现差关键词优化建议
    if total_poor_keywords > 0:
        insights.append("")
        insights.append("🎯 表现差关键词优化建议")
        insights.append("1. 高花费无转化关键词：立即否定或暂停")
        insights.append("2. 高ACOS关键词：降低出价50%或暂停")
        insights.append("3. 低ROAS关键词：优化出价或匹配类型")
        insights.append("4. 低CTR关键词：优化广告文案或图片")
    
    # 亚马逊算法优化建议
    insights.append("")
    insights.append("🤖 亚马逊广告算法优化建议")
    insights.append("1. 优先优化CTR和相关性得分，这两项直接影响广告排名")
    insights.append("2. 高ROAS关键词适当提高出价，获取更多流量")
    insights.append("3. 及时添加否定词，避免无效花费影响广告质量")
    insights.append("4. 重点关注表现差关键词，减少无效花费")
    insights.append("5. 根据搜索词表现调整匹配类型")
    
    # 本周执行清单
    insights.append("")
    insights.append("📋 本周优化执行清单")
    insights.append("✅ 立即执行:")
    insights.append("   1. 查看各广告组合工作表的'表现差的关键词'")
    insights.append("   2. 添加所有'否定精准'建议到否定列表")
    insights.append("   3. 暂停所有'暂停'建议的关键词")
    insights.append("   4. 处理高花费无转化的表现差关键词")
    insights.append("")
    insights.append("📅 本周内完成:")
    insights.append("   1. 根据'分组建议'重组广告结构")
    insights.append("   2. 优化'高潜力关键词'的落地页相关性")
    insights.append("   3. 分析表现差关键词的原因并针对性优化")
    
    return insights

# 在 main 函数的输出部分添加表现差关键词的概览
def main():
    """主程序"""
    # ... [原有代码保持不变] ...
    
    if save_to_excel(output_data, output_file):
        print(f"\n{'='*80}")
        print("🎉 亚马逊广告智能分析完成！")
        print(f"📁 Excel详细报告: {output_file}")
        print(f"{'='*80}")
        
        # ... [原有代码保持不变] ...
        
        # 新增：表现差关键词概览
        print(f"\n⚠️ 表现差关键词概览:")
        
        total_poor_keywords = 0
        total_poor_spend = 0
        
        for campaign_name, analysis in campaign_analyses.items():
            if analysis is None:
                continue
            
            if 'poor_performing_keywords' in analysis and not analysis['poor_performing_keywords'].empty:
                poor_keywords_count = len(analysis['poor_performing_keywords'])
                poor_spend = analysis['poor_performing_keywords']['spend'].sum()
                
                total_poor_keywords += poor_keywords_count
                total_poor_spend += poor_spend
                
                if poor_keywords_count > 0:
                    print(f"• {campaign_name}: {poor_keywords_count}个表现差关键词，花费¥{poor_spend:.2f}")
        
        if total_poor_keywords > 0:
            print(f"\n📊 表现差关键词总结:")
            print(f"• 总共有{total_poor_keywords}个表现差关键词")
            print(f"• 总计花费¥{total_poor_spend:.2f}")
            print(f"• 预计优化后每月可节省¥{total_poor_spend * 4:.2f}")
            
            print(f"\n🎯 表现差关键词优化建议:")
            print("1. 打开Excel报告，查看各广告组合工作表的'表现差的关键词'部分")
            print("2. 根据'表现差原因'采取相应的优化措施")
            print("3. 高花费无转化关键词：立即否定或暂停")
            print("4. 高ACOS关键词：降低出价50%或暂停")
            print("5. 低ROAS关键词：优化出价或匹配类型")
            print("6. 低CTR关键词：优化广告文案或图片")
            print("7. 低转化率关键词：优化产品详情页")
        else:
            print("✅ 恭喜！未发现明显表现差的关键词")
        
        # 操作建议
        print(f"\n🚀 立即操作建议:")
        print("1. 打开Excel报告，查看'关键洞察'工作表")
        print("2. 查看各广告组合工作表的详细建议")
        print("3. 根据'否定建议'添加否定词到广告后台")
        print("4. 根据'表现差关键词建议'优化或暂停表现差的关键词")
        print("5. 实施'出价建议'中的调整")
        print("6. 根据'分组建议'优化广告结构")
        print("7. 查看'可视化分析'工作表的图表")
        print("8. 分析'搜索词ASIN分析'识别竞品机会")
        print("9. 参考'广告文案建议'优化广告内容")
        
    else:
        print("错误: 生成Excel报告失败")
    
    # ... [原有代码保持不变] ...


# ================ 新增：高级分析模块函数 ================

def perform_market_analysis(df):
    """执行市场分析：市场规模、增长趋势、竞争格局"""
    try:
        analysis = {}
        
        # 1. 市场规模评估
        total_spend = df['spend'].sum()
        total_sales = df['sales'].sum()
        
        # 基于花费和销售额估计市场份额
        estimated_market_size = total_sales * 100  # 假设占1%市场份额
        analysis['市场规模评估'] = {
            '广告花费': f"¥{total_spend:,.2f}",
            '产生销售额': f"¥{total_sales:,.2f}",
            'ROAS': f"{total_sales/total_spend:.2f}" if total_spend > 0 else "N/A",
            '估计市场总规模': f"¥{estimated_market_size:,.2f}",
            '市场份额估计': f"{(total_sales/estimated_market_size*100):.2f}%" if estimated_market_size > 0 else "N/A"
        }
        
        # 2. 增长趋势分析
        if 'date' in df.columns and not df['date'].isna().all():
            df_date = df.copy()
            df_date['week'] = df_date['date'].dt.to_period('W')
            weekly_growth = df_date.groupby('week').agg({
                'spend': 'sum',
                'sales': 'sum',
                'orders': 'sum'
            }).reset_index()
            
            if len(weekly_growth) > 1:
                spend_growth = (weekly_growth['spend'].iloc[-1] / weekly_growth['spend'].iloc[-2] - 1) * 100 if weekly_growth['spend'].iloc[-2] > 0 else 0
                sales_growth = (weekly_growth['sales'].iloc[-1] / weekly_growth['sales'].iloc[-2] - 1) * 100 if weekly_growth['sales'].iloc[-2] > 0 else 0
                
                analysis['增长趋势'] = {
                    '周环比花费增长': f"{spend_growth:.1f}%",
                    '周环比销售额增长': f"{sales_growth:.1f}%",
                    '趋势判断': '上升' if sales_growth > 10 else ('稳定' if sales_growth > 0 else '下降')
                }
        
        # 3. 竞争格局分析
        if 'match_type' in df.columns:
            match_analysis = df.groupby('match_type').agg({
                'spend': 'sum',
                'sales': 'sum',
                'impressions': 'sum',
                'clicks': 'sum'
            }).reset_index()
            
            analysis['竞争格局'] = {
                '匹配类型分布': match_analysis.to_dict('records'),
                '竞争激烈度': '高' if len(df[df['impressions'] > 100]) > 10 else '中等'
            }
        
        # 4. 价格带分析
        if 'cpc' in df.columns and len(df[df['cpc'] > 0]) > 0:
            avg_cpc = df[df['cpc'] > 0]['cpc'].mean()
            cpc_std = df[df['cpc'] > 0]['cpc'].std()
            
            analysis['价格带分析'] = {
                '平均CPC': f"¥{avg_cpc:.2f}",
                'CPC标准差': f"¥{cpc_std:.2f}",
                '价格竞争程度': '高' if cpc_std > avg_cpc * 0.5 else '中等'
            }
        
        return analysis
        
    except Exception as e:
        print(f"市场分析出错: {str(e)}")
        return {}


def perform_customer_analysis(df):
    """执行客户分析：细分、留存、生命周期价值"""
    try:
        analysis = {}
        
        # 1. 客户细分分析
        # 基于关键词类型进行客户细分
        keyword_categories = categorize_keywords_by_intent(df)
        if not keyword_categories.empty:
            analysis['客户细分'] = {
                '细分维度': '购买意图',
                '细分结果': keyword_categories.to_dict('records')
            }
        
        # 2. 留存分析
        converting_keywords = df[df['orders'] > 0]
        if len(converting_keywords) > 0:
            repeat_orders = len(converting_keywords[converting_keywords['orders'] > 1])
            analysis['留存分析'] = {
                '总出单关键词': len(converting_keywords),
                '重复出单关键词': repeat_orders,
                '关键词留存率': f"{(repeat_orders/len(converting_keywords)*100):.1f}%" if len(converting_keywords) > 0 else "0%"
            }
        
        # 3. 客户生命周期价值分析
        total_sales = df['sales'].sum()
        total_orders = df['orders'].sum()
        total_spend = df['spend'].sum()
        
        if total_orders > 0:
            avg_order_value = total_sales / total_orders
            acquisition_cost = total_spend / total_orders if total_orders > 0 else 0
            
            analysis['生命周期价值'] = {
                '平均订单价值': f"¥{avg_order_value:.2f}",
                '获客成本': f"¥{acquisition_cost:.2f}",
                'ROI': f"{(avg_order_value/acquisition_cost):.2f}" if acquisition_cost > 0 else "N/A",
                '客户价值评估': '高价值' if avg_order_value > acquisition_cost * 3 else '中等价值'
            }
        
        # 4. 客户行为分析
        if 'ctr' in df.columns and 'conversion_rate' in df.columns:
            high_intent = df[(df['ctr'] > 0.005) & (df['conversion_rate'] > 0.02)]
            low_intent = df[(df['ctr'] < 0.002) | (df['conversion_rate'] < 0.005)]
            
            analysis['客户行为分析'] = {
                '高意向客户关键词': len(high_intent),
                '低意向客户关键词': len(low_intent),
                '高意向占比': f"{(len(high_intent)/len(df)*100):.1f}%" if len(df) > 0 else "0%"
            }
        
        return analysis
        
    except Exception as e:
        print(f"客户分析出错: {str(e)}")
        return {}


def perform_competition_analysis(df, competitor_asins):
    """执行竞争分析：竞争对手识别、SWOT分析、竞争策略"""
    try:
        analysis = {}
        
        # 1. 竞争对手识别
        analysis['竞争对手识别'] = {}
        
        if isinstance(competitor_asins, pd.DataFrame) and not competitor_asins.empty:
            top_competitors = competitor_asins.head(5)
            analysis['竞争对手识别']['主要竞争对手ASIN'] = top_competitors[['竞争对手ASIN', '出现次数', '威胁等级']].to_dict('records')
        
        # 从搜索词中识别竞争对手
        if 'keyword' in df.columns:
            competitor_keywords = []
            competitor_terms = ['vs', 'versus', 'compare', 'cheaper than', 'alternative to', 'like']
            
            for keyword in df['keyword'].astype(str):
                keyword_lower = keyword.lower()
                for term in competitor_terms:
                    if term in keyword_lower:
                        competitor_keywords.append(keyword)
                        break
            
            if competitor_keywords:
                analysis['竞争对手识别']['比较型关键词'] = competitor_keywords[:10]
        
        # 2. SWOT分析
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []
        
        # 优势分析
        high_roas = df[df['roas'] > 3]
        if len(high_roas) > 5:
            strengths.append(f"拥有{len(high_roas)}个高ROAS关键词（ROAS>3）")
        
        high_ctr = df[df['ctr'] > 0.005]
        if len(high_ctr) > 10:
            strengths.append(f"拥有{len(high_ctr)}个高CTR关键词（CTR>0.5%）")
        
        # 劣势分析
        waste_keywords = df[(df['orders'] == 0) & (df['spend'] > 0.5)]
        if len(waste_keywords) > 5:
            weaknesses.append(f"有{len(waste_keywords)}个无转化花费关键词")
        
        low_ctr = df[df['ctr'] < 0.001]
        if len(low_ctr) > 10:
            weaknesses.append(f"有{len(low_ctr)}个低CTR关键词（CTR<0.1%）")
        
        # 机会分析
        high_potential = df[(df['clicks'] > 5) & (df['orders'] == 0) & (df['quality_score'] > 50)]
        if len(high_potential) > 5:
            opportunities.append(f"有{len(high_potential)}个高潜力关键词（有点击无转化）")
        
        # 威胁分析
        if isinstance(competitor_asins, pd.DataFrame) and not competitor_asins.empty:
            high_threat = competitor_asins[competitor_asins['威胁等级'] == '高威胁']
            if len(high_threat) > 0:
                threats.append(f"面临{len(high_threat)}个高威胁竞争对手")
        
        analysis['SWOT分析'] = {
            '优势(Strengths)': strengths,
            '劣势(Weaknesses)': weaknesses,
            '机会(Opportunities)': opportunities,
            '威胁(Threats)': threats
        }
        
        # 3. 竞争策略建议
        strategies = []
        
        if len(high_roas) > 5:
            strategies.append("差异化策略：聚焦高ROAS关键词，建立竞争优势")
        
        if len(competitor_keywords) > 5:
            strategies.append("竞争策略：针对比较型关键词优化产品卖点")
        
        if len(waste_keywords) > 5:
            strategies.append("成本控制：及时否定无效关键词，降低ACOS")
        
        if len(high_potential) > 5:
            strategies.append("增长策略：优化高潜力关键词的转化路径")
        
        analysis['竞争策略'] = strategies
        
        return analysis
        
    except Exception as e:
        print(f"竞争分析出错: {str(e)}")
        return {}


def perform_forecast_analysis(df):
    """执行预测分析：销售预测、需求预测、风险预测"""
    try:
        analysis = {}
        
        # 1. 销售预测
        total_sales = df['sales'].sum()
        total_spend = df['spend'].sum()
        
        if total_spend > 0:
            current_roas = total_sales / total_spend
            
            # 基于历史趋势的简单预测
            if 'date' in df.columns and not df['date'].isna().all():
                df_date = df.copy()
                df_date['week'] = df_date['date'].dt.to_period('W')
                weekly_sales = df_date.groupby('week')['sales'].sum().reset_index()
                
                if len(weekly_sales) >= 2:
                    # 计算周均增长率
                    sales_values = weekly_sales['sales'].values
                    growth_rates = []
                    for i in range(1, len(sales_values)):
                        if sales_values[i-1] > 0:
                            growth_rate = (sales_values[i] / sales_values[i-1] - 1) * 100
                            growth_rates.append(growth_rate)
                    
                    if growth_rates:
                        avg_growth = sum(growth_rates) / len(growth_rates)
                        
                        # 4周销售预测
                        forecast_4weeks = []
                        current_sales = sales_values[-1]
                        for week in range(1, 5):
                            forecast_sales = current_sales * (1 + avg_growth/100) ** week
                            forecast_4weeks.append({
                                f'第{week}周预测': f"¥{forecast_sales:,.2f}",
                                '增长率': f"{avg_growth:.1f}%"
                            })
                        
                        analysis['销售预测'] = {
                            '当前周销售额': f"¥{current_sales:,.2f}",
                            '平均周增长率': f"{avg_growth:.1f}%",
                            '4周销售预测': forecast_4weeks
                        }
        
        # 2. 需求预测
        # 基于搜索量和季节性的需求预测
        total_impressions = df['impressions'].sum()
        total_clicks = df['clicks'].sum()
        
        if total_impressions > 0:
            avg_ctr = total_clicks / total_impressions
            estimated_demand = total_impressions * avg_ctr * 0.02  # 假设转化率2%
            
            analysis['需求预测'] = {
                '总展示量': f"{total_impressions:,}",
                '估计潜在需求': f"{estimated_demand:.0f}个点击",
                '市场热度': '高' if total_impressions > 10000 else ('中等' if total_impressions > 5000 else '低')
            }
        
        # 3. 风险预测
        risks = []
        
        # 财务风险
        high_spend_no_conversion = df[(df['orders'] == 0) & (df['spend'] > 2)]
        if len(high_spend_no_conversion) > 0:
            total_waste = high_spend_no_conversion['spend'].sum()
            risks.append(f"财务风险：{len(high_spend_no_conversion)}个关键词花费¥{total_waste:.2f}无转化")
        
        # 市场风险
        low_ctr_keywords = df[df['ctr'] < 0.001]
        if len(low_ctr_keywords) > 10:
            risks.append(f"市场风险：{len(low_ctr_keywords)}个关键词CTR低于0.1%")
        
        # 竞争风险
        if '竞争分析' in analysis and '竞争对手识别' in analysis['竞争分析']:
            competitor_count = len(analysis['竞争分析']['竞争对手识别'].get('主要竞争对手ASIN', []))
            if competitor_count > 3:
                risks.append(f"竞争风险：发现{competitor_count}个主要竞争对手")
        
        analysis['风险预测'] = {
            '风险类型': ['财务风险', '市场风险', '竞争风险'],
            '具体风险': risks
        }
        
        return analysis
        
    except Exception as e:
        print(f"预测分析出错: {str(e)}")
        return {}


def perform_optimization_analysis(df):
    """执行优化分析：关键词、出价、预算、广告文案优化"""
    try:
        analysis = {}
        
        # 1. 关键词优化分析
        keyword_optimizations = []
        
        # 低效关键词优化
        inefficient_keywords = df[(df['orders'] == 0) & (df['spend'] > 0.5) & (df['impressions'] > 50)]
        if len(inefficient_keywords) > 0:
            keyword_optimizations.append({
                '优化类型': '否定优化',
                '关键词数量': len(inefficient_keywords),
                '潜在节省': f"¥{inefficient_keywords['spend'].sum():.2f}",
                '建议': '添加到否定关键词列表'
            })
        
        # 高潜力关键词优化
        high_potential = df[(df['clicks'] > 5) & (df['orders'] == 0) & (df['ctr'] > 0.003)]
        if len(high_potential) > 0:
            keyword_optimizations.append({
                '优化类型': '潜力挖掘',
                '关键词数量': len(high_potential),
                '平均CTR': f"{high_potential['ctr'].mean():.3f}",
                '建议': '优化落地页或调整匹配类型'
            })
        
        analysis['关键词优化'] = keyword_optimizations
        
        # 2. 出价优化分析
        bid_optimizations = []
        
        # 高质量关键词出价优化
        high_quality = df[(df['quality_score'] > 70) & (df['roas'] > 2)]
        if len(high_quality) > 0:
            avg_cpc = high_quality['cpc'].mean()
            bid_optimizations.append({
                '关键词类型': '高质量高ROAS',
                '数量': len(high_quality),
                '平均CPC': f"¥{avg_cpc:.2f}",
                '建议': f'提高出价10-20%，目标CPC ¥{avg_cpc*1.15:.2f}'
            })
        
        # 中等质量关键词出价优化
        medium_quality = df[(df['quality_score'].between(50, 70)) & (df['roas'].between(1, 2))]
        if len(medium_quality) > 0:
            avg_cpc = medium_quality['cpc'].mean()
            bid_optimizations.append({
                '关键词类型': '中等质量',
                '数量': len(medium_quality),
                '平均CPC': f"¥{avg_cpc:.2f}",
                '建议': '维持当前出价，监控表现'
            })
        
        analysis['出价优化'] = bid_optimizations
        
        # 3. 预算优化分析
        total_spend = df['spend'].sum()
        total_sales = df['sales'].sum()
        
        if total_spend > 0:
            roas = total_sales / total_spend
            
            budget_suggestions = []
            if roas > 3:
                budget_suggestions.append(f"整体ROAS优秀({roas:.2f})，可增加10-20%预算")
            elif roas > 1.5:
                budget_suggestions.append(f"整体ROAS良好({roas:.2f})，保持当前预算")
            else:
                budget_suggestions.append(f"整体ROAS偏低({roas:.2f})，优化后考虑增加预算")
            
            analysis['预算优化'] = {
                '总花费': f"¥{total_spend:.2f}",
                '总销售额': f"¥{total_sales:.2f}",
                '整体ROAS': f"{roas:.2f}",
                '建议': budget_suggestions
            }
        
        # 4. 广告文案优化分析
        ad_copy_analysis = []
        
        # 分析高效词根
        converting_keywords = df[df['orders'] > 0]
        if len(converting_keywords) > 0:
            # 提取高频词根
            all_roots = []
            for keyword in converting_keywords['keyword']:
                roots = extract_roots(keyword)
                all_roots.extend(roots)
            
            if all_roots:
                root_counter = Counter(all_roots)
                top_roots = root_counter.most_common(5)
                
                ad_copy_analysis.append({
                    '优化维度': '核心卖点词',
                    '高频词根': [root for root, count in top_roots],
                    '建议': '将这些词根融入广告标题和描述'
                })
        
        # 分析高CTR关键词的特征
        high_ctr = df[df['ctr'] > df['ctr'].quantile(0.75)].head(10)
        if len(high_ctr) > 0:
            # 分析共同特征
            features = []
            for keyword in high_ctr['keyword']:
                if 'buy' in str(keyword).lower():
                    features.append('购买意图词')
                if 'best' in str(keyword).lower():
                    features.append('最佳/顶级描述')
                if 'review' in str(keyword).lower():
                    features.append('评价/评测词')
            
            if features:
                feature_counter = Counter(features)
                top_features = feature_counter.most_common(3)
                ad_copy_analysis.append({
                    '优化维度': '高CTR关键词特征',
                    '特征分析': [f"{feature}({count}次)" for feature, count in top_features],
                    '建议': '在文案中强化这些特征'
                })
        
        analysis['广告文案优化'] = ad_copy_analysis
        
        return analysis
        
    except Exception as e:
        print(f"优化分析出错: {str(e)}")
        return {}


def perform_risk_analysis(df, asin_analysis, competitor_asins):
    """执行风险分析：财务、运营、市场、合规风险"""
    try:
        analysis = {}
        risks = []
        mitigations = []
        
        # 1. 财务风险
        total_spend = df['spend'].sum()
        total_sales = df['sales'].sum()
        
        if total_spend > 0:
            roas = total_sales / total_spend
            acos = total_spend / total_sales if total_sales > 0 else 0
            
            if roas < 1:
                risks.append(f"财务风险：整体ROAS偏低({roas:.2f})，广告花费回报不足")
                mitigations.append("立即优化ACOS>100%的关键词，暂停无转化高花费关键词")
            elif roas < 1.5:
                risks.append(f"财务风险：整体ROAS中等({roas:.2f})，利润率偏低")
                mitigations.append("优化中等表现关键词，提高转化率")
        
        # 2. 运营风险
        # 依赖少数关键词的风险
        top_5_keywords = df.nlargest(5, 'spend')
        top_5_spend_ratio = top_5_keywords['spend'].sum() / total_spend if total_spend > 0 else 0
        
        if top_5_spend_ratio > 0.5:
            risks.append(f"运营风险：前5关键词花费占比过高({top_5_spend_ratio:.1%})")
            mitigations.append("分散关键词预算，拓展新关键词降低依赖")
        
        # 3. 市场风险
        low_ctr_keywords = df[df['ctr'] < 0.001]
        if len(low_ctr_keywords) > len(df) * 0.3:  # 超过30%关键词CTR低于0.1%
            risks.append(f"市场风险：{len(low_ctr_keywords)}个关键词CTR极低，市场竞争力不足")
            mitigations.append("优化广告相关性，测试新广告文案")
        
        # 4. 竞争风险
        if isinstance(competitor_asins, pd.DataFrame) and not competitor_asins.empty:
            high_threat = competitor_asins[competitor_asins['威胁等级'] == '高威胁']
            if len(high_threat) > 0:
                risks.append(f"竞争风险：发现{len(high_threat)}个高威胁竞争对手")
                mitigations.append("分析竞争对手优势，优化自身产品差异化卖点")
        
        # 5. 合规风险
        # 检查是否有违反亚马逊政策的风险
        suspicious_keywords = []
        policy_terms = ['free', '100%', 'guarantee', 'best', '#1', 'top']
        
        for keyword in df['keyword'].astype(str):
            keyword_lower = keyword.lower()
            for term in policy_terms:
                if term in keyword_lower and len(keyword_lower.split()) <= 3:
                    suspicious_keywords.append(keyword)
                    break
        
        if suspicious_keywords:
            risks.append(f"合规风险：发现{len(suspicious_keywords)}个可能违反广告政策的关键词")
            mitigations.append("审查关键词是否符合亚马逊广告政策，避免夸大宣传")
        
        analysis['风险识别'] = {
            '风险类型': ['财务风险', '运营风险', '市场风险', '竞争风险', '合规风险'],
            '具体风险': risks
        }
        
        analysis['风险缓解措施'] = mitigations
        
        # 风险评估矩阵
        risk_matrix = []
        for i, risk in enumerate(risks):
            # 简单评估影响和概率
            if '财务风险' in risk:
                impact = '高'
                probability = '中' if roas < 1.5 else '低'
            elif '运营风险' in risk:
                impact = '中'
                probability = '高' if top_5_spend_ratio > 0.5 else '中'
            elif '市场风险' in risk:
                impact = '中'
                probability = '高' if len(low_ctr_keywords) > len(df) * 0.3 else '中'
            elif '竞争风险' in risk:
                impact = '高'
                probability = '中' if len(high_threat) > 0 else '低'
            elif '合规风险' in risk:
                impact = '高'
                probability = '低'
            else:
                impact = '中'
                probability = '中'
            
            risk_matrix.append({
                '风险描述': risk,
                '影响程度': impact,
                '发生概率': probability,
                '风险等级': '高' if impact == '高' and probability == '高' else ('中' if impact == '中' or probability == '中' else '低')
            })
        
        analysis['风险评估矩阵'] = risk_matrix
        
        return analysis
        
    except Exception as e:
        print(f"风险分析出错: {str(e)}")
        return {}


def perform_growth_analysis(df, search_term_asin_analysis):
    """执行增长分析：机会识别、扩张潜力、增长预测"""
    try:
        analysis = {}
        
        # 1. 机会识别
        opportunities = []
        
        # 高潜力关键词机会
        high_potential = df[(df['clicks'] > 5) & (df['orders'] == 0) & (df['quality_score'] > 50)]
        if len(high_potential) > 0:
            opportunities.append({
                '机会类型': '关键词优化',
                '描述': f"发现{len(high_potential)}个高潜力关键词（有点击无转化）",
                '增长潜力': '中等',
                '建议措施': '优化落地页、调整匹配类型、测试不同出价'
            })
        
        # 长尾关键词机会
        df['word_count'] = df['keyword'].apply(lambda x: len(str(x).split()))
        long_tail = df[df['word_count'] >= 4]
        converting_long_tail = long_tail[long_tail['orders'] > 0]
        
        if len(converting_long_tail) > 0 and len(long_tail) > 0:
            long_tail_conversion_rate = len(converting_long_tail) / len(long_tail)
            opportunities.append({
                '机会类型': '长尾关键词',
                '描述': f"长尾关键词转化率{long_tail_conversion_rate:.1%}",
                '增长潜力': '高',
                '建议措施': '拓展更多长尾关键词，成本低转化高'
            })
        
        # ASIN关联机会
        if isinstance(search_term_asin_analysis, pd.DataFrame) and not search_term_asin_analysis.empty:
            high_performance_asins = search_term_asin_analysis[search_term_asin_analysis['performance_rating'] == '优秀']
            if len(high_performance_asins) > 0:
                opportunities.append({
                    '机会类型': 'ASIN关联',
                    '描述': f"发现{len(high_performance_asins)}个高表现关联ASIN",
                    '增长潜力': '高',
                    '建议措施': '围绕高表现ASIN拓展关键词和广告活动'
                })
        
        analysis['增长机会识别'] = opportunities
        
        # 2. 扩张潜力分析
        expansion_potentials = []
        
        # 市场扩张潜力
        total_impressions = df['impressions'].sum()
        if total_impressions > 0:
            market_coverage_estimate = total_impressions / 10000  # 简单估算
            expansion_potentials.append({
                '扩张维度': '市场覆盖',
                '当前水平': f"{total_impressions:,}次展示",
                '扩张潜力': '高' if market_coverage_estimate < 10 else '中等',
                '潜力评估': f"估计市场覆盖率约{market_coverage_estimate:.1f}%"
            })
        
        # 产品线扩张潜力
        if 'asin' in df.columns:
            unique_asins = df['asin'].nunique()
            expansion_potentials.append({
                '扩张维度': '产品线',
                '当前水平': f"{unique_asins}个ASIN",
                '扩张潜力': '高' if unique_asins < 3 else '中等',
                '潜力评估': '可考虑拓展相关产品线' if unique_asins < 5 else '产品线较为完善'
            })
        
        analysis['扩张潜力分析'] = expansion_potentials
        
        # 3. 增长预测
        growth_forecasts = []
        
        # 基于历史数据的增长预测
        if 'date' in df.columns and not df['date'].isna().all():
            df_date = df.copy()
            df_date['week'] = df_date['date'].dt.to_period('W')
            weekly_sales = df_date.groupby('week')['sales'].sum().reset_index()
            
            if len(weekly_sales) >= 2:
                # 计算平均增长率
                sales_values = weekly_sales['sales'].values
                growth_rates = []
                for i in range(1, len(sales_values)):
                    if sales_values[i-1] > 0:
                        growth_rate = (sales_values[i] / sales_values[i-1] - 1) * 100
                        growth_rates.append(growth_rate)
                
                if growth_rates:
                    avg_growth = sum(growth_rates) / len(growth_rates)
                    
                    # 月度增长预测
                    current_month_sales = df_date['sales'].sum()
                    monthly_growth_scenarios = []
                    
                    for scenario in ['保守', '基准', '乐观']:
                        if scenario == '保守':
                            growth_rate = avg_growth * 0.7
                        elif scenario == '基准':
                            growth_rate = avg_growth
                        else:  # 乐观
                            growth_rate = avg_growth * 1.3
                        
                        forecast_sales = current_month_sales * (1 + growth_rate/100)
                        monthly_growth_scenarios.append({
                            '场景': scenario,
                            '增长率': f"{growth_rate:.1f}%",
                            '预测月销售额': f"¥{forecast_sales:,.2f}"
                        })
                    
                    growth_forecasts.append({
                        '预测维度': '月度销售',
                        '当前月销售额': f"¥{current_month_sales:,.2f}",
                        '历史平均增长率': f"{avg_growth:.1f}%",
                        '不同场景预测': monthly_growth_scenarios
                    })
        
        analysis['增长预测'] = growth_forecasts
        
        # 4. 增长策略建议
        growth_strategies = []
        
        if len(high_potential) > 5:
            growth_strategies.append("优化策略：重点优化高潜力关键词转化路径")
        
        if len(long_tail) > 20 and len(converting_long_tail) > 5:
            growth_strategies.append("扩张策略：大力发展长尾关键词，提升转化率")
        
        if 'asin' in df.columns and df['asin'].nunique() < 5:
            growth_strategies.append("产品策略：拓展产品线，增加ASIN覆盖")
        
        analysis['增长策略'] = growth_strategies
        
        return analysis
        
    except Exception as e:
        print(f"增长分析出错: {str(e)}")
        return {}


def perform_seasonal_analysis(df):
    """执行季节性分析：模式识别、库存规划、营销日历"""
    try:
        analysis = {}
        
        if 'date' not in df.columns or df['date'].isna().all():
            return analysis
        
        df_date = df.copy()
        
        # 1. 季节性模式识别
        seasonal_patterns = []
        
        # 按月份分析
        df_date['month'] = df_date['date'].dt.month
        monthly_performance = df_date.groupby('month').agg({
            'sales': 'sum',
            'orders': 'sum',
            'spend': 'sum',
            'impressions': 'sum'
        }).reset_index()
        
        if len(monthly_performance) > 0:
            # 找出销售高峰月份
            peak_month = monthly_performance.loc[monthly_performance['sales'].idxmax()]
            trough_month = monthly_performance.loc[monthly_performance['sales'].idxmin()]
            
            seasonal_patterns.append({
                '分析维度': '月度销售',
                '销售高峰月': f"{peak_month['month']}月 (¥{peak_month['sales']:.2f})",
                '销售低谷月': f"{trough_month['month']}月 (¥{trough_month['sales']:.2f})",
                '季节性强度': '强' if peak_month['sales'] > trough_month['sales'] * 2 else '中等'
            })
        
        # 按季度分析
        df_date['quarter'] = df_date['date'].dt.quarter
        quarterly_performance = df_date.groupby('quarter').agg({
            'sales': 'sum',
            'orders': 'sum'
        }).reset_index()
        
        if len(quarterly_performance) > 0:
            peak_quarter = quarterly_performance.loc[quarterly_performance['sales'].idxmax()]
            seasonal_patterns.append({
                '分析维度': '季度销售',
                '最佳销售季': f"第{peak_quarter['quarter']}季度",
                '季度销售额': f"¥{peak_quarter['sales']:.2f}",
                '占总销售额': f"{(peak_quarter['sales']/df_date['sales'].sum()*100):.1f}%"
            })
        
        analysis['季节性模式'] = seasonal_patterns
        
        # 2. 库存规划建议
        inventory_suggestions = []
        
        if len(monthly_performance) >= 3:
            # 计算销售波动性
            sales_std = monthly_performance['sales'].std()
            sales_mean = monthly_performance['sales'].mean()
            cv = sales_std / sales_mean if sales_mean > 0 else 0
            
            if cv > 0.5:
                inventory_suggestions.append("高季节性：建议采用动态库存策略，高峰月增加30-50%库存")
            elif cv > 0.3:
                inventory_suggestions.append("中等季节性：建议采用缓冲库存策略，高峰月增加20-30%库存")
            else:
                inventory_suggestions.append("低季节性：采用稳定库存策略，保持安全库存水平")
        
        # 基于关键词趋势的库存建议
        seasonal_keywords = []
        season_terms = {
            '圣诞': ['christmas', 'xmas', 'holiday', 'gift'],
            '新年': ['new year', 'resolution', 'fitness'],
            '夏季': ['summer', 'hot', 'cool', 'fan'],
            '冬季': ['winter', 'cold', 'heater', 'warm']
        }
        
        for season, terms in season_terms.items():
            for keyword in df['keyword'].astype(str):
                keyword_lower = keyword.lower()
                if any(term in keyword_lower for term in terms):
                    seasonal_keywords.append((season, keyword))
                    break
        
        if seasonal_keywords:
            season_counter = Counter([season for season, _ in seasonal_keywords])
            top_season = season_counter.most_common(1)[0] if season_counter else None
            
            if top_season:
                inventory_suggestions.append(f"检测到{top_season[1]}个{top_season[0]}季关键词，建议提前规划库存")
        
        analysis['库存规划建议'] = inventory_suggestions
        
        # 3. 营销日历建议
        marketing_calendar = []
        
        # 重要营销节点
        important_months = {
            1: '新年促销',
            2: '情人节',
            5: '母亲节',
            6: '父亲节',
            7: 'Prime Day',
            10: '万圣节',
            11: '黑色星期五',
            12: '圣诞季'
        }
        
        for month_num, event in important_months.items():
            # 检查是否有该月份数据
            month_data = monthly_performance[monthly_performance['month'] == month_num]
            if not month_data.empty:
                month_sales = month_data['sales'].values[0]
                marketing_calendar.append({
                    '月份': f"{month_num}月",
                    '营销节点': event,
                    '历史销售': f"¥{month_sales:.2f}",
                    '建议活动': f"提前2-4周准备{event}营销活动"
                })
            else:
                marketing_calendar.append({
                    '月份': f"{month_num}月",
                    '营销节点': event,
                    '历史销售': '无数据',
                    '建议活动': f"规划{event}营销活动"
                })
        
        analysis['营销日历'] = marketing_calendar
        
        # 4. 季节性调整建议
        adjustment_suggestions = []
        
        if len(seasonal_patterns) > 0:
            # 出价调整建议
            for pattern in seasonal_patterns:
                if '销售高峰月' in pattern:
                    peak_month_num = int(pattern['销售高峰月'].split('月')[0])
                    adjustment_suggestions.append(f"{peak_month_num}月为销售高峰，建议提高广告出价10-20%")
            
            # 预算分配建议
            if len(monthly_performance) >= 6:
                # 计算季节指数
                total_sales = monthly_performance['sales'].sum()
                monthly_performance['seasonal_index'] = monthly_performance['sales'] / (total_sales/len(monthly_performance))
                
                high_season_months = monthly_performance[monthly_performance['seasonal_index'] > 1.2]['month'].tolist()
                low_season_months = monthly_performance[monthly_performance['seasonal_index'] < 0.8]['month'].tolist()
                
                if high_season_months:
                    adjustment_suggestions.append(f"旺季月份({','.join(map(str, high_season_months))}月)：增加预算分配")
                if low_season_months:
                    adjustment_suggestions.append(f"淡季月份({','.join(map(str, low_season_months))}月)：减少预算，侧重品牌维护")
        
        analysis['季节性调整建议'] = adjustment_suggestions
        
        return analysis
        
    except Exception as e:
        print(f"季节性分析出错: {str(e)}")
        return {}


def add_advanced_analysis_to_excel(writer, sheet_name, analysis, start_row):
    """将高级分析模块添加到Excel工作表中"""
    try:
        workbook = writer.book
        if sheet_name not in writer.sheets:
            return start_row
        
        ws = writer.sheets[sheet_name]
        
        # 添加高级分析标题
        start_row += 2
        title_cell = ws.cell(row=start_row, column=1, value="🚀 高级分析模块")
        title_cell.font = Font(name='微软雅黑', size=14, bold=True, color='1F4E79')
        title_cell.fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
        ws.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=10)
        start_row += 1
        
        # 1. 市场分析
        if 'market_analysis' in analysis and analysis['market_analysis']:
            start_row = add_analysis_section(ws, "📊 市场分析", analysis['market_analysis'], start_row)
        
        # 2. 客户分析
        if 'customer_analysis' in analysis and analysis['customer_analysis']:
            start_row = add_analysis_section(ws, "👥 客户分析", analysis['customer_analysis'], start_row)
        
        # 3. 竞争分析
        if 'competition_analysis' in analysis and analysis['competition_analysis']:
            start_row = add_analysis_section(ws, "⚔️ 竞争分析", analysis['competition_analysis'], start_row)
        
        # 4. 预测分析
        if 'forecast_analysis' in analysis and analysis['forecast_analysis']:
            start_row = add_analysis_section(ws, "🔮 预测分析", analysis['forecast_analysis'], start_row)
        
        # 5. 优化分析
        if 'optimization_analysis' in analysis and analysis['optimization_analysis']:
            start_row = add_analysis_section(ws, "🛠️ 优化分析", analysis['optimization_analysis'], start_row)
        
        # 6. 风险分析
        if 'risk_analysis' in analysis and analysis['risk_analysis']:
            start_row = add_analysis_section(ws, "⚠️ 风险分析", analysis['risk_analysis'], start_row)
        
        # 7. 增长分析
        if 'growth_analysis' in analysis and analysis['growth_analysis']:
            start_row = add_analysis_section(ws, "📈 增长分析", analysis['growth_analysis'], start_row)
        
        # 8. 季节性分析
        if 'seasonal_analysis' in analysis and analysis['seasonal_analysis']:
            start_row = add_analysis_section(ws, "📅 季节性分析", analysis['seasonal_analysis'], start_row)
        
        return start_row
        
    except Exception as e:
        print(f"添加高级分析到Excel时出错: {str(e)}")
        return start_row


def add_analysis_section(ws, section_title, section_data, start_row):
    """将单个分析部分添加到工作表"""
    try:
        # 添加章节标题
        start_row += 2
        title_cell = ws.cell(row=start_row, column=1, value=section_title)
        title_cell.font = Font(name='微软雅黑', size=12, bold=True, color='1F4E79')
        title_cell.fill = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
        ws.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=5)
        start_row += 1
        
        # 递归处理嵌套的字典和列表
        if isinstance(section_data, dict):
            for key, value in section_data.items():
                if isinstance(value, (dict, list)):
                    # 子标题
                    sub_title_cell = ws.cell(row=start_row, column=1, value=f"• {key}")
                    sub_title_cell.font = Font(name='微软雅黑', size=11, bold=True)
                    start_row += 1
                    
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, list):
                                for i, item in enumerate(sub_value):
                                    if isinstance(item, dict):
                                        for item_key, item_value in item.items():
                                            ws.cell(row=start_row, column=2, value=f"{item_key}: {item_value}")
                                            start_row += 1
                                    else:
                                        ws.cell(row=start_row, column=2, value=f"{item}")
                                        start_row += 1
                            else:
                                ws.cell(row=start_row, column=2, value=f"{sub_key}: {sub_value}")
                                start_row += 1
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            if isinstance(item, dict):
                                for item_key, item_value in item.items():
                                    ws.cell(row=start_row, column=2, value=f"{item_key}: {item_value}")
                                    start_row += 1
                            else:
                                ws.cell(row=start_row, column=2, value=f"{item}")
                                start_row += 1
                else:
                    ws.cell(row=start_row, column=1, value=f"  {key}: {value}")
                    start_row += 1
        elif isinstance(section_data, list):
            for i, item in enumerate(section_data):
                if isinstance(item, dict):
                    for key, value in item.items():
                        ws.cell(row=start_row, column=1, value=f"  {key}: {value}")
                        start_row += 1
                else:
                    ws.cell(row=start_row, column=1, value=f"  {item}")
                    start_row += 1
        
        return start_row
        
    except Exception as e:
        print(f"添加分析章节时出错: {str(e)}")
        return start_row


# 在 generate_key_insights 函数中添加高级分析摘要
def generate_key_insights(df, campaign_analyses, search_term_analysis):
    """生成关键洞察与建议 - 增强版，增加ASIN分析和高级分析摘要"""
    insights = []
    
    # ... [原有代码保持不变] ...
    
    # 新增：高级分析模块摘要
    insights.append("")
    insights.append("=" * 80)
    insights.append("🚀 高级分析模块摘要")
    insights.append("=" * 80)
    
    # 汇总所有广告组合的高级分析
    advanced_insights = []
    
    for campaign_name, analysis in campaign_analyses.items():
        if analysis is None:
            continue
        
        insights.append(f"\n📋 {campaign_name} - 高级分析摘要:")
        
        # 市场分析摘要
        if 'market_analysis' in analysis and analysis['market_analysis']:
            market = analysis['market_analysis']
            if '市场规模评估' in market and '市场份额估计' in market['市场规模评估']:
                insights.append(f"  📊 市场: {market['市场规模评估']['市场份额估计']}市场份额")
        
        # 风险分析摘要
        if 'risk_analysis' in analysis and analysis['risk_analysis']:
            risk = analysis['risk_analysis']
            if '风险评估矩阵' in risk:
                high_risks = [r for r in risk['风险评估矩阵'] if r['风险等级'] == '高']
                if high_risks:
                    insights.append(f"  ⚠️ 风险: 发现{len(high_risks)}个高风险项")
        
        # 增长分析摘要
        if 'growth_analysis' in analysis and analysis['growth_analysis']:
            growth = analysis['growth_analysis']
            if '增长机会识别' in growth:
                opportunities = growth['增长机会识别']
                if opportunities:
                    insights.append(f"  📈 机会: {len(opportunities)}个增长机会")
        
        # 季节性分析摘要
        if 'seasonal_analysis' in analysis and analysis['seasonal_analysis']:
            seasonal = analysis['seasonal_analysis']
            if '季节性模式' in seasonal and seasonal['季节性模式']:
                insights.append("  📅 季节性: 检测到明显季节性模式")
       # 表现差关键词总览
    insights.append("")
    insights.append("⚠️ 表现差关键词总览")
    
    total_poor_keywords = 0
    total_poor_spend = 0
    
    for campaign_name, analysis in campaign_analyses.items():
        if analysis is None or 'poor_performing_keywords' not in analysis:
            continue
        
        poor_keywords = analysis['poor_performing_keywords']
        if isinstance(poor_keywords, pd.DataFrame) and not poor_keywords.empty:
            poor_keywords_count = len(poor_keywords)
            poor_spend = poor_keywords['spend'].sum()
            
            total_poor_keywords += poor_keywords_count
            total_poor_spend += poor_spend
    
    insights.append(f"表现差关键词总数: {total_poor_keywords}个")
    insights.append(f"表现差关键词总花费: ¥{total_poor_spend:.2f}")
    insights.append(f"预计优化后每月可节省: ¥{total_poor_spend * 4:.2f}")
    
    return insights


# 在 main 函数的输出部分添加高级分析概览
def main():
    """主程序"""
    # ... [原有代码保持不变] ...
    
def save_to_excel(data, output_file):
    """将所有分析结果保存到Excel文件"""
    # ... [前面代码保持不变] ...
    
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            workbook = writer.book
            
            # ... [保存原始数据代码保持不变] ...
            
            # 保存广告组合分析 - 每个广告组合一个工作表
            if 'campaign_analysis' in data and data['campaign_analysis']:
                for idx, (campaign, analysis) in enumerate(data['campaign_analysis'].items()):
                    if analysis is None:
                        continue
                    
                    sheet_name = get_unique_sheet_name(campaign)
                    
                    # 创建主工作表
                    start_row = 0
                    
                    # 1. 写入广告组合建议
                    if 'campaign_recommendations' in analysis and analysis['campaign_recommendations']:
                        recommendations_df = pd.DataFrame(analysis['campaign_recommendations'], columns=['广告组合建议'])
                        recommendations_df.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
                        start_row += len(recommendations_df) + 3
                    
                    # 2. 写入摘要统计
                    if 'summary_stats' in analysis and analysis['summary_stats']:
                        summary_df = pd.DataFrame([analysis['summary_stats']])
                        summary_df.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
                        start_row += len(summary_df) + 3
                    
                    # 3. 写入TOP关键词
                    if not analysis['top_keywords'].empty:
                        analysis['top_keywords'].to_excel(writer, sheet_name=sheet_name, 
                                                         startrow=start_row, index=False)
                        start_row += len(analysis['top_keywords']) + 3
                    
                    # ================ 新增：写入表现差的关键词 ================
                    if 'poor_performing_keywords' in analysis and not analysis['poor_performing_keywords'].empty:
                        # 添加标题
                        title_cell = writer.sheets[sheet_name].cell(row=start_row, column=1, value="⚠️ 表现差的关键词（花费多、不出单、ACOS高）")
                        title_cell.font = Font(name='微软雅黑', size=12, bold=True, color='FF0000')
                        start_row += 1
                        
                        analysis['poor_performing_keywords'].to_excel(writer, sheet_name=sheet_name, 
                                                                     startrow=start_row, index=False)
                        start_row += len(analysis['poor_performing_keywords']) + 3
                    # ================ 新增结束 ================
                    
                    # 4. 写入否定关键词
                    if not analysis['waste_keywords'].empty:
                        analysis['waste_keywords'].to_excel(writer, sheet_name=sheet_name, 
                                                           startrow=start_row, index=False)
                        start_row += len(analysis['waste_keywords']) + 3
                    
                    # 5. 写入高效词根
                    if analysis['top_converting_roots']:
                        converting_roots_df = pd.DataFrame(analysis['top_converting_roots'], 
                                                          columns=['高效词根', '加权得分'])
                        converting_roots_df.to_excel(writer, sheet_name=sheet_name, 
                                                    startrow=start_row, index=False)
                        start_row += len(converting_roots_df) + 3
                    
                    # 6. 写入无效词根
                    if analysis['top_non_converting_roots']:
                        non_converting_roots_df = pd.DataFrame(analysis['top_non_converting_roots'], 
                                                              columns=['无效词根', '出现次数'])
                        non_converting_roots_df.to_excel(writer, sheet_name=sheet_name, 
                                                        startrow=start_row, index=False)
                        start_row += len(non_converting_roots_df) + 3
                    
                    # 7. 写入ASIN分析
                    if not analysis['asin_analysis'].empty:
                        asin_analysis_df = analysis['asin_analysis']
                        asin_analysis_df.to_excel(writer, sheet_name=sheet_name, 
                                                 startrow=start_row, index=False)
                        start_row += len(asin_analysis_df) + 3
                    
                    # 8. 写入搜索词ASIN分析
                    if 'search_term_asin_analysis' in analysis and not analysis['search_term_asin_analysis'].empty:
                        search_asin_df = analysis['search_term_asin_analysis']
                        search_asin_df.to_excel(writer, sheet_name=sheet_name, 
                                               startrow=start_row, index=False)
                        start_row += len(search_asin_df) + 3
                    
                    # ... [后续其他分析保持不变] ...
                    
                    # 应用格式化
                    apply_excel_formatting(writer.sheets[sheet_name], idx + 1)
            
            # ... [其他保存代码保持不变] ...
            ws = writer.sheets[sheet_name]

start_row = campaign_df.shape[0] + 3

poor_df = analysis.get('poor_performing_keywords')

if poor_df is not None and not poor_df.empty:
    ws.cell(row=start_row - 1, column=1, value="【表现差的关键词（建议优化 / 否定）】")

    poor_df.to_excel(
        writer,
        sheet_name=sheet_name,
        startrow=start_row,
        index=False
    )

        
        print(f"✅ Excel文件保存成功: {output_file}")
        
        # 添加可视化分析
        generate_visual_analysis(data['原始数据'], output_file)
        
        return True
        
    except Exception as e:
        print(f"❌ 保存Excel文件时出错: {str(e)}")
        traceback.print_exc()
        return False
    
    # ... [原有代码保持不变] ...

def contains_protected_words(keyword):
    """检查关键词是否包含受保护词"""
    keyword_lower = str(keyword).lower()
    for word in PROTECTED_WORDS:
        if word in keyword_lower:
            return True
    return False

def get_negation_reason_enhanced(row):
    """获取增强的否定原因"""
    reasons = []
    keyword = str(row['keyword']).lower()
    
    # 检查是否包含受保护词
    if contains_protected_words(keyword):
        reasons.append("包含产品核心词")
    
    if row['orders'] == 0:
        if row['spend'] > 1:
            reasons.append("高花费无转化")
        elif row['spend'] > 0.5:
            reasons.append("中等花费无转化")
        else:
            reasons.append("无转化")
    
    if row['ctr'] < 0.0005:
        reasons.append("CTR极低")
    elif row['ctr'] < 0.001:
        reasons.append("CTR低")
    
    if row['conversion_rate'] == 0 and row['clicks'] > 5:
        reasons.append("多次点击无转化")
    
    # 检查关键词相关性
    if not contains_protected_words(keyword) and row['impressions'] > 50:
        reasons.append("相关性低")
    
    return "，".join(reasons) if reasons else "表现不佳"

def analyze_search_term_asins(df):
    """分析搜索词中的商品ASIN表现"""
    try:
        # 检查是否有提取的ASIN数据
        if 'extracted_asins' not in df.columns or df['extracted_asins'].isna().all():
            return pd.DataFrame()
        
        # 展开数据：每行可能包含多个ASIN
        asin_data = []
        for idx, row in df.iterrows():
            if row['extracted_asins'] and len(row['extracted_asins']) > 0:
                for asin in row['extracted_asins']:
                    asin_data.append({
                        'asin': asin,
                        'keyword': row['keyword'],
                        'campaign': row['campaign'],
                        'ad_group': row['ad_group'],
                        'impressions': row['impressions'],
                        'clicks': row['clicks'],
                        'orders': row['orders'],
                        'spend': row['spend'],
                        'sales': row['sales'],
                        'ctr': row['ctr'],
                        'conversion_rate': row['conversion_rate'],
                        'roas': row['roas'],
                        'acos': row['acos'],
                        'quality_score': row['quality_score']
                    })
        
        if not asin_data:
            return pd.DataFrame()
        
        # 创建ASIN分析DataFrame
        asin_df = pd.DataFrame(asin_data)
        
        # 按ASIN汇总
        asin_analysis = asin_df.groupby('asin').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'orders': 'sum',
            'spend': 'sum',
            'sales': 'sum',
            'keyword': 'nunique',  # 关联的关键词数量
            'campaign': 'nunique',  # 出现在多少个广告组合
            'ad_group': 'nunique',  # 出现在多少个广告组
            'quality_score': 'mean'  # 平均质量得分
        }).reset_index()
        
        # 计算关键指标
        asin_analysis['ctr'] = asin_analysis['clicks'] / asin_analysis['impressions'].replace(0, 1)
        asin_analysis['conversion_rate'] = asin_analysis['orders'] / asin_analysis['clicks'].replace(0, 1)
        asin_analysis['acos'] = asin_analysis['spend'] / asin_analysis['sales'].replace(0, 1)
        asin_analysis['roas'] = asin_analysis['sales'] / asin_analysis['spend'].replace(0, 1)
        asin_analysis['cpc'] = asin_analysis['spend'] / asin_analysis['clicks'].replace(0, 1)
        
        # 计算ASIN表现得分
        asin_analysis['performance_score'] = (
            asin_analysis['conversion_rate'] * 40 +
            asin_analysis['roas'] * 30 +
            asin_analysis['ctr'] * 20 +
            np.log1p(asin_analysis['orders']) * 10
        )
        
        # 添加ASIN表现评级
        asin_analysis['performance_rating'] = asin_analysis['performance_score'].apply(
            lambda x: '优秀' if x > 60 else ('良好' if x > 40 else '需优化')
        )
        
        # 添加ASIN类型标识（从搜索词中提取）
        asin_analysis['asin_source'] = '搜索词提取'
        
        # 添加建议
        def get_search_term_asin_recommendation(row):
            if row['orders'] == 0 and row['spend'] > 1:
                return "搜索词包含但无转化，考虑暂停相关关键词"
            elif row['roas'] > 3 and row['orders'] >= 2:
                return "搜索词关联表现优秀，可围绕此ASIN拓展关键词"
            elif row['ctr'] < 0.002 and row['impressions'] > 50:
                return "搜索词关联但点击率低，优化相关关键词"
            elif row['conversion_rate'] < 0.01 and row['clicks'] > 10:
                return "搜索词关联但转化低，检查ASIN相关性"
            elif row['keyword'] >= 5:
                return f"与{row['keyword']}个关键词关联，表现稳定"
            else:
                return "保持监控"
        
        asin_analysis['recommendation'] = asin_analysis.apply(get_search_term_asin_recommendation, axis=1)
        
        # 按表现得分排序
        asin_analysis = asin_analysis.sort_values('performance_score', ascending=False)
        
        print(f"搜索词ASIN分析: 发现{len(asin_analysis)}个商品ASIN")
        
        return asin_analysis
    
    except Exception as e:
        print(f"分析搜索词ASIN时出错: {str(e)}")
        traceback.print_exc()
        return pd.DataFrame()

def analyze_campaign_asins(df):
    """分析广告组合中的ASIN表现"""
    if 'asin' not in df.columns or df['asin'].isna().all():
        return pd.DataFrame()
    
    try:
        # 过滤有效的ASIN
        asin_pattern = re.compile(r'^B0[0-9A-Z]{8,9}$')
        asin_df = df[df['asin'].notna() & df['asin'].apply(lambda x: bool(asin_pattern.match(str(x))) if pd.notna(x) else False)].copy()
        
        if len(asin_df) == 0:
            return pd.DataFrame()
        
        # 按ASIN汇总
        asin_analysis = asin_df.groupby('asin').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'orders': 'sum',
            'spend': 'sum',
            'sales': 'sum',
            'keyword': 'nunique',
            'campaign': 'first',
            'ad_group': lambda x: ', '.join(x.unique()[:3])  # 取前3个广告组
        }).reset_index()
        
        # 计算关键指标
        asin_analysis['ctr'] = asin_analysis['clicks'] / asin_analysis['impressions'].replace(0, 1)
        asin_analysis['conversion_rate'] = asin_analysis['orders'] / asin_analysis['clicks'].replace(0, 1)
        asin_analysis['acos'] = asin_analysis['spend'] / asin_analysis['sales'].replace(0, 1)
        asin_analysis['roas'] = asin_analysis['sales'] / asin_analysis['spend'].replace(0, 1)
        asin_analysis['cpc'] = asin_analysis['spend'] / asin_analysis['clicks'].replace(0, 1)
        
        # 计算ASIN表现得分
        asin_analysis['performance_score'] = (
            asin_analysis['conversion_rate'] * 40 +
            asin_analysis['roas'] * 30 +
            asin_analysis['ctr'] * 20 +
            np.log1p(asin_analysis['orders']) * 10
        )
        
        # 添加ASIN表现评级
        asin_analysis['performance_rating'] = asin_analysis['performance_score'].apply(
            lambda x: '优秀' if x > 60 else ('良好' if x > 40 else '需优化')
        )
        
        # 添加ASIN类型标识
        asin_analysis['asin_source'] = '广告数据'
        
        # 添加建议
        def get_asin_recommendation(row):
            if row['orders'] == 0 and row['spend'] > 1:
                return "考虑暂停投放或降低预算"
            elif row['roas'] > 3 and row['orders'] >= 3:
                return "增加预算，扩大投放"
            elif row['ctr'] < 0.002 and row['impressions'] > 50:
                return "优化Listing图片和标题"
            elif row['conversion_rate'] < 0.01 and row['clicks'] > 10:
                return "优化价格和促销"
            else:
                return "保持监控"
        
        asin_analysis['recommendation'] = asin_analysis.apply(get_asin_recommendation, axis=1)
        
        # 按表现得分排序
        asin_analysis = asin_analysis.sort_values('performance_score', ascending=False)
        
        return asin_analysis
    
    except Exception as e:
        print(f"分析ASIN时出错: {str(e)}")
        return pd.DataFrame()

def analyze_competitor_asins(df):
    """分析竞争对手ASIN表现"""
    try:
        # 从关键词中提取竞争对手ASIN（以B0开头）
        competitor_asins = []
        
        for keyword in df['keyword'].astype(str):
            # 查找关键词中的ASIN（以B0开头，不区分大小写）
            asins = re.findall(r'\b(B0[0-9A-Z]{8,9})\b', keyword.upper())
            for asin in asins:
                # 检查是否是竞争对手ASIN（不是自己的ASIN）
                if asin not in df['asin'].values:
                    competitor_asins.append(asin)
        
        if not competitor_asins:
            return pd.DataFrame()
        
        # 统计竞争对手ASIN出现频率
        competitor_counter = Counter(competitor_asins)
        
        # 创建竞争对手ASIN分析
        competitor_analysis = []
        for asin, frequency in competitor_counter.most_common(20):
            # 找出包含该ASIN的关键词
            matching_keywords = df[df['keyword'].str.contains(asin, case=False, na=False)]
            
            if not matching_keywords.empty:
                keyword_perf = matching_keywords.agg({
                    'impressions': 'sum',
                    'clicks': 'sum',
                    'orders': 'sum',
                    'spend': 'sum',
                    'sales': 'sum'
                })
                
                competitor_analysis.append({
                    '竞争对手ASIN': asin,
                    '出现次数': frequency,
                    '关联关键词数': len(matching_keywords),
                    '展示量': keyword_perf['impressions'],
                    '点击量': keyword_perf['clicks'],
                    '订单数': keyword_perf['orders'],
                    '花费': keyword_perf['spend'],
                    '销售额': keyword_perf['sales'],
                    'CTR': keyword_perf['clicks'] / keyword_perf['impressions'] if keyword_perf['impressions'] > 0 else 0,
                    '转化率': keyword_perf['orders'] / keyword_perf['clicks'] if keyword_perf['clicks'] > 0 else 0,
                    'ROAS': keyword_perf['sales'] / keyword_perf['spend'] if keyword_perf['spend'] > 0 else 0
                })
        
        if competitor_analysis:
            competitor_df = pd.DataFrame(competitor_analysis)
            
            # 添加竞争对手威胁等级
            def get_competitor_threat(row):
                if row['出现次数'] >= 10 and row['花费'] > 10:
                    return '高威胁'
                elif row['出现次数'] >= 5 and row['花费'] > 5:
                    return '中威胁'
                elif row['出现次数'] >= 3:
                    return '低威胁'
                else:
                    return '观察中'
            
            competitor_df['威胁等级'] = competitor_df.apply(get_competitor_threat, axis=1)
            
            # 添加应对建议
            def get_competitor_response(row):
                if row['威胁等级'] == '高威胁':
                    return "考虑对竞争对手ASIN进行精准否定，或创建针对性广告组"
                elif row['威胁等级'] == '中威胁':
                    return "监控竞争对手表现，优化自身产品优势"
                elif row['ROAS'] < 1 and row['花费'] > 2:
                    return "建议否定该ASIN相关关键词"
                else:
                    return "保持监控"
            
            competitor_df['应对建议'] = competitor_df.apply(get_competitor_response, axis=1)
            
            return competitor_df.sort_values(['威胁等级', '花费'], ascending=[True, False])
        
        return pd.DataFrame()
        
    except Exception as e:
        print(f"分析竞争对手ASIN时出错: {str(e)}")
        return pd.DataFrame()

def generate_budget_recommendations(df, asin_analysis, competitor_asins):
    """生成预算分配建议"""
    recommendations = []
    
    try:
        # 基础预算分析
        total_spend = df['spend'].sum()
        total_sales = df['sales'].sum()
        total_roas = total_sales / total_spend if total_spend > 0 else 0
        
        # 1. 整体预算建议
        if total_roas > 4:
            recommendations.append("✅ 整体ROAS优秀，可考虑增加10-20%预算")
        elif total_roas > 2:
            recommendations.append("📈 整体ROAS良好，保持当前预算")
        elif total_roas > 1:
            recommendations.append("⚠️ 整体ROAS偏低，建议优化后再增加预算")
        else:
            recommendations.append("❌ 整体ROAS不佳，建议减少预算并重点优化")
        
        # 2. 按广告组预算分配
        ad_group_performance = df.groupby('ad_group').agg({
            'spend': 'sum',
            'sales': 'sum',
            'orders': 'sum',
            'roas': 'mean'
        }).reset_index()
        
        if len(ad_group_performance) > 1:
            # 找出高ROAS和低ROAS广告组
            ad_group_performance = ad_group_performance.sort_values('roas', ascending=False)
            top_ad_groups = ad_group_performance.head(3)
            bottom_ad_groups = ad_group_performance.tail(3)
            
            if len(top_ad_groups) > 0:
                recommendations.append("💰 建议增加预算的广告组:")
                for _, row in top_ad_groups.iterrows():
                    if row['roas'] > 3 and row['orders'] >= 2:
                        recommendations.append(f"  • {row['ad_group']}: ROAS={row['roas']:.2f}, 建议增加20-30%预算")
            
            if len(bottom_ad_groups) > 0:
                recommendations.append("💸 建议减少预算的广告组:")
                for _, row in bottom_ad_groups.iterrows():
                    if row['roas'] < 1 and row['spend'] > 5:
                        recommendations.append(f"  • {row['ad_group']}: ROAS={row['roas']:.2f}, 建议减少50%预算或暂停")
        
        # 3. 按关键词类型预算分配
        keyword_types = categorize_keywords_by_intent(df)
        if not keyword_types.empty:
            recommendations.append("🎯 按关键词类型预算建议:")
            for _, row in keyword_types.iterrows():
                if row['关键词类型'] == '高转化词' and row['ROAS'] > 3:
                    recommendations.append(f"  • {row['关键词类型']}: 占比{row['花费占比']:.1%}, 可增加预算")
                elif row['关键词类型'] == '低效词' and row['花费占比'] > 0.3:
                    recommendations.append(f"  • {row['关键词类型']}: 占比{row['花费占比']:.1%}, 应减少预算")
        
        # 4. 按时间段预算分配（如果有日期数据）
        if 'date' in df.columns and df['date'].notna().any():
            time_budget_rec = analyze_time_budget_allocation(df)
            recommendations.extend(time_budget_rec)
        
        # 5. ASIN相关预算建议
        if not asin_analysis.empty:
            # 找出表现优秀的ASIN
            top_asins = asin_analysis[asin_analysis['performance_rating'] == '优秀']
            if len(top_asins) > 0:
                recommendations.append("🏆 ASIN预算建议:")
                for _, row in top_asins.head(3).iterrows():
                    recommendations.append(f"  • ASIN {row['asin']}: ROAS={row['roas']:.2f}, 建议为重点ASIN增加预算")
        
        # 6. 竞争对手相关预算建议
        if isinstance(competitor_asins, pd.DataFrame) and not competitor_asins.empty:
            high_threat = competitor_asins[competitor_asins['威胁等级'] == '高威胁']
            if len(high_threat) > 0:
                total_threat_spend = high_threat['花费'].sum()
                recommendations.append(f"⚠️ 竞争对手威胁: {len(high_threat)}个高威胁ASIN，花费¥{total_threat_spend:.2f}")
                recommendations.append("  建议将部分预算转移到防御性广告活动")
        
        # 7. 总体预算分配比例
        recommendations.append("📊 建议预算分配比例:")
        recommendations.append("  • 高效关键词/ASIN: 60-70%")
        recommendations.append("  • 测试新关键词: 20-25%")
        recommendations.append("  • 品牌/防御性投放: 10-15%")
        
        return recommendations
        
    except Exception as e:
        print(f"生成预算建议时出错: {str(e)}")
        return ["预算分析出现错误"]

def categorize_keywords_by_intent(df):
    """按购买意图分类关键词"""
    try:
        categorized = []
        
        for idx, row in df.iterrows():
            keyword = str(row['keyword']).lower()
            category = "其他"
            
            # 购买意图词
            if any(word in keyword for word in ['buy', 'purchase', 'cheap', 'price', 'deal', 'discount', 'sale']):
                category = "购买意图词"
            # 品牌词
            elif any(word in keyword for word in ['brand', 'best', 'top', 'quality', 'professional', 'premium']):
                category = "品牌词"
            # 比较词
            elif any(word in keyword for word in ['vs', 'versus', 'compare', 'comparison', 'better than']):
                category = "比较词"
            # 信息查询词
            elif any(word in keyword for word in ['how', 'what', 'why', 'review', 'benefit', 'advantage']):
                category = "信息查询词"
            # 核心产品词
            elif contains_protected_words(keyword):
                category = "核心产品词"
            
            categorized.append({
                '关键词': row['keyword'],
                '关键词类型': category,
                '花费': row['spend'],
                '订单': row['orders'],
                'ROAS': row['roas']
            })
        
        cat_df = pd.DataFrame(categorized)
        
        # 汇总各类型表现
        type_summary = cat_df.groupby('关键词类型').agg({
            '关键词': 'count',
            '花费': 'sum',
            '订单': 'sum',
            'ROAS': 'mean'
        }).reset_index()
        
        total_spend = type_summary['花费'].sum()
        if total_spend > 0:
            type_summary['花费占比'] = type_summary['花费'] / total_spend
        
        # 添加表现评级
        def get_type_performance(row):
            if row['ROAS'] > 3 and row['订单'] > 0:
                return '高转化词'
            elif row['ROAS'] > 1.5:
                return '中等词'
            elif row['花费'] > 0 and row['订单'] == 0:
                return '低效词'
            else:
                return '测试词'
        
        type_summary['表现评级'] = type_summary.apply(get_type_performance, axis=1)
        
        return type_summary.sort_values('花费', ascending=False)
        
    except:
        return pd.DataFrame()

def analyze_time_budget_allocation(df):
    """分析时间段预算分配"""
    recommendations = []
    
    try:
        if 'date' not in df.columns:
            return recommendations
        
        # 按星期分析
        df['weekday'] = df['date'].dt.dayofweek
        weekday_perf = df.groupby('weekday').agg({
            'spend': 'sum',
            'sales': 'sum',
            'orders': 'sum'
        }).reset_index()
        
        if len(weekday_perf) > 0:
            # 找出最佳和最差工作日
            weekday_perf['roas'] = weekday_perf['sales'] / weekday_perf['spend'].replace(0, 1)
            best_day = weekday_perf.loc[weekday_perf['roas'].idxmax()]
            worst_day = weekday_perf.loc[weekday_perf['roas'].idxmin()]
            
            day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            
            recommendations.append(f"📅 时间段表现:")
            recommendations.append(f"  • 最佳转化日: {day_names[int(best_day['weekday'])]}, ROAS={best_day['roas']:.2f}")
            recommendations.append(f"  • 最差转化日: {day_names[int(worst_day['weekday'])]}, ROAS={worst_day['roas']:.2f}")
            
            # 时间调整建议
            if best_day['roas'] > worst_day['roas'] * 1.5:
                recommendations.append(f"  💡 建议在{day_names[int(best_day['weekday'])]}增加出价10-20%")
        
        # 按小时分析（如果有小时数据）
        if 'date' in df.columns and df['date'].notna().any():
            df['hour'] = df['date'].dt.hour
            hour_perf = df.groupby('hour').agg({
                'spend': 'sum',
                'sales': 'sum',
                'orders': 'sum'
            }).reset_index()
            
            if len(hour_perf) > 0:
                hour_perf['roas'] = hour_perf['sales'] / hour_perf['spend'].replace(0, 1)
                best_hours = hour_perf.nlargest(3, 'roas')
                
                if len(best_hours) > 0:
                    recommendations.append("  ⏰ 最佳转化时段:")
                    for _, row in best_hours.iterrows():
                        recommendations.append(f"    • {int(row['hour'])}:00-{int(row['hour'])+1}:00, ROAS={row['roas']:.2f}")
        
        return recommendations
        
    except:
        return []

def generate_ad_copy_suggestions(df, top_converting_roots):
    """生成广告文案建议"""
    suggestions = []
    
    try:
        # 1. 核心卖点提取
        suggestions.append("🎯 广告文案核心建议:")
        
        # 从高效词根中提取核心卖点
        if top_converting_roots:
            top_roots = [root for root, _ in top_converting_roots[:5]]
            
            # 分析核心卖点词
            feature_words = ['quiet', 'silent', 'compact', 'portable', 'easy', 'comfortable', 
                           'adjustable', 'durable', 'stable', 'smooth']
            
            identified_features = []
            for root in top_roots:
                if root in feature_words:
                    identified_features.append(root)
            
            if identified_features:
                suggestions.append(f"  核心卖点: {', '.join(identified_features)}")
        
        # 2. 标题建议
        suggestions.append("📝 标题建议:")
        
        # 基于表现最佳的关键词生成标题
        top_keywords = df[df['orders'] > 0].sort_values('roas', ascending=False).head(5)
        if not top_keywords.empty:
            best_keyword = top_keywords.iloc[0]['keyword']
            words = str(best_keyword).split()
            
            # 生成标题变体
            if len(words) >= 3:
                title_variants = [
                    f"{' '.join(words)} | 静音设计 | 家庭健身",
                    f"专业{' '.join(words[:2])} | 高效燃脂 | 可调节",
                    f"{words[-1]}专用{words[0]} | 舒适体验 | 免费送货"
                ]
                
                for i, title in enumerate(title_variants[:2]):
                    suggestions.append(f"  标题{i+1}: {title}")
        
        # 3. 描述要点建议
        suggestions.append("📋 描述要点建议:")
        
        # 基于用户搜索词生成卖点
        high_ctr_keywords = df[df['ctr'] > df['ctr'].quantile(0.7)].head(10)
        if not high_ctr_keywords.empty:
            # 分析高频词
            all_words = []
            for keyword in high_ctr_keywords['keyword']:
                words = extract_roots(keyword, min_length=4)
                all_words.extend(words)
            
            if all_words:
                word_counter = Counter(all_words)
                common_words = [word for word, count in word_counter.most_common(5) 
                              if word not in STOP_WORDS and not is_protected_word(word)]
                
                if common_words:
                    suggestions.append(f"  重点突出: {', '.join(common_words)}")
        
        # 4. 行动号召建议
        suggestions.append("📢 行动号召建议:")
        call_to_actions = [
            "立即购买享受专属优惠",
            "限时免费送货",
            "30天无理由退货",
            "加入会员享受额外折扣"
        ]
        
        for cta in call_to_actions[:2]:
            suggestions.append(f"  • {cta}")
        
        # 5. 关键词插入建议
        suggestions.append("🔑 关键词插入位置:")
        suggestions.append("  • 标题: 核心产品词+核心卖点")
        suggestions.append("  • 首行描述: 核心卖点+用户痛点")
        suggestions.append("  • 中间描述: 功能特点+使用场景")
        suggestions.append("  • 结尾: 行动号召+信任因素")
        
        # 6. A/B测试建议
        suggestions.append("🧪 A/B测试建议:")
        suggestions.append("  • 测试不同价格表述")
        suggestions.append("  • 测试不同卖点顺序")
        suggestions.append("  • 测试不同行动号召")
        suggestions.append("  • 测试是否包含具体数字")
        
        return suggestions
        
    except Exception as e:
        print(f"生成广告文案建议时出错: {str(e)}")
        return ["广告文案分析出现错误"]

def analyze_time_performance(df):
    """分析时间段表现"""
    try:
        if 'date' not in df.columns:
            return pd.DataFrame()
        
        # 按星期分析
        df_time = df.copy()
        df_time['weekday'] = df_time['date'].dt.dayofweek
        df_time['weekday_name'] = df_time['weekday'].map({
            0: '周一', 1: '周二', 2: '周三', 3: '周四', 
            4: '周五', 5: '周六', 6: '周日'
        })
        
        # 按工作日汇总
        weekday_perf = df_time.groupby('weekday_name').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'orders': 'sum',
            'spend': 'sum',
            'sales': 'sum'
        }).reset_index()
        
        # 计算指标
        weekday_perf['CTR'] = weekday_perf['clicks'] / weekday_perf['impressions'].replace(0, 1)
        weekday_perf['转化率'] = weekday_perf['orders'] / weekday_perf['clicks'].replace(0, 1)
        weekday_perf['ROAS'] = weekday_perf['sales'] / weekday_perf['spend'].replace(0, 1)
        weekday_perf['ACOS'] = weekday_perf['spend'] / weekday_perf['sales'].replace(0, 1)
        
        # 添加表现评级
        weekday_perf['表现评级'] = weekday_perf['ROAS'].apply(
            lambda x: '优秀' if x > 3 else ('良好' if x > 2 else '一般')
        )
        
        # 排序（按周一至周日）
        weekday_order = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekday_perf['weekday_name'] = pd.Categorical(weekday_perf['weekday_name'], categories=weekday_order, ordered=True)
        weekday_perf = weekday_perf.sort_values('weekday_name')
        
        return weekday_perf
        
    except:
        return pd.DataFrame()

def generate_keyword_expansion_suggestions(df, top_converting_roots):
    """生成关键词扩展建议"""
    suggestions = []
    
    try:
        suggestions.append("🌱 关键词扩展建议:")
        
        if top_converting_roots:
            # 获取前5个高效词根
            top_roots = [root for root, _ in top_converting_roots[:5]]
            
            # 修饰词列表
            modifiers = {
                'buying_intent': ['buy', 'purchase', 'shop', 'order', 'cheap', 'discount', 'sale', 'best price'],
                'features': ['quiet', 'silent', 'compact', 'portable', 'easy', 'comfortable', 'adjustable', 'foldable'],
                'audience': ['for home', 'for office', 'for seniors', 'for beginners', 'professional', 'commercial'],
                'usage': ['under desk', 'desk exercise', 'cardio workout', 'low impact', 'full body']
            }
            
            # 为每个高效词根生成扩展建议
            for root in top_roots:
                if root not in STOP_WORDS and not is_protected_word(root):
                    # 生成不同维度的扩展
                    expansions = []
                    
                    # 购买意图扩展
                    for intent in modifiers['buying_intent'][:2]:
                        expansions.append(f"{intent} {root}")
                    
                    # 功能扩展
                    for feature in modifiers['features'][:2]:
                        expansions.append(f"{root} {feature}")
                    
                    # 使用场景扩展
                    for usage in modifiers['usage'][:2]:
                        expansions.append(f"{root} {usage}")
                    
                    if expansions:
                        suggestions.append(f"  • '{root}' 扩展词: {', '.join(expansions[:3])}")
        
        # 长尾词扩展建议
        suggestions.append("📈 长尾词挖掘方向:")
        
        # 分析现有长尾词表现
        df['word_count'] = df['keyword'].apply(lambda x: len(str(x).split()))
        long_tail = df[df['word_count'] >= 4]
        
        if not long_tail.empty:
            # 找出表现好的长尾词模式
            converting_long_tail = long_tail[long_tail['orders'] > 0]
            if not converting_long_tail.empty:
                # 分析共同模式
                patterns = []
                for keyword in converting_long_tail['keyword'].head(10):
                    words = str(keyword).split()
                    if len(words) >= 4:
                        # 提取中间部分作为模式
                        pattern = ' '.join(words[1:-1])
                        if pattern not in patterns and len(pattern) > 5:
                            patterns.append(pattern)
                
                if patterns:
                    suggestions.append(f"  有效长尾模式: {', '.join(patterns[:3])}")
        
        # 否定关键词扩展建议
        waste_keywords = df[(df['orders'] == 0) & (df['spend'] > 0.5)]
        if not waste_keywords.empty:
            # 找出共同的无效词根
            invalid_roots = []
            for keyword in waste_keywords['keyword'].head(20):
                roots = extract_roots(keyword)
                for root in roots:
                    if root not in PROTECTED_WORDS and root not in STOP_WORDS:
                        invalid_roots.append(root)
            
            if invalid_roots:
                root_counter = Counter(invalid_roots)
                common_invalid = [root for root, count in root_counter.most_common(3) if count >= 2]
                if common_invalid:
                    suggestions.append(f"  ⚠️ 建议否定词根: {', '.join(common_invalid)}")
        
        return suggestions
        
    except Exception as e:
        print(f"生成关键词扩展建议时出错: {str(e)}")
        return ["关键词扩展分析出现错误"]

def generate_targeting_optimizations(df):
    """生成投放策略优化建议"""
    suggestions = []
    
    try:
        suggestions.append("🎯 投放策略优化建议:")
        
        # 1. 匹配类型优化
        if 'match_type' in df.columns:
            match_perf = df.groupby('match_type').agg({
                'spend': 'sum',
                'sales': 'sum',
                'orders': 'sum',
                'roas': 'mean'
            }).reset_index()
            
            if not match_perf.empty:
                suggestions.append("  匹配类型表现:")
                for _, row in match_perf.iterrows():
                    if row['spend'] > 0:
                        suggestions.append(f"    • {row['match_type']}: ROAS={row['roas']:.2f}, 花费占比={(row['spend']/df['spend'].sum()):.1%}")
        
        # 2. 出价策略建议
        suggestions.append("  💰 出价策略:")
        
        # 分析不同质量得分关键词的表现
        df['quality_tier'] = pd.cut(df['quality_score'], bins=[0, 40, 60, 80, 100], 
                                   labels=['低质', '中质', '优质', '极优'])
        
        tier_perf = df.groupby('quality_tier').agg({
            'spend': 'sum',
            'sales': 'sum',
            'roas': 'mean',
            'cpc': 'mean'
        }).reset_index()
        
        if not tier_perf.empty:
            for _, row in tier_perf.iterrows():
                if row['spend'] > 0:
                    suggestions.append(f"    • {row['quality_tier']}词: ROAS={row['roas']:.2f}, CPC=¥{row['cpc']:.2f}")
        
        # 3. 投放位置建议
        if 'placement' in df.columns:
            placement_perf = df.groupby('placement').agg({
                'spend': 'sum',
                'sales': 'sum',
                'roas': 'mean'
            }).reset_index()
            
            if not placement_perf.empty:
                suggestions.append("  📍 投放位置:")
                for _, row in placement_perf.iterrows():
                    if row['spend'] > 0:
                        suggestions.append(f"    • {row['placement']}: ROAS={row['roas']:.2f}")
        
        # 4. 广告组结构建议
        ad_group_count = df['ad_group'].nunique()
        if ad_group_count > 1:
            suggestions.append(f"  🏗️ 广告组结构: 当前{ad_group_count}个广告组")
            
            # 检查广告组是否过于分散
            avg_keywords_per_group = len(df) / ad_group_count
            if avg_keywords_per_group < 5:
                suggestions.append("    ⚠️ 广告组可能过于分散，建议合并相似广告组")
            elif avg_keywords_per_group > 30:
                suggestions.append("    ⚠️ 广告组可能过于集中，建议细分以提高相关性")
        
        # 5. 否定策略建议
        negation_count = len(df[df['negation_suggestion'].str.contains('否定', na=False)])
        if negation_count > 0:
            suggestions.append(f"  🚫 否定策略: 发现{negation_count}个建议否定关键词")
            
            # 分析否定类型
            df_neg = df.copy()
            df_neg['否定类型'] = '保留'
            df_neg.loc[df_neg['negation_suggestion'].str.contains('否定精准', na=False), '否定类型'] = '精准否定'
            df_neg.loc[df_neg['negation_suggestion'].str.contains('否定词组', na=False), '否定类型'] = '词组否定'
            
            neg_summary = df_neg[df_neg['否定类型'] != '保留'].groupby('否定类型').agg({
                'spend': 'sum',
                'keyword': 'count'
            }).reset_index()
            
            if not neg_summary.empty:
                for _, row in neg_summary.iterrows():
                    suggestions.append(f"    • {row['否定类型']}: {row['keyword']}个词, 花费¥{row['spend']:.2f}")
        
        return suggestions
        
    except Exception as e:
        print(f"生成投放策略优化建议时出错: {str(e)}")
        return ["投放策略分析出现错误"]

def analyze_keyword_trends(df):
    """分析关键词趋势"""
    if 'date' not in df.columns or df['date'].isna().all():
        return pd.DataFrame()
    
    try:
        # 按周分析趋势
        df_trend = df.copy()
        df_trend['week'] = df_trend['date'].dt.to_period('W')
        
        # 获取每周表现
        weekly_performance = df_trend.groupby('week').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'orders': 'sum',
            'spend': 'sum',
            'sales': 'sum'
        }).reset_index()
        
        # 计算周环比
        if len(weekly_performance) > 1:
            weekly_performance['spend_growth'] = weekly_performance['spend'].pct_change() * 100
            weekly_performance['sales_growth'] = weekly_performance['sales'].pct_change() * 100
            weekly_performance['orders_growth'] = weekly_performance['orders'].pct_change() * 100
        
        return weekly_performance
    
    except:
        return pd.DataFrame()

def add_intelligent_negation_suggestions(df, converting_roots, non_converting_roots):
    """添加智能否定词建议"""
    converting_root_set = {root for root, _ in converting_roots}
    non_converting_root_set = {root for root, _ in non_converting_roots}
    
    for idx, row in df.iterrows():
        keyword = str(row['keyword']).lower()
        suggestion = "保留"
        
        # 首先检查是否包含受保护的核心词
        if contains_protected_words(keyword):
            suggestion = "保留 (包含核心词)"
        else:
            # 条件1: 无转化且花费高
            if row['orders'] == 0 and row['spend'] > 0.5:
                # 检查是否包含无效词根
                keyword_roots = set(extract_roots(keyword))
                invalid_roots = keyword_roots.intersection(non_converting_root_set)
                
                if len(invalid_roots) >= 2:
                    suggestion = f"否定词组: -{' '.join(list(invalid_roots)[:2])}"
                elif len(invalid_roots) == 1:
                    suggestion = f"否定词组: -{list(invalid_roots)[0]}"
                else:
                    # 检查是否完全不包含有效词根
                    if not keyword_roots.intersection(converting_root_set):
                        suggestion = f"否定精准: -{keyword}"
                    else:
                        suggestion = "监控 (含有效词根但无转化)"
            
            # 条件2: CTR极低
            elif row['ctr'] < 0.0005 and row['impressions'] > 100:
                suggestion = "否定精准 (CTR极低)"
            
            # 条件3: 高点击无转化
            elif row['orders'] == 0 and row['clicks'] > 10:
                suggestion = "否定精准 (高点击无转化)"
        
        df.at[idx, 'negation_suggestion'] = suggestion
    
    return df

def add_intelligent_grouping_suggestions(df, converting_roots):
    """添加智能分组建议"""
    if not converting_roots:
        return df
    
    # 获取高效词根并排除受保护词（它们会出现在所有分组中）
    top_roots = []
    for root, weight in converting_roots:
        if not is_protected_word(root) and weight > 2:  # 排除受保护词，要求一定权重
            top_roots.append((root, weight))
    
    # 取前8个
    top_roots = sorted(top_roots, key=lambda x: x[1], reverse=True)[:8]
    top_root_words = [root for root, _ in top_roots]
    
    for idx, row in df.iterrows():
        if row['orders'] > 0 or row['quality_score'] > 60:
            keyword = str(row['keyword']).lower()
            keyword_roots = extract_roots(keyword)
            
            # 找出匹配的高效词根（排除受保护词）
            matched_roots = []
            for root in keyword_roots:
                if root in top_root_words and not is_protected_word(root):
                    matched_roots.append(root)
            
            if matched_roots:
                # 使用权重最高的词根作为分组依据
                best_root = matched_roots[0]
                df.at[idx, 'grouping_suggestion'] = f"分组: {best_root}_相关"
            elif row['quality_score'] > 75:
                df.at[idx, 'grouping_suggestion'] = "分组: 高性能独立组"
            elif contains_protected_words(keyword):
                df.at[idx, 'grouping_suggestion'] = "分组: 核心产品词"
    
    return df

def add_match_type_suggestions(df):
    """添加匹配类型建议"""
    if 'match_type' not in df.columns:
        return df
    
    for idx, row in df.iterrows():
        suggestion = ""
        keyword = str(row['keyword']).lower()
        
        # 分析关键词特征
        words = keyword.split()
        word_count = len(words)
        
        # 长尾词建议短语匹配
        if word_count >= 4 and row['quality_score'] > 60:
            suggestion = "短语匹配"
        # 高转化关键词建议精准匹配
        elif row['orders'] >= 2 and row['conversion_rate'] > 0.1:
            suggestion = "精准匹配"
        # 高点击无转化建议广泛匹配
        elif row['clicks'] > 10 and row['orders'] == 0:
            suggestion = "广泛匹配+否定"
        # 核心产品词建议短语匹配
        elif contains_protected_words(keyword) and word_count <= 3:
            suggestion = "短语匹配"
        
        df.at[idx, 'match_type_suggestion'] = suggestion
    
    return df

def add_intelligent_bid_suggestions(df):
    """添加智能出价建议"""
    for idx, row in df.iterrows():
        suggestion = "维持"
        
        # 高质量高ROAS关键词 - 提高出价
        if (row['quality_score'] > 75 and 
            row['roas'] > 3 and 
            row['orders'] >= 2):
            increase_pct = min(50, (row['roas'] - 2) * 10)
            suggestion = f"提高{increase_pct:.0f}%"
        
        # 高相关性但低转化 - 小幅度提高测试
        elif (row['relevance_score'] > 8 and 
              row['orders'] == 0 and 
              row['clicks'] > 5 and
              row['ctr'] > 0.002):
            suggestion = "提高10%测试"
        
        # 低质量低ROAS关键词 - 降低出价或暂停
        elif (row['quality_score'] < 40 and 
              row['roas'] < 1 and
              row['spend'] > 0.5):
            if row['impressions'] < 30 or contains_protected_words(str(row['keyword'])):
                suggestion = "降低50%"
            else:
                suggestion = "暂停"
        
        # 高花费无产出 - 暂停
        elif (row['orders'] == 0 and 
              row['spend'] > 2 and
              row['ctr'] < 0.001):
            suggestion = "暂停"
        
        df.at[idx, 'bid_suggestion'] = suggestion
    
    return df

def add_asin_related_suggestions(df, asin_analysis):
    """添加ASIN相关建议"""
    if asin_analysis.empty or 'asin' not in df.columns:
        return df
    
    # 获取表现优秀的ASIN
    top_asins = asin_analysis[asin_analysis['performance_rating'] == '优秀']['asin'].head(3).tolist()
    
    for idx, row in df.iterrows():
        suggestion = ""
        
        # 如果关键词关联了优秀ASIN
        if 'asin' in row and row['asin'] in top_asins:
            suggestion = "关联优秀ASIN，可适当提高出价"
        
        df.at[idx, 'asin_related_suggestion'] = suggestion
    
    return df

def add_keyword_trend_labels(df):
    """添加关键词趋势标签"""
    if 'date' not in df.columns:
        return df
    
    try:
        # 如果有足够的历史数据，计算趋势
        df_trend = df.copy()
        df_trend['week'] = df_trend['date'].dt.to_period('W')
        
        # 这里简化处理，实际可以根据具体数据计算趋势
        for idx, row in df.iterrows():
            # 根据表现设置趋势标签
            if row['orders'] > 0 and row['roas'] > 2:
                df.at[idx, 'keyword_trend'] = "上升"
            elif row['orders'] == 0 and row['spend'] > 0.5:
                df.at[idx, 'keyword_trend'] = "下降"
            elif row['ctr'] > 0.005:
                df.at[idx, 'keyword_trend'] = "潜力"
            else:
                df.at[idx, 'keyword_trend'] = "稳定"
    
    except:
        pass
    
    return df

def generate_campaign_recommendations(df, converting_roots, waste_keywords, asin_analysis):
    """生成广告组合级别的建议"""
    recommendations = []
    
    # 基础信息
    total_keywords = len(df)
    converting_keywords = len(df[df['orders'] > 0])
    waste_keyword_count = len(waste_keywords)
    total_spend = df['spend'].sum()
    total_sales = df['sales'].sum()
    
    # 1. 整体表现评估
    if total_spend > 0:
        campaign_roas = total_sales / total_spend
        if campaign_roas > 3:
            recommendations.append("✅ 广告组合整体表现优秀，ROAS达到目标")
        elif campaign_roas > 1.5:
            recommendations.append("⚠️ 广告组合表现一般，有优化空间")
        else:
            recommendations.append("❌ 广告组合表现不佳，需要重点优化")
    
    # 2. 关键词质量建议
    quality_scores = df['quality_score']
    avg_quality = quality_scores.mean()
    if avg_quality > 70:
        recommendations.append("✅ 关键词整体质量较高，继续保持")
    elif avg_quality > 50:
        recommendations.append("⚠️ 关键词质量中等，建议优化低分关键词")
    else:
        recommendations.append("❌ 关键词质量普遍较低，需要全面优化")
    
    # 3. 高效词根建议
    if converting_roots:
        top_5_roots = [root for root, _ in converting_roots[:5]]
        recommendations.append(f"🎯 建议围绕这些高效词根拓展关键词: {', '.join(top_5_roots)}")
    
    # 4. 否定词建议
    if waste_keyword_count > 0:
        waste_spend = waste_keywords['spend'].sum()
        recommendations.append(f"💰 发现{waste_keyword_count}个待否定关键词，预计可节省¥{waste_spend:.2f}")
    
    # 5. ASIN相关建议
    if not asin_analysis.empty:
        top_asins = asin_analysis.head(3)
        if len(top_asins) > 0:
            asin_list = ', '.join(top_asins['asin'].tolist())
            recommendations.append(f"🏆 表现最佳ASIN: {asin_list}，建议重点投放")
        
        # 检查是否有表现差的ASIN
        poor_asins = asin_analysis[asin_analysis['performance_rating'] == '需优化']
        if len(poor_asins) > 0:
            recommendations.append(f"⚠️ 有{len(poor_asins)}个ASIN表现不佳，建议优化或暂停")
    
    # 6. 广告结构建议
    ad_groups = df['ad_group'].nunique()
    if ad_groups < 3:
        recommendations.append("📊 广告组数量较少，建议根据词根创建更多精准广告组")
    elif ad_groups > 10:
        recommendations.append("📊 广告组数量较多，建议合并相似广告组")
    
    # 7. 预算分配建议
    if total_spend > 100:
        high_roas_keywords = df[df['roas'] > 3]
        high_roas_spend = high_roas_keywords['spend'].sum()
        high_roas_ratio = high_roas_spend / total_spend
        
        if high_roas_ratio < 0.3:
            recommendations.append("💰 高ROAS关键词花费占比偏低，建议增加预算分配")
        elif high_roas_ratio > 0.7:
            recommendations.append("💰 高ROAS关键词花费集中，建议测试新关键词扩大流量")
    
    # 8. 时间优化建议
    if 'date' in df.columns:
        weekly_trend = df.groupby(df['date'].dt.dayofweek).agg({'orders': 'sum', 'spend': 'sum'})
        if not weekly_trend.empty:
            best_day = weekly_trend['orders'].idxmax() if weekly_trend['orders'].sum() > 0 else None
            if best_day is not None:
                day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
                recommendations.append(f"📅 最佳转化日为{day_names[best_day]}，可适当提高出价")
    
    return recommendations

def calculate_campaign_statistics(df, asin_analysis):
    """计算广告组合详细统计"""
    stats = {}
    
    # 基础统计
    stats['关键词总数'] = len(df)
    stats['出单关键词数'] = len(df[df['orders'] > 0])
    stats['高质量关键词数'] = len(df[df['quality_score'] > 70])
    stats['待否定关键词数'] = len(df[df['negation_suggestion'].str.contains('否定', na=False)])
    
    # 表现统计
    total_impressions = df['impressions'].sum()
    total_clicks = df['clicks'].sum()
    total_spend = df['spend'].sum()
    total_sales = df['sales'].sum()
    total_orders = df['orders'].sum()
    
    stats['总展示量'] = f"{total_impressions:,}"
    stats['总点击量'] = f"{total_clicks:,}"
    stats['总花费'] = f"¥{total_spend:,.2f}"
    stats['总销售额'] = f"¥{total_sales:,.2f}"
    stats['总订单数'] = f"{total_orders:,}"
    
    # 指标统计
    if total_impressions > 0:
        stats['平均CTR'] = f"{total_clicks/total_impressions:.2%}"
    if total_clicks > 0:
        stats['平均转化率'] = f"{total_orders/total_clicks:.2%}"
    if total_sales > 0:
        stats['平均ACOS'] = f"{total_spend/total_sales:.1%}"
    if total_spend > 0:
        stats['平均ROAS'] = f"{total_sales/total_spend:.2f}"
    
    # ASIN统计
    if not asin_analysis.empty:
        stats['ASIN数量'] = len(asin_analysis)
        stats['优秀ASIN数'] = len(asin_analysis[asin_analysis['performance_rating'] == '优秀'])
        stats['需优化ASIN数'] = len(asin_analysis[asin_analysis['performance_rating'] == '需优化'])
    
    # 分布统计
    stats['关键词长度分布'] = {
        '短词(1-2词)': len(df[df['keyword'].str.split().apply(len) <= 2]),
        '中词(3-4词)': len(df[df['keyword'].str.split().apply(len).between(3, 4)]),
        '长词(5+词)': len(df[df['keyword'].str.split().apply(len) >= 5])
    }
    
    return stats

def get_campaign_summary_stats(df):
    """获取广告组合摘要统计"""
    if len(df) == 0:
        return {}
    
    stats = {}
    
    # 基本统计
    stats['关键词总数'] = len(df)
    stats['出单关键词数'] = len(df[df['orders'] > 0])
    stats['高质量关键词数'] = len(df[df['quality_score'] > 70])
    stats['待否定关键词数'] = len(df[df['negation_suggestion'].str.contains('否定', na=False)])
    stats['核心产品关键词数'] = len(df[df['keyword'].apply(contains_protected_words)])
    
    # 花费统计
    stats['总花费'] = f"¥{df['spend'].sum():.2f}"
    stats['总销售额'] = f"¥{df['sales'].sum():.2f}"
    stats['总订单数'] = int(df['orders'].sum())
    
    # 表现指标
    total_impressions = df['impressions'].sum()
    total_clicks = df['clicks'].sum()
    total_spend = df['spend'].sum()
    total_sales = df['sales'].sum()
    
    if total_impressions > 0:
        stats['平均CTR'] = f"{total_clicks / total_impressions:.2%}"
    else:
        stats['平均CTR'] = "0%"
    
    if total_clicks > 0:
        stats['平均转化率'] = f"{df['orders'].sum() / total_clicks:.2%}"
    else:
        stats['平均转化率'] = "0%"
    
    if total_sales > 0:
        stats['平均ACOS'] = f"{total_spend / total_sales:.1%}"
    else:
        stats['平均ACOS'] = "0%"
    
    if total_spend > 0:
        stats['平均ROAS'] = f"{total_sales / total_spend:.2f}"
    else:
        stats['平均ROAS'] = "0"
    
    stats['平均质量得分'] = f"{df['quality_score'].mean():.1f}"
    
    # ASIN统计（如果有）
    if 'asin' in df.columns and df['asin'].notna().any():
        stats['关联ASIN数'] = df['asin'].nunique()
    
    # 优化建议统计
    high_priority = len(df[df['optimization_priority'] == '高'])
    medium_priority = len(df[df['optimization_priority'] == '中'])
    stats['高优先级优化'] = high_priority
    stats['中优先级优化'] = medium_priority
    
    return stats

def generate_search_term_analysis(df):
    """生成搜索词分析报告 - 增强版，增加ASIN分析"""
    analysis = {}
    
    try:
        # 1. 匹配类型分析
        if 'match_type' in df.columns:
            match_analysis = df.groupby('match_type').agg(
                impressions=('impressions', 'sum'),
                clicks=('clicks', 'sum'),
                orders=('orders', 'sum'),
                spend=('spend', 'sum'),
                sales=('sales', 'sum'),
                keyword_count=('keyword', 'nunique'),
                avg_quality_score=('quality_score', 'mean')
            ).reset_index()
            
            # 计算关键指标
            match_analysis['ctr'] = match_analysis['clicks'] / match_analysis['impressions'].replace(0, 1)
            match_analysis['conversion_rate'] = match_analysis['orders'] / match_analysis['clicks'].replace(0, 1)
            match_analysis['acos'] = match_analysis['spend'] / match_analysis['sales'].replace(0, 1)
            match_analysis['roas'] = match_analysis['sales'] / match_analysis['spend'].replace(0, 1)
            analysis['匹配类型分析'] = match_analysis
        
        # 2. 高潜力关键词 (高点击但低转化)
        if len(df) > 10:
            high_potential = df[
                (df['clicks'] > df['clicks'].quantile(0.7)) & 
                (df['conversion_rate'] < df['conversion_rate'].median()) &
                (df['quality_score'] > 50) &
                (~df['keyword'].apply(lambda x: '否定' in str(x)))
            ].sort_values('quality_score', ascending=False).head(20)
            analysis['高潜力关键词'] = high_potential
        
        # 3. 高转化高ROAS搜索词
        if len(df) > 10:
            high_performance = df[
                (df['orders'] > df['orders'].quantile(0.8)) & 
                (df['roas'] > df['roas'].quantile(0.8)) &
                (df['conversion_rate'] > 0.01)
            ].sort_values(['roas', 'orders'], ascending=[False, False]).head(20)
            analysis['高转化高ROAS搜索词'] = high_performance
        
        # 4. 搜索词词频分析
        keyword_freq = pd.DataFrame(Counter(df['keyword']).most_common(30), 
                                   columns=['keyword', 'frequency'])
        analysis['搜索词词频分析'] = keyword_freq
        
        # 5. 重复关键词分析
        keyword_performance = df.groupby('keyword').agg(
            campaign_count=('campaign', 'nunique'),
            ad_group_count=('ad_group', 'nunique'),
            total_spend=('spend', 'sum'),
            total_orders=('orders', 'sum'),
            avg_roas=('roas', 'mean'),
            avg_quality_score=('quality_score', 'mean')
        ).reset_index()
        
        duplicate_keywords = keyword_performance[keyword_performance['campaign_count'] > 1].sort_values('total_spend', ascending=False)
        analysis['重复关键词分析'] = duplicate_keywords
        
        # 6. 关键词组合分析
        analysis['关键词组合分析'] = generate_keyword_combinations_enhanced(df)
        
        # 7. 关键词相关性分析
        relevance_analysis = analyze_keyword_relevance(df)
        analysis['关键词相关性分析'] = relevance_analysis
        
        # 8. ASIN表现分析
        asin_analysis = generate_asin_analysis(df)
        analysis['ASIN表现分析'] = asin_analysis
        
        # 9. 新增：搜索词中的ASIN分析
        if 'extracted_asins' in df.columns:
            search_term_asins = analyze_search_term_asins_full(df)
            analysis['搜索词ASIN分析'] = search_term_asins
        
        # 10. 表现趋势分析
        if 'date' in df.columns and not df['date'].isna().all():
            trend_analysis = analyze_performance_trends(df)
            analysis['表现趋势分析'] = trend_analysis
        
        # 11. 否定词分析统计
        negation_stats = analyze_negation_statistics(df)
        analysis['否定词分析统计'] = negation_stats
        
        # 12. 广告组合对比分析
        campaign_comparison = generate_campaign_comparison(df)
        analysis['广告组合对比分析'] = campaign_comparison
        
        # 13. 关键词长度效益分析
        keyword_length_analysis = analyze_keyword_length_performance(df)
        analysis['关键词长度效益分析'] = keyword_length_analysis
        
    except Exception as e:
        print(f"生成搜索词分析时出错: {str(e)}")
        traceback.print_exc()
    
    return analysis

def analyze_search_term_asins_full(df):
    """全面分析搜索词中的ASIN表现"""
    try:
        # 检查是否有提取的ASIN数据
        if 'extracted_asins' not in df.columns or df['extracted_asins'].isna().all():
            return pd.DataFrame()
        
        # 展开数据：每行可能包含多个ASIN
        asin_data = []
        asin_keyword_map = {}  # 记录ASIN和关键词的对应关系
        
        for idx, row in df.iterrows():
            if row['extracted_asins'] and len(row['extracted_asins']) > 0:
                for asin in row['extracted_asins']:
                    asin_data.append({
                        'asin': asin,
                        'keyword': row['keyword'],
                        'campaign': row['campaign'],
                        'ad_group': row['ad_group'],
                        'impressions': row['impressions'],
                        'clicks': row['clicks'],
                        'orders': row['orders'],
                        'spend': row['spend'],
                        'sales': row['sales'],
                        'ctr': row['ctr'],
                        'conversion_rate': row['conversion_rate'],
                        'roas': row['roas'],
                        'acos': row['acos'],
                        'quality_score': row['quality_score']
                    })
                    
                    # 记录ASIN-关键词映射
                    if asin not in asin_keyword_map:
                        asin_keyword_map[asin] = []
                    asin_keyword_map[asin].append(row['keyword'])
        
        if not asin_data:
            return pd.DataFrame()
        
        # 创建ASIN分析DataFrame
        asin_df = pd.DataFrame(asin_data)
        
        # 按ASIN汇总
        asin_analysis = asin_df.groupby('asin').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'orders': 'sum',
            'spend': 'sum',
            'sales': 'sum',
            'keyword': 'nunique',
            'campaign': 'nunique',
            'ad_group': 'nunique',
            'quality_score': 'mean'
        }).reset_index()
        
        # 计算关键指标
        asin_analysis['ctr'] = asin_analysis['clicks'] / asin_analysis['impressions'].replace(0, 1)
        asin_analysis['conversion_rate'] = asin_analysis['orders'] / asin_analysis['clicks'].replace(0, 1)
        asin_analysis['acos'] = asin_analysis['spend'] / asin_analysis['sales'].replace(0, 1)
        asin_analysis['roas'] = asin_analysis['sales'] / asin_analysis['spend'].replace(0, 1)
        asin_analysis['cpc'] = asin_analysis['spend'] / asin_analysis['clicks'].replace(0, 1)
        
        # 计算ASIN表现得分
        asin_analysis['performance_score'] = (
            asin_analysis['conversion_rate'] * 40 +
            asin_analysis['roas'] * 30 +
            asin_analysis['ctr'] * 20 +
            np.log1p(asin_analysis['orders']) * 10
        )
        
        # 添加ASIN表现评级
        asin_analysis['performance_rating'] = asin_analysis['performance_score'].apply(
            lambda x: '优秀' if x > 60 else ('良好' if x > 40 else '需优化')
        )
        
        # 添加ASIN类型标识
        asin_analysis['asin_source'] = '搜索词提取'
        
        # 添加关联关键词示例
        asin_analysis['关联关键词示例'] = asin_analysis['asin'].apply(
            lambda x: ', '.join(asin_keyword_map.get(x, [])[:3])  # 显示前3个关联关键词
        )
        
        # 添加建议
        def get_search_term_asin_recommendation(row):
            recommendations = []
            
            if row['orders'] == 0:
                if row['spend'] > 1:
                    recommendations.append("搜索词包含但无转化，考虑暂停相关关键词")
                elif row['impressions'] > 100:
                    recommendations.append("有展示但无点击，检查ASIN相关性")
            elif row['roas'] > 3:
                recommendations.append("表现优秀，可围绕此ASIN拓展关键词")
            elif row['conversion_rate'] < 0.01 and row['clicks'] > 10:
                recommendations.append("点击多但转化低，检查ASIN是否为目标商品")
            
            if row['keyword'] >= 5:
                recommendations.append(f"与{row['keyword']}个关键词关联")
            
            return "；".join(recommendations) if recommendations else "表现正常"
        
        asin_analysis['recommendation'] = asin_analysis.apply(get_search_term_asin_recommendation, axis=1)
        
        # 按表现得分排序
        asin_analysis = asin_analysis.sort_values('performance_score', ascending=False)
        
        print(f"搜索词ASIN全面分析: 发现{len(asin_analysis)}个商品ASIN，来自{len(asin_data)}条数据")
        
        return asin_analysis
    
    except Exception as e:
        print(f"全面分析搜索词ASIN时出错: {str(e)}")
        traceback.print_exc()
        return pd.DataFrame()

def generate_campaign_comparison(df):
    """生成广告组合对比分析"""
    try:
        # 按广告组合汇总
        campaign_comparison = df.groupby('campaign').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'orders': 'sum',
            'spend': 'sum',
            'sales': 'sum',
            'keyword': 'nunique',
            'quality_score': 'mean'
        }).reset_index()
        
        # 计算关键指标
        campaign_comparison['ctr'] = campaign_comparison['clicks'] / campaign_comparison['impressions'].replace(0, 1)
        campaign_comparison['conversion_rate'] = campaign_comparison['orders'] / campaign_comparison['clicks'].replace(0, 1)
        campaign_comparison['acos'] = campaign_comparison['spend'] / campaign_comparison['sales'].replace(0, 1)
        campaign_comparison['roas'] = campaign_comparison['sales'] / campaign_comparison['spend'].replace(0, 1)
        campaign_comparison['cpc'] = campaign_comparison['spend'] / campaign_comparison['clicks'].replace(0, 1)
        
        # 计算效率得分
        campaign_comparison['效率得分'] = (
            campaign_comparison['conversion_rate'] * 40 +
            campaign_comparison['roas'] * 30 +
            campaign_comparison['ctr'] * 100 +
            np.log1p(campaign_comparison['orders']) * 10
        )
        
        # 添加排名
        campaign_comparison['CTR排名'] = campaign_comparison['ctr'].rank(ascending=False)
        campaign_comparison['转化率排名'] = campaign_comparison['conversion_rate'].rank(ascending=False)
        campaign_comparison['ROAS排名'] = campaign_comparison['roas'].rank(ascending=False)
        campaign_comparison['效率排名'] = campaign_comparison['效率得分'].rank(ascending=False)
        
        # 添加表现评级
        campaign_comparison['表现评级'] = campaign_comparison['效率得分'].apply(
            lambda x: '优秀' if x > 60 else ('良好' if x > 40 else '需优化')
        )
        
        return campaign_comparison.sort_values('效率得分', ascending=False)
        
    except:
        return pd.DataFrame()

def analyze_keyword_length_performance(df):
    """分析关键词长度与表现的关系"""
    try:
        # 计算关键词长度
        df_length = df.copy()
        df_length['keyword_length'] = df_length['keyword'].astype(str).apply(lambda x: len(x.split()))
        
        # 按关键词长度分组分析
        length_analysis = df_length.groupby('keyword_length').agg({
            'impressions': 'mean',
            'clicks': 'mean',
            'orders': 'mean',
            'spend': 'mean',
            'sales': 'mean',
            'ctr': 'mean',
            'conversion_rate': 'mean',
            'roas': 'mean',
            'quality_score': 'mean',
            'keyword': 'count'
        }).reset_index()
        
        # 重命名列
        length_analysis = length_analysis.rename(columns={
            'keyword': '关键词数量',
            'impressions': '平均展示量',
            'clicks': '平均点击量',
            'orders': '平均订单量',
            'spend': '平均花费',
            'sales': '平均销售额',
            'ctr': '平均CTR',
            'conversion_rate': '平均转化率',
            'roas': '平均ROAS',
            'quality_score': '平均质量得分'
        })
        
        return length_analysis.sort_values('keyword_length')
        
    except:
        return pd.DataFrame()

def generate_asin_analysis(df):
    """生成ASIN分析报告"""
    if 'asin' not in df.columns or df['asin'].isna().all():
        return pd.DataFrame()
    
    try:
        # 过滤有效的ASIN
        asin_pattern = re.compile(r'^B0[0-9A-Z]{8,9}$')
        asin_df = df[df['asin'].notna() & df['asin'].apply(lambda x: bool(asin_pattern.match(str(x))) if pd.notna(x) else False)].copy()
        
        if len(asin_df) == 0:
            return pd.DataFrame()
        
        # 按ASIN汇总
        asin_analysis = asin_df.groupby('asin').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'orders': 'sum',
            'spend': 'sum',
            'sales': 'sum',
            'keyword': 'nunique',
            'campaign': 'nunique',
            'ad_group': 'nunique',
            'quality_score': 'mean'
        }).reset_index()
        
        # 计算关键指标
        asin_analysis['ctr'] = asin_analysis['clicks'] / asin_analysis['impressions'].replace(0, 1)
        asin_analysis['conversion_rate'] = asin_analysis['orders'] / asin_analysis['clicks'].replace(0, 1)
        asin_analysis['acos'] = asin_analysis['spend'] / asin_analysis['sales'].replace(0, 1)
        asin_analysis['roas'] = asin_analysis['sales'] / asin_analysis['spend'].replace(0, 1)
        asin_analysis['cpc'] = asin_analysis['spend'] / asin_analysis['clicks'].replace(0, 1)
        
        # 计算综合得分
        asin_analysis['综合得分'] = (
            asin_analysis['conversion_rate'] * 40 +
            asin_analysis['roas'] * 30 +
            asin_analysis['ctr'] * 20 +
            np.log1p(asin_analysis['orders']) * 10
        )
        
        # 添加评级
        asin_analysis['评级'] = asin_analysis['综合得分'].apply(
            lambda x: '优秀' if x > 60 else ('良好' if x > 40 else '需优化')
        )
        
        # 添加建议
        def get_asin_recommendation(row):
            if row['orders'] == 0 and row['spend'] > 1:
                return "暂停投放"
            elif row['roas'] > 4 and row['orders'] >= 5:
                return "增加预算，重点投放"
            elif row['ctr'] < 0.001 and row['impressions'] > 100:
                return "优化Listing主图"
            elif row['conversion_rate'] < 0.005 and row['clicks'] > 20:
                return "优化价格和促销"
            elif row['keyword'] < 3:
                return "增加关键词覆盖"
            else:
                return "保持监控"
        
        asin_analysis['优化建议'] = asin_analysis.apply(get_asin_recommendation, axis=1)
        
        # 按综合得分排序
        asin_analysis = asin_analysis.sort_values('综合得分', ascending=False)
        
        return asin_analysis
        
    except Exception as e:
        print(f"生成ASIN分析时出错: {str(e)}")
        return pd.DataFrame()

def generate_keyword_combinations_enhanced(df):
    """生成关键词组合分析报告 - 增强版"""
    try:
        # 提取所有高效词根
        converting_keywords = df[df['orders'] > 0]
        
        if len(converting_keywords) == 0:
            return pd.DataFrame()
        
        converting_roots = []
        for keyword in converting_keywords['keyword']:
            roots = extract_roots(keyword)
            # 排除受保护的核心词（它们太通用）
            filtered_roots = [root for root in roots if not is_protected_word(root)]
            for root in filtered_roots:
                keyword_orders = converting_keywords[converting_keywords['keyword'] == keyword]['orders'].values[0]
                converting_roots.append((root, keyword_orders))
        
        converting_root_counter = Counter()
        for root, weight in converting_roots:
            converting_root_counter[root] += weight
        
        # 取前10个非受保护的高频词根
        top_roots = [root for root, count in converting_root_counter.most_common(20) 
                    if not is_protected_word(root) and count >= 2][:10]
        
        if len(top_roots) < 2:
            return pd.DataFrame()
        
        # 生成词根组合
        root_combinations = []
        for i in range(2, 4):  # 生成2-3个词根的组合
            for combo in combinations(top_roots, i):
                root_combinations.append(" ".join(combo))
        
        # 分析现有关键词中是否包含这些组合
        existing_combos = []
        for combo in root_combinations:
            matching_keywords = df[df['keyword'].str.contains(combo, case=False, na=False)]
            if not matching_keywords.empty:
                combo_perf = matching_keywords.agg({
                    'impressions': 'sum',
                    'clicks': 'sum',
                    'orders': 'sum',
                    'spend': 'sum',
                    'sales': 'sum'
                })
                
                existing_combos.append({
                    '关键词组合': combo,
                    '现有关键词数': len(matching_keywords),
                    '展示量': combo_perf['impressions'],
                    '点击量': combo_perf['clicks'],
                    '订单数': combo_perf['orders'],
                    '花费': combo_perf['spend'],
                    '销售额': combo_perf['sales'],
                    '状态': '已存在'
                })
            else:
                # 新组合建议
                existing_combos.append({
                    '关键词组合': combo,
                    '现有关键词数': 0,
                    '展示量': 0,
                    '点击量': 0,
                    '订单数': 0,
                    '花费': 0,
                    '销售额': 0,
                    '状态': '建议添加'
                })
        
        # 创建结果DataFrame
        if existing_combos:
            combo_df = pd.DataFrame(existing_combos)
            combo_df['CTR'] = combo_df['点击量'] / combo_df['展示量'].replace(0, 1)
            combo_df['转化率'] = combo_df['订单数'] / combo_df['点击量'].replace(0, 1)
            combo_df['ROAS'] = combo_df['销售额'] / combo_df['花费'].replace(0, 1)
            combo_df['效率得分'] = combo_df['订单数'] / (combo_df['花费'] + 0.01)
            combo_df = combo_df.sort_values(['状态', '效率得分'], ascending=[True, False])
        else:
            combo_df = pd.DataFrame()
        
        return combo_df
        
    except Exception as e:
        print(f"生成关键词组合分析时出错: {str(e)}")
        return pd.DataFrame()

def analyze_keyword_relevance(df):
    """分析关键词相关性"""
    try:
        # 分类关键词
        keyword_categories = []
        
        for idx, row in df.iterrows():
            keyword = str(row['keyword']).lower()
            category = "其他"
            
            # 检查是否包含核心产品词
            if contains_protected_words(keyword):
                category = "核心产品词"
            # 检查是否包含购买意图词
            elif any(word in keyword for word in ['buy', 'purchase', 'price', 'cheap', 'sale', 'discount']):
                category = "购买意图词"
            # 检查是否包含功能描述词
            elif any(word in keyword for word in ['how', 'use', 'work', 'benefit', 'review', 'compare']):
                category = "信息查询词"
            # 检查是否包含品牌词
            elif any(word in keyword for word in ['brand', 'best', 'top', 'quality', 'professional']):
                category = "品牌/质量词"
            
            keyword_categories.append({
                '关键词': row['keyword'],
                '分类': category,
                '花费': row['spend'],
                '订单': row['orders'],
                'ROAS': row['roas'],
                '质量得分': row['quality_score']
            })
        
        category_df = pd.DataFrame(keyword_categories)
        
        # 按分类汇总
        category_summary = category_df.groupby('分类').agg({
            '关键词': 'count',
            '花费': 'sum',
            '订单': 'sum',
            'ROAS': 'mean',
            '质量得分': 'mean'
        }).reset_index()
        
        category_summary = category_summary.rename(columns={
            '关键词': '关键词数量',
            '花费': '总花费',
            '订单': '总订单'
        })
        
        return category_summary
        
    except:
        return pd.DataFrame()

def analyze_performance_trends(df):
    """分析表现趋势"""
    try:
        if 'date' not in df.columns or df['date'].isna().all():
            return pd.DataFrame()
        
        # 按周分组
        df_trend = df.copy()
        df_trend['week'] = df_trend['date'].dt.isocalendar().week
        df_trend['year'] = df_trend['date'].dt.year
        df_trend['year_week'] = df_trend['year'].astype(str) + '-W' + df_trend['week'].astype(str).str.zfill(2)
        
        weekly_trend = df_trend.groupby('year_week').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'orders': 'sum',
            'spend': 'sum',
            'sales': 'sum'
        }).reset_index()
        
        # 计算指标
        weekly_trend['CTR'] = weekly_trend['clicks'] / weekly_trend['impressions'].replace(0, 1)
        weekly_trend['转化率'] = weekly_trend['orders'] / weekly_trend['clicks'].replace(0, 1)
        weekly_trend['ROAS'] = weekly_trend['sales'] / weekly_trend['spend'].replace(0, 1)
        weekly_trend['ACOS'] = weekly_trend['spend'] / weekly_trend['sales'].replace(0, 1)
        weekly_trend['CPC'] = weekly_trend['spend'] / weekly_trend['clicks'].replace(0, 1)
        
        # 计算周环比
        if len(weekly_trend) > 1:
            weekly_trend['花费环比'] = weekly_trend['spend'].pct_change() * 100
            weekly_trend['销售额环比'] = weekly_trend['sales'].pct_change() * 100
            weekly_trend['ROAS环比'] = weekly_trend['ROAS'].pct_change() * 100
        
        return weekly_trend
        
    except:
        return pd.DataFrame()

def analyze_negation_statistics(df):
    """分析否定词统计"""
    if 'negation_suggestion' not in df.columns:
        return pd.DataFrame()
    
    try:
        # 分类否定建议
        df_neg = df.copy()
        df_neg['否定类型'] = '保留'
        
        # 分类否定类型
        mask_neg_exact = df_neg['negation_suggestion'].str.contains('否定精准', na=False)
        mask_neg_phrase = df_neg['negation_suggestion'].str.contains('否定词组', na=False)
        mask_monitor = df_neg['negation_suggestion'].str.contains('监控', na=False)
        
        df_neg.loc[mask_neg_exact, '否定类型'] = '精准否定'
        df_neg.loc[mask_neg_phrase, '否定类型'] = '词组否定'
        df_neg.loc[mask_monitor, '否定类型'] = '监控'
        
        # 按类型汇总
        negation_summary = df_neg.groupby('否定类型').agg({
            'keyword': 'count',
            'spend': 'sum',
            'orders': 'sum',
            'impressions': 'sum',
            'clicks': 'sum'
        }).reset_index()
        
        negation_summary = negation_summary.rename(columns={
            'keyword': '关键词数量',
            'spend': '总花费',
            'orders': '总订单',
            'impressions': '总展示',
            'clicks': '总点击'
        })
        
        # 计算节省潜力
        total_waste_spend = negation_summary[negation_summary['否定类型'].isin(['精准否定', '词组否定'])]['总花费'].sum()
        potential_savings = total_waste_spend * 0.7  # 假设节省70%
        
        savings_row = pd.DataFrame([{
            '否定类型': '潜在节省',
            '关键词数量': 0,
            '总花费': potential_savings,
            '总订单': 0,
            '总展示': 0,
            '总点击': 0
        }])
        
        negation_summary = pd.concat([negation_summary, savings_row], ignore_index=True)
        
        return negation_summary
        
    except:
        return pd.DataFrame()

def generate_campaign_analysis(df):
    """生成广告活动分析报告"""
    try:
        # 按广告组合和广告组汇总
        summary = df.groupby(['campaign', 'ad_group']).agg(
            impressions=('impressions', 'sum'),
            clicks=('clicks', 'sum'),
            orders=('orders', 'sum'),
            spend=('spend', 'sum'),
            sales=('sales', 'sum'),
            keyword_count=('keyword', 'nunique'),
            avg_quality_score=('quality_score', 'mean'),
            avg_relevance_score=('relevance_score', 'mean')
        ).reset_index()
        
        # 计算关键指标
        summary['ctr'] = summary['clicks'] / summary['impressions'].replace(0, 1)
        summary['conversion_rate'] = summary['orders'] / summary['clicks'].replace(0, 1)
        summary['acos'] = summary['spend'] / summary['sales'].replace(0, 1)
        summary['roas'] = summary['sales'] / summary['spend'].replace(0, 1)
        summary['cpc'] = summary['spend'] / summary['clicks'].replace(0, 1)
        
        # 计算广告组效率得分 - 增强算法
        summary['efficiency_score'] = (
            summary['conversion_rate'] * 40 + 
            summary['roas'] * 30 +
            summary['ctr'] * 100 +  # 放大CTR权重
            np.log1p(summary['orders']) * 15 +
            summary['avg_quality_score'] * 0.5 +
            summary['avg_relevance_score'] * 0.3
        )
        
        # 添加总体汇总
        total = df.agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'orders': 'sum',
            'spend': 'sum',
            'sales': 'sum',
            'keyword': 'nunique',
            'quality_score': 'mean',
            'relevance_score': 'mean'
        }).to_dict()
        
        total['campaign'] = '总体'
        total['ad_group'] = '汇总'
        total['ctr'] = total['clicks'] / total['impressions'] if total['impressions'] > 0 else 0
        total['conversion_rate'] = total['orders'] / total['clicks'] if total['clicks'] > 0 else 0
        total['acos'] = total['spend'] / total['sales'] if total['sales'] > 0 else 0
        total['roas'] = total['sales'] / total['spend'] if total['spend'] > 0 else 0
        total['cpc'] = total['spend'] / total['clicks'] if total['clicks'] > 0 else 0
        total['avg_quality_score'] = total['quality_score']
        total['avg_relevance_score'] = total['relevance_score']
        total['efficiency_score'] = (
            total['conversion_rate'] * 40 + 
            total['roas'] * 30 +
            total['ctr'] * 100 +
            np.log1p(total['orders']) * 15 +
            total['avg_quality_score'] * 0.5 +
            total['avg_relevance_score'] * 0.3
        )
        
        # 合并结果
        full_summary = pd.concat([summary, pd.DataFrame([total])], ignore_index=True)
        full_summary = full_summary.sort_values('efficiency_score', ascending=False)
        
        # 最佳关键词分析
        best_keywords = []
        for campaign in df['campaign'].unique():
            campaign_df = df[df['campaign'] == campaign]
            if not campaign_df.empty:
                # 取综合得分最高的关键词
                campaign_df['composite_score'] = campaign_df['quality_score'] * 0.7 + campaign_df['relevance_score'] * 0.3
                best = campaign_df.sort_values('composite_score', ascending=False).iloc[0]
                best_keywords.append({
                    '广告组合': campaign,
                    '最佳关键词': best['keyword'],
                    '质量得分': best['quality_score'],
                    '相关性得分': best['relevance_score'],
                    '综合得分': best['composite_score'],
                    '订单数': best['orders'],
                    '花费': best['spend'],
                    'ROAS': best['roas'],
                    'CTR': best['ctr'],
                    '转化率': best['conversion_rate']
                })
        
        return {
            '广告活动汇总': full_summary,
            '最佳关键词分析': pd.DataFrame(best_keywords)
        }
        
    except Exception as e:
        print(f"生成广告活动分析时出错: {str(e)}")
        return {'广告活动汇总': pd.DataFrame(), '最佳关键词分析': pd.DataFrame()}

def generate_visual_analysis(df, output_file):
    """生成可视化分析图表"""
    try:
        # 创建图表工作表
        with pd.ExcelWriter(output_file, engine='openpyxl', mode='a') as writer:
            workbook = writer.book
            
            # 创建可视化工作表
            ws = workbook.create_sheet('可视化分析')
            
            # 写入标题
            ws['A1'] = '亚马逊广告可视化分析报告'
            ws['A1'].font = TITLE_FONT
            ws['A1'].fill = TITLE_FILL
            ws.merge_cells('A1:H1')
            
            # 写入关键指标
            ws['A3'] = '核心指标概览'
            ws['A3'].font = HEADER_FONT
            ws['A3'].fill = HEADER_FILL
            ws.merge_cells('A3:H3')
            
            # 计算核心指标
            total_spend = df['spend'].sum()
            total_sales = df['sales'].sum()
            total_orders = df['orders'].sum()
            total_clicks = df['clicks'].sum()
            total_impressions = df['impressions'].sum()
            
            roas = total_sales / total_spend if total_spend > 0 else 0
            acos = total_spend / total_sales if total_sales > 0 else 0
            ctr = total_clicks / total_impressions if total_impressions > 0 else 0
            conversion_rate = total_orders / total_clicks if total_clicks > 0 else 0
            
            # 写入指标数据
            metrics = [
                ['指标', '数值', '目标值', '状态'],
                ['总花费', f'¥{total_spend:,.2f}', '根据预算调整', '实际'],
                ['总销售额', f'¥{total_sales:,.2f}', '最大化', '实际'],
                ['ROAS', f'{roas:.2f}', '>3.0', '优秀' if roas > 3 else ('良好' if roas > 2 else '需优化')],
                ['ACOS', f'{acos:.1%}', '<30%', '优秀' if acos < 0.3 else ('良好' if acos < 0.5 else '需优化')],
                ['CTR', f'{ctr:.2%}', '>0.5%', '优秀' if ctr > 0.005 else ('良好' if ctr > 0.003 else '需优化')],
                ['转化率', f'{conversion_rate:.2%}', '>1%', '优秀' if conversion_rate > 0.01 else ('良好' if conversion_rate > 0.005 else '需优化')]
            ]
            
            for i, row in enumerate(metrics):
                for j, value in enumerate(row):
                    cell = ws.cell(row=4+i, column=1+j, value=value)
                    cell.font = DEFAULT_FONT
                    cell.border = THIN_BORDER
                    cell.alignment = CENTER_ALIGN
                    
                    # 设置标题行样式
                    if i == 0:
                        cell.font = HEADER_FONT
                        cell.fill = HEADER_FILL
                    elif j == 3:  # 状态列
                        if value == '优秀':
                            cell.font = POSITIVE_FONT
                            cell.fill = POSITIVE_FILL
                        elif value == '需优化':
                            cell.font = NEGATIVE_FONT
                            cell.fill = NEGATIVE_FILL
            
            # 添加关键词质量分布
            ws['A12'] = '关键词质量分布'
            ws['A12'].font = HEADER_FONT
            ws['A12'].fill = HEADER_FILL
            ws.merge_cells('A12:H12')
            
            # 计算质量分布
            quality_bins = pd.cut(df['quality_score'], bins=[0, 40, 60, 80, 100], 
                                labels=['差(<40)', '中(40-60)', '良(60-80)', '优(>80)'])
            quality_dist = quality_bins.value_counts().sort_index()
            
            quality_data = [
                ['质量等级', '关键词数量', '占比'],
                ['优(>80)', quality_dist.get('优(>80)', 0), f"{quality_dist.get('优(>80)', 0)/len(df)*100:.1f}%"],
                ['良(60-80)', quality_dist.get('良(60-80)', 0), f"{quality_dist.get('良(60-80)', 0)/len(df)*100:.1f}%"],
                ['中(40-60)', quality_dist.get('中(40-60)', 0), f"{quality_dist.get('中(40-60)', 0)/len(df)*100:.1f}%"],
                ['差(<40)', quality_dist.get('差(<40)', 0), f"{quality_dist.get('差(<40)', 0)/len(df)*100:.1f}%"]
            ]
            
            for i, row in enumerate(quality_data):
                for j, value in enumerate(row):
                    cell = ws.cell(row=13+i, column=1+j, value=value)
                    cell.font = DEFAULT_FONT
                    cell.border = THIN_BORDER
                    cell.alignment = CENTER_ALIGN
                    
                    if i == 0:
                        cell.font = HEADER_FONT
                        cell.fill = HEADER_FILL
            
            # 调整列宽
            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 30)
                ws.column_dimensions[column_letter].width = adjusted_width
        
        print(f"可视化分析已添加到Excel文件")
        
    except Exception as e:
        print(f"生成可视化分析时出错: {str(e)}")

def generate_key_insights(df, campaign_analyses, search_term_analysis):
    """生成关键洞察与建议 - 增强版，增加ASIN分析"""
    insights = []
    
    # 总体表现
    total = df.agg({
        'spend': 'sum',
        'sales': 'sum',
        'orders': 'sum',
        'impressions': 'sum',
        'clicks': 'sum'
    })
    
    overall_roas = total['sales'] / total['spend'] if total['spend'] > 0 else 0
    overall_acos = total['spend'] / total['sales'] if total['sales'] > 0 else 0
    overall_ctr = total['clicks'] / total['impressions'] if total['impressions'] > 0 else 0
    overall_cr = total['orders'] / total['clicks'] if total['clicks'] > 0 else 0
    
    insights.append("=" * 80)
    insights.append("📊 亚马逊广告智能分析报告")
    insights.append("=" * 80)
    insights.append("")
    insights.append("🎯 核心表现指标")
    insights.append(f"总花费: ¥{total['spend']:.2f}")
    insights.append(f"总销售额: ¥{total['sales']:.2f}")
    insights.append(f"总订单: {int(total['orders'])}")
    insights.append(f"总体ROAS: {overall_roas:.2f} | ACOS: {overall_acos:.1%}")
    insights.append(f"总体CTR: {overall_ctr:.2%} | 转化率: {overall_cr:.2%}")
    
    # 关键词质量分析
    high_quality = len(df[df['quality_score'] >= 70])
    medium_quality = len(df[(df['quality_score'] >= 50) & (df['quality_score'] < 70)])
    low_quality = len(df[df['quality_score'] < 50])
    
    insights.append("")
    insights.append("📈 关键词质量分析")
    insights.append(f"高质量关键词(≥70分): {high_quality}个 ({high_quality/len(df)*100:.1f}%)")
    insights.append(f"中等质量关键词(50-69分): {medium_quality}个 ({medium_quality/len(df)*100:.1f}%)")
    insights.append(f"低质量关键词(<50分): {low_quality}个 ({low_quality/len(df)*100:.1f}%)")
    
    # 相关性分析
    core_keywords = len(df[df['keyword'].apply(contains_protected_words)])
    insights.append(f"核心产品关键词: {core_keywords}个 ({core_keywords/len(df)*100:.1f}%)")
    
    # ASIN分析 - 增强部分
    if 'asin' in df.columns and df['asin'].notna().any():
        asin_count = df['asin'].nunique()
        insights.append(f"关联ASIN数量: {asin_count}个")
    
    # 搜索词中的ASIN分析
    if 'extracted_asins' in df.columns:
        # 统计包含ASIN的搜索词
        asin_search_terms = df[df['extracted_asins'].apply(lambda x: len(x) > 0)]
        insights.append(f"包含商品ASIN的搜索词: {len(asin_search_terms)}个 ({len(asin_search_terms)/len(df)*100:.1f}%)")
        
        # 分析搜索词中的ASIN表现
        if '搜索词ASIN分析' in search_term_analysis and not search_term_analysis['搜索词ASIN分析'].empty:
            asin_analysis = search_term_analysis['搜索词ASIN分析']
            top_asins = asin_analysis.head(3)
            if len(top_asins) > 0:
                insights.append("")
                insights.append("🔍 搜索词中的商品ASIN表现:")
                for idx, row in top_asins.iterrows():
                    insights.append(f"  • {row['asin']}: ROAS={row['roas']:.2f}, 订单={row['orders']}, 关联{row['keyword']}个关键词")
        
        # 检查ASIN表现分析
        if 'ASIN表现分析' in search_term_analysis and not search_term_analysis['ASIN表现分析'].empty:
            asin_analysis = search_term_analysis['ASIN表现分析']
            top_asins = asin_analysis.head(3)
            if len(top_asins) > 0:
                insights.append("")
                insights.append("🏆 最佳表现ASIN:")
                for idx, row in top_asins.iterrows():
                    insights.append(f"  • {row['asin']}: ROAS={row['roas']:.2f}, 订单={row['orders']}")
    
    # 否定词分析
    negation_keywords = len(df[df['negation_suggestion'].str.contains('否定', na=False)])
    if negation_keywords > 0:
        waste_spend = df[df['negation_suggestion'].str.contains('否定', na=False)]['spend'].sum()
        insights.append("")
        insights.append("💰 否定词优化机会")
        insights.append(f"建议否定关键词: {negation_keywords}个")
        insights.append(f"潜在节省花费: ¥{waste_spend:.2f}")
        insights.append(f"预计每月节省: ¥{waste_spend * 4:.2f}")
    
    # 广告组合表现概览
    insights.append("")
    insights.append("📊 广告组合表现概览")
    for campaign_name, analysis in campaign_analyses.items():
        if analysis and 'summary_stats' in analysis:
            stats = analysis['summary_stats']
            if '总花费' in stats and '总订单数' in stats:
                spend_str = stats['总花费']
                orders_str = stats['总订单数']
                
                # 添加ASIN信息
                asin_info = ""
                if 'search_term_asin_analysis' in analysis and not analysis['search_term_asin_analysis'].empty:
                    asin_count = len(analysis['search_term_asin_analysis'])
                    asin_info = f", 搜索词ASIN:{asin_count}个"
                
                insights.append(f"• {campaign_name}: {spend_str}, 订单{orders_str}{asin_info}")
    
    # 最佳表现关键词
    if '最佳关键词分析' in search_term_analysis:
        best_df = search_term_analysis['最佳关键词分析']
        if not best_df.empty:
            insights.append("")
            insights.append("🏆 各广告组合最佳关键词")
            for _, row in best_df.head(5).iterrows():
                insights.append(f"• {row['广告组合']}: {row['最佳关键词']} (得分:{row['综合得分']:.1f}, ROAS:{row['ROAS']:.2f})")
    
    # 匹配类型建议
    if '匹配类型分析' in search_term_analysis:
        match_analysis = search_term_analysis['匹配类型分析']
        if not match_analysis.empty:
            insights.append("")
            insights.append("🎯 匹配类型优化建议")
            for _, row in match_analysis.iterrows():
                if row['keyword_count'] > 0:
                    insights.append(f"• {row['match_type']}: {row['keyword_count']}个词, ROAS:{row['roas']:.2f}, 转化率:{row['conversion_rate']:.2%}")
    
    # 高潜力关键词
    if '高潜力关键词' in search_term_analysis:
        high_potential = search_term_analysis['高潜力关键词']
        if not high_potential.empty:
            insights.append("")
            insights.append("🚀 高潜力关键词 (高点击低转化)")
            for _, row in high_potential.head(5).iterrows():
                insights.append(f"• {row['keyword']}: 点击{int(row['clicks'])}, 转化率{row['conversion_rate']:.2%}, 得分{row['quality_score']:.1f}")
    
    # 亚马逊算法优化建议 - 增加ASIN相关建议
    insights.append("")
    insights.append("🤖 亚马逊广告算法优化建议")
    insights.append("1. 优先优化CTR和相关性得分，这两项直接影响广告排名")
    insights.append("2. 高ROAS关键词适当提高出价，获取更多流量")
    insights.append("3. 及时添加否定词，避免无效花费影响广告质量")
    insights.append("4. 根据搜索词表现调整匹配类型：")
    insights.append("   - 高转化词 → 精准匹配")
    insights.append("   - 中等转化词 → 短语匹配") 
    insights.append("   - 探索新词 → 广泛匹配+否定")
    insights.append("5. 关注表现最佳的ASIN，围绕其优化关键词和广告内容")
    insights.append("6. 分析搜索词中的商品ASIN，识别竞品和关联商品机会")
    
    # 本周执行清单 - 增加ASIN相关任务
    insights.append("")
    insights.append("📋 本周优化执行清单")
    insights.append("✅ 立即执行:")
    insights.append("   1. 添加所有'否定精准'建议到否定列表")
    insights.append("   2. 将'提高出价'建议的关键词出价提高10-30%")
    insights.append("   3. 暂停所有'暂停'建议的关键词")
    insights.append("   4. 查看搜索词中的商品ASIN分析，识别竞品")
    insights.append("")
    insights.append("📅 本周内完成:")
    insights.append("   1. 根据'分组建议'重组广告结构")
    insights.append("   2. 测试'关键词组合分析'中的新组合")
    insights.append("   3. 优化'高潜力关键词'的落地页相关性")
    insights.append("   4. 分析表现最佳ASIN的成功因素并复制")
    insights.append("   5. 针对搜索词中的高频ASIN制定竞争策略")
    insights.append("")
    insights.append("📊 下周检查:")
    insights.append("   1. 监控调整后关键词的CTR变化")
    insights.append("   2. 检查否定词添加后的花费变化")
    insights.append("   3. 评估新分组结构的效率")
    insights.append("   4. 跟踪ASIN表现的变化趋势")
    insights.append("   5. 分析搜索词ASIN带来的转化变化")
    
    return insights

def clean_sheet_name(name):
    """清理工作表名称中的无效字符"""
    if not isinstance(name, str):
        name = str(name)
    
    # Excel工作表名称不允许的字符: : \ / ? * [ ]
    invalid_chars = r'[:\\/*?\[\]]'
    
    # 替换无效字符为下划线
    cleaned = re.sub(invalid_chars, '_', name)
    
    # 工作表名称不能以'或'开头，且不能超过31个字符
    cleaned = cleaned.strip().lstrip("'").rstrip("'")
    cleaned = cleaned[:31]
    
    # 如果清理后为空，使用默认名称
    if not cleaned:
        cleaned = "Sheet"
    
    return cleaned

def apply_excel_formatting(ws, sheet_index):
    """应用Excel格式化"""
    try:
        # 设置工作表标签颜色
        if sheet_index < len(SHEET_COLORS):
            ws.sheet_properties.tabColor = SHEET_COLORS[sheet_index % len(SHEET_COLORS)]
        
        # 设置默认字体
        for row in ws.iter_rows():
            for cell in row:
                # 设置默认字体
                if cell.font.name != '微软雅黑' or cell.font.size != 12:
                    cell.font = DEFAULT_FONT
                
                # 设置边框
                cell.border = THIN_BORDER
                
                # 设置对齐方式
                if cell.value is not None:
                    if isinstance(cell.value, (int, float)):
                        cell.alignment = RIGHT_ALIGN
                    else:
                        cell.alignment = LEFT_ALIGN
        
        # 设置标题行样式
        for cell in ws[1]:
            cell.font = HEADER_FONT
            cell.fill = HEADER_FILL
            cell.alignment = CENTER_ALIGN
        
        # 自动调整列宽
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 30)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        print(f"已格式化工作表: {ws.title}")
        
    except Exception as e:
        print(f"格式化工作表时出错: {str(e)}")

def save_to_excel(data, output_file):
    """将所有分析结果保存到Excel文件"""
    # 跟踪已使用的工作表名称，避免重复
    used_sheet_names = set()
    
    def get_unique_sheet_name(base_name):
        """获取唯一的工作表名称"""
        cleaned_name = clean_sheet_name(base_name)
        if cleaned_name not in used_sheet_names:
            used_sheet_names.add(cleaned_name)
            return cleaned_name
        else:
            # 如果名称已存在，添加数字后缀
            counter = 1
            while True:
                new_name = f"{cleaned_name[:28]}_{counter}" if len(cleaned_name) >= 28 else f"{cleaned_name}_{counter}"
                if new_name not in used_sheet_names:
                    used_sheet_names.add(new_name)
                    return new_name
                counter += 1
    
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            workbook = writer.book
            
            # 保存原始数据
            if '原始数据' in data and isinstance(data['原始数据'], pd.DataFrame) and not data['原始数据'].empty:
                sheet_name = get_unique_sheet_name('原始数据')
                data['原始数据'].to_excel(writer, sheet_name=sheet_name, index=False)
                apply_excel_formatting(writer.sheets[sheet_name], 0)
            
            # 保存广告组合分析 - 每个广告组合一个工作表
            if 'campaign_analysis' in data and data['campaign_analysis']:
                for idx, (campaign, analysis) in enumerate(data['campaign_analysis'].items()):
                    if analysis is None:
                        continue
                    
                    sheet_name = get_unique_sheet_name(campaign)
                    
                    # 创建主工作表
                    start_row = 0
                    
                    # 1. 写入广告组合建议
                    if 'campaign_recommendations' in analysis and analysis['campaign_recommendations']:
                        recommendations_df = pd.DataFrame(analysis['campaign_recommendations'], columns=['广告组合建议'])
                        recommendations_df.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
                        start_row += len(recommendations_df) + 3
                    
                    # 2. 写入摘要统计
                    if 'summary_stats' in analysis and analysis['summary_stats']:
                        summary_df = pd.DataFrame([analysis['summary_stats']])
                        summary_df.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
                        start_row += len(summary_df) + 3
                    
                    # 3. 写入TOP关键词
                    if not analysis['top_keywords'].empty:
                        analysis['top_keywords'].to_excel(writer, sheet_name=sheet_name, 
                                                         startrow=start_row, index=False)
                        start_row += len(analysis['top_keywords']) + 3
                    
                    # 4. 写入否定关键词
                    if not analysis['waste_keywords'].empty:
                        analysis['waste_keywords'].to_excel(writer, sheet_name=sheet_name, 
                                                           startrow=start_row, index=False)
                        start_row += len(analysis['waste_keywords']) + 3
                    
                    # 5. 写入高效词根
                    if analysis['top_converting_roots']:
                        converting_roots_df = pd.DataFrame(analysis['top_converting_roots'], 
                                                          columns=['高效词根', '加权得分'])
                        converting_roots_df.to_excel(writer, sheet_name=sheet_name, 
                                                    startrow=start_row, index=False)
                        start_row += len(converting_roots_df) + 3
                    
                    # 6. 写入无效词根
                    if analysis['top_non_converting_roots']:
                        non_converting_roots_df = pd.DataFrame(analysis['top_non_converting_roots'], 
                                                              columns=['无效词根', '出现次数'])
                        non_converting_roots_df.to_excel(writer, sheet_name=sheet_name, 
                                                        startrow=start_row, index=False)
                        start_row += len(non_converting_roots_df) + 3
                    
                    # 7. 写入ASIN分析
                    if not analysis['asin_analysis'].empty:
                        asin_analysis_df = analysis['asin_analysis']
                        asin_analysis_df.to_excel(writer, sheet_name=sheet_name, 
                                                 startrow=start_row, index=False)
                        start_row += len(asin_analysis_df) + 3
                    
                    # 8. 写入搜索词ASIN分析（新增）
                    if 'search_term_asin_analysis' in analysis and not analysis['search_term_asin_analysis'].empty:
                        search_asin_df = analysis['search_term_asin_analysis']
                        search_asin_df.to_excel(writer, sheet_name=sheet_name, 
                                               startrow=start_row, index=False)
                        start_row += len(search_asin_df) + 3
                    
                    # 9. 写入竞争对手ASIN分析
                    if isinstance(analysis['competitor_asins'], pd.DataFrame) and not analysis['competitor_asins'].empty:
                        competitor_df = analysis['competitor_asins']
                        competitor_df.to_excel(writer, sheet_name=sheet_name, 
                                              startrow=start_row, index=False)
                        start_row += len(competitor_df) + 3
                    
                    # 10. 写入预算分配建议
                    if 'budget_recommendations' in analysis and analysis['budget_recommendations']:
                        budget_df = pd.DataFrame(analysis['budget_recommendations'], columns=['预算分配建议'])
                        budget_df.to_excel(writer, sheet_name=sheet_name, 
                                          startrow=start_row, index=False)
                        start_row += len(budget_df) + 3
                    
                    # 11. 写入广告文案建议
                    if 'ad_copy_suggestions' in analysis and analysis['ad_copy_suggestions']:
                        ad_copy_df = pd.DataFrame(analysis['ad_copy_suggestions'], columns=['广告文案建议'])
                        ad_copy_df.to_excel(writer, sheet_name=sheet_name, 
                                           startrow=start_row, index=False)
                        start_row += len(ad_copy_df) + 3
                    
                    # 12. 写入时间段表现分析
                    if isinstance(analysis['time_performance_analysis'], pd.DataFrame) and not analysis['time_performance_analysis'].empty:
                        time_df = analysis['time_performance_analysis']
                        time_df.to_excel(writer, sheet_name=sheet_name, 
                                        startrow=start_row, index=False)
                        start_row += len(time_df) + 3
                    
                    # 13. 写入关键词扩展建议
                    if 'keyword_expansion_suggestions' in analysis and analysis['keyword_expansion_suggestions']:
                        expansion_df = pd.DataFrame(analysis['keyword_expansion_suggestions'], columns=['关键词扩展建议'])
                        expansion_df.to_excel(writer, sheet_name=sheet_name, 
                                             startrow=start_row, index=False)
                        start_row += len(expansion_df) + 3
                    
                    # 14. 写入投放策略优化
                    if 'targeting_optimizations' in analysis and analysis['targeting_optimizations']:
                        targeting_df = pd.DataFrame(analysis['targeting_optimizations'], columns=['投放策略优化建议'])
                        targeting_df.to_excel(writer, sheet_name=sheet_name, 
                                             startrow=start_row, index=False)
                    
                    # 应用格式化
                    apply_excel_formatting(writer.sheets[sheet_name], idx + 1)
            
            # 保存其他分析
            categories = ['搜索词分析', '广告活动分析']
            
            for category in categories:
                if category in data:
                    analysis_data = data[category]
                    
                    # 处理字典类型的分析结果
                    if isinstance(analysis_data, dict):
                        for sheet_idx, (sheet_key, df_section) in enumerate(analysis_data.items()):
                            if isinstance(df_section, pd.DataFrame) and not df_section.empty:
                                base_sheet_name = f"{category}_{sheet_key}" if sheet_key else category
                                sheet_name = get_unique_sheet_name(base_sheet_name)
                                df_section.to_excel(writer, sheet_name=sheet_name, index=False)
                                apply_excel_formatting(writer.sheets[sheet_name], len(used_sheet_names))
                    
                    # 处理DataFrame类型的分析结果
                    elif isinstance(analysis_data, pd.DataFrame) and not analysis_data.empty:
                        sheet_name = get_unique_sheet_name(category)
                        analysis_data.to_excel(writer, sheet_name=sheet_name, index=False)
                        apply_excel_formatting(writer.sheets[sheet_name], len(used_sheet_names))
            
            # 保存关键洞察
            if '关键洞察' in data and data['关键洞察']:
                sheet_name = get_unique_sheet_name('关键洞察')
                insights_df = pd.DataFrame(data['关键洞察'], columns=['洞察内容'])
                insights_df.to_excel(writer, sheet_name=sheet_name, index=False)
                apply_excel_formatting(writer.sheets[sheet_name], len(used_sheet_names))
        
        print(f"✅ Excel文件保存成功: {output_file}")
        
        # 添加可视化分析
        generate_visual_analysis(data['原始数据'], output_file)
        
        return True
        
    except Exception as e:
        print(f"❌ 保存Excel文件时出错: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """主程序"""
    desktop_path = Path.home() / "Desktop"
    
    # 查找输入文件
    input_files = [
        desktop_path / "商品推广_搜索词_报告.xls",
        desktop_path / "商品推广_搜索词_报告.xlsx",
        desktop_path / "商品推广_搜索词_报告.csv"
    ]
    
    input_file = next((f for f in input_files if f.exists()), None)
    
    if not input_file:
        print("错误: 未找到文件，请确保桌面有广告报告文件")
        return
    
    print(f"找到文件: {input_file}")
    
    try:
        # 读取数据
        print("正在读取文件...")
        df = read_data_file(input_file)
        
        if df is None or df.empty:
            print("错误: 无法读取文件或文件为空")
            return
        
        print(f"成功读取数据，共 {len(df)} 行，{len(df.columns)} 列")
        
        # 数据清洗
        print("正在进行数据清洗...")
        report_type = 'search_term' if "搜索词" in input_file.name else 'keyword'
        df, detected_report_type = clean_data(df, report_type)
        print(f"报告类型: {detected_report_type}")
        print("数据清洗完成")
        
        if 'campaign' not in df.columns:
            print("错误: 'campaign' 列不存在，无法进行分析")
            return
        
        # 分析各广告组合
        print("分析各广告组合...")
        campaign_analyses = {}
        campaigns = df['campaign'].unique()
        
        print(f"发现 {len(campaigns)} 个广告组合")
        
        for i, campaign in enumerate(campaigns, 1):
            print(f"分析广告组合 [{i}/{len(campaigns)}]: {campaign}")
            analysis = analyze_campaign(df, campaign)
            campaign_analyses[campaign] = analysis
        
        # 生成搜索词分析
        print("生成搜索词分析...")
        search_term_analysis = generate_search_term_analysis(df)
        
        # 生成广告活动分析
        print("生成广告活动分析...")
        campaign_analysis = generate_campaign_analysis(df)
        
        # 生成关键洞察
        print("生成关键洞察...")
        key_insights = generate_key_insights(df, campaign_analyses, search_term_analysis)
        
        # 准备输出数据
        output_data = {
            '原始数据': df,
            'campaign_analysis': campaign_analyses,
            '搜索词分析': search_term_analysis,
            '广告活动分析': campaign_analysis,
            '关键洞察': key_insights
        }
        
        # 生成Excel报告
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = desktop_path / f"亚马逊广告智能分析_{timestamp}.xlsx"
        print(f"生成Excel报告: {output_file}")
        
        if save_to_excel(output_data, output_file):
            print(f"\n{'='*80}")
            print("🎉 亚马逊广告智能分析完成！")
            print(f"📁 Excel详细报告: {output_file}")
            print(f"{'='*80}")
            
            # 输出关键洞察
            print("\n📊 关键洞察摘要:")
            for insight in key_insights[:20]:
                print(insight)
            
            # 统计信息
            print(f"\n📈 分析统计:")
            print(f"• 分析关键词总数: {len(df)}")
            print(f"• 广告组合数量: {len(campaign_analyses)}")
            print(f"• 出单关键词数: {len(df[df['orders'] > 0])}")
            
            # ASIN统计
            if 'asin' in df.columns:
                asin_count = df['asin'].nunique()
                print(f"• 商品ASIN数量: {asin_count}个")
            
            if 'extracted_asins' in df.columns:
                asin_search_terms = df[df['extracted_asins'].apply(lambda x: len(x) > 0)]
                print(f"• 包含商品ASIN的搜索词: {len(asin_search_terms)}个")
            
            # 广告组合建议概览
            print(f"\n🎯 广告组合建议概览:")
            for campaign_name, analysis in campaign_analyses.items():
                if analysis and 'campaign_recommendations' in analysis and analysis['campaign_recommendations']:
                    print(f"\n{campaign_name}:")
                    for rec in analysis['campaign_recommendations'][:3]:  # 只显示前3条建议
                        print(f"  • {rec}")
            
            # 新增功能概览
            print(f"\n🚀 新增分析功能概览:")
            print("• 商品ASIN分析: 从搜索词中提取并分析商品ASIN表现")
            print("• 竞争对手ASIN分析: 识别并分析关键词中的竞争对手ASIN")
            print("• 预算分配建议: 基于ROAS和关键词表现提供预算优化建议")
            print("• 广告文案建议: 根据高效词根和关键词表现生成文案建议")
            print("• 时间段表现分析: 分析工作日和时段表现")
            print("• 关键词扩展建议: 基于高效词根提供关键词扩展方向")
            print("• 投放策略优化: 提供匹配类型、出价、广告组结构优化建议")
            
            # 操作建议
            print(f"\n🚀 立即操作建议:")
            print("1. 打开Excel报告，查看'关键洞察'工作表")
            print("2. 查看各广告组合工作表的详细建议")
            print("3. 根据'否定建议'添加否定词到广告后台")
            print("4. 实施'出价建议'中的调整")
            print("5. 根据'分组建议'优化广告结构")
            print("6. 查看'可视化分析'工作表的图表")
            print("7. 分析'搜索词ASIN分析'识别竞品机会")
            print("8. 参考'广告文案建议'优化广告内容")
            # 新增：表现差关键词概览
            print(f"\n⚠️ 表现差关键词概览:")
            
            total_poor_keywords = 0
            total_poor_spend = 0
            
            for campaign_name, analysis in campaign_analyses.items():
                if analysis is None:
                    continue
                
                if 'poor_performing_keywords' in analysis and not analysis['poor_performing_keywords'].empty:
                    poor_keywords_count = len(analysis['poor_performing_keywords'])
                    poor_spend = analysis['poor_performing_keywords']['spend'].sum()
                    
                    total_poor_keywords += poor_keywords_count
                    total_poor_spend += poor_spend
                    
                    if poor_keywords_count > 0:
                        print(f"• {campaign_name}: {poor_keywords_count}个表现差关键词,花费¥{poor_spend:.2f}")
            
            if total_poor_keywords > 0:
                print(f"\n📊 表现差关键词总结:")
                print(f"• 总共有{total_poor_keywords}个表现差关键词")
                print(f"• 总计花费¥{total_poor_spend:.2f}")
                print(f"• 预计优化后每月可节省¥{total_poor_spend * 4:.2f}")
                
                print(f"\n🎯 表现差关键词优化建议:")
                print("1. 高花费无转化关键词:立即否定或暂停")
                print("2. 高ACOS关键词:降低出价50%或暂停")
                print("3. 低ROAS关键词:优化出价或匹配类型")
                print("4. 低CTR关键词:优化广告文案或图片")
            else:
                print("✅ 恭喜!未发现明显表现差的关键词")
            
        else:
            print("错误: 生成Excel报告失败")
        
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()