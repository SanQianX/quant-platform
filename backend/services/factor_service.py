# 因子数据服务
"""
因子库 - 包含技术因子和基本面因子
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class FactorService:
    """因子服务"""
    
    @staticmethod
    def get_technical_factors(kline_data: List[Dict]) -> List[Dict]:
        """
        获取技术因子
        
        Args:
            kline_data: K线数据
            
        Returns:
            包含技术因子的数据
        """
        if not kline_data or len(kline_data) < 5:
            return kline_data
        
        df = pd.DataFrame(kline_data)
        df = df.sort_values('date')
        
        # 价格变化率
        df['pct_change'] = df['close'].pct_change() * 100
        
        # 成交量变化率
        df['volume_change'] = df['volume'].pct_change() * 100
        
        # 波动率 (20日)
        df['volatility_20'] = df['pct_change'].rolling(window=20).std()
        
        # 成交额
        df['amount'] = df['close'] * df['volume']
        
        # 均价 (20日)
        df['avg_price_20'] = df['close'].rolling(window=20).mean()
        
        # 均价偏离度
        df['price_deviation'] = (df['close'] - df['avg_price_20']) / df['avg_price_20'] * 100
        
        # 转换为字典列表
        result = []
        for _, row in df.iterrows():
            item = {'date': row['date'], 'close': row['close']}
            
            for col in ['pct_change', 'volume_change', 'volatility_20', 'amount', 'avg_price_20', 'price_deviation']:
                value = row.get(col)
                if pd.notna(value):
                    item[col] = round(value, 4)
            
            result.append(item)
        
        return result
    
    @staticmethod
    def get_momentum_factors(kline_data: List[Dict]) -> List[Dict]:
        """
        获取动量因子
        
        Args:
            kline_data: K线数据
            
        Returns:
            包含动量因子的数据
        """
        if not kline_data or len(kline_data) < 60:
            return kline_data
        
        df = pd.DataFrame(kline_data)
        df = df.sort_values('date')
        
        # 动量因子
        for period in [5, 10, 20, 60]:
            df[f'momentum_{period}'] = df['close'].pct_change(period) * 100
        
        # 相对强弱
        df['rs_20'] = df['close'] / df['close'].rolling(window=20).mean() * 100
        
        # 转换为字典列表
        result = []
        for _, row in df.iterrows():
            item = {'date': row['date'], 'close': row['close']}
            
            for col in ['momentum_5', 'momentum_10', 'momentum_20', 'momentum_60', 'rs_20']:
                value = row.get(col)
                if pd.notna(value):
                    item[col] = round(value, 4)
            
            result.append(item)
        
        return result
    
    @staticmethod
    def get_volume_factors(kline_data: List[Dict]) -> List[Dict]:
        """
        获取成交量因子
        
        Args:
            kline_data: K线数据
            
        Returns:
            包含成交量因子的数据
        """
        if not kline_data or len(kline_data) < 20:
            return kline_data
        
        df = pd.DataFrame(kline_data)
        df = df.sort_values('date')
        
        # 成交量均线
        for period in [5, 10, 20]:
            df[f'volume_ma_{period}'] = df['volume'].rolling(window=period).mean()
        
        # 成交量比率
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(window=20).mean()
        
        # 成交额均线
        df['amount'] = df['close'] * df['volume']
        for period in [5, 10, 20]:
            df[f'amount_ma_{period}'] = df['amount'].rolling(window=period).mean()
        
        # 换手率因子
        df['turnover_rate'] = df['volume'] / 10000000 * 100  # 简化计算
        
        # 转换为字典列表
        result = []
        for _, row in df.iterrows():
            item = {'date': row['date'], 'close': row['close'], 'volume': row['volume']}
            
            for col in ['volume_ma_5', 'volume_ma_10', 'volume_ma_20', 
                       'volume_ratio', 'turnover_rate']:
                value = row.get(col)
                if pd.notna(value):
                    item[col] = round(value, 4)
            
            result.append(item)
        
        return result
    
    @staticmethod
    def get_all_factors(kline_data: List[Dict]) -> Dict[str, List[Dict]]:
        """
        获取所有因子
        
        Args:
            kline_data: K线数据
            
        Returns:
            所有因子数据
        """
        return {
            "technical": FactorService.get_technical_factors(kline_data),
            "momentum": FactorService.get_momentum_factors(kline_data),
            "volume": FactorService.get_volume_factors(kline_data)
        }


# 模拟财务因子（实际应从数据库获取）
FINANCIAL_FACTORS = {
    "pe": {"name": "市盈率", "description": "Price to Earnings Ratio"},
    "pb": {"name": "市净率", "description": "Price to Book Ratio"},
    "ps": {"name": "市销率", "description": "Price to Sales Ratio"},
    "roe": {"name": "净资产收益率", "description": "Return on Equity"},
    "roa": {"name": "资产收益率", "description": "Return on Assets"},
    "gross_margin": {"name": "毛利率", "description": "Gross Margin"},
    "net_margin": {"name": "净利率", "description": "Net Profit Margin"},
    "debt_ratio": {"name": "资产负债率", "description": "Debt Ratio"},
    "current_ratio": {"name": "流动比率", "description": "Current Ratio"},
    "quick_ratio": {"name": "速动比率", "description": "Quick Ratio"},
}

def get_financial_factors(stock_code: str) -> Dict[str, Any]:
    """
    获取财务因子
    
    Args:
        stock_code: 股票代码
        
    Returns:
        财务因子数据
    """
    # 模拟数据 - 实际应从数据库获取
    return {
        "stock_code": stock_code,
        "report_date": "2024-12-31",
        "factors": {
            "pe": 15.5,
            "pb": 2.3,
            "ps": 3.2,
            "roe": 12.5,
            "roa": 8.5,
            "gross_margin": 35.2,
            "net_margin": 18.5,
            "debt_ratio": 45.0,
            "current_ratio": 1.8,
            "quick_ratio": 1.5
        }
    }
