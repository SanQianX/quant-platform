# 股票复权数据API路由
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
import random

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票复权"])


def _generate_kline_data(code: str, adj_type: str, days: int = 100):
    """
    生成模拟K线数据
    
    Args:
        code: 股票代码
        adj_type: 复权类型 (forward/backward)
        days: 数据天数
        
    Returns:
        list: K线数据列表
    """
    data = []
    base_price = random.uniform(10, 100)
    today = datetime.now()
    
    # 复权因子 (模拟)
    if adj_type == "forward":
        # 前复权：价格会逐渐降低
        adj_factor = random.uniform(0.8, 1.2)
    else:
        # 后复权：价格会逐渐升高
        adj_factor = random.uniform(1.0, 1.5)
    
    for i in range(days, 0, -1):
        date = today - timedelta(days=i)
        
        # 生成价格数据
        open_price = base_price * random.uniform(0.95, 1.05)
        close_price = base_price * random.uniform(0.95, 1.05)
        high_price = max(open_price, close_price) * random.uniform(1.0, 1.03)
        low_price = min(open_price, close_price) * random.uniform(0.97, 1.0)
        volume = random.randint(1000000, 50000000)
        
        # 应用复权因子
        if adj_type == "forward":
            # 前复权：历史价格向当前价格靠拢
            factor = adj_factor ** (i / days)
            open_price = round(open_price * factor, 2)
            close_price = round(close_price * factor, 2)
            high_price = round(high_price * factor, 2)
            low_price = round(low_price * factor, 2)
        else:
            # 后复权：当前价格向历史价格靠拢
            factor = adj_factor ** (i / days)
            open_price = round(open_price * factor, 2)
            close_price = round(close_price * factor, 2)
            high_price = round(high_price * factor, 2)
            low_price = round(low_price * factor, 2)
        
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": volume,
            "amount": round(volume * close_price, 2),
            "adj_factor": round(factor, 6) if adj_type == "forward" else round(1/factor, 6)
        })
        
        # 更新基础价格
        base_price = close_price
    
    return data


@router.get("/{code}/adj/forward")
def get_forward_adj_data(
    code: str,
    days: int = Query(100, ge=1, le=500, description="返回数据天数，默认100天")
):
    """
    获取股票前复权K线数据
    
    前复权：将历史K线数据按照最新的复权因子进行调整，
    使其与当前价格保持一致，便于技术分析
    
    Args:
        code: 股票代码 (如: 000001)
        days: 返回数据天数
        
    Returns:
        dict: 统一响应格式，包含前复权K线数据
    """
    # 验证股票代码
    if not code or not code.isdigit() or len(code) != 6:
        raise HTTPException(status_code=400, detail="股票代码格式错误，应为6位数字")
    
    # 生成模拟数据
    kline_data = _generate_kline_data(code, "forward", days)
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "code": code,
            "name": f"股票{code}",
            "adj_type": "forward",
            "adj_name": "前复权",
            "description": "前复权：保持当前价格不变，将历史价格按复权因子向上调整",
            "data": kline_data
        }
    }


@router.get("/{code}/adj/backward")
def get_backward_adj_data(
    code: str,
    days: int = Query(100, ge=1, le=500, description="返回数据天数，默认100天")
):
    """
    获取股票后复权K线数据
    
    后复权：将最新K线数据按照历史的复权因子进行调整，
    使其与历史价格保持一致，便于与历史数据比较
    
    Args:
        code: 股票代码 (如: 000001)
        days: 返回数据天数
        
    Returns:
        dict: 统一响应格式，包含后复权K线数据
    """
    # 验证股票代码
    if not code or not code.isdigit() or len(code) != 6:
        raise HTTPException(status_code=400, detail="股票代码格式错误，应为6位数字")
    
    # 生成模拟数据
    kline_data = _generate_kline_data(code, "backward", days)
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "code": code,
            "name": f"股票{code}",
            "adj_type": "backward",
            "adj_name": "后复权",
            "description": "后复权：保持历史价格不变，将当前价格按复权因子向下调整",
            "data": kline_data
        }
    }


@router.get("/{code}/adj/info")
def get_adj_info(code: str):
    """
    获取股票复权信息
    
    返回股票的复权因子、分红送股等信息
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 统一响应格式，包含复权信息
    """
    # 验证股票代码
    if not code or not code.isdigit() or len(code) != 6:
        raise HTTPException(status_code=400, detail="股票代码格式错误，应为6位数字")
    
    # 生成模拟复权信息
    return {
        "code": 0,
        "message": "success",
        "data": {
            "code": code,
            "name": f"股票{code}",
            "forward_factor": round(random.uniform(1.0, 2.0), 6),
            "backward_factor": round(random.uniform(0.5, 1.0), 6),
            "last_dividend_date": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "last_split_date": (datetime.now() - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d"),
            "split_count": random.randint(0, 10),
            "dividend_count": random.randint(0, 20)
        }
    }
