# 涨跌停价格API路由
"""
涨跌停价格数据接口

提供股票今日涨跌停价格查询
"""

from fastapi import APIRouter, Path, HTTPException
import random
from datetime import datetime
from models.response import success_response, error_response
from config import MOCK_DATA_CONFIG
from utils.logger import logger

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票涨跌停价格"])


def get_stock_limit_price(stock_code: str) -> dict:
    """
    获取股票涨跌停价格
    
    Args:
        stock_code: 股票代码
        
    Returns:
        dict: 涨跌停价格数据
    """
    # 基于股票代码生成稳定的随机数
    seed = int(stock_code) if stock_code.isdigit() else hash(stock_code) % 10000
    random.seed(seed)
    
    # 判断股票所属板块和涨跌幅限制
    limit_rate = 10.0  # 默认主板 ±10%
    
    # ST股票
    if "ST" in stock_code or "*ST" in stock_code:
        limit_rate = 5.0
    # 科创板 (688xxx)
    elif stock_code.startswith("688"):
        limit_rate = 20.0
    # 创业板 (300xxx)
    elif stock_code.startswith("300"):
        limit_rate = 20.0
    # 北交所 (8xxxxx, 4xxxxx)
    elif stock_code.startswith("8") or stock_code.startswith("4"):
        limit_rate = 30.0
    
    # 基础价格 (模拟昨日收盘价)
    base_prices = {
        "600519": 1850.0,
        "000001": 12.50,
        "300750": 210.0,
        "600036": 36.00,
        "601318": 46.00,
        "000858": 155.0,
        "002594": 260.0,
        "600900": 23.00,
        "601888": 72.00,
        "300059": 21.00,
    }
    base_price = base_prices.get(stock_code, round(random.uniform(10, 100), 2))
    
    # 计算涨跌停价格
    limit_up = round(base_price * (1 + limit_rate / 100), 2)
    limit_down = round(base_price * (1 - limit_rate / 100), 2)
    
    # 获取当前日期
    today = datetime.now().strftime("%Y-%m-%d")
    
    return {
        "code": stock_code,
        "date": today,
        "base_price": base_price,        # 昨收价/基准价
        "limit_rate": limit_rate,        # 涨跌幅限制(%)
        "limit_up": limit_up,            # 涨停价
        "limit_down": limit_down,        # 跌停价
        "price_change": round(limit_up - base_price, 2),   # 涨停涨幅
        "price_change_ratio": limit_rate,                     # 涨幅比例(%)
    }


@router.get("/{code}/limit-price")
def get_limit_price(code: str = Path(..., description="股票代码", min_length=1, max_length=20)):
    """
    获取股票涨跌停价格
    
    获取指定股票今日的涨停价和跌停价
    
    A股涨跌幅限制:
    - 主板: ±10%
    - ST股票: ±5%
    - 科创板/创业板: ±20%
    - 北交所: ±30%
    
    Args:
        code: 股票代码 (如: 600519, 000001, 300750)
        
    Returns:
        dict: 统一响应格式，包含涨跌停价格信息
    """
    try:
        data = get_stock_limit_price(code)
        return success_response(data, "涨跌停价格查询成功")
    except Exception as e:
        logger.error(f"获取涨跌停价格失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取涨跌停价格失败: {str(e)}")
