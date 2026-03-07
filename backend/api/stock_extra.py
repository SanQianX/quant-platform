# 股票详情API
"""
提供股票详细信息
"""

from fastapi import APIRouter, HTTPException
from services.stock_service import StockService
from models.response import success_response, error_response

router = APIRouter(prefix="/api/stock", tags=["股票"])

@router.get("/{code}/info")
def get_stock_info(code: str):
    """
    获取股票详细信息
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 股票详细信息
    """
    from database import SessionLocal
    from models.stock import Stock
    
    try:
        db = SessionLocal()
        stock = db.query(Stock).filter(Stock.code == code).first()
        
        if not stock:
            return error_response(f"未找到股票: {code}")
        
        result = {
            "code": stock.code,
            "name": stock.name,
            "market": stock.market,
            "stock_type": stock.stock_type,
            "description": stock.description or "",
            "market_name": "上海证券交易所" if stock.market == "sh" else "深圳证券交易所",
            "type_name": "指数" if stock.stock_type == "index" else "股票"
        }
        
        return success_response(result)
    except Exception as e:
        return error_response(f"获取股票信息失败: {str(e)}")
    finally:
        db.close()

@router.get("/{code}/realtime")
def get_realtime_quotes(code: str):
    """
    获取股票实时行情（模拟）
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 实时行情数据
    """
    import random
    from datetime import datetime
    
    # 模拟实时数据
    base_prices = {
        "600519": 1800, "000001": 12, "300750": 200,
        "600036": 35, "601318": 45, "000858": 150,
        "002594": 250, "600900": 22, "601888": 70, "300059": 20
    }
    
    base = base_prices.get(code, 100)
    now = datetime.now()
    
    result = {
        "code": code,
        "name": code,  # 简化处理
        "price": round(base * (1 + random.uniform(-0.01, 0.01)), 2),
        "change": round(random.uniform(-5, 5), 2),
        "change_percent": round(random.uniform(-3, 3), 2),
        "volume": random.randint(1000000, 50000000),
        "amount": random.randint(100000000, 1000000000),
        "time": now.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return success_response(result)
