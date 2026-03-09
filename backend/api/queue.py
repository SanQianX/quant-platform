# 股票委托队列API路由
"""
股票委托队列数据接口

提供股票委托队列数据（更多档位的买卖盘委托）
使用模拟数据

委托队列与五档买卖盘的区别：
- 五档买卖盘：显示买一至买五、卖一至卖五（共10档）
- 委托队列：显示更多档位（如前50档），可以看到更完整的订单簿结构
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from models.response import success_response, error_response
from config import MOCK_DATA_CONFIG
from utils.logger import logger
import random

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票委托队列"])

# 默认委托队列深度
DEFAULT_QUEUE_DEPTH = 50
MAX_QUEUE_DEPTH = 100


def get_mock_queue_data(stock_code: str, depth: int = 50) -> dict:
    """
    生成模拟委托队列数据
    
    委托队列显示更深的订单簿，包括：
    - 卖盘：从低到高排列的卖出委托
    - 买盘：从高到低排列的买入委托
    
    Args:
        stock_code: 股票代码
        depth: 委托队列深度，默认50档
        
    Returns:
        dict: 模拟委托队列数据
    """
    # 限制深度
    if depth < 1:
        depth = 1
    if depth > MAX_QUEUE_DEPTH:
        depth = MAX_QUEUE_DEPTH
    
    # 基于股票代码生成稳定的随机数
    seed = int(stock_code) if stock_code.isdigit() else hash(stock_code) % 10000
    random.seed(seed)
    
    # 常用股票基础价格
    base_prices = {
        "600519": 1850.0,
        "000001": 12.5,
        "300750": 210.0,
        "600036": 36.0,
        "601318": 46.0,
        "000858": 155.0,
        "002594": 260.0,
        "600900": 23.0,
        "601888": 72.0,
        "300059": 21.0,
        "600036": 36.5,
        "601166": 18.5,
        "600030": 15.2,
        "600016": 28.8,
        "601012": 45.6,
        "600028": 8.2,
        "601857": 12.8,
        "600050": 5.8,
        "601766": 28.5,
        "601398": 5.2,
    }
    base_price = base_prices.get(stock_code, 50.0)
    
    # 股票名称映射
    stock_names = {
        "600519": "贵州茅台",
        "000001": "平安银行",
        "300750": "宁德时代",
        "600036": "招商银行",
        "601318": "中国平安",
        "000858": "五粮液",
        "002594": "比亚迪",
        "600900": "长江电力",
        "601888": "中国中免",
        "300059": "东方财富",
        "600036": "招商银行",
        "601166": "兴业银行",
        "600030": "中信证券",
        "600016": "民生银行",
        "601012": "隆基绿能",
        "600028": "中国石化",
        "601857": "中国石油",
        "600050": "中国联通",
        "601766": "中国中车",
        "601398": "工商银行",
    }
    
    # 计算最新价格和昨日收盘价
    latest_price = round(base_price * (1 + random.uniform(-0.01, 0.01)), 2)
    prev_close = round(base_price * 0.998, 2)
    
    # 生成卖盘价格（从低到高）
    ask_prices = []
    for i in range(depth):
        # 卖盘价格递增，间隔0.01-0.03元
        if i == 0:
            price = latest_price
        else:
            price = round(ask_prices[i-1] + random.uniform(0.01, 0.03), 2)
        ask_prices.append(price)
    
    # 生成买盘价格（从高到低）
    bid_prices = []
    for i in range(depth):
        if i == 0:
            price = latest_price
        else:
            price = round(bid_prices[i-1] - random.uniform(0.01, 0.03), 2)
        bid_prices.append(price)
    
    # 生成卖盘数据
    ask = []
    total_ask_volume = 0
    total_ask_amount = 0
    for i in range(depth):
        # 随机委托数量，距离现价越远数量越少
        distance_factor = 1.0 / (1 + i * 0.1)
        volume = random.randint(100, int(100000 * distance_factor))
        price = ask_prices[i]
        amount = round(price * volume, 2)
        orders = random.randint(5, int(200 * distance_factor))
        
        total_ask_volume += volume
        total_ask_amount += amount
        
        ask.append({
            "position": i + 1,  # 档位位置
            "price": price,
            "volume": volume,
            "amount": amount,
            "orders": orders,
            "volume_ratio": round(volume / 10000, 4)  # 万手比
        })
    
    # 生成买盘数据
    bid = []
    total_bid_volume = 0
    total_bid_amount = 0
    for i in range(depth):
        # 随机委托数量，距离现价越远数量越少
        distance_factor = 1.0 / (1 + i * 0.1)
        volume = random.randint(100, int(100000 * distance_factor))
        price = bid_prices[i]
        amount = round(price * volume, 2)
        orders = random.randint(5, int(200 * distance_factor))
        
        total_bid_volume += volume
        total_bid_amount += amount
        
        bid.append({
            "position": i + 1,  # 档位位置
            "price": price,
            "volume": volume,
            "amount": amount,
            "orders": orders,
            "volume_ratio": round(volume / 10000, 4)  # 万手比
        })
    
    # 计算买卖价差
    spread = round(ask_prices[0] - bid_prices[0], 2)
    spread_pct = round((ask_prices[0] - bid_prices[0]) / latest_price * 100, 2)
    
    # 计算委托队列密度分析
    # 买一至买五占比
    bid_top5_volume = sum(b["volume"] for b in bid[:5])
    bid_top5_ratio = round(bid_top5_volume / total_bid_volume * 100, 2) if total_bid_volume > 0 else 0
    
    # 卖一至卖五占比
    ask_top5_volume = sum(a["volume"] for a in ask[:5])
    ask_top5_ratio = round(ask_top5_volume / total_ask_volume * 100, 2) if total_ask_volume > 0 else 0
    
    # 委比（买入委托总量/卖出委托总量-1）
    if total_ask_volume > 0:
        committee_ratio = round((total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume) * 100, 2)
    else:
        committee_ratio = 100.0
    
    # 内外盘
    # 内盘：主动卖出（价格<=买一）
    # 外盘：主动买入（价格>=卖一）
    inner_volume = int(total_ask_volume * 0.4)  # 假设内盘占40%
    outer_volume = int(total_bid_volume * 0.6)  # 假设外盘占60%
    
    return {
        "code": stock_code,
        "name": stock_names.get(stock_code, f"股票{stock_code}"),
        "latest_price": latest_price,
        "prev_close": prev_close,
        "change": round(latest_price - prev_close, 2),
        "change_pct": round((latest_price - prev_close) / prev_close * 100, 2),
        "depth": depth,
        "ask": ask,
        "bid": bid,
        "summary": {
            "total_ask_volume": total_ask_volume,
            "total_bid_volume": total_bid_volume,
            "total_ask_amount": round(total_ask_amount, 2),
            "total_bid_amount": round(total_bid_amount, 2),
            "spread": spread,
            "spread_pct": spread_pct,
            "bid_top5_ratio": bid_top5_ratio,
            "ask_top5_ratio": ask_top5_ratio,
            "committee_ratio": committee_ratio,
            "inner_volume": inner_volume,
            "outer_volume": outer_volume,
            "inner_ratio": round(inner_volume / (inner_volume + outer_volume) * 100, 2) if (inner_volume + outer_volume) > 0 else 0,
            "outer_ratio": round(outer_volume / (inner_volume + outer_volume) * 100, 2) if (inner_volume + outer_volume) > 0 else 0
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@router.get("/{code}/queue")
def get_stock_queue(
    code: str,
    depth: int = Query(DEFAULT_QUEUE_DEPTH, ge=1, le=MAX_QUEUE_DEPTH, description="委托队列深度，默认50档")
):
    """
    获取股票委托队列
    
    返回股票的深度委托队列数据，显示更多档位的买卖盘委托
    
    委托队列与五档买卖盘的区别：
    - 五档买卖盘：仅显示买一至买五、卖一至卖五（共10档）
    - 委托队列：显示指定深度的订单簿，默认50档，最多100档
    
    Args:
        code: 股票代码 (如: 600519)
        depth: 委托队列深度，默认50档，可选1-100
        
    Returns:
        dict: 统一响应格式，包含委托队列数据
    """
    logger.info(f"获取委托队列: {code}, depth={depth}")
    
    # 验证股票代码
    if not code or len(code) != 6:
        return error_response("股票代码格式错误，应为6位数字")
    
    # 检查是否启用模拟数据
    if not MOCK_DATA_CONFIG["enabled"]:
        # 如果未启用模拟数据，尝试从真实数据源获取
        try:
            import akshare as ak
            
            # 确定市场
            if code.startswith("6"):
                symbol = f"sh{code}"
            else:
                symbol = f"sz{code}"
            
            # 从 AkShare 获取委托队列数据（需要深度数据接口）
            # 这里简化处理，实际需要解析 Level 2 行情数据
            logger.info(f"使用 AkShare 获取 {symbol} 委托队列数据")
            
        except Exception as e:
            logger.warning(f"AkShare获取委托队列失败: {e}，使用模拟数据")
    
    # 使用模拟数据
    return success_response(get_mock_queue_data(code, depth))
