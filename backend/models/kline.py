# -*- coding: utf-8 -*-
"""
K线数据模型
支持日K、周K、月K、分时数据
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Index
from sqlalchemy.sql import func
from database import Base


class KLineDaily(Base):
    """日K线数据模型
    
    Attributes:
        id: 主键ID
        stock_code: 股票代码 (如: 600519)
        trade_date: 交易日期
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        pre_close: 昨收价
        change: 涨跌额
        pct_chg: 涨跌幅
        vol: 成交量 (手)
        amount: 成交额 (千元)
    """
    __tablename__ = "kline_daily"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), index=True, nullable=False)
    trade_date = Column(Date, index=True, nullable=False)
    open = Column(Float, comment="开盘价")
    high = Column(Float, comment="最高价")
    low = Column(Float, comment="最低价")
    close = Column(Float, comment="收盘价")
    pre_close = Column(Float, comment="昨收价")
    change = Column(Float, comment="涨跌额")
    pct_chg = Column(Float, comment="涨跌幅")
    vol = Column(Float, comment="成交量(手)")
    amount = Column(Float, comment="成交额(千元)")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_stock_date', 'stock_code', 'trade_date'),
        Index('idx_code', 'stock_code'),
    )

    def __repr__(self):
        return f"<KLineDaily(code={self.stock_code}, date={self.trade_date})>"


class KLineWeekly(Base):
    """周K线数据模型
    
    Attributes:
        id: 主键ID
        stock_code: 股票代码
        trade_date: 交易周最后一天日期
        open: 周开盘价
        high: 周最高价
        low: 周最低价
        close: 周收盘价
        vol: 周成交量
        amount: 周成交额
    """
    __tablename__ = "kline_weekly"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), index=True, nullable=False)
    trade_date = Column(Date, index=True, nullable=False)
    open = Column(Float, comment="周开盘价")
    high = Column(Float, comment="周最高价")
    low = Column(Float, comment="周最低价")
    close = Column(Float, comment="周收盘价")
    vol = Column(Float, comment="周成交量")
    amount = Column(Float, comment="周成交额")
    pct_chg = Column(Float, comment="周涨跌幅")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_stock_weekly_date', 'stock_code', 'trade_date'),
    )

    def __repr__(self):
        return f"<KLineWeekly(code={self.stock_code}, date={self.trade_date})>"


class KLineMonthly(Base):
    """月K线数据模型
    
    Attributes:
        id: 主键ID
        stock_code: 股票代码
        trade_date: 月份最后一天日期
        open: 月开盘价
        high: 月最高价
        low: 月最低价
        close: 月收盘价
        vol: 月成交量
        amount: 月成交额
    """
    __tablename__ = "kline_monthly"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), index=True, nullable=False)
    trade_date = Column(Date, index=True, nullable=False)
    open = Column(Float, comment="月开盘价")
    high = Column(Float, comment="月最高价")
    low = Column(Float, comment="月最低价")
    close = Column(Float, comment="月收盘价")
    vol = Column(Float, comment="月成交量")
    amount = Column(Float, comment="月成交额")
    pct_chg = Column(Float, comment="月涨跌幅")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_stock_monthly_date', 'stock_code', 'trade_date'),
    )

    def __repr__(self):
        return f"<KLineMonthly(code={self.stock_code}, date={self.trade_date})>"


class KLineMinute(Base):
    """分时数据模型
    
    Attributes:
        id: 主键ID
        stock_code: 股票代码
        trade_date: 交易日期
        trade_time: 交易时间
        open: 开盘价
        high: 最高价
        low: 最低价
        close: 收盘价
        volume: 成交量
        amount: 成交额
        freq: 频率 (1min/5min/15min/30min/60min)
    """
    __tablename__ = "kline_minute"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), index=True, nullable=False)
    trade_date = Column(Date, index=True)
    trade_time = Column(DateTime, index=True, nullable=False)
    open = Column(Float, comment="开盘价")
    high = Column(Float, comment="最高价")
    low = Column(Float, comment="最低价")
    close = Column(Float, comment="收盘价")
    volume = Column(Float, comment="成交量")
    amount = Column(Float, comment="成交额")
    freq = Column(String(10), comment="频率: 1min/5min/15min/30min/60min")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_stock_minute_time', 'stock_code', 'freq', 'trade_time'),
        Index('idx_stock_freq_date', 'stock_code', 'freq', 'trade_date'),
    )

    def __repr__(self):
        return f"<KLineMinute(code={self.stock_code}, freq={self.freq}, time={self.trade_time})>"
