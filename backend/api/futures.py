# 期货数据API路由
"""
期货数据接口

提供期货行情查询、期货合约列表等功能
使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import random

# 创建路由
router = APIRouter(prefix="/api/futures", tags=["期货数据"])

# 期货合约配置
FUTURES_CONTRACTS = {
    # 商品期货
    "CU": {"name": "沪铜", "exchange": "SHFE", "base_price": 75000},
    "AL": {"name": "沪铝", "exchange": "SHFE", "base_price": 19500},
    "ZN": {"name": "沪锌", "exchange": "SHFE", "base_price": 23500},
    "PB": {"name": "沪铅", "exchange": "SHFE", "base_price": 16500},
    "NI": {"name": "沪镍", "exchange": "SHFE", "base_price": 125000},
    "AU": {"name": "沪金", "exchange": "SHFE", "base_price": 450},
    "AG": {"name": "沪银", "exchange": "SHFE", "base_price": 5500},
    "RU": {"name": "沪橡胶", "exchange": "SHFE", "base_price": 13000},
    "RU2505": {"name": "橡胶2505", "exchange": "SHFE", "base_price": 13200},
    "RU2509": {"name": "橡胶2509", "exchange": "SHFE", "base_price": 13500},
    "FU": {"name": "沪燃油", "exchange": "SHFE", "base_price": 3500},
    "WR": {"name": "沪线材", "exchange": "SHFE", "base_price": 3800},
    "HC": {"name": "热轧卷板", "exchange": "SHFE", "base_price": 3600},
    "RB": {"name": "螺纹钢", "exchange": "SHFE", "base_price": 3450},
    "SS": {"name": "不锈钢", "exchange": "SHFE", "base_price": 13500},
    "FU": {"name": "燃料油", "exchange": "SHFE", "base_price": 3200},
    "SC": {"name": "原油", "exchange": "SC", "base_price": 580},
    "SC2505": {"name": "原油2505", "exchange": "SC", "base_price": 585},
    "SC2509": {"name": "原油2509", "exchange": "SC", "base_price": 590},
    "AP": {"name": "苹果", "exchange": "CZCE", "base_price": 7500},
    "CJ": {"name": "红枣", "exchange": "CZCE", "base_price": 10500},
    "CS": {"name": "玉米", "exchange": "CZCE", "base_price": 2450},
    "CY": {"name": "棉纱", "exchange": "CZCE", "base_price": 23500},
    "FG": {"name": "玻璃", "exchange": "CZCE", "base_price": 1450},
    "JR": {"name": "粳米", "exchange": "CZCE", "base_price": 3550},
    "LR": {"name": "晚籼稻", "exchange": "CZCE", "base_price": 2750},
    "MA": {"name": "甲醇", "exchange": "CZCE", "base_price": 2650},
    "OI": {"name": "菜籽油", "exchange": "CZCE", "base_price": 8500},
    "PF": {"name": "短纤", "exchange": "CZCE", "base_price": 6800},
    "PK": {"name": "花生", "exchange": "CZCE", "base_price": 8500},
    "PM": {"name": "普麦", "exchange": "CZCE", "base_price": 2550},
    "PR": {"name": "早籼稻", "exchange": "CZCE", "base_price": 2650},
    "RI": {"name": "籼稻", "exchange": "CZCE", "base_price": 2850},
    "RM": {"name": "菜粕", "exchange": "CZCE", "base_price": 2850},
    "RS": {"name": "菜籽", "exchange": "CZCE", "base_price": 5800},
    "SM": {"name": "锰硅", "exchange": "CZCE", "base_price": 6500},
    "SR": {"name": "白糖", "exchange": "CZCE", "base_price": 6200},
    "TA": {"name": "PTA", "exchange": "CZCE", "base_price": 5500},
    "UR": {"name": "尿素", "exchange": "CZCE", "base_price": 1750},
    "V": {"name": "PVC", "exchange": "CZCE", "base_price": 5500},
    "WH": {"name": "强麦", "exchange": "CZCE", "base_price": 2950},
    "ZM": {"name": "豆粕", "exchange": "DCE", "base_price": 3200},
    "A": {"name": "豆一", "exchange": "DCE", "base_price": 4200},
    "B": {"name": "豆二", "exchange": "DCE", "base_price": 3800},
    "BB": {"name": "胶合板", "exchange": "DCE", "base_price": 115},
    "C": {"name": "玉米", "exchange": "DCE", "base_price": 2350},
    "CS": {"name": "玉米淀粉", "exchange": "DCE", "base_price": 2850},
    "EB": {"name": "苯乙烯", "exchange": "DCE", "base_price": 8500},
    "EG": {"name": "乙二醇", "exchange": "DCE", "base_price": 4500},
    "F": {"name": "纤维板", "exchange": "DCE", "base_price": 65},
    "I": {"name": "铁矿石", "exchange": "DCE", "base_price": 780},
    "I2505": {"name": "铁矿石2505", "exchange": "DCE", "base_price": 785},
    "I2509": {"name": "铁矿石2509", "exchange": "DCE", "base_price": 790},
    "J": {"name": "焦炭", "exchange": "DCE", "base_price": 2050},
    "JM": {"name": "焦煤", "exchange": "DCE", "base_price": 1350},
    "L": {"name": "塑料", "exchange": "DCE", "base_price": 8200},
    "LH": {"name": "生猪", "exchange": "DCE", "base_price": 14500},
    "M": {"name": "豆粕", "exchange": "DCE", "base_price": 3250},
    "P": {"name": "棕榈油", "exchange": "DCE", "base_price": 7500},
    "PP": {"name": "聚丙烯", "exchange": "DCE", "base_price": 7500},
    "RR": {"name": "粳米", "exchange": "DCE", "base_price": 3550},
    "V": {"name": "PVC", "exchange": "DCE", "base_price": 5600},
    "Y": {"name": "豆油", "exchange": "DCE", "base_price": 7800},
    # 金融期货
    "IF": {"name": "沪深300指数", "exchange": "CFFEX", "base_price": 3800},
    "IF2505": {"name": "沪深300指数2505", "exchange": "CFFEX", "base_price": 3820},
    "IF2506": {"name": "沪深300指数2506", "exchange": "CFFEX", "base_price": 3835},
    "IF2509": {"name": "沪深300指数2509", "exchange": "CFFEX", "base_price": 3850},
    "IH": {"name": "上证50指数", "exchange": "CFFEX", "base_price": 2650},
    "IH2505": {"name": "上证50指数2505", "exchange": "CFFEX", "base_price": 2660},
    "IH2506": {"name": "上证50指数2506", "exchange": "CFFEX", "base_price": 2670},
    "IC": {"name": "中证500指数", "exchange": "CFFEX", "base_price": 5500},
    "IC2505": {"name": "中证500指数2505", "exchange": "CFFEX", "base_price": 5520},
    "IC2506": {"name": "中证500指数2506", "exchange": "CFFEX", "base_price": 5540},
    "T": {"name": "10年期国债", "exchange": "CFFEX", "base_price": 102.5},
    "TF": {"name": "5年期国债", "exchange": "CFFEX", "base_price": 103.2},
    "TS": {"name": "2年期国债", "exchange": "CFFEX", "base_price": 101.8},
    "TL": {"name": "2年期国债", "exchange": "CFFEX", "base_price": 101.8},
    "IM": {"name": "中证1000指数", "exchange": "CFFEX", "base_price": 6200},
    "IM2505": {"name": "中证1000指数2505", "exchange": "CFFEX", "base_price": 6220},
    "IM2506": {"name": "中证1000指数2506", "exchange": "CFFEX", "base_price": 6240},
}


def get_mock_futures_list() -> list:
    """
    生成模拟期货列表数据
    
    Returns:
        list: 模拟期货列表
    """
    contracts = []
    for code, info in FUTURES_CONTRACTS.items():
        contracts.append({
            "code": code,
            "name": info["name"],
            "exchange": info["exchange"],
            "base_price": info["base_price"],
            "status": "Trading",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return contracts


def get_mock_futures_quote(code: str = None) -> dict:
    """
    生成模拟期货实时行情数据
    
    Args:
        code: 期货代码，如果为None则返回所有合约的行情
        
    Returns:
        dict: 模拟期货行情数据
    """
    quotes = []
    
    # 确定要查询的合约列表
    if code:
        contracts_to_query = {code: FUTURES_CONTRACTS.get(code)} if code in FUTURES_CONTRACTS else {}
    else:
        contracts_to_query = FUTURES_CONTRACTS
    
    for contract_code, info in contracts_to_query.items():
        if info is None:
            continue
            
        base_price = info["base_price"]
        
        # 生成随机价格变动
        change_pct = random.uniform(-3, 3)
        prev_close = base_price * (1 - change_pct / 100)
        
        # 最新价格
        latest_price = base_price
        
        # 涨跌
        change = latest_price - prev_close
        
        # 生成交易数据
        volume = random.randint(1000, 100000)
        open_interest = random.randint(10000, 500000)
        
        # 生成买卖价差
        spread = base_price * 0.001  # 0.1%价差
        bid = round(latest_price - spread, 2)
        ask = round(latest_price + spread, 2)
        
        quotes.append({
            "code": contract_code,
            "name": info["name"],
            "exchange": info["exchange"],
            "latest_price": latest_price,
            "prev_close": round(prev_close, 2),
            "open": round(prev_close * (1 + random.uniform(-0.01, 0.01)), 2),
            "high": round(latest_price * (1 + random.uniform(0, 0.03)), 2),
            "low": round(latest_price * (1 - random.uniform(0, 0.03)), 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": volume,
            "open_interest": open_interest,
            "turnover": round(latest_price * volume * 10, 2),  # 假设每手10吨
            "bid": bid,
            "ask": ask,
            "bid_size": random.randint(10, 500),
            "ask_size": random.randint(10, 500),
            "settlement": round(latest_price, 2),
            "prev_settlement": round(prev_close, 2),
            "delta": round(random.uniform(-1, 1), 4),
            "gamma": round(random.uniform(0, 0.1), 4),
            "theta": round(random.uniform(-10, 0), 2),
            "vega": round(random.uniform(0, 50), 2),
            "status": "Trading",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return quotes


@router.get("/list")
async def get_futures_list():
    """
    获取期货合约列表
    
    返回所有可交易的期货合约列表
    
    Returns:
        期货合约列表数据
    """
    try:
        contracts = get_mock_futures_list()
        return {
            "code": 0,
            "message": "success",
            "data": {
                "contracts": contracts,
                "total_count": len(contracts),
                "exchanges": list(set([c["exchange"] for c in contracts])),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    except Exception as e:
        return {
            "code": -1,
            "message": str(e),
            "data": None
        }


@router.get("/quote")
async def get_futures_quote(code: str = None):
    """
    获取期货实时行情
    
    返回期货的实时行情数据，支持查询单个合约或所有合约
    
    Args:
        code: 期货代码，可选。如果不指定则返回所有合约行情
        
    Returns:
        期货实时行情数据
    """
    try:
        quotes = get_mock_futures_quote(code)
        return {
            "code": 0,
            "message": "success",
            "data": {
                "quotes": quotes,
                "total_count": len(quotes),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    except Exception as e:
        return {
            "code": -1,
            "message": str(e),
            "data": None
        }
