# 融资融券数据API路由
"""
融资融券数据接口

提供融资融券列表查询、个股融资融券详情等功能
使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import random

# 创建路由
router = APIRouter(prefix="/api/margin", tags=["融资融券数据"])

# 融资融券股票配置 - 模拟A股市场中支持融资融券的股票
MARGIN_STOCKS = {
    "600519": {"name": "贵州茅台", "industry": "白酒", "base_price": 1650.0},
    "600036": {"name": "招商银行", "industry": "银行", "base_price": 35.8},
    "600900": {"name": "长江电力", "industry": "电力", "base_price": 22.5},
    "601318": {"name": "中国平安", "industry": "保险", "base_price": 48.2},
    "601398": {"name": "工商银行", "industry": "银行", "base_price": 5.2},
    "601939": {"name": "建设银行", "industry": "银行", "base_price": 6.8},
    "600028": {"name": "中国石化", "industry": "石油", "base_price": 6.5},
    "600030": {"name": "中信证券", "industry": "证券", "base_price": 22.8},
    "600887": {"name": "伊利股份", "industry": "食品", "base_price": 28.5},
    "600276": {"name": "恒瑞医药", "industry": "医药", "base_price": 52.3},
    "601888": {"name": "中国中免", "industry": "旅游", "base_price": 68.5},
    "600309": {"name": "万华化学", "industry": "化工", "base_price": 98.6},
    "601012": {"name": "隆基绿能", "industry": "光伏", "base_price": 28.2},
    "002594": {"name": "比亚迪", "industry": "汽车", "base_price": 268.5},
    "000858": {"name": "五粮液", "industry": "白酒", "base_price": 145.8},
    "000333": {"name": "美的集团", "industry": "家电", "base_price": 58.6},
    "000651": {"name": "格力电器", "industry": "家电", "base_price": 38.2},
    "002475": {"name": "立讯精密", "industry": "电子", "base_price": 32.5},
    "300750": {"name": "宁德时代", "industry": "新能源", "base_price": 185.6},
    "600104": {"name": "上汽集团", "industry": "汽车", "base_price": 18.5},
    "601166": {"name": "兴业银行", "industry": "银行", "base_price": 18.6},
    "600016": {"name": "民生银行", "industry": "银行", "base_price": 4.8},
    "601328": {"name": "交通银行", "industry": "银行", "base_price": 5.6},
    "601988": {"name": "中国银行", "industry": "银行", "base_price": 3.8},
    "600000": {"name": "浦发银行", "industry": "银行", "base_price": 8.5},
    "601288": {"name": "农业银行", "industry": "银行", "base_price": 3.5},
    "600015": {"name": "华夏银行", "industry": "银行", "base_price": 6.8},
    "601229": {"name": "上海银行", "industry": "银行", "base_price": 6.2},
    "600919": {"name": "江苏银行", "industry": "银行", "base_price": 7.5},
    "600926": {"name": "杭州银行", "industry": "银行", "base_price": 12.8},
    "000001": {"name": "平安银行", "industry": "银行", "base_price": 12.5},
    "601818": {"name": "光大银行", "industry": "银行", "base_price": 3.6},
    "601169": {"name": "北京银行", "industry": "银行", "base_price": 4.5},
    "600015": {"name": "华夏银行", "industry": "银行", "base_price": 6.8},
    "002142": {"name": "深圳机场", "industry": "机场", "base_price": 8.2},
    "601111": {"name": "中国交建", "industry": "基建", "base_price": 10.5},
    "600585": {"name": "海螺水泥", "industry": "水泥", "base_price": 28.6},
    "600690": {"name": "青岛海尔", "industry": "家电", "base_price": 25.8},
    "600050": {"name": "中国联通", "industry": "通信", "base_price": 5.8},
    "600030": {"name": "中信证券", "industry": "证券", "base_price": 22.8},
    "601688": {"name": "中国中车", "industry": "高铁", "base_price": 6.8},
    "601766": {"name": "中国中车", "industry": "高铁", "base_price": 6.5},
    "601390": {"name": "中国中铁", "industry": "基建", "base_price": 6.2},
    "601186": {"name": "中国铁建", "industry": "基建", "base_price": 8.6},
    "600048": {"name": "保利发展", "industry": "房地产", "base_price": 12.8},
    "600383": {"name": "金地集团", "industry": "房地产", "base_price": 8.5},
    "000002": {"name": "万科A", "industry": "房地产", "base_price": 8.2},
    "601857": {"name": "中国石油", "industry": "石油", "base_price": 5.2},
    "600028": {"name": "中国石化", "industry": "石油", "base_price": 6.5},
    "600346": {"name": "恒力石化", "industry": "化工", "base_price": 15.8},
    "600009": {"name": "上海机场", "industry": "机场", "base_price": 45.6},
}


def get_mock_margin_list() -> list:
    """
    生成模拟融资融券列表数据
    
    Returns:
        list: 模拟融资融券列表
    """
    margin_list = []
    
    for code, info in MARGIN_STOCKS.items():
        # 生成模拟数据
        base_price = info["base_price"]
        
        # 融资相关数据
        margin_balance = random.randint(100000000, 5000000000)  # 融资余额
        margin_purchase = random.randint(50000000, 500000000)  # 融资买入额
        margin_repayment = random.randint(30000000, 400000000)  # 融资偿还额
        
        # 融券相关数据
        short_balance = random.randint(10000000, 500000000)  # 融券余额
        short_selling = random.randint(1000000, 50000000)  # 融券卖出量
        short_covering = random.randint(800000, 40000000)  # 融券偿还量
        
        # 计算融资融券余额
        total_margin = margin_balance + short_balance
        
        # 计算融资占比
        margin_ratio = round(margin_balance / total_margin * 100, 2) if total_margin > 0 else 0
        
        # 生成涨跌幅
        change_pct = round(random.uniform(-5, 5), 2)
        change = round(base_price * change_pct / 100, 2)
        latest_price = round(base_price + change, 2)
        
        margin_list.append({
            "code": code,
            "name": info["name"],
            "industry": info["industry"],
            "latest_price": latest_price,
            "change": change,
            "change_pct": change_pct,
            "margin_balance": margin_balance,
            "margin_purchase": margin_purchase,
            "margin_repayment": margin_repayment,
            "short_balance": short_balance,
            "short_selling": short_selling,
            "short_covering": short_covering,
            "total_margin": total_margin,
            "margin_ratio": margin_ratio,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # 按融资余额排序
    margin_list.sort(key=lambda x: x["margin_balance"], reverse=True)
    
    return margin_list


def get_mock_margin_detail(code: str) -> dict:
    """
    生成模拟个股融资融券详情数据
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 模拟个股融资融券详情
    """
    if code not in MARGIN_STOCKS:
        raise HTTPException(status_code=404, detail=f"股票代码 {code} 不存在")
    
    info = MARGIN_STOCKS[code]
    base_price = info["base_price"]
    
    # 生成模拟数据
    margin_balance = random.randint(100000000, 5000000000)  # 融资余额
    margin_purchase = random.randint(50000000, 500000000)  # 融资买入额
    margin_repayment = random.randint(30000000, 400000000)  # 融资偿还额
    margin_buy_amount = random.randint(40000000, 300000000)  # 融资买入金额
    margin_buy_volume = random.randint(1000000, 10000000)  # 融资买入数量
    margin_sell_amount = random.randint(20000000, 250000000)  # 融资卖出金额
    margin_sell_volume = random.randint(800000, 8000000)  # 融资卖出数量
    
    # 融券相关数据
    short_balance = random.randint(10000000, 500000000)  # 融券余额
    short_balance_volume = random.randint(1000000, 50000000)  # 融券余量
    short_selling = random.randint(1000000, 50000000)  # 融券卖出量
    short_covering = random.randint(800000, 40000000)  # 融券偿还量
    
    # 计算融资融券余额
    total_margin = margin_balance + short_balance
    
    # 计算融资占比
    margin_ratio = round(margin_balance / total_margin * 100, 2) if total_margin > 0 else 0
    
    # 融资占比变化
    margin_ratio_change = round(random.uniform(-2, 2), 2)
    
    # 生成价格数据
    change_pct = round(random.uniform(-5, 5), 2)
    change = round(base_price * change_pct / 100, 2)
    latest_price = round(base_price + change, 2)
    prev_close = base_price
    open_price = round(base_price * (1 + random.uniform(-0.02, 0.02)), 2)
    high_price = round(latest_price * (1 + random.uniform(0, 0.03)), 2)
    low_price = round(latest_price * (1 - random.uniform(0, 0.03)), 2)
    
    # 融资成本
    margin_rate = round(random.uniform(5.5, 8.5), 2)  # 融资利率
    
    # 融券费率
    short_rate = round(random.uniform(8.0, 12.0), 2)  # 融券费率
    
    # 保证金比例
    margin_ratio_required = round(random.uniform(50, 80), 2)  # 保证金比例
    
    # 融资可用余额
    margin_available = random.randint(500000000, 3000000000)
    
    # 融券可用余量
    short_available = random.randint(5000000, 100000000)
    
    return {
        "code": code,
        "name": info["name"],
        "industry": info["industry"],
        "latest_price": latest_price,
        "prev_close": prev_close,
        "open": open_price,
        "high": high_price,
        "low": low_price,
        "change": change,
        "change_pct": change_pct,
        # 融资数据
        "margin_balance": margin_balance,
        "margin_balance_change": random.randint(-100000000, 100000000),
        "margin_purchase": margin_purchase,
        "margin_repayment": margin_repayment,
        "margin_buy_amount": margin_buy_amount,
        "margin_buy_volume": margin_buy_volume,
        "margin_sell_amount": margin_sell_amount,
        "margin_sell_volume": margin_sell_volume,
        "margin_available": margin_available,
        "margin_rate": margin_rate,
        # 融券数据
        "short_balance": short_balance,
        "short_balance_volume": short_balance_volume,
        "short_balance_change": random.randint(-10000000, 10000000),
        "short_selling": short_selling,
        "short_covering": short_covering,
        "short_available": short_available,
        "short_rate": short_rate,
        # 汇总数据
        "total_margin": total_margin,
        "margin_ratio": margin_ratio,
        "margin_ratio_change": margin_ratio_change,
        "margin_ratio_required": margin_ratio_required,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@router.get("/list")
async def get_margin_list():
    """
    获取融资融券列表
    
    返回所有支持融资融券的股票列表及融资融券数据
    
    Returns:
        融资融券列表数据
    """
    try:
        margin_list = get_mock_margin_list()
        
        # 计算汇总数据
        total_margin_balance = sum(item["margin_balance"] for item in margin_list)
        total_short_balance = sum(item["short_balance"] for item in margin_list)
        total_margin = total_margin_balance + total_short_balance
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "list": margin_list,
                "total_count": len(margin_list),
                "summary": {
                    "total_margin_balance": total_margin_balance,
                    "total_short_balance": total_short_balance,
                    "total_margin": total_margin,
                    "avg_margin_ratio": round(total_margin_balance / total_margin * 100, 2) if total_margin > 0 else 0
                },
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    except Exception as e:
        return {
            "code": -1,
            "message": str(e),
            "data": None
        }


@router.get("/{code}")
async def get_margin_detail(code: str):
    """
    获取个股融资融券详情
    
    返回指定股票的融资融券详细数据
    
    Args:
        code: 股票代码
        
    Returns:
        个股融资融券详情数据
    """
    try:
        detail = get_mock_margin_detail(code)
        return {
            "code": 0,
            "message": "success",
            "data": detail
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "code": -1,
            "message": str(e),
            "data": None
        }
