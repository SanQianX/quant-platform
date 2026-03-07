# 类型定义
"""
公共类型定义
用于提高代码可读性和类型安全
"""

from typing import TypeAlias, Union, List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import date

# 响应类型
JSON: TypeAlias = Dict[str, Any]
ResponseData: TypeAlias = Dict[str, Union[int, str, Any]]

# 股票相关类型
StockCode: TypeAlias = str
StockName: TypeAlias = str
MarketType: TypeAlias = str  # "sh" | "sz"
StockType: TypeAlias = str   # "stock" | "index"

@dataclass
class StockInfo:
    """股票信息"""
    code: StockCode
    name: StockName
    market: MarketType
    stock_type: StockType

@dataclass
class KLineData:
    """K线数据"""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float

# API响应码
class ResponseCode:
    """响应码定义"""
    SUCCESS = 0
    ERROR = -1
    NOT_FOUND = 404
    BAD_REQUEST = 400
    SERVER_ERROR = 500
