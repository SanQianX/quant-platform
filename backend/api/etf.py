# ETF基金API路由
"""
ETF基金数据接口

提供ETF基金列表查询、实时行情等功能
使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import random

# 创建路由
router = APIRouter(prefix="/api/etf", tags=["ETF基金"])


# ETF模拟数据列表
ETF_LIST = [
    {"code": "510300", "name": "沪深300ETF", "type": "股票ETF"},
    {"code": "510500", "name": "中证500ETF", "type": "股票ETF"},
    {"code": "159919", "name": "创业板ETF", "type": "股票ETF"},
    {"code": "510050", "name": "上证50ETF", "type": "股票ETF"},
    {"code": "159915", "name": "创业板50ETF", "type": "股票ETF"},
    {"code": "512880", "name": "证券ETF", "type": "股票ETF"},
    {"code": "512660", "name": "军工ETF", "type": "股票ETF"},
    {"code": "512880", "name": "券商ETF", "type": "股票ETF"},
    {"code": "159992", "name": "创新药ETF", "type": "股票ETF"},
    {"code": "159995", "name": "券商ETF", "type": "股票ETF"},
    {"code": "510880", "name": "红利ETF", "type": "股票ETF"},
    {"code": "159919", "name": "创业板ETF", "type": "股票ETF"},
    {"code": "512690", "name": "消费ETF", "type": "股票ETF"},
    {"code": "159807", "name": "科技ETF", "type": "股票ETF"},
    {"code": "512800", "name": "银行ETF", "type": "股票ETF"},
    {"code": "159928", "name": "中证消费ETF", "type": "股票ETF"},
    {"code": "510500", "name": "中证500ETF", "type": "股票ETF"},
    {"code": "159920", "name": "华夏上证50ETF", "type": "股票ETF"},
    {"code": "159981", "name": "能源ETF", "type": "股票ETF"},
    {"code": "510010", "name": "上证180ETF", "type": "股票ETF"},
]


def get_mock_etf_quote(etf_code: str) -> dict:
    """
    生成模拟ETF实时行情数据
    
    Args:
        etf_code: ETF基金代码
        
    Returns:
        dict: 模拟行情数据
    """
    # 基于ETF代码生成稳定的随机数
    seed = int(etf_code) if etf_code.isdigit() else hash(etf_code) % 10000
    random.seed(seed)
    
    # 常见ETF的基础价格
    base_prices = {
        "510300": 3.85,
        "510500": 6.12,
        "159919": 2.45,
        "510050": 2.75,
        "159915": 0.95,
        "512880": 1.25,
        "512660": 1.35,
        "159992": 1.08,
        "510880": 2.95,
        "512690": 1.15,
        "159807": 1.28,
        "512800": 1.05,
        "159928": 3.25,
    }
    base_price = base_prices.get(etf_code, 1.0)
    
    # 生成随机价格
    change_pct = random.uniform(-3, 3)
    price = base_price * (1 + change_pct / 100)
    prev_close = base_price
    
    return {
        "code": etf_code,
        "name": _get_etf_name(etf_code),
        "latest_price": round(price, 3),
        "prev_close": round(prev_close, 3),
        "open": round(prev_close * (1 + random.uniform(-0.01, 0.01)), 3),
        "high": round(price * (1 + random.uniform(0, 0.02)), 3),
        "low": round(price * (1 - random.uniform(0, 0.02)), 3),
        "change": round(price - prev_close, 3),
        "change_pct": round(change_pct, 2),
        "volume": random.randint(100000, 10000000),
        "amount": round(price * random.randint(100000, 10000000), 2),
        "bid_price1": round(price * 0.998, 3),
        "bid_price2": round(price * 0.996, 3),
        "bid_price3": round(price * 0.994, 3),
        "ask_price1": round(price * 1.002, 3),
        "ask_price2": round(price * 1.004, 3),
        "ask_price3": round(price * 1.006, 3),
        "bid_volume1": random.randint(1000, 100000),
        "bid_volume2": random.randint(1000, 100000),
        "bid_volume3": random.randint(1000, 100000),
        "ask_volume1": random.randint(1000, 100000),
        "ask_volume2": random.randint(1000, 100000),
        "ask_volume3": random.randint(1000, 100000),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def _get_etf_name(code: str) -> str:
    """获取ETF名称"""
    for etf in ETF_LIST:
        if etf["code"] == code:
            return etf["name"]
    return f"ETF{code}"


@router.get("/list")
def get_etf_list():
    """
    获取ETF基金列表
    
    返回所有支持的ETF基金列表
    
    Returns:
        dict: 统一响应格式，包含ETF列表
    """
    return {
        "code": 0,
        "message": "success",
        "data": ETF_LIST
    }


@router.get("/{code}/quote")
def get_etf_quote(code: str):
    """
    获取ETF实时行情
    
    获取指定ETF的实时行情数据
    
    Args:
        code: ETF基金代码
        
    Returns:
        dict: 统一响应格式，包含ETF行情数据
    """
    # 验证ETF代码是否存在
    etf_exists = any(etf["code"] == code for etf in ETF_LIST)
    if not etf_exists:
        raise HTTPException(status_code=404, detail=f"ETF代码 {code} 不存在")
    
    quote_data = get_mock_etf_quote(code)
    
    return {
        "code": 0,
        "message": "success",
        "data": quote_data
    }
