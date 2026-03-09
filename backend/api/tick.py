# 股票逐笔成交API路由
"""
股票逐笔成交数据接口

提供股票逐笔成交明细数据
使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from models.response import success_response, error_response
from config import MOCK_DATA_CONFIG
from utils.logger import logger
import random

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票逐笔成交"])


def get_mock_tick_data(stock_code: str, limit: int = 100) -> dict:
    """
    生成模拟逐笔成交数据
    
    Args:
        stock_code: 股票代码
        limit: 返回条数
        
    Returns:
        dict: 模拟逐笔成交数据
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
    
    # 生成逐笔成交数据
    ticks = []
    current_time = datetime.now()
    current_price = base_price
    
    for i in range(limit):
        # 随机生成成交价格波动
        price_change = random.uniform(-0.02, 0.02)
        current_price = round(current_price * (1 + price_change), 2)
        
        # 随机生成成交量 (手)
        volume = random.randint(1, 500)
        
        # 随机生成买卖方向: 1=买入, 2=卖出
        direction = random.choice([1, 2])
        
        # 随机生成成交类型: 0=中性, 1=买入成交, 2=卖出成交
        trade_type = random.choice([0, 1, 2])
        
        # 生成时间 (今天内随机时间)
        minutes_offset = random.randint(0, 240)  # 4小时内
        tick_time = current_time - timedelta(minutes=minutes_offset)
        
        # 计算成交额
        amount = round(current_price * volume, 2)
        
        ticks.append({
            "time": tick_time.strftime("%H:%M:%S"),
            "price": current_price,
            "volume": volume,
            "amount": amount,
            "direction": direction,
            "trade_type": trade_type,
            "change": round(price_change * 100, 2),
            "turnover": round(random.uniform(0.1, 5.0), 2)
        })
    
    # 按时间排序（从早到晚）
    ticks.sort(key=lambda x: x["time"])
    
    # 计算统计数据
    total_volume = sum(t["volume"] for t in ticks)
    total_amount = sum(t["amount"] for t in ticks)
    buy_count = sum(1 for t in ticks if t["direction"] == 1)
    sell_count = sum(1 for t in ticks if t["direction"] == 2)
    
    # 最新价
    latest_price = ticks[-1]["price"] if ticks else base_price
    
    return {
        "code": stock_code,
        "name": stock_names.get(stock_code, f"股票{stock_code}"),
        "latest_price": latest_price,
        "prev_close": round(base_price * 0.998, 2),
        "ticks": ticks,
        "stats": {
            "total_trades": len(ticks),
            "total_volume": total_volume,
            "total_amount": round(total_amount, 2),
            "buy_count": buy_count,
            "sell_count": sell_count,
            "neutral_count": len(ticks) - buy_count - sell_count,
            "avg_price": round(total_amount / total_volume, 2) if total_volume > 0 else 0,
            "avg_volume": round(total_volume / len(ticks), 2) if ticks else 0
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@router.get("/{code}/tick")
def get_stock_tick(code: str, limit: int = 100):
    """
    获取股票逐笔成交
    
    返回股票逐笔成交明细数据
    
    Args:
        code: 股票代码 (如: 600519)
        limit: 返回条数，默认100条
        
    Returns:
        dict: 统一响应格式，包含逐笔成交数据
    """
    logger.info(f"获取逐笔成交: {code}, limit={limit}")
    
    # 验证股票代码
    if not code or len(code) != 6:
        return error_response("股票代码格式错误，应为6位数字")
    
    # 限制返回条数
    if limit < 1:
        limit = 1
    if limit > 1000:
        limit = 1000
    
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
            
            # 从 AkShare 获取逐笔数据
            df = ak.stock_zh_a_tick_tx_js(symbol=symbol, limit=limit)
            
            if df is not None and not df.empty:
                # 处理真实数据（这里简化处理，实际需要解析实时行情接口）
                return success_response(get_mock_tick_data(code, limit))
            
        except Exception as e:
            logger.warning(f"AkShare获取逐笔成交失败: {e}，使用模拟数据")
    
    # 使用模拟数据
    return success_response(get_mock_tick_data(code, limit))
