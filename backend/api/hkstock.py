# 港股数据API路由
"""
港股数据接口

提供港股列表查询、港股行情等功能
使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import random

# 创建路由
router = APIRouter(prefix="/api/hkstock", tags=["港股数据"])

# 港股配置 - 主要港股上市公司
HKSTOCKS = {
    # 蓝筹股
    "00001.HK": {"name": "汇丰控股", "industry": "银行", "base_price": 65.5},
    "00005.HK": {"name": "汇丰控股", "industry": "银行", "base_price": 65.5},
    "00006.HK": {"name": "电能实业", "industry": "公用事业", "base_price": 52.3},
    "01128.HK": {"name": "中国平安", "industry": "保险", "base_price": 48.2},
    "00981.HK": {"name": "中芯国际", "industry": "半导体", "base_price": 18.6},
    "00939.HK": {"name": "建设银行", "industry": "银行", "base_price": 5.8},
    "00981.HK": {"name": "中芯国际", "industry": "半导体", "base_price": 18.6},
    "01398.HK": {"name": "工商银行", "industry": "银行", "base_price": 4.9},
    "02318.HK": {"name": "中国平安", "industry": "保险", "base_price": 48.2},
    "02628.HK": {"name": "中国人寿", "industry": "保险", "base_price": 12.5},
    "03690.HK": {"name": "美团-W", "industry": "互联网", "base_price": 128.3},
    "09988.HK": {"name": "阿里巴巴-SW", "industry": "互联网", "base_price": 72.6},
    "09999.HK": {"name": "网易-S", "industry": "互联网", "base_price": 135.8},
    "02269.HK": {"name": "药明生物", "industry": "医药", "base_price": 18.2},
    "00175.HK": {"name": "吉利汽车", "industry": "汽车", "base_price": 12.8},
    "02333.HK": {"name": "长城汽车", "industry": "汽车", "base_price": 9.8},
    "01299.HK": {"name": "友邦保险", "industry": "保险", "base_price": 68.5},
    "01810.HK": {"name": "小米集团-W", "industry": "科技", "base_price": 15.8},
    "00700.HK": {"name": "腾讯控股", "industry": "互联网", "base_price": 312.6},
    "03888.HK": {"name": "金山软件", "industry": "软件", "base_price": 28.5},
    "06098.HK": {"name": "碧桂园服务", "industry": "物业", "base_price": 8.2},
    "02018.HK": {"name": "瑞声科技", "industry": "电子", "base_price": 18.6},
    "00267.HK": {"name": "中信股份", "industry": "综合", "base_price": 9.8},
    "02669.HK": {"name": "中国海外", "industry": "房地产", "base_price": 22.5},
    "00001.HK": {"name": "长和", "industry": "综合", "base_price": 42.3},
    "00016.HK": {"name": "九龙仓集团", "industry": "房地产", "base_price": 28.6},
    "00017.HK": {"name": "新世界发展", "industry": "房地产", "base_price": 18.2},
    "00101.HK": {"name": "恒生银行", "industry": "银行", "base_price": 128.5},
    "00003.HK": {"name": "中华煤气", "industry": "公用事业", "base_price": 8.6},
    "00688.HK": {"name": "中国海外发展", "industry": "房地产", "base_price": 22.5},
    "06808.HK": {"name": "中国奥园", "industry": "房地产", "base_price": 2.8},
    "01928.HK": {"name": "金沙中国", "industry": "博彩", "base_price": 22.8},
    "01928.HK": {"name": "金沙中国", "industry": "博彩", "base_price": 22.8},
    "00027.HK": {"name": "银河娱乐", "industry": "博彩", "base_price": 45.2},
    "02208.HK": {"name": "金风科技", "industry": "新能源", "base_price": 8.5},
    "09668.HK": {"name": "比亚迪股份", "industry": "汽车", "base_price": 168.2},
    "00285.HK": {"name": "比亚迪电子", "industry": "电子", "base_price": 18.6},
    "01886.HK": {"name": "中国民航信息网络", "industry": "航空", "base_price": 12.8},
    "00990.HK": {"name": "中国石油", "industry": "能源", "base_price": 5.2},
    "01186.HK": {"name": "中国铁建", "industry": "基建", "base_price": 8.6},
    "01199.HK": {"name": "中远海运", "industry": "航运", "base_price": 12.5},
    "02628.HK": {"name": "中国人寿", "industry": "保险", "base_price": 12.5},
    "03968.HK": {"name": "招商银行", "industry": "银行", "base_price": 38.5},
    "03606.HK": {"name": "龙湖集团", "industry": "房地产", "base_price": 18.2},
    "02318.HK": {"name": "中国平安", "industry": "保险", "base_price": 48.2},
    "00939.HK": {"name": "建设银行", "industry": "银行", "base_price": 5.8},
    "00981.HK": {"name": "中芯国际", "industry": "半导体", "base_price": 18.6},
    "02333.HK": {"name": "长城汽车", "industry": "汽车", "base_price": 9.8},
    "00175.HK": {"name": "吉利汽车", "industry": "汽车", "base_price": 12.8},
    "02269.HK": {"name": "药明生物", "industry": "医药", "base_price": 18.2},
    "09999.HK": {"name": "网易-S", "industry": "互联网", "base_price": 135.8},
    "09988.HK": {"name": "阿里巴巴-SW", "industry": "互联网", "base_price": 72.6},
    "03690.HK": {"name": "美团-W", "industry": "互联网", "base_price": 128.3},
    "01810.HK": {"name": "小米集团-W", "industry": "科技", "base_price": 15.8},
    "00700.HK": {"name": "腾讯控股", "industry": "互联网", "base_price": 312.6},
    "09668.HK": {"name": "比亚迪股份", "industry": "汽车", "base_price": 168.2},
    "01299.HK": {"name": "友邦保险", "industry": "保险", "base_price": 68.5},
    "00101.HK": {"name": "恒生银行", "industry": "银行", "base_price": 128.5},
}


def get_mock_hkstock_list() -> list:
    """
    生成模拟港股列表数据
    
    Returns:
        list: 模拟港股列表
    """
    # 去重
    seen = set()
    stocks = []
    for code, info in HKSTOCKS.items():
        if code not in seen:
            seen.add(code)
            stocks.append({
                "code": code,
                "name": info["name"],
                "industry": info["industry"],
                "base_price": info["base_price"],
                "status": "Trading",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    
    return stocks


def get_mock_hkstock_quote(code: str = None) -> list:
    """
    生成模拟港股实时行情数据
    
    Args:
        code: 港股代码，如果为None则返回所有股票的行情
        
    Returns:
        list: 模拟港股行情数据
    """
    quotes = []
    
    # 去重
    seen = set()
    stocks_to_query = {}
    if code:
        for c, info in HKSTOCKS.items():
            if c == code and c not in seen:
                seen.add(c)
                stocks_to_query[c] = info
                break
    else:
        for c, info in HKSTOCKS.items():
            if c not in seen:
                seen.add(c)
                stocks_to_query[c] = info
    
    for stock_code, info in stocks_to_query.items():
        base_price = info["base_price"]
        
        # 生成随机价格变动 (-3% 到 +3%)
        change_pct = random.uniform(-3, 3)
        prev_close = base_price * (1 - change_pct / 100)
        
        # 最新价格
        latest_price = base_price
        
        # 涨跌
        change = latest_price - prev_close
        
        # 生成交易数据
        volume = random.randint(100000, 50000000)
        turnover = latest_price * volume
        
        # 生成买卖价差
        spread = base_price * 0.002  # 0.2%价差
        bid = round(latest_price - spread, 2)
        ask = round(latest_price + spread, 2)
        
        # 52周高低
        week52_high = round(base_price * (1 + random.uniform(0.1, 0.4)), 2)
        week52_low = round(base_price * (1 - random.uniform(0.1, 0.4)), 2)
        
        quotes.append({
            "code": stock_code,
            "name": info["name"],
            "industry": info["industry"],
            "latest_price": latest_price,
            "prev_close": round(prev_close, 2),
            "open": round(prev_close * (1 + random.uniform(-0.02, 0.02)), 2),
            "high": round(latest_price * (1 + random.uniform(0, 0.05)), 2),
            "low": round(latest_price * (1 - random.uniform(0, 0.05)), 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": volume,
            "turnover": round(turnover, 2),
            "bid": bid,
            "ask": ask,
            "bid_size": random.randint(1000, 50000),
            "ask_size": random.randint(1000, 50000),
            "week52_high": week52_high,
            "week52_low": week52_low,
            "market_cap": round(latest_price * random.randint(1000000000, 50000000000), 2),
            "pe_ratio": round(random.uniform(5, 30), 2),
            "dividend_yield": round(random.uniform(1, 8), 2),
            "eps": round(latest_price / random.uniform(10, 25), 2),
            "status": "Trading",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return quotes


@router.get("/list")
async def get_hkstock_list():
    """
    获取港股列表
    
    返回所有可交易的港股列表
    
    Returns:
        港股列表数据
    """
    try:
        stocks = get_mock_hkstock_list()
        return {
            "code": 0,
            "message": "success",
            "data": {
                "stocks": stocks,
                "total_count": len(stocks),
                "industries": list(set([s["industry"] for s in stocks])),
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
async def get_hkstock_quote(code: str):
    """
    获取港股实时行情
    
    返回指定港股的实时行情数据
    
    Args:
        code: 港股代码，如 00700.HK
        
    Returns:
        港股实时行情数据
    """
    try:
        quotes = get_mock_hkstock_quote(code)
        if not quotes:
            raise HTTPException(status_code=404, detail=f"港股代码 {code} 不存在")
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "quotes": quotes,
                "total_count": len(quotes),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "code": -1,
            "message": str(e),
            "data": None
        }
