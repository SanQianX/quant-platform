# 数据模型
from sqlalchemy import Column, Integer, String, Float, Date, Text
from database import Base

class Stock(Base):
    """股票模型"""
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, comment="股票代码")
    name = Column(String(50), comment="股票名称")
    market = Column(String(10), comment="市场类型: sh/sz")
    stock_type = Column(String(10), comment="股票类型: stock/index")
    description = Column(Text, nullable=True, comment="描述")

class KLine(Base):
    """K线数据模型"""
    __tablename__ = "klines"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), index=True)
    date = Column(Date, index=True)
    open = Column(Float, comment="开盘价")
    high = Column(Float, comment="最高价")
    low = Column(Float, comment="最低价")
    close = Column(Float, comment="收盘价")
    volume = Column(Float, comment="成交量")
