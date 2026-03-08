# 技术指标 API
"""
常用技术指标接口
- MA: 移动平均线
- MACD: 指数平滑异同移动平均线
- RSI: 相对强弱指标
- BB: 布林带
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from services.stock_service import StockService
from services.technical_indicators import TechnicalIndicators, get_indicators

router = APIRouter(prefix="/api/indicators", tags=["技术指标"])

@router.get("/{code}/ma")
def get_ma_indicators(
    code: str,
    periods: str = Query("5,10,20,60", description="均线周期,逗号分隔"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD")
):
    """
    获取MA均线指标
    
    Args:
        code: 股票代码
        periods: 均线周期,如 "5,10,20,60"
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        MA指标数据
    """
    # 解析周期
    try:
        period_list = [int(p.strip()) for p in periods.split(',')]
    except:
        raise HTTPException(status_code=400, detail="无效的周期参数")
    
    # 获取K线数据
    result = StockService.get_history_kline(code, "daily", start_date, end_date)
    
    # 检查返回
    if isinstance(result, dict):
        if result.get("code") != 0:
            raise HTTPException(status_code=400, detail=result.get("message", "获取数据失败"))
        data = result.get("data", [])
    else:
        data = result
    
    if not data:
        raise HTTPException(status_code=404, detail="没有数据")
    
    # 计算MA指标
    ma_data = TechnicalIndicators.calculate_ma(data, period_list)
    
    return {
        "code": 0,
        "data": ma_data
    }


@router.get("/{code}/macd")
def get_macd_indicators(
    code: str,
    fast: int = Query(12, description="快线周期"),
    slow: int = Query(26, description="慢线周期"),
    signal: int = Query(9, description="信号线周期"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
):
    """
    获取MACD指标
    
    Args:
        code: 股票代码
        fast: 快线周期 (默认12)
        slow: 慢线周期 (默认26)
        signal: 信号线周期 (默认9)
        
    Returns:
        MACD指标数据 (dif, dea, macd)
    """
    # 获取K线数据
    result = StockService.get_history_kline(code, "daily", start_date, end_date)
    
    if isinstance(result, dict):
        if result.get("code") != 0:
            raise HTTPException(status_code=400, detail=result.get("message", "获取数据失败"))
        data = result.get("data", [])
    else:
        data = result
    
    if not data:
        raise HTTPException(status_code=404, detail="没有数据")
    
    # 计算MACD指标
    macd_data = TechnicalIndicators.calculate_macd(data, fast, slow, signal)
    
    return {
        "code": 0,
        "data": macd_data
    }


@router.get("/{code}/rsi")
def get_rsi_indicators(
    code: str,
    periods: str = Query("6,12,24", description="RSI周期,逗号分隔"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
):
    """
    获取RSI指标
    
    Args:
        code: 股票代码
        periods: RSI周期,如 "6,12,24"
        
    Returns:
        RSI指标数据
    """
    # 解析周期
    try:
        period_list = [int(p.strip()) for p in periods.split(',')]
    except:
        raise HTTPException(status_code=400, detail="无效的周期参数")
    
    # 获取K线数据
    result = StockService.get_history_kline(code, "daily", start_date, end_date)
    
    if isinstance(result, dict):
        if result.get("code") != 0:
            raise HTTPException(status_code=400, detail=result.get("message", "获取数据失败"))
        data = result.get("data", [])
    else:
        data = result
    
    if not data:
        raise HTTPException(status_code=404, detail="没有数据")
    
    # 计算RSI指标
    rsi_data = TechnicalIndicators.calculate_rsi(data, period_list)
    
    return {
        "code": 0,
        "data": rsi_data
    }


@router.get("/{code}/bollinger")
def get_bollinger_bands(
    code: str,
    period: int = Query(20, description="布林带周期"),
    std_dev: float = Query(2.0, description="标准差倍数"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
):
    """
    获取布林带指标
    
    Args:
        code: 股票代码
        period: 周期 (默认20)
        std_dev: 标准差倍数 (默认2.0)
        
    Returns:
        布林带数据 (upper, mid, lower)
    """
    # 获取K线数据
    result = StockService.get_history_kline(code, "daily", start_date, end_date)
    
    if isinstance(result, dict):
        if result.get("code") != 0:
            raise HTTPException(status_code=400, detail=result.get("message", "获取数据失败"))
        data = result.get("data", [])
    else:
        data = result
    
    if not data:
        raise HTTPException(status_code=404, detail="没有数据")
    
    # 计算布林带
    bb_data = TechnicalIndicators.calculate_bollinger_bands(data, period, std_dev)
    
    return {
        "code": 0,
        "data": bb_data
    }


@router.get("/{code}/all")
def get_all_indicators(
    code: str,
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
):
    """
    获取所有技术指标
    
    Args:
        code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        所有指标数据
    """
    # 获取K线数据
    result = StockService.get_history_kline(code, "daily", start_date, end_date)
    
    if isinstance(result, dict):
        if result.get("code") != 0:
            raise HTTPException(status_code=400, detail=result.get("message", "获取数据失败"))
        data = result.get("data", [])
    else:
        data = result
    
    if not data:
        raise HTTPException(status_code=404, detail="没有数据")
    
    # 计算所有指标
    indicators = get_indicators(data, ["ma", "macd", "rsi", "bollinger"])
    
    return {
        "code": 0,
        "data": indicators
    }
