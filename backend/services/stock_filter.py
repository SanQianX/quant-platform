# 选股筛选服务
"""
股票筛选功能
支持多条件组合筛选
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import pandas as pd

class StockFilter:
    """股票筛选器"""
    
    @staticmethod
    def filter_stocks(
        stocks: List[Dict],
        filters: Dict[str, Any]
    ) -> List[Dict]:
        """
        筛选股票
        
        Args:
            stocks: 股票列表
            filters: 筛选条件
            
        Returns:
            符合条件的股票列表
        """
        if not stocks:
            return []
        
        # 转换为DataFrame便于处理
        df = pd.DataFrame(stocks)
        
        if df.empty:
            return []
        
        results = []
        
        for stock in stocks:
            # 获取股票数据
            stock_data = StockFilter._get_stock_data(stock['code'])
            
            if not stock_data:
                # 没有数据的股票默认通过筛选
                results.append(stock)
                continue
            
            # 应用筛选条件
            if StockFilter._apply_filters(stock_data, filters):
                # 添加筛选数据到结果
                result = stock.copy()
                result['price_data'] = stock_data
                results.append(result)
        
        return results
    
    @staticmethod
    def _get_stock_data(code: str) -> Optional[Dict]:
        """获取股票实时数据"""
        # 这里应该调用实时数据API
        # 简化处理，返回None表示无数据
        return None
    
    @staticmethod
    def _apply_filters(stock_data: Dict, filters: Dict) -> bool:
        """应用筛选条件"""
        # 如果没有数据，默认通过
        if not stock_data:
            return True
        
        # 价格涨跌幅筛选
        if 'min_change' in filters:
            change = stock_data.get('change_percent', 0)
            if change < filters['min_change']:
                return False
        
        if 'max_change' in filters:
            change = stock_data.get('change_percent', 0)
            if change > filters['max_change']:
                return False
        
        # 成交量筛选
        if 'min_volume' in filters:
            volume = stock_data.get('volume', 0)
            if volume < filters['min_volume']:
                return False
        
        # 市值筛选
        if 'min_market_cap' in filters:
            market_cap = stock_data.get('market_cap', 0)
            if market_cap < filters['min_market_cap']:
                return False
        
        if 'max_market_cap' in filters:
            market_cap = stock_data.get('market_cap', 0)
            if market_cap > filters['max_market_cap']:
                return False
        
        # 股价筛选
        if 'min_price' in filters:
            price = stock_data.get('price', 0)
            if price < filters['min_price']:
                return False
        
        if 'max_price' in filters:
            price = stock_data.get('price', 0)
            if price > filters['max_price']:
                return False
        
        return True
    
    @staticmethod
    def filter_by_technical(
        stocks: List[Dict],
        indicator: str,
        condition: str,
        value: float
    ) -> List[Dict]:
        """
        根据技术指标筛选
        
        Args:
            stocks: 股票列表
            indicator: 指标名称 (ma/rsi/macd)
            condition: 条件 (above/below/cross)
            value: 数值
            
        Returns:
            符合条件的股票列表
        """
        results = []
        
        for stock in stocks:
            # 获取技术指标数据
            # 这里应该调用指标API
            # 简化处理
            pass
        
        return results


# 预设筛选条件
PRESET_FILTERS = {
    "涨幅超过5%": {"min_change": 5},
    "跌幅超过5%": {"max_change": -5},
    "成交量放大": {"min_volume": 100000000},
    "低价股": {"max_price": 10},
    "高价股": {"min_price": 100},
    "大盘股": {"min_market_cap": 100000000000},
    "小盘股": {"max_market_cap": 10000000000},
}
