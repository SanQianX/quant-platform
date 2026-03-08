# 技术指标服务
"""
常用技术指标计算
- MA: 移动平均线
- MACD: 指数平滑异同移动平均线
- RSI: 相对强弱指标
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional

class TechnicalIndicators:
    """技术指标计算类"""
    
    @staticmethod
    def calculate_ma(data: List[Dict], periods: List[int] = [5, 10, 20, 60]) -> List[Dict]:
        """
        计算移动平均线 MA
        
        Args:
            data: K线数据 [{date, open, high, low, close, volume}, ...]
            periods: 均线周期列表
            
        Returns:
            包含MA值的数据
        """
        if not data or len(data) < max(periods):
            return data
        
        # 转换为DataFrame
        df = pd.DataFrame(data)
        
        # 确保按日期排序
        df = df.sort_values('date')
        
        # 计算各周期均线
        for period in periods:
            df[f'ma{period}'] = df['close'].rolling(window=period).mean()
        
        # 转换为字典列表
        result = []
        for _, row in df.iterrows():
            item = {
                'date': row['date'],
                'close': row['close']
            }
            for period in periods:
                ma_value = row.get(f'ma{period}')
                if pd.notna(ma_value):
                    item[f'ma{period}'] = round(ma_value, 2)
            
            result.append(item)
        
        return result
    
    @staticmethod
    def calculate_macd(
        data: List[Dict], 
        fast: int = 12, 
        slow: int = 26, 
        signal: int = 9
    ) -> List[Dict]:
        """
        计算MACD指标
        
        Args:
            data: K线数据
            fast: 快线周期 (默认12)
            slow: 慢线周期 (默认26)
            signal: 信号线周期 (默认9)
            
        Returns:
            包含MACD值的数据
        """
        if not data or len(data) < slow:
            return data
        
        df = pd.DataFrame(data)
        df = df.sort_values('date')
        
        # 计算EMA
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        
        # DIF (差离值)
        df['dif'] = ema_fast - ema_slow
        
        # DEA (信号线)
        df['dea'] = df['dif'].ewm(span=signal, adjust=False).mean()
        
        # MACD柱 = (DIF - DEA) * 2
        df['macd'] = (df['dif'] - df['dea']) * 2
        
        # 转换为字典列表
        result = []
        for _, row in df.iterrows():
            item = {
                'date': row['date'],
                'close': row['close']
            }
            
            dif = row.get('dif')
            dea = row.get('dea')
            macd = row.get('macd')
            
            if pd.notna(dif):
                item['dif'] = round(dif, 4)
            if pd.notna(dea):
                item['dea'] = round(dea, 4)
            if pd.notna(macd):
                item['macd'] = round(macd, 4)
            
            result.append(item)
        
        return result
    
    @staticmethod
    def calculate_rsi(data: List[Dict], periods: List[int] = [6, 12, 24]) -> List[Dict]:
        """
        计算RSI指标
        
        Args:
            data: K线数据
            periods: RSI周期列表
            
        Returns:
            包含RSI值的数据
        """
        if not data or len(data) < max(periods):
            return data
        
        df = pd.DataFrame(data)
        df = df.sort_values('date')
        
        # 计算价格变化
        delta = df['close'].diff()
        
        # 分离上涨和下跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 计算各周期RSI
        for period in periods:
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            # 相对强度
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            df[f'rsi{period}'] = rsi
        
        # 转换为字典列表
        result = []
        for _, row in df.iterrows():
            item = {
                'date': row['date'],
                'close': row['close']
            }
            
            for period in periods:
                rsi_value = row.get(f'rsi{period}')
                if pd.notna(rsi_value):
                    item[f'rsi{period}'] = round(rsi_value, 2)
            
            result.append(item)
        
        return result
    
    @staticmethod
    def calculate_bollinger_bands(
        data: List[Dict], 
        period: int = 20, 
        std_dev: float = 2.0
    ) -> List[Dict]:
        """
        计算布林带指标
        
        Args:
            data: K线数据
            period: 周期 (默认20)
            std_dev: 标准差倍数 (默认2.0)
            
        Returns:
            包含布林带数据
        """
        if not data or len(data) < period:
            return data
        
        df = pd.DataFrame(data)
        df = df.sort_values('date')
        
        # 计算中轨
        df['bb_mid'] = df['close'].rolling(window=period).mean()
        
        # 计算标准差
        std = df['close'].rolling(window=period).std()
        
        # 计算上轨和下轨
        df['bb_upper'] = df['bb_mid'] + (std_dev * std)
        df['bb_lower'] = df['bb_mid'] - (std_dev * std)
        
        # 转换为字典列表
        result = []
        for _, row in df.iterrows():
            item = {
                'date': row['date'],
                'close': row['close']
            }
            
            for col in ['bb_upper', 'bb_mid', 'bb_lower']:
                value = row.get(col)
                if pd.notna(value):
                    item[col] = round(value, 2)
            
            result.append(item)
        
        return result


# 便捷函数
def get_indicators(
    data: List[Dict],
    indicators: List[str] = ["ma", "macd", "rsi"]
) -> Dict[str, List[Dict]]:
    """
    获取多个技术指标
    
    Args:
        data: K线数据
        indicators: 需要计算的指标列表
        
    Returns:
        {'ma': [...], 'macd': [...], 'rsi': [...]}
    """
    service = TechnicalIndicators()
    result = {}
    
    if "ma" in indicators:
        result["ma"] = service.calculate_ma(data)
    
    if "macd" in indicators:
        result["macd"] = service.calculate_macd(data)
    
    if "rsi" in indicators:
        result["rsi"] = service.calculate_rsi(data)
    
    if "bollinger" in indicators:
        result["bollinger"] = service.calculate_bollinger_bands(data)
    
    return result
