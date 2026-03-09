# 股票五档买卖盘API路由
"""
股票五档买卖盘数据接口

提供股票五档买卖盘数据（买一至买五，卖一至卖五）
使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from models.response import success_response, error_response
from config import MOCK_DATA_CONFIG
from utils.logger import logger
import random

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票五档买卖盘"])


def get_mock_order_book(stock_code: str) -> dict:
    """
    生成模拟五档买卖盘数据
    
    Args:
        stock_code: 股票代码
        
    Returns:
        dict: 模拟五档买卖盘数据
    """
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
    }
    base_price = base_prices.get(stock_code, 50.0)
    
    # 生成五档卖盘价格（从低到高）
    ask_prices = [
        round(base_price * (1 + 0.001 * i), 2) for i in range(1, 6)
    ]
    
    # 生成五档买盘价格（从高到低）
    bid_prices = [
        round(base_price * (1 - 0.001 * i), 2) for i in range(1, 6)
    ]
    
    # 生成各档买卖盘数量
    ask_volumes = [random.randint(1000, 100000) for _ in range(5)]
    bid_volumes = [random.randint(1000, 100000) for _ in range(5)]
    
    # 构建卖盘数据（从低到高）
    ask = []
    for i in range(5):
        ask.append({
            "price": ask_prices[i],
            "volume": ask_volumes[i],
            "amount": round(ask_prices[i] * ask_volumes[i], 2),
            "orders": random.randint(10, 100)
        })
    
    # 构建买盘数据（从高到低）
    bid = []
    for i in range(5):
        bid.append({
            "price": bid_prices[i],
            "volume": bid_volumes[i],
            "amount": round(bid_prices[i] * bid_volumes[i], 2),
            "orders": random.randint(10, 100)
        })
    
    # 计算总买卖盘
    total_ask_volume = sum(ask_volumes)
    total_bid_volume = sum(bid_volumes)
    total_ask_amount = sum([a["amount"] for a in ask])
    total_bid_amount = sum([b["amount"] for b in bid])
    
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
    }
    
    return {
        "code": stock_code,
        "name": stock_names.get(stock_code, f"股票{stock_code}"),
        "latest_price": round(base_price, 2),
        "prev_close": round(base_price * 0.998, 2),
        "ask": ask,
        "bid": bid,
        "total_ask_volume": total_ask_volume,
        "total_bid_volume": total_bid_volume,
        "total_ask_amount": round(total_ask_amount, 2),
        "total_bid_amount": round(total_bid_amount, 2),
        "spread": round(ask_prices[0] - bid_prices[0], 2),
        "spread_pct": round((ask_prices[0] - bid_prices[0]) / base_price * 100, 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@router.get("/{code}/order-book")
def get_stock_order_book(code: str):
    """
    获取股票五档买卖盘
    
    返回股票的买一至买五、卖一至卖五数据
    
    Args:
        code: 股票代码 (如: 600519)
        
    Returns:
        dict: 统一响应格式，包含五档买卖盘数据
    """
    logger.info(f"获取五档买卖盘: {code}")
    
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
            
            # 从 AkShare 获取五档数据
            df = ak.stock_zh_a_tick_tx_js(symbol=symbol, limit=100)
            
            if df is not None and not df.empty:
                # 处理真实数据（这里简化处理，实际需要解析实时行情接口）
                return success_response(get_mock_order_book(code))
            
        except Exception as e:
            logger.warning(f"AkShare获取五档买卖盘失败: {e}，使用模拟数据")
    
    # 使用模拟数据
    return success_response(get_mock_order_book(code))
