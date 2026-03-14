# 数据模型
"""
数据模型定义
使用SQLAlchemy ORM
"""

from sqlalchemy import Column, Integer, String, Float, Date, Text
from database import Base

class Stock(Base):
    """股票模型
    
    Attributes:
        id: 主键ID
        code: 股票代码 (如: 600519)
        name: 股票名称 (如: 贵州茅台)
        market: 市场类型 (sh=上海, sz=深圳)
        stock_type: 股票类型 (stock=股票, index=指数)
        description: 描述信息
    """
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, comment="股票代码")
    name = Column(String(50), comment="股票名称")
    market = Column(String(10), comment="市场类型: sh/sz")
    stock_type = Column(String(10), comment="股票类型: stock/index")
    description = Column(Text, nullable=True, comment="描述")

    def __repr__(self):
        return f"<Stock(code={self.code}, name={self.name})>"

class KLine(Base):
    """K线数据模型
    
    Attributes:
        id: 主键ID
        stock_code: 股票代码
        date: 交易日期
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量
    """
    __tablename__ = "kline_daily"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), index=True)
    date = Column("trade_date", Date, index=True)
    open = Column(Float, comment="开盘价")
    high = Column(Float, comment="最高价")
    low = Column(Float, comment="最低价")
    close = Column(Float, comment="收盘价")
    volume = Column("vol", Float, comment="成交量")

    def __repr__(self):
        return f"<KLine(code={self.stock_code}, date={self.date})>"
