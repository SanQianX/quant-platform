# 大宗交易数据API路由
"""
大宗交易数据接口

提供大宗交易列表查询、个股大宗交易详情等功能
使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import random

# 创建路由
router = APIRouter(prefix="/api/block-trade", tags=["大宗交易数据"])

# 大宗交易股票配置 - 模拟A股市场中的大宗交易股票
BLOCK_TRADE_STOCKS = {
    "600519": {"name": "贵州茅台", "industry": "白酒", "base_price": 1650.0},
    "600036": {"name": "招商银行", "industry": "银行", "base_price": 35.8},
    "600900": {"name": "长江电力", "industry": "电力", "base_price": 22.5},
    "601318": {"name": "中国平安", "industry": "保险", "base_price": 48.2},
    "601398": {"name": "工商银行", "industry": "银行", "base_price": 5.2},
    "600887": {"name": "伊利股份", "industry": "食品", "base_price": 28.5},
    "600276": {"name": "恒瑞医药", "industry": "医药", "base_price": 52.3},
    "601888": {"name": "中国中免", "industry": "旅游", "base_price": 68.5},
    "600309": {"name": "万华化学", "industry": "化工", "base_price": 98.6},
    "601012": {"name": "隆基绿能", "industry": "光伏", "base_price": 28.2},
    "002594": {"name": "比亚迪", "industry": "汽车", "base_price": 268.5},
    "000858": {"name": "五粮液", "industry": "白酒", "base_price": 145.8},
    "000333": {"name": "美的集团", "industry": "家电", "base_price": 58.6},
    "000651": {"name": "格力电器", "industry": "家电", "base_price": 38.2},
    "300750": {"name": "宁德时代", "industry": "新能源", "base_price": 185.6},
    "600048": {"name": "保利发展", "industry": "房地产", "base_price": 12.8},
    "000002": {"name": "万科A", "industry": "房地产", "base_price": 8.2},
    "600028": {"name": "中国石化", "industry": "石油", "base_price": 6.5},
    "600585": {"name": "海螺水泥", "industry": "水泥", "base_price": 28.6},
    "600009": {"name": "上海机场", "industry": "机场", "base_price": 45.6},
}


def generate_block_trade_date(days_ago: int = 0) -> str:
    """生成交易日期"""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d")


def get_mock_block_trade_list() -> list:
    """
    生成模拟大宗交易列表数据
    
    Returns:
        list: 模拟大宗交易列表
    """
    trade_list = []
    
    # 为每只股票生成多笔大宗交易记录
    for code, info in BLOCK_TRADE_STOCKS.items():
        # 每只股票生成1-5笔交易
        num_trades = random.randint(1, 5)
        
        for i in range(num_trades):
            base_price = info["base_price"]
            
            # 大宗交易价格（通常比市价有一定折价）
            discount = random.uniform(0.92, 0.99)
            trade_price = round(base_price * discount, 2)
            
            # 成交量（股数）
            volume = random.randint(100000, 5000000)
            
            # 成交金额
            amount = volume * trade_price
            
            # 折价率
            discount_rate = round((1 - discount) * 100, 2)
            
            # 买卖方向
            direction = random.choice(["买方", "卖方", "双方"])
            
            # 交易日
            trade_date = generate_block_trade_date(random.randint(0, 30))
            
            # 营业部
            departments = [
                "中信证券股份有限公司北京总部证券营业部",
                "华泰证券股份有限公司深圳益田路证券营业部",
                "中国国际金融股份有限公司北京建国门外证券营业部",
                "国泰君安证券股份有限公司上海江苏路证券营业部",
                "海通证券股份有限公司杭州解放路证券营业部",
                "广发证券股份有限公司广州天河北路证券营业部",
                "申万宏源证券有限公司上海新昌路证券营业部",
                "招商证券股份有限公司深圳蛇口证券营业部"
            ]
            department = random.choice(departments)
            
            trade_list.append({
                "code": code,
                "name": info["name"],
                "industry": info["industry"],
                "trade_date": trade_date,
                "trade_price": trade_price,
                "volume": volume,
                "amount": amount,
                "discount_rate": discount_rate,
                "direction": direction,
                "department": department,
                "prev_close": base_price,
                "change_pct": round(random.uniform(-5, 5), 2)
            })
    
    # 按日期排序（最近的在前）
    trade_list.sort(key=lambda x: x["trade_date"], reverse=True)
    
    return trade_list


def get_mock_block_trade_detail(code: str) -> dict:
    """
    生成模拟个股大宗交易详情数据
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 模拟个股大宗交易详情
    """
    if code not in BLOCK_TRADE_STOCKS:
        raise HTTPException(status_code=404, detail=f"股票代码 {code} 不存在")
    
    info = BLOCK_TRADE_STOCKS[code]
    base_price = info["base_price"]
    
    # 生成该股票的多笔大宗交易
    trades = []
    num_trades = random.randint(5, 15)
    
    departments = [
        "中信证券股份有限公司北京总部证券营业部",
        "华泰证券股份有限公司深圳益田路证券营业部",
        "中国国际金融股份有限公司北京建国门外证券营业部",
        "国泰君安证券股份有限公司上海江苏路证券营业部",
        "海通证券股份有限公司杭州解放路证券营业部",
        "广发证券股份有限公司广州天河北路证券营业部",
        "申万宏源证券有限公司上海新昌路证券营业部",
        "招商证券股份有限公司深圳蛇口证券营业部"
    ]
    
    for i in range(num_trades):
        # 大宗交易价格
        discount = random.uniform(0.92, 0.99)
        trade_price = round(base_price * discount, 2)
        
        # 成交量
        volume = random.randint(100000, 5000000)
        
        # 成交金额
        amount = volume * trade_price
        
        # 折价率
        discount_rate = round((1 - discount) * 100, 2)
        
        # 买卖方向
        direction = random.choice(["买方", "卖方", "双方"])
        
        # 交易日
        trade_date = generate_block_trade_date(random.randint(0, 60))
        
        # 营业部
        department = random.choice(departments)
        
        trades.append({
            "trade_date": trade_date,
            "trade_price": trade_price,
            "volume": volume,
            "amount": amount,
            "discount_rate": discount_rate,
            "direction": direction,
            "department": department
        })
    
    # 按日期排序
    trades.sort(key=lambda x: x["trade_date"], reverse=True)
    
    # 计算汇总统计
    total_volume = sum(t["volume"] for t in trades)
    total_amount = sum(t["amount"] for t in trades)
    avg_price = round(total_amount / total_volume, 2) if total_volume > 0 else 0
    avg_discount = round(sum(t["discount_rate"] for t in trades) / len(trades), 2)
    
    # 最新价格
    change_pct = round(random.uniform(-5, 5), 2)
    latest_price = round(base_price * (1 + change_pct / 100), 2)
    
    return {
        "code": code,
        "name": info["name"],
        "industry": info["industry"],
        "latest_price": latest_price,
        "prev_close": base_price,
        "change_pct": change_pct,
        "trades": trades,
        "summary": {
            "total_trades": len(trades),
            "total_volume": total_volume,
            "total_amount": total_amount,
            "avg_price": avg_price,
            "avg_discount": avg_discount,
            "max_discount": max(t["discount_rate"] for t in trades),
            "min_discount": min(t["discount_rate"] for t in trades)
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@router.get("/list")
async def get_block_trade_list():
    """
    获取大宗交易列表
    
    返回所有大宗交易记录列表
    
    Returns:
        大宗交易列表数据
    """
    try:
        trade_list = get_mock_block_trade_list()
        
        # 计算汇总数据
        total_volume = sum(item["volume"] for item in trade_list)
        total_amount = sum(item["amount"] for item in trade_list)
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "list": trade_list,
                "total_count": len(trade_list),
                "summary": {
                    "total_volume": total_volume,
                    "total_amount": total_amount,
                    "avg_price": round(total_amount / total_volume, 2) if total_volume > 0 else 0
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
async def get_block_trade_detail(code: str):
    """
    获取个股大宗交易详情
    
    返回指定股票的大宗交易详细数据
    
    Args:
        code: 股票代码
        
    Returns:
        个股大宗交易详情数据
    """
    try:
        detail = get_mock_block_trade_detail(code)
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
