# 数据质量监控 API
"""
数据质量检查和因子数据接口
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional
from services.stock_service import StockService
from services.data_quality import DataQualityMonitor
from services.factor_service import FactorService, get_financial_factors

router = APIRouter(prefix="/api/data", tags=["数据质量"])

@router.get("/quality/{code}")
def get_data_quality(
    code: str = Path(..., description="股票代码"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
):
    """
    获取数据质量报告
    
    检查数据完整性和准确性
    """
    # 获取K线数据
    result = StockService.get_history_kline(code, "daily", start_date, end_date)
    
    if isinstance(result, dict):
        if result.get("code") != 0:
            raise HTTPException(status_code=400, detail=result.get("message", "获取数据失败"))
        kline_data = result.get("data", [])
    else:
        kline_data = result
    
    # 生成质量报告
    quality_report = DataQualityMonitor.get_quality_report(code, kline_data)
    
    return {
        "code": 0,
        "data": quality_report
    }


@router.get("/quality/{code}/completeness")
def get_data_completeness(
    code: str = Path(..., description="股票代码"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
):
    """
    获取数据完整性报告
    """
    result = StockService.get_history_kline(code, "daily", start_date, end_date)
    
    if isinstance(result, dict):
        if result.get("code") != 0:
            raise HTTPException(status_code=400, detail=result.get("message"))
        kline_data = result.get("data", [])
    else:
        kline_data = result
    
    completeness = DataQualityMonitor.check_data_completeness(code, kline_data)
    
    return {
        "code": 0,
        "data": completeness
    }


@router.get("/quality/{code}/accuracy")
def get_data_accuracy(
    code: str = Path(..., description="股票代码"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
):
    """
    获取数据准确性报告
    """
    result = StockService.get_history_kline(code, "daily", start_date, end_date)
    
    if isinstance(result, dict):
        if result.get("code") != 0:
            raise HTTPException(status_code=400, detail=result.get("message"))
        kline_data = result.get("data", [])
    else:
        kline_data = result
    
    accuracy = DataQualityMonitor.check_data_accuracy(code, kline_data)
    
    return {
        "code": 0,
        "data": accuracy
    }


@router.get("/factors/{code}/technical")
def get_technical_factors(
    code: str = Path(..., description="股票代码"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
):
    """
    获取技术因子数据
    """
    result = StockService.get_history_kline(code, "daily", start_date, end_date)
    
    if isinstance(result, dict):
        if result.get("code") != 0:
            raise HTTPException(status_code=400, detail=result.get("message"))
        kline_data = result.get("data", [])
    else:
        kline_data = result
    
    factors = FactorService.get_technical_factors(kline_data)
    
    return {
        "code": 0,
        "data": factors
    }


@router.get("/factors/{code}/momentum")
def get_momentum_factors(
    code: str = Path(..., description="股票代码"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
):
    """
    获取动量因子数据
    """
    result = StockService.get_history_kline(code, "daily", start_date, end_date)
    
    if isinstance(result, dict):
        if result.get("code") != 0:
            raise HTTPException(status_code=400, detail=result.get("message"))
        kline_data = result.get("data", [])
    else:
        kline_data = result
    
    factors = FactorService.get_momentum_factors(kline_data)
    
    return {
        "code": 0,
        "data": factors
    }


@router.get("/factors/{code}/volume")
def get_volume_factors(
    code: str = Path(..., description="股票代码"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
):
    """
    获取成交量因子数据
    """
    result = StockService.get_history_kline(code, "daily", start_date, end_date)
    
    if isinstance(result, dict):
        if result.get("code") != 0:
            raise HTTPException(status_code=400, detail=result.get("message"))
        kline_data = result.get("data", [])
    else:
        kline_data = result
    
    factors = FactorService.get_volume_factors(kline_data)
    
    return {
        "code": 0,
        "data": factors
    }


@router.get("/factors/{code}/all")
def get_all_factors(
    code: str = Path(..., description="股票代码"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
):
    """
    获取所有因子数据
    """
    result = StockService.get_history_kline(code, "daily", start_date, end_date)
    
    if isinstance(result, dict):
        if result.get("code") != 0:
            raise HTTPException(status_code=400, detail=result.get("message"))
        kline_data = result.get("data", [])
    else:
        kline_data = result
    
    factors = FactorService.get_all_factors(kline_data)
    
    return {
        "code": 0,
        "data": factors
    }


@router.get("/factors/{code}/financial")
def get_financial_factors(
    code: str = Path(..., description="股票代码")
):
    """
    获取财务因子数据
    """
    factors = get_financial_factors(code)
    
    return {
        "code": 0,
        "data": factors
    }
