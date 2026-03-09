# 可转债API路由
"""
可转债数据接口

提供可转债列表查询、实时行情等功能
使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import random

# 创建路由
router = APIRouter(prefix="/api/bond", tags=["可转债"])


# 可转债模拟数据列表
BOND_LIST = [
    {"code": "113009", "name": "广汽转债", "stock_code": "601238", "stock_name": "广汽集团"},
    {"code": "127010", "name": "平银转债", "stock_code": "000001", "stock_name": "平安银行"},
    {"code": "128095", "name": "恩捷转债", "stock_code": "002812", "stock_name": "恩捷股份"},
    {"code": "113596", "name": "璞泰转债", "stock_code": "603659", "stock_name": "璞泰来"},
    {"code": "128136", "name": "立讯转债", "stock_code": "002475", "stock_name": "立讯精密"},
    {"code": "113025", "name": "明珠转债", "stock_code": "600873", "stock_name": "西藏明珠"},
    {"code": "128017", "name": "金禾转债", "stock_code": "002597", "stock_name": "金禾实业"},
    {"code": "113017", "name": "吉视转债", "stock_code": "601929", "stock_name": "吉视传媒"},
    {"code": "128033", "name": "东方转债", "stock_code": "002811", "stock_name": "东方雨虹"},
    {"code": "113015", "name": "久立转债", "stock_code": "002318", "stock_name": "久立特材"},
    {"code": "123038", "name": "利尔转债", "stock_code": "002258", "stock_name": "利尔化学"},
    {"code": "113020", "name": "桐昆转债", "stock_code": "601233", "stock_name": "桐昆股份"},
    {"code": "128100", "name": "石英转债", "stock_code": "603688", "stock_name": "石英股份"},
    {"code": "113550", "name": "博威转债", "stock_code": "601137", "stock_name": "博威合金"},
    {"code": "123105", "name": "拓尔转债", "stock_code": "300229", "stock_name": "拓尔思"},
    {"code": "113056", "name": "重银转债", "stock_code": "601998", "stock_name": "中信银行"},
    {"code": "128014", "name": "久其转债", "stock_code": "002279", "stock_name": "久其软件"},
    {"code": "127004", "name": "模塑转债", "stock_code": "000700", "stock_name": "模塑科技"},
    {"code": "113012", "name": "双环转债", "stock_code": "002472", "stock_name": "双环传动"},
    {"code": "128013", "name": "洪涛转债", "stock_code": "002325", "stock_name": "洪涛股份"},
]


def get_mock_bond_quote(bond_code: str) -> dict:
    """
    生成模拟可转债实时行情数据
    
    Args:
        bond_code: 可转债代码
        
    Returns:
        dict: 模拟行情数据
    """
    # 基于可转债代码生成稳定的随机数
    seed = int(bond_code) if bond_code.isdigit() else hash(bond_code) % 10000
    random.seed(seed)
    
    # 常见可转债的基础价格
    base_prices = {
        "113009": 108.50,
        "127010": 112.30,
        "128095": 145.80,
        "113596": 128.60,
        "128136": 138.90,
        "113025": 105.20,
        "128017": 116.40,
        "113017": 103.80,
        "128033": 125.70,
        "113015": 108.90,
        "123038": 115.60,
        "113020": 110.20,
        "128100": 168.50,
        "113550": 108.30,
        "123105": 108.70,
        "113056": 102.50,
        "128014": 106.80,
        "127004": 105.90,
        "113012": 107.20,
        "128013": 101.50,
    }
    base_price = base_prices.get(bond_code, 100.0)
    
    # 生成随机价格
    change_pct = random.uniform(-2.5, 2.5)
    price = base_price * (1 + change_pct / 100)
    prev_close = base_price
    
    # 获取对应的正股代码和名称
    bond_info = next((b for b in BOND_LIST if b["code"] == bond_code), None)
    stock_code = bond_info["stock_code"] if bond_info else "000000"
    stock_name = bond_info["stock_name"] if bond_info else "未知"
    
    return {
        "code": bond_code,
        "name": bond_info["name"] if bond_info else f"可转债{bond_code}",
        "stock_code": stock_code,
        "stock_name": stock_name,
        "latest_price": round(price, 2),
        "prev_close": round(prev_close, 2),
        "open": round(prev_close * (1 + random.uniform(-0.005, 0.005)), 2),
        "high": round(price * (1 + random.uniform(0, 0.015)), 2),
        "low": round(price * (1 - random.uniform(0, 0.015)), 2),
        "change": round(price - prev_close, 2),
        "change_pct": round(change_pct, 2),
        "volume": random.randint(10000, 1000000),
        "amount": round(price * random.randint(10000, 1000000), 2),
        "bid_price1": round(price * 0.998, 2),
        "bid_price2": round(price * 0.996, 2),
        "bid_price3": round(price * 0.994, 2),
        "ask_price1": round(price * 1.002, 2),
        "ask_price2": round(price * 1.004, 2),
        "ask_price3": round(price * 1.006, 2),
        "bid_volume1": random.randint(100, 10000),
        "bid_volume2": random.randint(100, 10000),
        "bid_volume3": random.randint(100, 10000),
        "ask_volume1": random.randint(100, 10000),
        "ask_volume2": random.randint(100, 10000),
        "ask_volume3": random.randint(100, 10000),
        "conversion_price": round(base_price * 0.85, 2),
        "conversion_value": round(price / (base_price * 0.85) * 100, 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@router.get("/list")
def get_bond_list():
    """
    获取可转债列表
    
    返回所有支持的可转债列表
    
    Returns:
        dict: 统一响应格式，包含可转债列表
    """
    return {
        "code": 0,
        "message": "success",
        "data": BOND_LIST
    }


@router.get("/{code}/quote")
def get_bond_quote(code: str):
    """
    获取可转债实时行情
    
    获取指定可转债的实时行情数据
    
    Args:
        code: 可转债代码
        
    Returns:
        dict: 统一响应格式，包含可转债行情数据
    """
    # 验证可转债代码是否存在
    bond_exists = any(bond["code"] == code for bond in BOND_LIST)
    if not bond_exists:
        raise HTTPException(status_code=404, detail=f"可转债代码 {code} 不存在")
    
    quote_data = get_mock_bond_quote(code)
    
    return {
        "code": 0,
        "message": "success",
        "data": quote_data
    }
