# 期权数据API路由
"""
期权数据接口

提供期权列表查询、期权行情等功能
由于akshare期权接口不稳定，使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import random

# 创建路由
router = APIRouter(prefix="/api/options", tags=["期权数据"])


def get_mock_option_list(stock_code: str) -> list:
    """
    生成模拟期权列表数据
    
    Args:
        stock_code: 股票代码
        
    Returns:
        list: 模拟期权列表
    """
    # 基于股票代码生成稳定的随机数
    seed = int(stock_code) if stock_code.isdigit() else hash(stock_code) % 10000
    random.seed(seed)
    
    # 基础价格（根据股票代码）
    base_prices = {
        "600519": 1850.0,   # 贵州茅台
        "000001": 12.5,     # 平安银行
        "300750": 210.0,   # 宁德时代
        "600036": 36.0,    # 招商银行
        "601318": 46.0,    # 中国平安
        "000858": 155.0,   # 五粮液
        "002594": 260.0,   # 比亚迪
        "600900": 23.0,    # 长江电力
        "601888": 72.0,    # 中国中免
        "300059": 21.0,    # 东方财富
    }
    base_price = base_prices.get(stock_code, 50.0)
    
    options = []
    expiry_dates = [
        (datetime.now() + timedelta(days=7)).strftime("%Y-%m"),
        (datetime.now() + timedelta(days=14)).strftime("%Y-%m"),
        (datetime.now() + timedelta(days=30)).strftime("%Y-%m"),
        (datetime.now() + timedelta(days=60)).strftime("%Y-%m"),
        (datetime.now() + timedelta(days=90)).strftime("%Y-%m"),
    ]
    
    # 认购期权（看涨期权）
    for i, expiry in enumerate(expiry_dates):
        strike_ratio = [0.95, 0.97, 1.0, 1.03, 1.05][i % 5]
        strike_price = round(base_price * strike_ratio, 2)
        
        # 内在价值和时间价值
        if strike_ratio < 1.0:
            # 实值期权
            intrinsic = round(base_price - strike_price, 2)
            premium = round(intrinsic + random.uniform(5, 20), 2)
        elif strike_ratio > 1.0:
            # 虚值期权
            intrinsic = 0
            premium = round(random.uniform(3, 15), 2)
        else:
            # 平值期权
            intrinsic = 0
            premium = round(random.uniform(8, 25), 2)
        
        option_code = f"{stock_code}C{expiry.replace('-', '')}{int(strike_price * 100):08d}"
        
        options.append({
            "option_code": option_code,
            "underlying_code": stock_code,
            "underlying_name": f"股票{stock_code}",
            "option_type": "C",  # 认购期权（看涨）
            "strike_price": strike_price,
            "expiry_date": expiry,
            "premium": premium,
            "bid": round(premium * 0.98, 2),
            "ask": round(premium * 1.02, 2),
            "volume": random.randint(100, 10000),
            "open_interest": random.randint(1000, 50000),
            "delta": round(random.uniform(0.1, 0.9), 3) if strike_ratio <= 1.0 else round(random.uniform(-0.1, 0.4), 3),
            "gamma": round(random.uniform(0.001, 0.05), 4),
            "theta": round(random.uniform(-5, -0.1), 2),
            "vega": round(random.uniform(0.1, 2.0), 2),
            "rho": round(random.uniform(-0.5, 0.5), 3),
            "implied_volatility": round(random.uniform(0.15, 0.45), 3),
            "status": "Trading",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # 认沽期权（看跌期权）
    for i, expiry in enumerate(expiry_dates):
        strike_ratio = [0.95, 0.97, 1.0, 1.03, 1.05][i % 5]
        strike_price = round(base_price * strike_ratio, 2)
        
        # 内在价值和时间价值
        if strike_ratio > 1.0:
            # 实值期权
            intrinsic = round(strike_price - base_price, 2)
            premium = round(intrinsic + random.uniform(5, 20), 2)
        elif strike_ratio < 1.0:
            # 虚值期权
            intrinsic = 0
            premium = round(random.uniform(3, 15), 2)
        else:
            # 平值期权
            intrinsic = 0
            premium = round(random.uniform(8, 25), 2)
        
        option_code = f"{stock_code}P{expiry.replace('-', '')}{int(strike_price * 100):08d}"
        
        options.append({
            "option_code": option_code,
            "underlying_code": stock_code,
            "underlying_name": f"股票{stock_code}",
            "option_type": "P",  # 认沽期权（看跌）
            "strike_price": strike_price,
            "expiry_date": expiry,
            "premium": premium,
            "bid": round(premium * 0.98, 2),
            "ask": round(premium * 1.02, 2),
            "volume": random.randint(100, 10000),
            "open_interest": random.randint(1000, 50000),
            "delta": round(random.uniform(-0.9, -0.1), 3) if strike_ratio >= 1.0 else round(random.uniform(-0.4, 0.1), 3),
            "gamma": round(random.uniform(0.001, 0.05), 4),
            "theta": round(random.uniform(-5, -0.1), 2),
            "vega": round(random.uniform(0.1, 2.0), 2),
            "rho": round(random.uniform(-0.5, 0.5), 3),
            "implied_volatility": round(random.uniform(0.15, 0.45), 3),
            "status": "Trading",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return options


def get_mock_option_quote(stock_code: str) -> dict:
    """
    生成模拟期权实时行情数据
    
    Args:
        stock_code: 股票代码
        
    Returns:
        dict: 模拟期权行情数据
    """
    # 获取期权列表
    options = get_mock_option_list(stock_code)
    
    # 取前5个期权作为实时行情示例
    quotes = []
    for option in options[:5]:
        change_pct = random.uniform(-10, 10)
        prev_premium = option["premium"] / (1 + change_pct / 100)
        
        quotes.append({
            "option_code": option["option_code"],
            "underlying_code": option["underlying_code"],
            "underlying_name": option["underlying_name"],
            "option_type": option["option_type"],
            "strike_price": option["strike_price"],
            "expiry_date": option["expiry_date"],
            "latest_price": option["premium"],
            "prev_close": round(prev_premium, 2),
            "open": round(prev_premium * (1 + random.uniform(-0.02, 0.02)), 2),
            "high": round(option["premium"] * (1 + random.uniform(0, 0.05)), 2),
            "low": round(option["premium"] * (1 - random.uniform(0, 0.05)), 2),
            "change": round(option["premium"] - prev_premium, 2),
            "change_pct": round(change_pct, 2),
            "bid": option["bid"],
            "ask": option["ask"],
            "bid_size": random.randint(10, 100),
            "ask_size": random.randint(10, 100),
            "volume": option["volume"],
            "open_interest": option["open_interest"],
            "implied_volatility": option["implied_volatility"],
            "delta": option["delta"],
            "gamma": option["gamma"],
            "theta": option["theta"],
            "vega": option["vega"],
            "rho": option["rho"],
            "theoretical_price": option["premium"],
            "status": option["status"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return {
        "underlying_code": stock_code,
        "underlying_name": f"股票{stock_code}",
        "underlying_price": random.uniform(10, 2000),
        "quotes": quotes,
        "total_count": len(options),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@router.get("/{code}")
async def get_option_list(code: str):
    """
    获取期权列表
    
    根据股票代码查询其所有期权合约
    
    Args:
        code: 股票代码
        
    Returns:
        期权列表数据
    """
    try:
        options = get_mock_option_list(code)
        return {
            "code": 0,
            "message": "success",
            "data": {
                "underlying_code": code,
                "underlying_name": f"股票{code}",
                "options": options,
                "total_count": len(options),
                "call_count": len([o for o in options if o["option_type"] == "C"]),
                "put_count": len([o for o in options if o["option_type"] == "P"]),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    except Exception as e:
        return {
            "code": -1,
            "message": str(e),
            "data": None
        }


@router.get("/{code}/quote")
async def get_option_quote(code: str):
    """
    获取期权实时行情
    
    根据股票代码查询其期权的实时行情数据
    
    Args:
        code: 股票代码
        
    Returns:
        期权实时行情数据
    """
    try:
        quote_data = get_mock_option_quote(code)
        return {
            "code": 0,
            "message": "success",
            "data": quote_data
        }
    except Exception as e:
        return {
            "code": -1,
            "message": str(e),
            "data": None
        }
