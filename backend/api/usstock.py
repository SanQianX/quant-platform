# 美股数据API路由
"""
美股数据接口

提供美股列表查询、美股行情等功能
使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import random

# 创建路由
router = APIRouter(prefix="/api/usstock", tags=["美股数据"])

# 美股配置 - 主要美股上市公司
USSTOCKS = {
    # 科技股
    "AAPL": {"name": "苹果公司", "industry": "科技", "base_price": 185.5},
    "MSFT": {"name": "微软公司", "industry": "科技", "base_price": 378.2},
    "GOOGL": {"name": "Alphabet Inc.", "industry": "科技", "base_price": 141.8},
    "GOOG": {"name": "Alphabet Inc. C", "industry": "科技", "base_price": 140.2},
    "AMZN": {"name": "亚马逊公司", "industry": "电商", "base_price": 178.5},
    "META": {"name": "Meta Platforms", "industry": "社交媒体", "base_price": 485.2},
    "NVDA": {"name": "英伟达公司", "industry": "半导体", "base_price": 875.3},
    "TSLA": {"name": "特斯拉公司", "industry": "新能源汽车", "base_price": 245.8},
    "BRK.B": {"name": "伯克希尔哈撒韦", "industry": "综合", "base_price": 408.5},
    "BRK.A": {"name": "伯克希尔哈撒韦A", "industry": "综合", "base_price": 608250.0},
    "UNH": {"name": "联合健康集团", "industry": "医疗保健", "base_price": 528.5},
    "JNJ": {"name": "强生公司", "industry": "医疗保健", "base_price": 156.8},
    "V": {"name": "Visa Inc.", "industry": "金融", "base_price": 275.6},
    "XOM": {"name": "埃克森美孚", "industry": "能源", "base_price": 104.5},
    "JPM": {"name": "摩根大通", "industry": "银行", "base_price": 198.5},
    "WMT": {"name": "沃尔玛公司", "industry": "零售", "base_price": 165.2},
    "PG": {"name": "宝洁公司", "industry": "消费品", "base_price": 158.8},
    "MA": {"name": "万事达卡", "industry": "金融", "base_price": 458.2},
    "HD": {"name": "家得宝公司", "industry": "零售", "base_price": 345.6},
    "CVX": {"name": "雪佛龙公司", "industry": "能源", "base_price": 152.8},
    "MRK": {"name": "默克集团", "industry": "医疗保健", "base_price": 125.5},
    "LLY": {"name": "礼来公司", "industry": "医疗保健", "base_price": 765.2},
    "ABBV": {"name": "艾伯维公司", "industry": "医疗保健", "base_price": 168.5},
    "PFE": {"name": "辉瑞公司", "industry": "医疗保健", "base_price": 28.5},
    "KO": {"name": "可口可乐公司", "industry": "饮料", "base_price": 62.5},
    "PEP": {"name": "百事可乐公司", "industry": "饮料", "base_price": 172.5},
    "COST": {"name": "好市多公司", "industry": "零售", "base_price": 725.8},
    "AVGO": {"name": "博通公司", "industry": "半导体", "base_price": 1285.5},
    "TMO": {"name": "赛默飞世尔", "industry": "医疗保健", "base_price": 545.2},
    "MCD": {"name": "麦当劳公司", "industry": "餐饮", "base_price": 295.8},
    "CSCO": {"name": "思科系统", "industry": "科技", "base_price": 52.5},
    "ACN": {"name": "埃森哲公司", "industry": "科技", "base_price": 345.8},
    "ABT": {"name": "雅培公司", "industry": "医疗保健", "base_price": 108.5},
    "DHR": {"name": "丹纳赫公司", "industry": "医疗保健", "base_price": 252.8},
    "NKE": {"name": "耐克公司", "industry": "消费品", "base_price": 98.5},
    "TXN": {"name": "德州仪器", "industry": "半导体", "base_price": 175.2},
    "ORCL": {"name": "甲骨文公司", "industry": "科技", "base_price": 125.5},
    "NEE": {"name": "NextEra Energy", "industry": "公用事业", "base_price": 72.5},
    "PM": {"name": "菲利普莫里斯", "industry": "消费品", "base_price": 98.5},
    "UNP": {"name": "联合太平洋", "industry": "铁路", "base_price": 245.8},
    "BMY": {"name": "百时美施贵宝", "industry": "医疗保健", "base_price": 52.5},
    "RTX": {"name": "RTX公司", "industry": "航空航天", "base_price": 108.5},
    "HON": {"name": "霍尼韦尔", "industry": "工业", "base_price": 205.5},
    "LOW": {"name": "劳氏公司", "industry": "零售", "base_price": 235.8},
    "UPS": {"name": "联合包裹服务", "industry": "物流", "base_price": 145.2},
    "BA": {"name": "波音公司", "industry": "航空航天", "base_price": 185.5},
    "AMGN": {"name": "安进公司", "industry": "医疗保健", "base_price": 285.5},
    "IBM": {"name": "IBM公司", "industry": "科技", "base_price": 188.5},
    "CAT": {"name": "卡特彼勒公司", "industry": "工业", "base_price": 325.8},
    "SBUX": {"name": "星巴克公司", "industry": "餐饮", "base_price": 95.5},
    "GE": {"name": "通用电气", "industry": "工业", "base_price": 168.5},
    "INTC": {"name": "英特尔公司", "industry": "半导体", "base_price": 42.5},
    "AMD": {"name": "超微半导体", "industry": "半导体", "base_price": 175.5},
    "QCOM": {"name": "高通公司", "industry": "半导体", "base_price": 168.5},
    "DIS": {"name": "迪士尼公司", "industry": "娱乐", "base_price": 112.5},
    "T": {"name": "AT&T公司", "industry": "电信", "base_price": 17.5},
    "VZ": {"name": "威瑞信电信", "industry": "电信", "base_price": 42.5},
    "ADBE": {"name": "Adobe公司", "industry": "科技", "base_price": 575.5},
    "CRM": {"name": "Salesforce", "industry": "科技", "base_price": 285.5},
    "NFLX": {"name": "奈飞公司", "industry": "娱乐", "base_price": 625.5},
    "PYPL": {"name": "PayPal公司", "industry": "金融", "base_price": 62.5},
    "SQ": {"name": "Block公司", "industry": "金融", "base_price": 75.5},
    "SHOP": {"name": "Shopify公司", "industry": "电商", "base_price": 78.5},
    "SNAP": {"name": "Snap公司", "industry": "社交媒体", "base_price": 11.5},
    "TWTR": {"name": "Twitter公司", "industry": "社交媒体", "base_price": 54.5},
    "UBER": {"name": "优步公司", "industry": "科技", "base_price": 72.5},
    "LYFT": {"name": "Lyft公司", "industry": "科技", "base_price": 12.5},
    "COIN": {"name": "Coinbase公司", "industry": "加密货币", "base_price": 175.5},
    "RBLX": {"name": "Roblox公司", "industry": "游戏", "base_price": 38.5},
    "SNOW": {"name": "Snowflake公司", "industry": "科技", "base_price": 165.5},
    "ZM": {"name": "Zoom公司", "industry": "科技", "base_price": 68.5},
    "DOCU": {"name": "DocuSign公司", "industry": "科技", "base_price": 58.5},
    "PLTR": {"name": "Palantir公司", "industry": "科技", "base_price": 22.5},
    "U": {"name": "Unity Software", "industry": "游戏", "base_price": 28.5},
    "DDOG": {"name": "Datadog公司", "industry": "科技", "base_price": 115.5},
    "CRWD": {"name": "CrowdStrike", "industry": "网络安全", "base_price": 245.5},
    "NET": {"name": "Cloudflare公司", "industry": "科技", "base_price": 85.5},
    "OKTA": {"name": "Okta公司", "industry": "网络安全", "base_price": 78.5},
    "SPLK": {"name": "Splunk公司", "industry": "科技", "base_price": 145.5},
    "PANW": {"name": "Palo Alto", "industry": "网络安全", "base_price": 325.5},
    "FTNT": {"name": "Fortinet公司", "industry": "网络安全", "base_price": 68.5},
    "MDB": {"name": "MongoDB公司", "industry": "科技", "base_price": 385.5},
    "TEAM": {"name": "Atlassian公司", "industry": "科技", "base_price": 195.5},
    "WORK": {"name": "Slack公司", "industry": "科技", "base_price": 42.5},
    "ZEN": {"name": "Zendesk公司", "industry": "科技", "base_price": 78.5},
}


def get_mock_usstock_list() -> list:
    """
    生成模拟美股列表数据
    
    Returns:
        list: 模拟美股列表
    """
    # 去重
    seen = set()
    stocks = []
    for code, info in USSTOCKS.items():
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


def get_mock_usstock_quote(code: str = None) -> list:
    """
    生成模拟美股实时行情数据
    
    Args:
        code: 美股代码，如果为None则返回所有股票的行情
        
    Returns:
        list: 模拟美股行情数据
    """
    quotes = []
    
    # 去重
    seen = set()
    stocks_to_query = {}
    if code:
        for c, info in USSTOCKS.items():
            if c.upper() == code.upper() and c not in seen:
                seen.add(c)
                stocks_to_query[c] = info
                break
    else:
        for c, info in USSTOCKS.items():
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
        volume = random.randint(1000000, 100000000)
        turnover = latest_price * volume
        
        # 生成买卖价差
        spread = base_price * 0.001  # 0.1%价差
        bid = round(latest_price - spread, 2)
        ask = round(latest_price + spread, 2)
        
        # 52周高低
        week52_high = round(base_price * (1 + random.uniform(0.1, 0.5)), 2)
        week52_low = round(base_price * (1 - random.uniform(0.1, 0.5)), 2)
        
        # 市值 (单位: 百万美元)
        market_cap = round(latest_price * random.randint(1000000000, 3000000000) / 1000000, 2)
        
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
            "bid_size": random.randint(10000, 500000),
            "ask_size": random.randint(10000, 500000),
            "week52_high": week52_high,
            "week52_low": week52_low,
            "market_cap": market_cap,
            "pe_ratio": round(random.uniform(10, 40), 2),
            "dividend_yield": round(random.uniform(0, 5), 2),
            "eps": round(latest_price / random.uniform(10, 50), 2),
            "beta": round(random.uniform(0.5, 2.0), 2),
            "status": "Trading",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return quotes


@router.get("/list")
async def get_usstock_list():
    """
    获取美股列表
    
    返回所有可交易的美股列表
    
    Returns:
        美股列表数据
    """
    try:
        stocks = get_mock_usstock_list()
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
async def get_usstock_quote(code: str):
    """
    获取美股实时行情
    
    返回指定美股的实时行情数据
    
    Args:
        code: 美股代码，如 AAPL, MSFT
        
    Returns:
        美股实时行情数据
    """
    try:
        quotes = get_mock_usstock_quote(code)
        if not quotes:
            raise HTTPException(status_code=404, detail=f"美股代码 {code} 不存在")
        
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
