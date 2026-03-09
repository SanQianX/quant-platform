# 股票停复牌API路由
from fastapi import APIRouter
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票停复牌"])

# 停牌数据模型
class Suspension(BaseModel):
    ts_code: str  # 股票代码
    name: str  # 股票名称
    suspend_date: str  # 停牌日期
    suspend_reason: str  # 停牌原因
    pre_price: Optional[float] = None  # 停牌前价格

# 复牌数据模型
class Resumption(BaseModel):
    ts_code: str  # 股票代码
    name: str  # 股票名称
    resume_date: str  # 复牌日期
    suspend_date: str  # 停牌日期
    suspend_reason: str  # 停牌原因
    resume_reason: str  # 复牌原因

# 模拟停牌股票数据
SUSPENSIONS = [
    {
        "ts_code": "000001.SZ",
        "name": "平安银行",
        "suspend_date": "2026-03-07",
        "suspend_reason": "重大资产重组",
        "pre_price": 12.35
    },
    {
        "ts_code": "000002.SZ",
        "name": "万科A",
        "suspend_date": "2026-03-05",
        "suspend_reason": "重大事项公告",
        "pre_price": 8.92
    },
    {
        "ts_code": "600000.SH",
        "name": "浦发银行",
        "suspend_date": "2026-03-08",
        "suspend_reason": "增发股票",
        "pre_price": 7.56
    },
    {
        "ts_code": "600519.SH",
        "name": "贵州茅台",
        "suspend_date": "2026-03-09",
        "suspend_reason": "要约收购",
        "pre_price": 1688.00
    },
    {
        "ts_code": "000858.SZ",
        "name": "五粮液",
        "suspend_date": "2026-03-06",
        "suspend_reason": "重大资产重组",
        "pre_price": 128.50
    },
    {
        "ts_code": "601318.SH",
        "name": "中国平安",
        "suspend_date": "2026-03-07",
        "suspend_reason": "股份回购",
        "pre_price": 45.80
    },
    {
        "ts_code": "000333.SZ",
        "name": "美的集团",
        "suspend_date": "2026-03-08",
        "suspend_reason": "发行股份购买资产",
        "pre_price": 62.35
    },
    {
        "ts_code": "002594.SZ",
        "name": "比亚迪",
        "suspend_date": "2026-03-05",
        "suspend_reason": "重大合同公告",
        "pre_price": 268.90
    }
]

# 模拟复牌股票数据
RESUMPTIONS = [
    {
        "ts_code": "000004.SZ",
        "name": "国华网安",
        "resume_date": "2026-03-09",
        "suspend_date": "2026-03-01",
        "suspend_reason": "重大资产重组",
        "resume_reason": "重组完成"
    },
    {
        "ts_code": "600036.SH",
        "name": "招商银行",
        "resume_date": "2026-03-08",
        "suspend_date": "2026-03-03",
        "suspend_reason": "要约收购",
        "resume_reason": "收购完成"
    },
    {
        "ts_code": "000001.SZ",
        "name": "平安银行",
        "resume_date": "2026-03-07",
        "suspend_date": "2026-02-28",
        "suspend_reason": "重大事项公告",
        "resume_reason": "事项已公告"
    },
    {
        "ts_code": "601166.SH",
        "name": "兴业银行",
        "resume_date": "2026-03-06",
        "suspend_date": "2026-02-27",
        "suspend_reason": "增发股票",
        "resume_reason": "增发完成"
    },
    {
        "ts_code": "002415.SZ",
        "name": "海康威视",
        "resume_date": "2026-03-05",
        "suspend_date": "2026-02-25",
        "suspend_reason": "重大合同公告",
        "resume_reason": "合同已公告"
    },
    {
        "ts_code": "600276.SH",
        "name": "恒瑞医药",
        "resume_date": "2026-03-04",
        "suspend_date": "2026-02-24",
        "suspend_reason": "重大资产重组",
        "resume_reason": "重组终止"
    }
]

@router.get("/suspension/list")
def get_suspension_list():
    """
    获取停牌股票列表
    
    返回当前停牌的股票列表
    
    Returns:
        dict: 统一响应格式，包含停牌股票列表
    """
    return {
        "code": 0,
        "message": "success",
        "data": SUSPENSIONS
    }

@router.get("/resumption/list")
def get_resumption_list():
    """
    获取复牌股票列表
    
    返回近期复牌的股票列表
    
    Returns:
        dict: 统一响应格式，包含复牌股票列表
    """
    return {
        "code": 0,
        "message": "success",
        "data": RESUMPTIONS
    }
